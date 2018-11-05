#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from Tkinter import *
import tkMessageBox
import downloadFlie_ftp2 as dlFf
class Application(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.pack()
        self.createWidgets()
    def createWidgets(self):
        self.ftpiplabel=Label(self,text='ftp_ip(default:172.16.1.182)')#FTP IP
        self.ftpiplabel.pack()
        self.ipInput=Entry(self)
        self.ipInput.pack()
        self.userNameLabel=Label(self,text='user_name(default:dev)')#user name
        self.userNameLabel.pack()
        self.userNameInput=Entry(self)
        self.userNameInput.pack()
        self.userPassWDLabel=Label(self,text='user_password(default:dev)')#user password
        self.userPassWDLabel.pack()
        self.userPassWDInput=Entry(self)
        self.userPassWDInput.pack()
        self.filePathLabel=Label(self,text='ftp_path(default:"/test1_test2/iTN8600/")')#file path
        self.filePathLabel.pack()
        self.filePathInput=Entry(self)
        self.filePathInput.pack()
        self.fileNameLabel=Label(self,text='file_name')#file name
        self.fileNameLabel.pack()
        self.fileNameInput=Entry(self)
        self.fileNameInput.pack()
        self.localPathLabel=Label(self,text='local_path(default:d:/py_ftp_download/)')#local path
        self.localPathLabel.pack()
        self.localPathInput=Entry(self)
        self.localPathInput.pack()
        self.alertButton=Button(self,text='Download',command=self.Download)
        self.alertButton.pack()
    def Download(self):
        ftpip=self.ipInput.get() or '172.16.1.182'
        ftpusername=self.userNameInput.get() or 'dev'
        ftpuserpassword=self.userPassWDInput.get() or 'dev'
        filePath=self.filePathInput.get() or '/test1_test2/iTN8600/'
        fileName=self.fileNameInput.get() or 'none'
        localPath=self.localPathInput.get() or 'd:/py_ftp_download/'
        if fileName!='none':
            file_is_unique=0
            dlFf.downloadFtpFile2(ftpip,21,30,ftpusername,ftpuserpassword,filePath,fileName,file_is_unique,localPath)
            tkMessageBox.showinfo('Message','download_finished:%s' %(fileName))
app=Application()
app.master.title('Hello world again!')
app.master.geometry('800x600')
app.mainloop()