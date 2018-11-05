#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from Tkinter import *
import tkMessageBox
import sys,os,re
import telnet2_mutiprocess as telnetDownload
import multiprocessing
class Application(Frame):
    global window
    window=Tk()
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.pack()
        self.createWidgets()
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
                fileList=fileList+card_bootrom+'.bootrom;'
            if card_system:
                fileList=fileList+card_system+'.system-boot;'
                fileList.strip(';')
            if card_fpga:
                fileList=fileList+card_fpga+'.fpga;'
                fileList.strip(';')
            self.CardListText.insert('end','\n'+card_name+':'+fileList.strip(';'))
        self.defaultCard.set('')
        self.defaultboot.set('')
        self.defaultsys.set('')
        self.defaultfpga.set('')
    def getFtpServerSettings(self):
        FtpServerUsr=self.FtpUserEntry.get()
        FtpServerPWD=self.FtpPasswordEntry.get()
        insideManageFtpServerIp=self.FtpIPEntry.get()
        return [insideManageFtpServerIp,FtpServerUsr,FtpServerPWD]

    def DownloadFileThroughTelnet(self):
        DevList=self.DevListText.get('1.0','end')
        CardList=self.CardListText.get('1.0','end')
        FtpSet=self.getFtpServerSettings()
        DevList_clear=DevList.encode('utf8').strip().split('\n')#['ip;mask;daiwai','ip;mask;dainei'....]
        CardList_clear=CardList.encode('utf8').strip().split('\n')#['cardname:.boot;.sys;.fpga','cardname:.boot;.sys;.fpga']
        print DevList_clear
        print CardList_clear
        print FtpSet#['inside server ip','3cd usrname','3cd password']
        if (len(DevList_clear)>0)and(len(CardList_clear)>0):
            downloadState=telnetDownload.downloadSvcfileMulti_forGUI(DevList_clear,CardList_clear,FtpSet)
            tkMessageBox.showinfo('Message',downloadState)

    def do_job(self):
        pass


    def createWidgets(self):
        self.Menubar=Menu(self)
        self.fileMenu=Menu(self.Menubar,tearoff=0)
        self.Menubar.add_cascade(label='File',menu=self.fileMenu)
        self.fileMenu.add_command(label='Old',command=self.do_job)
        self.fileMenu.add_command(label='New',command=self.do_job)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Exit',command=self.quit)
        self.Menubar.add_cascade(label='Edit',menu=self.fileMenu)
        #self.EditMenu_subMenu=Menu()
        window.config(menu=self.Menubar)
#============add device to list

        self.DevAddDeviceLabel_Father=Label(self,bg='green',width=80,height=3)#width=15, height=5
        self.DevAddDeviceLabel_Father.pack(side=LEFT,expand='no',anchor='nw')

        self.invalidIpWarning = StringVar()
        self.DevAddDevLabel=Label(self.DevAddDeviceLabel_Father,text=u'设备IP地址:',textvariable = self.invalidIpWarning,bg='green',width=15,height=3)#width=15, height=5
        self.DevAddDevLabel.pack(side=TOP,expand='no')
        self.defaultIp = StringVar()
        self.DevAddDevEntry=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIp)
        self.DevAddDevEntry.pack(side=TOP,expand='no')
        self.DevAddLabel2=Label(self.DevAddDeviceLabel_Father,text=u'设备IP掩码:',bg='green',width=15,height=3)#width=15, height=5
        self.DevAddLabel2.pack(side=TOP,expand='no')
        self.defaultIpMask = StringVar()
        self.DevAddEntry2=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIpMask)
        self.defaultIpMask.set('255.255.255.0')
        self.DevAddEntry2.pack(side=TOP,expand='no')
        self.DevInsideIntVar = IntVar()
        self.DevInsideCheckbutton=Checkbutton(self.DevAddDeviceLabel_Father, text=u'带内管理', variable=self.DevInsideIntVar, onvalue=1, offvalue=0,height=1)#command=self.print_selection
        self.DevInsideCheckbutton.pack(side=TOP,expand='no')
        self.addDevButton=Button(self.DevAddDeviceLabel_Father,text=u'添加至设备列表',command=self.addDevIpToList)
        self.addDevButton.pack(side=TOP,expand='no')
#============device list
        self.DevListLabel=Label(self.DevAddDeviceLabel_Father,bg='green',width=75,height=5)#width=15, height=5
        self.DevListLabel.pack(side=TOP,expand='no',anchor='nw')
        self.DevListLabel_top=Label(self.DevListLabel,text=u'设备IP列表',bg='green',font=('Arial', 12),width=15,height=3)#width=15, height=5
        self.DevListLabel_top.pack()
        self.DevListText=Text(self.DevListLabel,width=15,height=21)
        self.DevListText.pack()
#============card name
        self.DevAddCardLabel_Father=Label(self,bg='#9ACD32',width=75,height=3)#width=15, height=5
        self.DevAddCardLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevCardNameLabel_Father=Label(self.DevAddCardLabel_Father,bg='#9ACD32',width=80,height=3)#width=15, height=5
        self.DevCardNameLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevAddCardLabel=Label(self.DevCardNameLabel_Father,text=u'板卡名称:',bg='#9ACD32',width=21,height=3)#width=15, height=5
        self.DevAddCardLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultCard=StringVar()
        self.DevAddCardEntry=Entry(self.DevCardNameLabel_Father,width=60,textvariable = self.defaultCard)
        self.DevAddCardEntry.pack(side=LEFT,expand='no')
#============bootrom
        self.DevAddBooRomLabel_Father=Label(self.DevAddCardLabel_Father,bg='#9ACD32',width=80,height=3)#width=15, height=5
        self.DevAddBooRomLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddBooRomLabel=Label(self.DevAddBooRomLabel_Father,text=u'Bootrom文件名:',bg='#9ACD32',width=15,height=3)#width=15, height=5
        self.DevAddBooRomLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultboot=StringVar()
        self.DevAddBooRomEntry=Entry(self.DevAddBooRomLabel_Father,width=60,textvariable = self.defaultboot)
        self.DevAddBooRomEntry.pack(side=LEFT,expand='no')

#============system-boot
        self.DevAddsystemLabel_Father=Label(self.DevAddCardLabel_Father,bg='#9ACD32',width=80,height=3)#width=15, height=5
        self.DevAddsystemLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddsystemLabel=Label(self.DevAddsystemLabel_Father,text=u'system-boot文件名:',bg='#9ACD32',width=15,height=3)#width=15, height=5
        self.DevAddsystemLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultsys=StringVar()
        self.DevAddsystemEntry=Entry(self.DevAddsystemLabel_Father,width=60,textvariable = self.defaultsys)
        self.DevAddsystemEntry.pack(side=LEFT,expand='no')

#============fpga
        self.DevAddfpgaLabel_Father=Label(self.DevAddCardLabel_Father,bg='#9ACD32',width=80,height=3)#width=15, height=5
        self.DevAddfpgaLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddfpgaLabel=Label(self.DevAddfpgaLabel_Father,text=u'FPGA文件名:',bg='#9ACD32',width=15,height=3)#width=15, height=5
        self.DevAddfpgaLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultfpga=StringVar()
        self.DevAddfpgaEntry=Entry(self.DevAddfpgaLabel_Father,width=60,textvariable = self.defaultfpga)
        self.DevAddfpgaEntry.pack(side=LEFT,expand='no')

        self.addCardButton=Button(self.DevAddCardLabel_Father,text=u'添加至升级板卡列表',command=self.addCardToList)
        self.addCardButton.pack(side=TOP,expand='yes')
#============Card list
        self.CardListLabel=Label(self.DevAddCardLabel_Father,text=u'升\n级\n板\n卡\n及\n文\n件\n列\n表',font=('Arial', 12),bg='#9ACD32',width=2,height=10)
        self.CardListLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.CardListText=Text(self.DevAddCardLabel_Father,width=78,height=15)
        self.CardListText.pack(side=LEFT,expand='yes',anchor='nw')
#============3CD FTP
        self.BottomLabel_Father=Label(self,bg='#98FB98',width=90,height=5)#width=15, height=5
        self.BottomLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.FtpSetLabel=Label(self.BottomLabel_Father,bg='#98FB98',text=u'3CD FTP 配置（带外管理设备可忽略此项）',width=45,height=5)#width=15, height=5
        self.FtpSetLabel.pack(side=LEFT,expand='no',anchor='nw')
        
        self.FtpIPLabel_brother=Label(self.FtpSetLabel,bg='#98FB98',width=45,height=1)#width=15, height=5
        self.FtpIPLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpIPLabel=Label(self.FtpIPLabel_brother,bg='#98FB98',text=u'Ftp Server IP',width=15,height=1)#width=15, height=5
        self.FtpIPLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.FtpIPEntry=Entry(self.FtpIPLabel_brother,width=30)
        self.FtpIPEntry.pack(side=LEFT,expand='no')

        self.FtpUserLabel_brother=Label(self.FtpSetLabel,bg='#98FB98',text=u'Ftp Server 用户名',width=15,height=1)#width=15, height=5
        self.FtpUserLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpUserLabel=Label(self.FtpUserLabel_brother,bg='#98FB98',text=u'Ftp Server 用户名',width=15,height=1)#width=15, height=5
        self.FtpUserLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultUsername = StringVar()
        self.FtpUserEntry=Entry(self.FtpUserLabel_brother,width=30,textvariable = self.defaultUsername)
        self.defaultUsername.set('pydd')
        self.FtpUserEntry.pack(side=LEFT,expand='no')

        self.FtpPasswordLabel_brother=Label(self.FtpSetLabel,bg='#98FB98',text=u'Ftp Server 密码',width=15,height=1)#width=15, height=5
        self.FtpPasswordLabel_brother.pack(side=TOP,expand='no',anchor='nw')
        self.FtpPasswordLabel=Label(self.FtpPasswordLabel_brother,bg='#98FB98',text=u'Ftp Server 密码',width=15,height=1)#width=15, height=5
        self.FtpPasswordLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.defaultPassword = StringVar()
        self.FtpPasswordEntry=Entry(self.FtpPasswordLabel_brother,width=30,textvariable = self.defaultPassword)
        self.defaultPassword.set('123456')
        self.FtpPasswordEntry.pack(side=LEFT,expand='no')
#============Run
        self.RunButton=Button(self.BottomLabel_Father,text=u'开始升级',width=44,height=5,command=self.DownloadFileThroughTelnet)
        self.RunButton.pack(side=LEFT,expand='yes')

if __name__=='__main__':
    multiprocessing.freeze_support()
    app=Application()
    app.master.title('Hello world again!')
    app.master.geometry('900x650')
    app.mainloop()