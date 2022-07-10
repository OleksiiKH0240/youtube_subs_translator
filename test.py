import os
import subprocess

import ctypes, sys
import time

command2connect = r'wireguard /installtunnelservice "D:\GoogleDrive\PythonPr\youtube_subs_translator\resources\WireGuardConfFiles\JP-FREE_6.conf"'
command2disconnect = 'wireguard /uninstalltunnelservice "JP-FREE_6"'

# ctypes.windll.shell32.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c ' + command2connect)
# ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
# print(ctypes.windll.shell32.IsUserAnAdmin())
# input()
# ctypes.windll.shell32.ShellExecuteW(None, None, "cmd.exe", "/c " + command2connect, None, 1)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if is_admin():
    # Code of your program here
    ctypes.windll.shell32.ShellExecuteW(None, None, "cmd.exe", "/c " + command2connect, None, 1)
    time.sleep(20)
    ctypes.windll.shell32.ShellExecuteW(None, None, "cmd.exe", "/c " + command2disconnect, None, 1)


else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
