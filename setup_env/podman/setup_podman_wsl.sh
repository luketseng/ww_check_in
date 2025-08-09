#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "Podman Setup for WSL (Ubuntu)"
echo "=================================================="

# 1) Basic checks
if ! grep -qi microsoft /proc/version; then
  echo "⚠️  This does not look like WSL. Continuing anyway..."
fi

source /etc/os-release || true
if [[ "${ID:-}" != "ubuntu" ]]; then
  echo "⚠️  Detected non-Ubuntu distro (${ID:-unknown}). Script is tuned for Ubuntu 20.04/22.04+"
fi

echo "🔧 Installing packages (sudo required): podman, uidmap, slirp4netns, fuse-overlayfs"
sudo apt-get update -y
sudo apt-get install -y podman uidmap slirp4netns fuse-overlayfs

# 2) Ensure subuid/subgid for rootless
if ! grep -q "^${USER}:" /etc/subuid 2>/dev/null; then
  echo "👤 Adding subuid for ${USER}"
  echo "${USER}:100000:65536" | sudo tee -a /etc/subuid >/dev/null
fi
if ! grep -q "^${USER}:" /etc/subgid 2>/dev/null; then
  echo "👤 Adding subgid for ${USER}"
  echo "${USER}:100000:65536" | sudo tee -a /etc/subgid >/dev/null
fi

# 3) Configure rootless storage
mkdir -p "$HOME/.config/containers"

OVERLAY_CONF="$HOME/.config/containers/storage.conf"
VFS_CONF="$HOME/.config/containers/storage_vfs.conf"

if [[ ! -f "$OVERLAY_CONF" ]]; then
  cat >"$OVERLAY_CONF" <<'EOF'
[storage]
driver = "overlay"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
  echo "✅ Wrote $OVERLAY_CONF (overlay + fuse-overlayfs)"
else
  echo "ℹ️  $OVERLAY_CONF already exists, leaving as-is"
fi

if [[ ! -f "$VFS_CONF" ]]; then
  cat >"$VFS_CONF" <<'EOF'
[storage]
driver = "vfs"
EOF
  echo "✅ Wrote $VFS_CONF (vfs)"
else
  echo "ℹ️  $VFS_CONF already exists, leaving as-is"
fi

# 4) Create wrapper that auto-selects storage driver based on path (/mnt/* → vfs)
mkdir -p "$HOME/.local/bin"
WRAPPER="$HOME/.local/bin/podman-wsl"
cat >"$WRAPPER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Use vfs on Windows-mounted paths (/mnt/*), overlay on native Linux paths
if [[ "${PWD:-}" =~ ^/mnt/ ]]; then
  export CONTAINERS_STORAGE_CONF="$HOME/.config/containers/storage_vfs.conf"
else
  export CONTAINERS_STORAGE_CONF="$HOME/.config/containers/storage.conf"
fi

exec podman "$@"
EOF
chmod +x "$WRAPPER"
echo "✅ Installed wrapper: $WRAPPER"

# 5) Ensure ~/.local/bin on PATH
if ! grep -q "\.local/bin" "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  echo "✅ Added ~/.local/bin to PATH in ~/.bashrc (restart shell or: source ~/.bashrc)"
else
  echo "ℹ️  ~/.local/bin already on PATH"
fi

# 6) Configure registries (short-name) and containers engine
mkdir -p "$HOME/.config/containers"

REG_CONF="$HOME/.config/containers/registries.conf"
if [[ ! -f "$REG_CONF" ]]; then
  cat >"$REG_CONF" <<'EOF'
unqualified-search-registries = ["docker.io"]
short-name-mode = "permissive"
EOF
  echo "✅ Wrote $REG_CONF (short-name permissive; default registry docker.io)"
else
  echo "ℹ️  $REG_CONF already exists, leaving as-is"
fi

ENG_CONF="$HOME/.config/containers/containers.conf"
if [[ ! -f "$ENG_CONF" ]]; then
  cat >"$ENG_CONF" <<'EOF'
[engine]
cgroup_manager = "cgroupfs"
events_logger = "file"
EOF
  echo "✅ Wrote $ENG_CONF (cgroupfs + file events logger)"
else
  echo "ℹ️  $ENG_CONF already exists, leaving as-is"
fi

# 7) Quick info
echo ""
echo "💡 Usage tips:"
echo "- Use 'podman-wsl' (wrapper) when working under /mnt/* to avoid overlayfs issues."
echo "- For best performance, keep the project under your Linux home (e.g., ~/projects)."
echo ""
echo "🔍 Driver check:"
echo "  podman-wsl info | grep -E 'store:\\s+GraphDriverName'"
echo "  (should show 'overlay' on Linux paths, 'vfs' on /mnt/*)"
echo ""
echo "✅ Podman WSL setup completed."
