#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "Podman Setup for macOS or Ubuntu"
echo "=================================================="

OS_NAME="$(uname -s)" || OS_NAME=""

if [[ "$OS_NAME" == "Darwin" ]]; then
  echo "🔎 Detected macOS"
  # Homebrew
  if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew not found. Please install from https://brew.sh then re-run."
    exit 1
  fi

  echo "📦 Installing Podman via Homebrew..."
  brew install podman || true

  echo "🖥️  Initializing Podman machine (if needed)..."
  podman machine inspect >/dev/null 2>&1 || podman machine init
  podman machine start

  echo "✅ macOS Podman setup completed"
  echo ""
  echo "Next: build and run"
  echo "  podman build -t ww-check-in:offline-v1 ."
  echo "  podman run --rm \
    --env-file ./.env \
    -e HEADLESS=\${HEADLESS:-true} \
    -v \"$PWD:/app\" \
    -v \"$PWD/logs:/app/logs\" \
    ww-check-in:offline-v1"
  exit 0
fi

if [[ "$OS_NAME" == "Linux" ]]; then
  source /etc/os-release || true
  if [[ "${ID:-}" != "ubuntu" ]]; then
    echo "⚠️  Non-Ubuntu Linux detected (${ID:-unknown}). This script targets Ubuntu."
  else
    echo "🔎 Detected Ubuntu"
  fi

  echo "📦 Installing Podman (sudo required)..."
  sudo apt-get update -y
  sudo apt-get install -y podman uidmap slirp4netns fuse-overlayfs

  echo "👤 Ensuring subuid/subgid for rootless..."
  if ! grep -q "^${USER}:" /etc/subuid 2>/dev/null; then
    echo "${USER}:100000:65536" | sudo tee -a /etc/subuid >/dev/null
  fi
  if ! grep -q "^${USER}:" /etc/subgid 2>/dev/null; then
    echo "${USER}:100000:65536" | sudo tee -a /etc/subgid >/dev/null
  fi

  echo "🗂️  Configuring rootless storage & registries..."
  mkdir -p "$HOME/.config/containers"

  # storage (overlay with fuse-overlayfs)
  cat >"$HOME/.config/containers/storage.conf" <<'EOF'
[storage]
driver = "overlay"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF

  # registries (short-name permissive to docker.io)
  cat >"$HOME/.config/containers/registries.conf" <<'EOF'
unqualified-search-registries = ["docker.io"]
short-name-mode = "permissive"
EOF

  # engine
  cat >"$HOME/.config/containers/containers.conf" <<'EOF'
[engine]
cgroup_manager = "cgroupfs"
events_logger = "file"
EOF

  echo "✅ Ubuntu Podman setup completed"
  echo ""
  echo "Next: build and run"
  echo "  podman build -t ww-check-in:offline-v1 ."
  echo "  podman run --rm \
    --env-file ./.env \
    -e HEADLESS=\${HEADLESS:-true} \
    -v \"$PWD:/app\" \
    -v \"$PWD/logs:/app/logs\" \
    ww-check-in:offline-v1"
  exit 0
fi

echo "❌ Unsupported OS: $OS_NAME"
exit 1


