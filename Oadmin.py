import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        print("当前未使用管理员权限运行，程序将退出，请右键以管理员身份重新打开")
        input()
        sys.exit(1)
    from main import main
    main()