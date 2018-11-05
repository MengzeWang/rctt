#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from Tkinter import *
from multiprocessing import Process
import telnet2Dev as t2D
import tkMessageBox
import sys,os,re,time
import multiprocessing



class Application(Frame):
    global window
    window=Tk()
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.pack()
        self.createWidgets()
    def addOPIntoTempList(self,event):
        self.DevAddedOPlistListbox.insert(END,self.DevOPlistListbox.get(self.DevOPlistListbox.curselection())+'_'+str(self.DevOPTimesEntry.get())+u'_次')
        self.defaultOPTimes.set('1')
    def RemoveFromOPIntoTempList(self,event):
        try:
            self.DevAddedOPlistListbox.delete(int(self.DevAddedOPlistListbox.curselection()[0]))
        except Exception as e:
            print(u'已选操作列表为空或者你点偏了！又或者你鼠标没动，一直在双击！')
    def addGenerateOPTask(self):
        curValue_loopTimes=int(self.DevLoopTimesEntry.get())
        if curValue_loopTimes<0:
            curValue_loopTimes=0
        curListLen=self.DevAddedOPlistListbox.size()
        print(curListLen)
        taskListStr=''#用于显示（ip:备盘复位_1_次->人工倒换_1_次）
        for curListLeni in range(0,int(curListLen)):
            #print(self.DevAddedOPlistListbox.get(curListLeni))
            taskListStr=taskListStr+self.DevAddedOPlistListbox.get(curListLeni)+'->'
        taskListStr=self.DevAddDevEntry.get()+':'+taskListStr.strip('->')+':'+str(curValue_loopTimes)
        if (self.DevAddDevEntry.get())and(curListLen!=0):
            print(taskListStr)
            self.DevGenerateOPlistListbox.insert(END,taskListStr)
        else:
            tkMessageBox.showinfo('Message',u'未填设备ip或已选操作列表为空！')
    def clearTaskList(self):
        curListLen=self.DevAddedOPlistListbox.size()
        self.DevAddedOPlistListbox.delete(0,curListLen)
    def startToRun(self):
        curListLen=self.DevGenerateOPlistListbox.size()
        for curListLeni in range(0,int(curListLen)):
            TaskList_ip=self.DevGenerateOPlistListbox.get(curListLeni).split(':')[0]
            TaskList_sub=self.DevGenerateOPlistListbox.get(curListLeni).split(':')[1]
            TaskList_loopTimes=int(self.DevGenerateOPlistListbox.get(curListLeni).split(':')[2])
            p = Process(target=t2D.doTaskSingleDev2, args=(TaskList_ip,TaskList_sub,TaskList_loopTimes,))
            print(TaskList_ip+':start do job')
            p.start()
    def openUpgradeLogDir(self):
        os.system('start D:\\')
    def minusLoopTimes(self):
        curValue=int(self.DevLoopTimesEntry.get())
        if curValue>0:
            self.defaultLoopTimes.set(str(curValue-1))
    def plusLoopTimes(self):
        curValue=int(self.DevLoopTimesEntry.get())
        if curValue>=0:
            self.defaultLoopTimes.set(str(curValue+1))
    def minusOpTimes(self):
        curValue=int(self.DevOPTimesEntry.get())
        if curValue>0:
            self.defaultOPTimes.set(str(curValue-1))
    def plusOpTimes(self):
        curValue=int(self.DevOPTimesEntry.get())
        if curValue>=0:
            self.defaultOPTimes.set(str(curValue+1))
    def createWidgets(self):
        self.DevUPSideLabel_Father=Label(self,bg='red',width=100,height=28)#上半部分基底（28）
        self.DevUPSideLabel_Father.pack(side=TOP,expand='no')
        self.DevDOWNSideLabel_Father=Label(self,bg='blue',width=100,height=20)#下半部分基底（20）
        self.DevDOWNSideLabel_Father.pack(side=BOTTOM,expand='yes')
        
        self.DevALLOPLabel_Father=Label(self.DevUPSideLabel_Father,bg='yellow',width=44,height=28)#可选操作列表基底
        self.DevALLOPLabel_Father.pack(side=LEFT,expand='no',anchor='nw')
        self.DevAddOPLabel_Father=Label(self.DevUPSideLabel_Father,bg='green',width=10,height=28)#添加用的中间栏基底
        self.DevAddOPLabel_Father.pack(side=LEFT,expand='yes',anchor='nw')
        self.DevOPViewLabel_Father=Label(self.DevUPSideLabel_Father,bg='yellow',width=44,height=28)#构建操作序列的列表基底
        self.DevOPViewLabel_Father.pack(side=LEFT,expand='no',anchor='nw')
        #设备ip
        self.DevAddDevLabel_Father=Label(self.DevAddOPLabel_Father,width=10,height=1)
        self.DevAddDevLabel_Father.pack(side=TOP,expand='no',anchor='n')
        self.DevAddDevLabel=Label(self.DevAddDevLabel_Father,text=u'设备IP地址:',width=10,height=1)
        self.DevAddDevLabel.pack(side=TOP,expand='no',anchor='n')
        self.defaultIp = StringVar()
        self.DevAddDevEntry=Entry(self.DevAddDevLabel_Father,textvariable = self.defaultIp)
        self.DevAddDevEntry.pack(side=TOP,expand='no',anchor='n')
        #执行次数
        self.DevOPTimes_title=Label(self.DevAddOPLabel_Father,text=u'单步执行次数',width=10,height=1)
        self.DevOPTimes_title.pack(side=TOP,expand='no',anchor='n')
        self.DevOPTimes_title2=Label(self.DevAddOPLabel_Father,width=20,height=1)
        self.DevOPTimes_title2.pack(side=TOP,expand='yes',anchor='n')
        
        self.minusOpTimesButton=Button(self.DevOPTimes_title2,text='-',width=3,command=self.minusOpTimes)
        self.minusOpTimesButton.pack(side=LEFT)
        self.defaultOPTimes = StringVar()
        self.DevOPTimesEntry=Entry(self.DevOPTimes_title2,width=3,textvariable = self.defaultOPTimes)#执行次数
        self.defaultOPTimes.set('1')
        self.DevOPTimesEntry.pack(side=LEFT)
        self.plusOpTimesButton=Button(self.DevOPTimes_title2,text='+',width=3,command=self.plusOpTimes)
        self.plusOpTimesButton.pack(side=LEFT)
        #可选操作列表标题
        self.DevAddDevLabel_title=Label(self.DevALLOPLabel_Father,text=u'可选操作列表',width=44,height=1)
        self.DevAddDevLabel_title.pack(side=TOP,expand='no',anchor='nw')
        #可选操作列表
        self.DevOPListLabel_Father=Label(self.DevALLOPLabel_Father,width=44)#可选操作列表基底
        self.DevOPListLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevOPListStr=StringVar()
        self.DevOPlistListbox=Listbox(self.DevOPListLabel_Father,listvariable=self.DevOPListStr,width=44,height=26)
        self.DevOPListStr.set(('整机重启','主盘复位','清除倒换','锁定','强制倒换','人工倒换','等待主备同步'))
        self.DevOPlistListbox.bind('<Double-Button-1>',self.addOPIntoTempList)
        self.DevOPlistListbox.pack()
        #配置操作次数
        self.DevOPTimesLabel_Father=Label(self.DevAddOPLabel_Father,bg='green',width=12,height=14)#添加用的中间栏基底
        self.DevOPTimesLabel_Father.pack(side=TOP,expand='no',anchor='n')
        #已选操作列表标题
        self.DevAddDevLabel_Father=Label(self.DevOPViewLabel_Father,text=u'已选择的操作',width=44,height=1)
        self.DevAddDevLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        #已选操作列表
        self.DevAddedOPListLabel_Father=Label(self.DevOPViewLabel_Father,width=44)#已添加的操作列表基底
        self.DevAddedOPListLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevAddedOPListStr=StringVar()#用于清空
        self.DevAddedOPlistListbox=Listbox(self.DevAddedOPListLabel_Father,listvariable=self.DevAddedOPListStr,width=44,height=25)
        self.DevAddedOPlistListbox.bind('<Double-Button-1>',self.RemoveFromOPIntoTempList)
        self.DevAddedOPlistListbox.pack()
        #设置主循环次数
        self.DevSetMainLoopTimesLabel=Label(self.DevAddedOPListLabel_Father,width=43,height=1,bg='red')#设置主循环次数基底
        self.DevSetMainLoopTimesLabel.pack()
        #清空已选列表-按钮
        self.clearTaskListButton=Button(self.DevSetMainLoopTimesLabel,width=6,text=u'清空列表',command=self.clearTaskList)
        self.clearTaskListButton.pack(side=LEFT,expand='no')
        #设置主循环次数-标题
        self.DevSetMainLoopTimesLabel_title=Label(self.DevSetMainLoopTimesLabel,text=u'主循环次数(0代表无限循环)',width=23,height=1,bg='green')#设置主循环次数基底
        self.DevSetMainLoopTimesLabel_title.pack(side=LEFT)
        #主循环次数减按钮
        self.minusLoopTimesButton=Button(self.DevSetMainLoopTimesLabel,text='-',width=3,command=self.minusLoopTimes).pack(side=LEFT)
        self.defaultLoopTimes = StringVar()
        self.DevLoopTimesEntry=Entry(self.DevSetMainLoopTimesLabel,textvariable = self.defaultLoopTimes,width=4)#执行次数
        self.defaultLoopTimes.set('0')
        self.DevLoopTimesEntry.pack(side=LEFT,expand='yes')
        #主循环次数加按钮
        self.plusLoopTimesButton=Button(self.DevSetMainLoopTimesLabel,text='+',width=3,command=self.plusLoopTimes).pack(side=LEFT)
        #生成计划任务-按钮
        self.addGenerateOPTaskButton=Button(self.DevAddOPLabel_Father,text=u'生成计划任务',command=self.addGenerateOPTask)
        self.addGenerateOPTaskButton.pack(side=TOP,expand='no')
        #已生成的计划任务标题
        self.DevOPProjectLabel_Father=Label(self.DevDOWNSideLabel_Father,width=100,height=1)#已生成的计划任务标题基底
        self.DevOPProjectLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevOPProjectLabel_Father2=Label(self.DevDOWNSideLabel_Father,width=100,height=19)#已生成的计划任务列表基底
        self.DevOPProjectLabel_Father2.pack(side=TOP,expand='no',anchor='nw')
        self.DevOPProjectLabel_title=Label(self.DevOPProjectLabel_Father,text=u'当前计划任务',width=110,height=1)
        self.DevOPProjectLabel_title.pack(side=TOP,expand='no',anchor='nw')
        #已生成的计划任务列表
        self.DevGenerateOPListStr=StringVar()#用于清空
        self.DevGenerateOPlistListbox=Listbox(self.DevOPProjectLabel_Father2,listvariable=self.DevGenerateOPListStr,width=90,height=19)
        self.DevGenerateOPlistListbox.bind('<Double-Button-1>',self.RemoveFromOPIntoTempList)
        self.DevGenerateOPlistListbox.pack(side=LEFT,expand='no')
        #开始运行按钮
        self.addGenerateOPTaskButton=Button(self.DevOPProjectLabel_Father2,text=u'开始执行',width=10,height=19,command=self.startToRun)
        self.addGenerateOPTaskButton.pack(side=LEFT,expand='no')
        #打开log文件夹按钮
        self.openLogDirButton=Button(self.DevOPProjectLabel_Father2,text=u'查看log',width=10,height=19,command=self.openUpgradeLogDir)
        self.openLogDirButton.pack(side=LEFT,expand='no')


if __name__=='__main__':
    multiprocessing.freeze_support()
    app=Application()
    app.master.title(u'ITN8600夜间无限循环')
    app.master.geometry('900x650')
    app.mainloop()