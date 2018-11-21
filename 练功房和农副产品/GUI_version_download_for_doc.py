#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from Tkinter import *
import tkMessageBox
import read_word_doc as rwd
class Application(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.pack()
        self.createWidgets()
    def createWidgets(self):
        self.doc_pathlabel=Label(self,text=u'指定word所在路径(默认:D:\py_ftp_download\\test_doc_collect)',width=90)
        self.doc_pathlabel.pack()
        self.doc_pathInput=Entry(self,width=90)
        self.doc_pathInput.pack()
        self.wordfile_nameLabel=Label(self,text=u'提测单文件名（去掉.doc后缀）',width=90)
        self.wordfile_nameLabel.pack()
        self.wordfile_nameInput=Entry(self,width=90)
        self.wordfile_nameInput.pack()
        self.downloadTo_pathLabel=Label(self,text=u'指定版本存放路径(默认:D:\py_ftp_download\doc_based_download)',width=90)
        self.downloadTo_pathLabel.pack()
        self.downloadTo_pathInput=Entry(self,width=90)
        self.downloadTo_pathInput.pack()
        self.alertButton=Button(self,text='Download',command=self.Download)
        self.alertButton.pack()
        self.Text=Text(self)
        self.Text.pack()
    def Download(self):
        doc_path=self.doc_pathInput.get() or r'D:\py_ftp_download\test_doc_collect'
        wordfile=self.wordfile_nameInput.get() or None
        downloadTo=self.downloadTo_pathInput.get() or 'd:\py_ftp_download\doc_based_download'
        if wordfile:
            file_is_unique=1
            sucess_file=rwd.GetDoc_version(doc_path,wordfile,downloadTo)[0]
            self.Text.insert('end',sucess_file)
            tkMessageBox.showinfo('Message',u'下载完成:%s' %(wordfile))

app=Application()
app.master.title(u'给我一个提测单，还你几个文件...')
app.master.geometry('800x600')
app.mainloop()