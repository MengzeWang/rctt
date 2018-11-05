import os
import win32api
import win32con
import win32gui
import Tkinter as tk
import tkFont
import ttk

CONFIG_FILE_NAME = 'SecureCRTTool.txt'
TAG_MODULE = 'Module:'
TAG_FUNCTION = 'Function:'
TAG_COMMENT = '//'
HISTORY_COMMAND_NAME = 'HistoryCmd.txt'
SECURE_CRT_WND_NAME = 'VanDyke Software - SecureCRT'
HISTORY_COMMAND_MAX_SIZE = 15


def ReadConfigFile():
    moduleName = ""
    functionDefinition = ""
    functionOfOneModule = []
    comment = ""
    commentOfOneModule = []
    ModulesInFile = []
    FunctionsInFile = []
    CommentsInFile = []
    if False == os.path.exists(CONFIG_FILE_NAME):
        return [], [], []
    configFile = open(CONFIG_FILE_NAME, 'rt')
    try:
        configFileContent = configFile.readlines()
        for line in configFileContent:
            moduleName, functionDefinition, comment = AnalysisConfigFileLine(line)
            if len(moduleName) > 0:
                if len(ModulesInFile) > 0:
                    FunctionsInFile.append(functionOfOneModule)
                    CommentsInFile.append(commentOfOneModule)
                ModulesInFile.append(moduleName)
                functionOfOneModule = []
                commentOfOneModule = []
            if len(functionDefinition) > 0:
                functionOfOneModule.append(functionDefinition)
                commentOfOneModule.append(comment)
        FunctionsInFile.append(functionOfOneModule)  # last module's fuctions
        CommentsInFile.append(commentOfOneModule)
    finally:
        configFile.close()
    return ModulesInFile, FunctionsInFile, CommentsInFile

def AnalysisConfigFileLine(lineContent):
    moduleName = ""
    functionDefinition = ""
    comment = ""
    lineContent = lineContent.strip()
    if 0 == len(lineContent):
        return "", "", ""
    if 0 == lineContent.find(TAG_MODULE):
        moduleName = lineContent[len(TAG_MODULE):]
        moduleName.strip()
    elif 0 == lineContent.find(TAG_FUNCTION):
        commentIndex = lineContent.find(TAG_COMMENT)
        if -1 != commentIndex:
            functionDefinition = lineContent[len(TAG_FUNCTION):commentIndex]
            comment = lineContent[commentIndex + len(TAG_COMMENT):]
        else:
            functionDefinition = lineContent[len(TAG_FUNCTION):]
        functionDefinition.strip()
        comment.strip()
    return moduleName, functionDefinition, comment

def ReadHistoryCmdFile():
    historyCmdDict = {}
    latestModuleName = ''
    historyCmdOfModule = []
    if False == os.path.exists(HISTORY_COMMAND_NAME):
        return {}
    historyCmdFile = open(HISTORY_COMMAND_NAME, 'rt')
    try:
        historyCmdFileContent = historyCmdFile.readlines()
        for line in historyCmdFileContent:
            moduleName, cmdString = AnalysisHistoryCmdLine(line)
            if len(moduleName) > 0:
                if len(latestModuleName) > 0:
                    historyCmdDict[latestModuleName] = historyCmdOfModule
                latestModuleName = moduleName
                historyCmdOfModule = []
            if len(cmdString) > 0:
                historyCmdOfModule.append(cmdString)
        historyCmdDict[latestModuleName] = historyCmdOfModule # last module's history cmd
    finally:
        historyCmdFile.close()
    return historyCmdDict

def AnalysisHistoryCmdLine(lineContent):
    lineContent = lineContent.strip()
    if 0 == len(lineContent):
        return "", ""
    if 0 == lineContent.find(TAG_MODULE):
        moduleName = lineContent[len(TAG_MODULE):]
        moduleName.strip()
        return moduleName, ""
    else:
        cmdString = lineContent.strip()
        return "", cmdString



def SendKeyToWnd(hCmdWin, keyValue):
    win32api.SendMessage(hCmdWin, win32con.WM_CHAR, keyValue, 1)  # chr(65) rd('l')

def SendStringToWnd(hCmdWin, cmdString):
    if len(cmdString) == 0 or None == hCmdWin:
        return
    for key in cmdString:
        SendKeyToWnd(hCmdWin, ord(key))
    SendKeyToWnd(hCmdWin, 10) # SendKeyToWnd(hWnd, 13)

def SendCmdToSecureCRT(cmdString):
    hSecureCRTWnd = win32gui.FindWindow(SECURE_CRT_WND_NAME, None)
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




class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.ModulesInFile = []
        self.FunctionsInFile = []
        self.CommentsInFile = []
        self.ModulesInFile, self.FunctionsInFile, self.CommentsInFile = ReadConfigFile()
        self.historyCmdDict = ReadHistoryCmdFile()
        self.bWriteHistoryCmd = False

        self.INIT_WINDOW_STATUS = 0
        self.FOCUS_IN_STATUS = 1
        self.FOCUS_OUT_STATUS = 2
        self.windowStatus = self.INIT_WINDOW_STATUS
        self.winWidth = 322
        self.winHeight = 419

        # Set Window Attribute
        winSizePos = '%dx%d-%d+%d' % (self.winWidth, self.winHeight, 80, 0)  # center: (root.winfo_screenwidth()-self.winWidth)/2 , (root.winfo_screenheight()-self.winHeight)/2
        self.master.geometry(winSizePos)
        self.master.title("SecureCRT'Tool")
        #self.master.iconbitmap('Compass.ico')
        self.master.resizable(width=False, height=False)
        self.grid(sticky=tk.N + tk.S + tk.E + tk.W)
        self.master.wm_attributes('-topmost', 1)
        self.master.wm_attributes('-toolwindow', 1)
        self.master.bind('<Motion>', self.ShowWnindowWhenMouseOn)
        self.master.bind('<FocusIn>', self.ShowWnindowWhenFocusIn)
        self.master.bind('<FocusOut>', self.HideWindowWhenFocusOut)
        self.master.bind('<Destroy>', self.DestroyWindow)
        self.createWidgets()


    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.rowconfigure(0, minsize=30) # minsize   weight
        self.rowconfigure(1, minsize=74)
        self.rowconfigure(2, minsize=10)
        self.rowconfigure(3, minsize=30)
        self.rowconfigure(4, minsize=100)
        self.rowconfigure(5, minsize=10)
        self.rowconfigure(6, minsize=35)
        self.rowconfigure(7, minsize=25)
        self.columnconfigure(0, minsize=55)
        self.columnconfigure(1, minsize=180)
        self.columnconfigure(2, minsize=15)
        self.columnconfigure(3, minsize=65)

        widgetXorYPad = 3
        winFont = tkFont.Font(family='Fixdsys', size=9, weight=tkFont.NORMAL)

        # Module Section
        tk.Label(self, text="Module:", font=winFont).grid(row=0, column=0, sticky=tk.W, padx=widgetXorYPad)
        self.currModuleVar = tk.StringVar()
        #self.cmbCurrModule = ttk.Combobox(self, textvariable=self.currModuleVar, font=winFont, state="readonly" , values=self.ModulesInFile)
        #self.cmbCurrModule.grid(row=0, column=1, sticky= tk.E + tk.W + tk.N + tk.S, pady=8)
        #self.cmbCurrModule.bind("<<ComboboxSelected>>", self.SelectModule)
        if len(self.ModulesInFile):
            self.optMenu = tk.OptionMenu(self, self.currModuleVar, *self.ModulesInFile, command=self.SelectModule) # apply(tk.OptionMenu, (self,self.currModuleVar) + tuple(self.ModulesInFile))
        else:
            self.optMenu = tk.OptionMenu(self, self.currModuleVar, None, command=self.SelectModule)
        self.optMenu.grid(row=0, column=1, columnspan=2, sticky=tk.E + tk.W + tk.N + tk.S, pady=widgetXorYPad)
        self.optMenu.config(font=winFont)
        self.optMenu['menu'].config(font=winFont, fg="blue")
        if len(self.ModulesInFile) > 0:
            self.currModuleVar.set(self.ModulesInFile[0])


        # Functions Section
        self.yScrollDebugFunctions = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScrollDebugFunctions.grid(row=1, column=2, sticky=tk.N + tk.S + tk.E + tk.W)
        self.xScrollDebugFunctions = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.xScrollDebugFunctions.grid(row=2, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        tk.Label(self, text="Debug  \nMethod:", font=winFont).grid(row=1, column=0, sticky=tk.W, padx=widgetXorYPad)
        self.lbDebugFunctions = tk.Listbox(self, font=winFont, activestyle='none', xscrollcommand=self.xScrollDebugFunctions.set, yscrollcommand=self.yScrollDebugFunctions.set)
        self.lbDebugFunctions.grid(row=1, column=1, sticky=tk.N + tk.S + tk.E + tk.W)
        self.xScrollDebugFunctions["command"] = self.lbDebugFunctions.xview
        self.yScrollDebugFunctions["command"] = self.lbDebugFunctions.yview
        self.lbDebugFunctions.bind('<ButtonRelease-1>', self.SelectFunction)
        self.lbDebugFunctions.bind('<Double-Button-1>', self.SelectFunction)
        self.ShowDebugFunctionToListBox()

        # Command and Send Command
        tk.Label(self, text="Command:", font=winFont).grid(row=3, column=0, sticky=tk.W, padx=widgetXorYPad)
        self.currCmdVar = tk.StringVar()
        self.editAddFunction = tk.Entry(self, textvariable=self.currCmdVar, font=winFont)
        self.editAddFunction.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=widgetXorYPad)
        self.btnSendCmd = tk.Button(self, text="SEND", font=winFont, fg="blue")
        self.btnSendCmd.grid(row=3, column=3, sticky=tk.E + tk.W, padx=widgetXorYPad)
        self.btnSendCmd.bind('<ButtonRelease-1>', self.SendCmd)

        # History Commands
        self.yScrollHistoryCommand = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScrollHistoryCommand.grid(row=4, column=2, sticky=tk.N + tk.S + tk.E + tk.W)
        self.xScrollHistoryCommand = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.xScrollHistoryCommand.grid(row=5, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        tk.Label(self, text="History \nCommand:", font=winFont).grid(row=4, column=0, sticky=tk.W, padx=widgetXorYPad)
        self.lbHistoryCommand = tk.Listbox(self, font=winFont, activestyle="none", xscrollcommand=self.xScrollHistoryCommand.set, yscrollcommand=self.yScrollHistoryCommand.set)
        self.lbHistoryCommand.grid(row=4, column=1, sticky=tk.N + tk.S + tk.E + tk.W)
        self.xScrollHistoryCommand["command"] = self.lbHistoryCommand.xview
        self.yScrollHistoryCommand["command"] = self.lbHistoryCommand.yview
        self.lbHistoryCommand.bind('<ButtonRelease-1>', self.SelectHistoryCmd)
        self.lbHistoryCommand.bind('<Double-Button-1>', self.SelectHistoryCmdAndSendToSecureCRT)
        self.ShowHistoryCmdToListBox()

        # Show Comment and "QUIT" Button
        tk.Label(self, text="Comment:", font=winFont).grid(row=6, column=0, sticky=tk.W, padx=widgetXorYPad)
        self.commentVar = tk.StringVar()
        tk.Label(self, textvariable=self.commentVar, font=winFont, wraplength = 190, justify=tk.LEFT).grid(row=6, rowspan=2, column=1, columnspan=2, sticky=tk.N + tk.S + tk.E + tk.W)
        self.btnQUIT = tk.Button(self, text="QUIT", font=winFont, fg="red", command=root.destroy)
        self.btnQUIT.grid(row=6, column=3, sticky=tk.E + tk.W, padx=widgetXorYPad)

    def SelectModule(self, event):
        self.ShowDebugFunctionToListBox()
        self.ShowHistoryCmdToListBox()

    def GetCurrModuleIndex(self):
        moduleNum = len(self.ModulesInFile)
        for index in range(0, moduleNum):
            if self.currModuleVar.get() == self.ModulesInFile[index]:
                return index
        return -1

    def ShowDebugFunctionToListBox(self):
        self.lbDebugFunctions.delete(0, tk.END)
        currIndex = self.GetCurrModuleIndex() #self.cmbCurrModule.current()
        if -1 == currIndex:
            return
        for line in self.FunctionsInFile[currIndex]:
            self.lbDebugFunctions.insert(tk.END, line)

    def SelectFunction(self, event):
        currSelection = self.lbDebugFunctions.curselection()
        if len(currSelection) > 0 :
            self.currCmdVar.set(self.lbDebugFunctions.get(currSelection))
            moduleIndex = self.GetCurrModuleIndex() #sself.cmbCurrModule.current()
            self.commentVar.set(self.CommentsInFile[moduleIndex][currSelection[0]].decode('gbk').encode('utf8'))

    def SendCmd(self, event):
        cmdString = self.currCmdVar.get().strip()
        if 0 == len(cmdString):
            return
        SendCmdToSecureCRT(cmdString)
        self.AddCmdStringToHistoryCmd(cmdString)

    def SelectHistoryCmd(self, event):
        currSelection = self.lbHistoryCommand.curselection()
        if len(currSelection) > 0 :
            self.currCmdVar.set(self.lbHistoryCommand.get(currSelection[0]))

    def SelectHistoryCmdAndSendToSecureCRT(self, event):
        currSelection = self.lbHistoryCommand.curselection()
        if len(currSelection) > 0 :
            cmdString = self.lbHistoryCommand.get(currSelection[0])
            self.currCmdVar.set(cmdString)
            SendCmdToSecureCRT(cmdString)
            self.AddCmdStringToHistoryCmd(cmdString)

    def AddCmdStringToHistoryCmd(self, cmdString):
        if 0 == len(cmdString):
            return
        if self.lbHistoryCommand.get(0) == cmdString:
            return
        self.DeleteCmdStringInHistroyCmd(cmdString)
        if self.historyCmdDict.has_key(self.currModuleVar.get()):
            historyCmdOfModule = self.historyCmdDict[self.currModuleVar.get()]
            historyCmdOfModule.insert(0, cmdString)
        else:
            self.historyCmdDict[self.currModuleVar.get()] = [cmdString]
        self.ShowHistoryCmdToListBox()

    def ShowHistoryCmdToListBox(self):
        self.lbHistoryCommand.delete(0, tk.END)
        if self.historyCmdDict.has_key(self.currModuleVar.get()):
            historyCmdOfModule = self.historyCmdDict[self.currModuleVar.get()]
            for cmdString in historyCmdOfModule:
                self.lbHistoryCommand.insert(tk.END, cmdString)

    def DeleteCmdStringInHistroyCmd(self, toBeDelete):
        if self.historyCmdDict.has_key(self.currModuleVar.get()):
            historyCmdOfModule = self.historyCmdDict[self.currModuleVar.get()]
            historyCmdSize = len(historyCmdOfModule)
            for index in range(0, historyCmdSize):
                if toBeDelete == historyCmdOfModule[index]:
                    historyCmdOfModule.pop(index)
                    return
            if HISTORY_COMMAND_MAX_SIZE == historyCmdSize:
                historyCmdOfModule.pop()
                return


    def ShowWnindowWhenFocusIn(self, event):
        if self.windowStatus == self.FOCUS_OUT_STATUS:
            self.windowStatus == self.FOCUS_IN_STATUS
            winSizePos = '%dx%d+%d+%d' % (self.winWidth, self.winHeight, self.master.winfo_x(),  self.master.winfo_y())
            self.master.geometry(winSizePos)

    def HideWindowWhenFocusOut(self, event):
        if self.master.winfo_y() <= 0:
            self.windowStatus = self.FOCUS_OUT_STATUS
            winSizePos = '%dx%d+%d+%d' % (self.winWidth, self.winHeight, self.master.winfo_x(), -self.winHeight-19)
            self.master.geometry(winSizePos)

    def ShowWnindowWhenMouseOn(self, event):
        if self.master.winfo_y() < -100 :
            self.windowStatus = self.INIT_WINDOW_STATUS
            winSizePos = '%dx%d+%d+%d' % (self.winWidth, self.winHeight, self.master.winfo_x(), 0)
            self.master.geometry(winSizePos)
            self.master.focus_force()
            self.btnSendCmd.focus_set()

    def DestroyWindow(self, event):
        if True == self.bWriteHistoryCmd:
            return
        historyCmdFile = open(HISTORY_COMMAND_NAME, 'wt')
        try:
            for module in self.historyCmdDict.keys():
                historyCmdFile.write(TAG_MODULE+module+'\n')
                historyCmdOfModule = self.historyCmdDict[module]
                for cmdString in historyCmdOfModule:
                    historyCmdFile.write(cmdString+'\n')
                historyCmdFile.write('\n')
        finally:
            historyCmdFile.close()
        self.bWriteHistoryCmd = True





root = tk.Tk()
app = Application(root)
app.mainloop()