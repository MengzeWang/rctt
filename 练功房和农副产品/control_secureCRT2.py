import os
import win32api
import win32con
import win32gui
SECURE_CRT_WND_NAME = 'VanDyke Software - SecureCRT'
SECURE_CRT_WND_NAME2='192.168.23.121 - SecureCRT'

def SendKeyToWnd(hCmdWin, keyValue):
    win32api.SendMessage(hCmdWin, win32con.WM_CHAR, keyValue, 1)  # chr(65) rd('l')

def SendStringToWnd(hCmdWin, cmdString):
    if len(cmdString) == 0 or None == hCmdWin:
        return
    for key in cmdString:
        SendKeyToWnd(hCmdWin, ord(key))
    SendKeyToWnd(hCmdWin, 10) # SendKeyToWnd(hWnd, 13)

def SendCmdToSecureCRT(cmdString):
    hSecureCRTWnd = win32gui.FindWindow(None,SECURE_CRT_WND_NAME)
    if None == hSecureCRTWnd:
        return;
    hCmdWndParent = win32gui.FindWindowEx(hSecureCRTWnd, None, 'MDIClient', None)
    if 0 == hCmdWndParent:
        # SecureCRT V6.2
        hCmdWnd = win32gui.FindWindowEx(hSecureCRTWnd, None, 'AfxFrameOrView90u', None)
        if None != hCmdWnd :
            SendStringToWnd(hCmdWnd, cmdString)
    else:
        # SecureCRT V7.3
        win32gui.EnumChildWindows(hCmdWndParent, EnumTabCtrlChildWinProc, cmdString)

    #win32gui.SetForegroundWindow(hSecureCRTWnd)
    # win32gui.SetWindowPos(hSecureCRTWnd, win32con.HWND_TOP, 0,0,0,0,  win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

def EnumTabCtrlChildWinProc(hWnd, cmdString):
    if IsSecureCRTTopCmdWnd(hWnd):
        SendStringToWnd(hWnd, cmdString)
def IsSecureCRTTopCmdWnd(hWnd):
    # no effect: win32gui.IsWindowEnabled(hWnd)  win32gui.IsWindowVisible(hWnd)
    if 'AfxFrameOrView120u' != win32gui.GetClassName(hWnd):
        return False
    if 0 != win32gui.GetWindow(win32gui.GetParent(hWnd), win32con.GW_HWNDPREV):
        return False
    return True
if __name__=='__main__':
    SendCmdToSecureCRT('aa')