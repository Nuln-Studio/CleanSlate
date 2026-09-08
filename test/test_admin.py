import ctypes
print(bool(ctypes.windll.shell32.IsUserAnAdmin()))
input()