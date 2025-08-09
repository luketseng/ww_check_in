#!/usr/bin/env python3
"""
Simple script to run check-in with manual punch type selection
"""
import sys
from test_check_in_complete import test_check_in


def main():
    # 檢查命令行參數
    if len(sys.argv) > 1:
        punch_type = sys.argv[1]
        if punch_type not in ["Time-In", "Time-Out", "auto"]:
            print("❌ 無效的參數！請使用 'Time-In'、'Time-Out' 或 'auto'")
            print("用法: python run_check_in.py [Time-In|Time-Out|auto]")
            print("範例:")
            print("  python run_check_in.py Time-In   # 上班打卡")
            print("  python run_check_in.py Time-Out  # 下班打卡")
            print("  python run_check_in.py auto      # 自動判斷")
            print("  python run_check_in.py           # 互動模式")
            sys.exit(1)

        if punch_type == "auto":
            print("🕐 使用自動判斷模式...")
            success = test_check_in()
        else:
            print(f"🎯 使用指定參數: {punch_type}")
            success = test_check_in(punch_type)

        if success:
            print("🎉 打卡測試完成！")
        else:
            print("💥 打卡測試失敗！")
            sys.exit(1)
        return

    # 互動模式
    print("=== WW打卡系統 ===")
    print("請選擇打卡類型：")
    print("1. 上班打卡 (Time-In)")
    print("2. 下班打卡 (Time-Out)")
    print("3. 自動判斷 (根據當前時間)")
    print("4. 退出")

    while True:
        choice = input("\n請輸入選項 (1-4): ").strip()

        if choice == "1":
            print("🕐 執行上班打卡...")
            success = test_check_in("Time-In")
            break
        elif choice == "2":
            print("🕐 執行下班打卡...")
            success = test_check_in("Time-Out")
            break
        elif choice == "3":
            print("🕐 根據時間自動判斷...")
            success = test_check_in()
            break
        elif choice == "4":
            print("👋 再見！")
            sys.exit(0)
        else:
            print("❌ 無效選項，請重新選擇")

    if success:
        print("🎉 打卡測試完成！")
    else:
        print("💥 打卡測試失敗！")
        sys.exit(1)


if __name__ == "__main__":
    main()
