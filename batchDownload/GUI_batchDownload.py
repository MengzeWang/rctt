#-*- encoding: utf8 -*-
__author__ = 'MengZe'
try:
    from Tkinter import *#py2
    import tkMessageBox
    pyVer=2
except ImportError:
    from tkinter import *#py3
    import tkinter.messagebox
    pyVer=3

import sys,os,re,time
sys.path.append('D:\pyS\\')
import telnet2Dev_BD as telnetDownload
import multiprocessing
import read_word_doc as rwd
from start_ftpServer2 import start3CD
import threading

class Application(Frame):
    global window
    window=Tk()
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.MainDir=r'D:\py_ftp_download'
        self.doc_path=self.MainDir+r'\test_doc_collect'
        self.downloadTo=self.MainDir+'\doc_based_download'
        self.conf_path=self.MainDir+r'\configDir'
        self.conf_fresh_dev=self.conf_path+'\\'+'DevList_fresh.txt'
        self.conf_history_dev=self.conf_path+'\\'+'DevList_'+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'.txt'
        self.conf_fresh_card=self.conf_path+'\\'+'CardList_fresh.txt'
        self.conf_history_card=self.conf_path+'\\'+'CardList_'+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'.txt'
        self.conf_fresh_ftp=self.conf_path+'\\'+'FtpSet_fresh.txt'
        self.conf_history_ftp=self.conf_path+'\\'+'FtpSet_'+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'.txt'
        self.CreatepyddDir()
        self.pack()
        self.createWidgets()
        self.defaultPath=os.getcwd()
    def addDevIpToList(self):
        DevIP=self.DevAddDevEntry.get()
        DevIP_Mask=self.DevAddEntry2.get()
        if DevIP:
            DevIP_arr=DevIP.split('.')
            DevIP_Mask_arr=DevIP_Mask.split('.')
            if (len(DevIP_arr)==4)and(len(DevIP_Mask_arr)==4):
                if (re.match('^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$',DevIP))and(re.match('^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$',DevIP_Mask)):
                    ip_part_index=0
                    for ip_part in DevIP_arr:
                        if (int(ip_part)<0)or(int(ip_part)>255):
                            self.invalidIpWarning.set(u'IP非法,请检查')
                            return
                        if (int(DevIP_Mask_arr[ip_part_index])<0)or(int(DevIP_Mask_arr[ip_part_index])>255):
                            self.invalidIpWarning.set(u'IP掩码非法,请检查')
                            return
                        ip_part_index=ip_part_index+1
                    ip_part_index=None

                    self.DevListText.insert('end','\n'+DevIP+';'+DevIP_Mask+';'+str(self.DevInsideIntVar.get()))
                    self.defaultIp.set('')#clear ip entry
                    self.defaultIpMask.set(DevIP_Mask)#clear mask entry
                else:
                    self.invalidIpWarning.set(u'IP或掩码非法,\n请检查')
                    return
            else:
                self.invalidIpWarning.set(u'IP或掩码长度不对,\n请重新输入')
                return

    def addCardToList(self):
        card_name=self.DevAddCardEntry.get()
        card_bootrom=self.DevAddBooRomEntry.get()
        card_system=self.DevAddsystemEntry.get()
        card_fpga=self.DevAddfpgaEntry.get()
        if card_name:
            fileList=''
            if card_bootrom:
                card_bootrom_arr=card_bootrom.split(';')
                for card_bootrom_arri in card_bootrom_arr:
                    if card_bootrom_arri[-7:]!='bootrom':
                        fileList=fileList+card_bootrom_arri+'.bootrom;'
                    else:
                        fileList=fileList+card_bootrom_arri+';'
                #fileList=fileList+card_bootrom+'.bootrom;'
            if card_system:
                card_system_arr=card_system.split(';')
                for card_system_arri in card_system_arr:
                    if card_system_arri[-11:]!='system-boot':
                        if card_system_arri[-3:]=='HEX':
                            fileList=fileList+card_system_arri+'.mcu;'
                        else:
                            fileList=fileList+card_system_arri+'.system-boot;'
                    else:
                        fileList=fileList+card_system_arri+';'
                #fileList=fileList+card_system+'.system-boot;'
                fileList.strip(';')
            if card_fpga:
                card_fpga_arr=card_fpga.split(';')
                for card_fpga_arri in card_fpga_arr:
                    if card_fpga_arri[-4:]!='fpga':
                        fileList=fileList+card_fpga_arri+'.fpga;'
                    else:
                        fileList=fileList+card_fpga_arri+';'
                #fileList=fileList+card_fpga+'.fpga;'
                fileList.strip(';')
            self.CardListText.insert('end','\n'+card_name+'_'+str(self.ResetCardIntVar.get())+':'+fileList.strip(';'))#'ss8_1:xx.bin;xx.sys;...'
            self.defaultCard.set('')
            self.defaultboot.set('')
            self.defaultsys.set('')
            self.defaultfpga.set('')
            self.defaultWord.set('')
        else:
            if pyVer==2:
                tkMessageBox.showinfo('Message',u'请填写板卡名称！')
            else:
                tkinter.messagebox.showinfo('Message',u'请填写板卡名称！')

    def getFtpServerSettings(self):
        FtpServerUsr=self.FtpUserEntry.get()
        FtpServerPWD=self.FtpPasswordEntry.get()
        insideManageFtpServerIp=self.FtpIPEntry.get()
        return [insideManageFtpServerIp,FtpServerUsr,FtpServerPWD]

    def DownloadFileThroughTelnet(self):
        DevList=self.DevListText.get('1.0','end')
        CardList=self.CardListText.get('1.0','end')
        FtpSet=self.getFtpServerSettings()
        DevList_clear_raw=DevList.encode('utf8').strip().split('\n')#['ip;mask;daiwai','ip;mask;dainei'....]
        DevList_clear=[]
        for DevList_clear_rawi in DevList_clear_raw:
            if DevList_clear_rawi:
                DevList_clear.append(DevList_clear_rawi)
        CardList_clear_raw=CardList.encode('utf8').strip().split('\n')#['cardname_resetLabel:.boot;.sys;.fpga','cardname:.boot;.sys;.fpga']
        CardList_clear=[]
        for CardList_clear_rawi in CardList_clear_raw:
            if CardList_clear_rawi:
                CardList_clear.append(CardList_clear_rawi)
        if self.ResetAllIntVar.get()==1:#in the end,usr change his mind,choose to reset all
            resetAllOption=1
        else:
            resetAllOption=0
        print(DevList_clear)
        print(CardList_clear)
        print(FtpSet)#['inside server ip','3cd usrname','3cd password']
        if (len(DevList_clear)>0)and(len(CardList_clear)>0):
            #myTask2=multiprocessing.Process(target=telnetDownload.downloadSvcfileMulti_forGUI,args=(DevList_clear,CardList_clear,FtpSet,resetAllOption,))
            #myTask2.daemon=False#设置为非守护进程
            myTask3=threading.Thread(target=telnetDownload.downloadSvcfileMulti_forGUI_BD,args=(DevList_clear,CardList_clear,FtpSet,resetAllOption,))
            myTask3.daemon=False#设置为非守护线程
            time.sleep(4)
            #myTask2.start()
            myTask3.start()
            #myTask3.join()
            #downloadState=telnetDownload.downloadSvcfileMulti_forGUI(DevList_clear,CardList_clear,FtpSet,resetAllOption)
            #tkMessageBox.showinfo('Message',downloadState)

    def UpLoadDevConfig(self):
        DevList=self.DevListText.get('1.0','end')
        DevList_clear_raw=DevList.encode('utf8').strip().split('\n')#['ip;mask;daiwai','ip;mask;dainei'....]
        DevList_str_raw=''
        for DevList_clear_rawi in DevList_clear_raw:
            if DevList_clear_rawi:
                DevList_str_raw+=DevList_clear_rawi.split(';')[0]+','
        telnetDownload.upLoadConfig_mutil(DevList_str_raw)
    def start3CD_button(self):
        os.chdir(self.defaultPath)
        myTask1=multiprocessing.Process(target=start3CD,args=())
        myTask1.daemon=True#设置为守护进程
        myTask1.start()
        
    def openUpgradeLogDir(self):
        os.system(r'start D:\py_ftp_download\upgrade_log\\')
    def DownloadFileInWord(self):
        self.wordfile=self.DevWordEntry.get() or None
        if self.wordfile:
            file_is_unique=1
            self.sucess_file=rwd.GetDoc_version(self.doc_path,self.wordfile,self.downloadTo)[1]#[[bootrom,xxx.bin],[system-boot,xxx.z],[fpga,xxx.xxx],....]
            doc_boot=''
            doc_sys=''
            doc_fpga=''
            for file_typex in self.sucess_file:
                print('file_typex',file_typex)
                if (file_typex[0]=='bootrom')and(file_typex[1][-3:]=='bin')and('no_header' not in file_typex[1])and('backup' not in file_typex[1]):
                    doc_boot=doc_boot+file_typex[1]+'.bootrom'+';'
                elif file_typex[0]=='system-boot':
                    doc_sys=doc_sys+file_typex[1]+'.system-boot'+';'
                elif file_typex[0]=='fpga':
                    doc_fpga=doc_fpga+file_typex[1]+'.fpga'+';'
                else:
                    pass
            #for more than one fpga and so on..
            self.defaultboot.set(doc_boot.strip(';').strip('bootrom').strip('r.'))
            self.defaultsys.set(doc_sys.strip(';').strip('system-boot').strip('r.'))
            self.defaultfpga.set(doc_fpga.strip(';').strip('fpga').strip('r.'))
            self.GuessCardNameByWordIput()
            self.defaultCard.set(self.shortCardName)
    
    def GuessCardNameByWordIput(self):
        if self.wordfile:
            fullCardName=self.wordfile.split('_')[0]
            self.shortCardName=fullCardName.split('-')[len(fullCardName.split('-'))-1]
    
    def CreatepyddDir(self):
        if not os.path.isdir(self.MainDir):
            os.mkdir(self.MainDir)
        if not os.path.isdir(self.doc_path):
            os.mkdir(self.doc_path)
        if not os.path.isdir(self.downloadTo):
            os.mkdir(self.downloadTo)
        if not os.path.isdir(self.conf_path):
            os.mkdir(self.conf_path)

    def saveDevList(self):#save ftp setting too
        if not self.DevListText.get('1.0','end'):#如果为空则直接退出function
            return
        if os.path.isfile(self.conf_fresh_dev):
            os.remove(self.conf_fresh_dev)
        if os.path.isfile(self.conf_fresh_ftp):
            os.remove(self.conf_fresh_ftp)
        print('save DevList into:'+self.conf_fresh_dev)

#open
        conf_fresh_writer=open(self.conf_fresh_dev,'a+')
        conf_history_writer=open(self.conf_history_dev,'a+')
        conf_ftp_writer=open(self.conf_fresh_ftp,'a+')#ftp setting

#write
        conf_fresh_writer.write(self.DevListText.get('1.0','end'))
        conf_history_writer.write(self.DevListText.get('1.0','end'))
        FtpSet=self.getFtpServerSettings()
        for FtpSet_i in FtpSet:
            conf_ftp_writer.write(FtpSet_i+'\n')

#close
        conf_fresh_writer.close()
        conf_history_writer.close()
        conf_ftp_writer.close()
    def saveCardList(self):
        if not self.CardListText.get('1.0','end'):#如果为空则直接退出function
            return
        if os.path.isfile(self.conf_fresh_card):
            os.remove(self.conf_fresh_card)
        print('save DevList into:'+self.conf_fresh_card)
        conf_fresh_writer=open(self.conf_fresh_card,'a+')
        conf_history_writer=open(self.conf_history_card,'a+')
        conf_fresh_writer.write(self.CardListText.get('1.0','end'))
        conf_history_writer.write(self.CardListText.get('1.0','end'))
        conf_fresh_writer.close()
        conf_history_writer.close()
    def loadDevList(self):
        if os.path.isfile(self.conf_fresh_dev):#text exist
        # load dev list
            self.DevListText.delete(1.0,'end')#clear 
            conf_fresh_reader=open(self.conf_fresh_dev,'a+')
            self.DevListText.insert('end',conf_fresh_reader.read())
            conf_fresh_reader.close()

        #load ftp settings
            if not os.path.isfile(self.conf_fresh_ftp):#text not exist,use default
                return
            conf_fresh_ftp_reader=open(self.conf_fresh_ftp,'a+')
            conf_fresh_ftp=conf_fresh_ftp_reader.read().split('\n')
            self.defaultFtpIp.set(conf_fresh_ftp[0].strip('\n'))
            self.defaultUsername.set(conf_fresh_ftp[1].strip('\n'))
            self.defaultPassword.set(conf_fresh_ftp[2].strip('\n'))
            conf_fresh_ftp_reader.close()
        else:
            if pyVer==2:
                tkMessageBox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)
            else:
                tkinter.messagebox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)
    def loadCardList(self):
        if os.path.isfile(self.conf_fresh_card):
            self.CardListText.delete(1.0,'end')
            conf_fresh_reader=open(self.conf_fresh_card,'a+')
            self.CardListText.insert('end',conf_fresh_reader.read())
            conf_fresh_reader.close()
        else:
            if pyVer==2:
                tkMessageBox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)
            else:
                tkinter.messagebox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)



    def createWidgets(self):
        self.Menubar=Menu(self)
        self.fileMenu=Menu(self.Menubar,tearoff=0)
        self.Menubar.add_cascade(label=u'软件配置保存',menu=self.fileMenu)
        self.fileMenu.add_command(label=u'保存当前设备列表',command=self.saveDevList)
        self.fileMenu.add_command(label=u'保存当前板卡列表',command=self.saveCardList)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=u'退出',command=self.quit)
        self.EditMenu=Menu(self.Menubar,tearoff=0)
        self.Menubar.add_cascade(label=u'软件配置加载',menu=self.EditMenu)
        self.EditMenu.add_command(label=u'加载上次设备列表',command=self.loadDevList)
        self.EditMenu.add_command(label=u'加载上次板卡列表',command=self.loadCardList)
        self.toolsMenu=Menu(self.Menubar,tearoff=0)
        self.Menubar.add_cascade(label=u'工具箱',menu=self.toolsMenu)
        self.toolsMenu.add_command(label=u'批量上传配置文件',command=self.UpLoadDevConfig)
        window.config(menu=self.Menubar)
#============add device to list

        self.DevAddDeviceLabel_Father=Label(self,width=80,height=3)#width=15, height=5
        self.DevAddDeviceLabel_Father.pack(side=LEFT,expand='no',anchor='nw')

        self.invalidIpWarning = StringVar()
        self.DevAddDevLabel=Label(self.DevAddDeviceLabel_Father,text=u'设备IP地址:',textvariable = self.invalidIpWarning,width=15,height=3)#width=15, height=5
        self.DevAddDevLabel.pack(side=TOP,expand='no')
        self.defaultIp = StringVar()
        self.DevAddDevEntry=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIp)
        self.DevAddDevEntry.pack(side=TOP,expand='no')
        self.DevAddLabel2=Label(self.DevAddDeviceLabel_Father,text=u'设备IP掩码:',width=15,height=3)#width=15, height=5
        self.DevAddLabel2.pack(side=TOP,expand='no')
        self.defaultIpMask = StringVar()
        self.DevAddEntry2=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIpMask)
        self.defaultIpMask.set('255.255.255.0')
        self.DevAddEntry2.pack(side=TOP,expand='no')
        self.DevInsideIntVar = IntVar()
        self.DevInsideCheckbutton=Checkbutton(self.DevAddDeviceLabel_Father, text=u'使用指定FTP_Server_IP', variable=self.DevInsideIntVar, onvalue=1, offvalue=0,height=1)#command=self.print_selection
        self.DevInsideCheckbutton.pack(side=TOP,expand='no')
        self.addDevButton=Button(self.DevAddDeviceLabel_Father,text=u'添加至设备列表',command=self.addDevIpToList)
        self.addDevButton.pack(side=TOP,expand='no')
#============device list
        self.DevListLabel=Label(self.DevAddDeviceLabel_Father,width=75,height=5)#width=15, height=5
        self.DevListLabel.pack(side=TOP,expand='no',anchor='nw')
        self.DevListLabel_top=Label(self.DevListLabel,text=u'设备IP列表',font=('Arial', 12),width=15,height=3)#width=15, height=5
        self.DevListLabel_top.pack()
        self.DevListText=Text(self.DevListLabel,width=15,height=21)
        self.DevListText.pack()
#============card name
        self.DevAddCardLabel_Father=Label(self,width=75,height=3)#width=15, height=5
        self.DevAddCardLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevCardNameLabel_Father=Label(self.DevAddCardLabel_Father,width=80,height=3)#width=15, height=5
        self.DevCardNameLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevAddCardLabel=Label(self.DevCardNameLabel_Father,text=u'板卡名称:',width=15,height=3)#width=15, height=5
        self.DevAddCardLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultCard=StringVar()
        self.DevAddCardEntry=Entry(self.DevCardNameLabel_Father,width=20,textvariable = self.defaultCard)
        self.DevAddCardEntry.pack(side=LEFT,expand='no')
#============ti ce dan word file
        self.DevWordLabel=Label(self.DevCardNameLabel_Father,text=u'提测单名:',width=15,height=3)#width=15, height=5
        self.DevWordLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultWord=StringVar()
        self.DevWordEntry=Entry(self.DevCardNameLabel_Father,width=40,textvariable = self.defaultWord)
        self.DevWordEntry.pack(side=LEFT,expand='no')
        self.downloadUseWordButton=Button(self.DevCardNameLabel_Father,text=u'下载版本',command=self.DownloadFileInWord)
        self.downloadUseWordButton.pack(side=TOP,expand='yes')
#============bootrom
        self.DevAddBooRomLabel_Father=Label(self.DevAddCardLabel_Father,width=80,height=3)#width=15, height=5
        self.DevAddBooRomLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddBooRomLabel=Label(self.DevAddBooRomLabel_Father,text=u'Bootrom文件名:',width=15,height=3)#width=15, height=5
        self.DevAddBooRomLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultboot=StringVar()
        self.DevAddBooRomEntry=Entry(self.DevAddBooRomLabel_Father,width=60,textvariable = self.defaultboot)
        self.DevAddBooRomEntry.pack(side=LEFT,expand='no')

#============system-boot
        self.DevAddsystemLabel_Father=Label(self.DevAddCardLabel_Father,width=80,height=3)#width=15, height=5
        self.DevAddsystemLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddsystemLabel=Label(self.DevAddsystemLabel_Father,text=u'system-boot文件名:',width=15,height=3)#width=15, height=5
        self.DevAddsystemLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultsys=StringVar()
        self.DevAddsystemEntry=Entry(self.DevAddsystemLabel_Father,width=60,textvariable = self.defaultsys)
        self.DevAddsystemEntry.pack(side=LEFT,expand='no')

#============fpga
        self.DevAddfpgaLabel_Father=Label(self.DevAddCardLabel_Father,width=80,height=3)#width=15, height=5
        self.DevAddfpgaLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddfpgaLabel=Label(self.DevAddfpgaLabel_Father,text=u'FPGA文件名:',width=15,height=3)#width=15, height=5
        self.DevAddfpgaLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultfpga=StringVar()
        self.DevAddfpgaEntry=Entry(self.DevAddfpgaLabel_Father,width=60,textvariable = self.defaultfpga)
        self.DevAddfpgaEntry.pack(side=LEFT,expand='no')
#============reset card or reset all add card list
        self.addCardButtonLabel_father=Label(self.DevAddCardLabel_Father)
        self.addCardButtonLabel_father.pack(side=TOP,expand='yes')

        self.ResetCardIntVar = IntVar()
        self.ResetCardCheckbutton=Checkbutton(self.addCardButtonLabel_father, text=u'下载完成立刻重启该单盘', variable=self.ResetCardIntVar, onvalue=1, offvalue=0,height=1)
        self.ResetCardCheckbutton.pack(side=LEFT,expand='no')

        self.ResetAllIntVar = IntVar()
        self.ResetAllCheckbutton=Checkbutton(self.addCardButtonLabel_father, text=u'所有单盘下载完成后整机重启', variable=self.ResetAllIntVar, onvalue=1, offvalue=0,height=1)
        self.ResetAllCheckbutton.pack(side=LEFT,expand='no')

        self.addCardButton=Button(self.addCardButtonLabel_father,text=u'添加至升级板卡列表',command=self.addCardToList)
        self.addCardButton.pack(side=LEFT,expand='yes')

#============Card list
        self.CardListLabel=Label(self.DevAddCardLabel_Father,text=u'升\n级\n板\n卡\n及\n文\n件\n列\n表',font=('Arial', 12),width=2,height=10)
        self.CardListLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.CardListText=Text(self.DevAddCardLabel_Father,width=78,height=15)
        self.CardListText.pack(side=LEFT,expand='yes',anchor='nw')
#============3CD FTP
        self.BottomLabel_Father=Label(self,width=90,height=5)#width=15, height=5
        self.BottomLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.FtpSetLabel=Label(self.BottomLabel_Father,text=u'3CD FTP 配置（带外管理设备可忽略此项）',width=45,height=5)#width=15, height=5
        self.FtpSetLabel.pack(side=LEFT,expand='no',anchor='nw')
        
        self.FtpIPLabel_brother=Label(self.FtpSetLabel,width=45,height=1)#width=15, height=5
        self.FtpIPLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpIPLabel=Label(self.FtpIPLabel_brother,text=u'Ftp Server IP',width=15,height=1)#width=15, height=5
        self.FtpIPLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultFtpIp = StringVar()
        self.FtpIPEntry=Entry(self.FtpIPLabel_brother,width=30,textvariable = self.defaultFtpIp)
        self.FtpIPEntry.pack(side=LEFT,expand='no')

        self.FtpUserLabel_brother=Label(self.FtpSetLabel,text=u'Ftp Server 用户名',width=15,height=1)#width=15, height=5
        self.FtpUserLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpUserLabel=Label(self.FtpUserLabel_brother,text=u'Ftp Server 用户名',width=15,height=1)#width=15, height=5
        self.FtpUserLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultUsername = StringVar()
        self.FtpUserEntry=Entry(self.FtpUserLabel_brother,width=30,textvariable = self.defaultUsername)
        self.defaultUsername.set('pydd')
        self.FtpUserEntry.pack(side=LEFT,expand='no')

        self.FtpPasswordLabel_brother=Label(self.FtpSetLabel,text=u'Ftp Server 密码',width=15,height=1)#width=15, height=5
        self.FtpPasswordLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpPasswordLabel=Label(self.FtpPasswordLabel_brother,text=u'Ftp Server 密码',width=15,height=1)#width=15, height=5
        self.FtpPasswordLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultPassword = StringVar()
        self.FtpPasswordEntry=Entry(self.FtpPasswordLabel_brother,width=30,textvariable = self.defaultPassword)
        self.defaultPassword.set('123456')
        self.FtpPasswordEntry.pack(side=LEFT,expand='no')
#============Run
        self.RunButton=Button(self.BottomLabel_Father,text=u'开启3CD',width=11,height=5,command=self.start3CD_button)
        self.RunButton.pack(side=LEFT,expand='yes')
        self.RunButton=Button(self.BottomLabel_Father,text=u'开始升级',width=22,height=5,command=self.DownloadFileThroughTelnet)
        self.RunButton.pack(side=LEFT,expand='yes')
        self.RunButton=Button(self.BottomLabel_Father,text=u'查看升级log',width=11,height=5,command=self.openUpgradeLogDir)
        self.RunButton.pack(side=LEFT,expand='yes')

if __name__=='__main__':
    multiprocessing.freeze_support()
    app=Application()
    app.master.title('Hello world again!请将word文件放在:%s文件夹内' %(app.doc_path))
    app.master.geometry('900x650')
    app.mainloop()