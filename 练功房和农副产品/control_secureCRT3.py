import win32api,win32con,win32gui,time
hn=win32gui.FindWindow(None,'192.168.23.121 - SecureCRT')    #查找到桌面上10.20.1.33 - SecureCRT的窗口
win32gui.ShowWindow(hn,win32con.SW_SHOWNORMAL)    #正常显示这个窗口
time.sleep(1)
hWndChildList = []  
win32gui.EnumChildWindows(hn, lambda hWnd, param: param.append(hWnd),  hWndChildList)
print hWndChildList
for x in hWndChildList:
    print str(x)+':'+win32gui.GetWindowText(x)+'-'+win32gui.GetClassName(x)

hn2=win32gui.FindWindowEx(hn,None,'MDIClient',None)            #用spy++查找#32770的窗口，因为我发现它下面有‘edit’控件。
hn2=263886
print hn2
#hn2=win32gui.FindWindowEx(hn,None,'Edit',None)                #查找到edit控件
time.sleep(1)
win32gui.SetForegroundWindow(hn2)                    #选中edit控件
time.sleep(1)
win32gui.PostMessage(hn2, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)  
win32gui.PostMessage(hn2, win32con.WM_KEYUP, win32con.VK_RETURN, 0) 


win32gui.SendMessage(hn2,win32con.WM_SETTEXT,None,'show card')        #向这个窗口输入setup指令（‘setup’是linux上的一个shell命令）
time.sleep(1)
win32gui.PostMessage(hn2, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)  
win32gui.PostMessage(hn2, win32con.WM_KEYUP, win32con.VK_RETURN, 0) 
win32gui.GetMessage(263886,win32con.WM_SETTEXT,1)

