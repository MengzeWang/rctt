#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from Tkinter import *
import tkMessageBox
class Application(Frame):
    global window
    window=Tk()
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.pack()
        self.createWidgets()
    def print_selection(self):
        if self.var1.get()==1:
            self.Text.insert('end','1')
        else:
            self.Text.insert('end','0')
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

        self.ftpiplabel=Label(self,text='ftp_ip(default:172.16.1.182)',bg='green')#FTP IP
        self.ftpiplabel.pack()
        self.ipInput=Entry(self)
        self.ipInput.pack()
        self.alertButton=Button(self,text='Download',command=self.Download)
        self.alertButton.pack()
        self.Text=Text(self,height=2)
        self.Text.insert('end','abc')
        self.Text.insert('end','\nabc')
        self.Text.pack()
        self.var1 = IntVar()
        self.Checkbutton=Checkbutton(window, text='Python', variable=self.var1, onvalue=1, offvalue=0,command=self.print_selection)
        self.Checkbutton.pack()

    def Download(self):
        ftpip=self.ipInput.get() or '172.16.1.182'
    def do_job(self):
        self.ftpiplabel.config(text='do_job test')

app=Application()
app.master.title('Hello world again!')
app.master.geometry('800x600')
app.mainloop()