#-*- encoding: utf8 -*-
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import random,time
import threading
FtpServerUsr='pydd'
FtpServerPWD='123456'
FtpServerPath='D:/'
def startFTPServerOne(FtpServerUsr,FtpServerPWD,FtpServerPath,FtpServerIP,passive_ports_range):
    FtpServerUsr=str(FtpServerUsr)
    FtpServerPWD=str(FtpServerPWD)
    #实例化虚拟用户，这是FTP验证首要条件
    authorizer = DummyAuthorizer()
    #添加用户权限和路径，括号内的参数是(用户名， 密码， 用户目录， 权限)
    authorizer.add_user(FtpServerUsr, FtpServerPWD, FtpServerPath, perm='elradfmw')
    #初始化ftp句柄
    handler = FTPHandler
    handler.authorizer = authorizer
    #添加被动端口范围
    handler.passive_ports = passive_ports_range
    #a=random.randint(2000,3000)
    #handler.passive_ports = range(a,a+1)
    #监听ip 和 端口
    FTPServer((FtpServerIP, 21), handler).serve_forever(timeout=3, blocking=True, handle_exit=True)
    #开始服务
    print('start ftpserver now!')
def startFTPServer_muti(FtpServerUsr,FtpServerPWD,FtpServerPath,FtpServerIP_list):
    FtpServerUsr=str(FtpServerUsr)
    FtpServerPWD=str(FtpServerPWD)
    FtpServerIP_list_arr=FtpServerIP_list.split(',')
    FtpServerIP_list_len=len(FtpServerIP_list_arr)
    spyFtpTaskList=[]
    ftpInstance_list=[]
    passive_ports_range_init=2000
    passive_ports_range_list=[]
    for FtpServerIP_list_arri in FtpServerIP_list_arr:
        #passive_ports_range_i=range(passive_ports_range_init,passive_ports_range_init+10)
        passive_ports_range_i=range(2000,3000)
        passive_ports_range_list.append(passive_ports_range_i)
        passive_ports_range_init=passive_ports_range_init+11
    #print passive_ports_range_list
    for FtpServerIP_list_arri in range(FtpServerIP_list_len):
        t=threading.Thread(target=startFTPServerOne,args=(FtpServerUsr,FtpServerPWD,FtpServerPath,FtpServerIP_list_arr[FtpServerIP_list_arri],passive_ports_range_list[FtpServerIP_list_arri]))
        t.start()
        time.sleep(1)
        #spyFtpTaskList.append(t)

    #for FtpServerIP_list_arri in range(FtpServerIP_list_len):
    #    spyFtpTaskList[FtpServerIP_list_arri].start()
    #    time.sleep(0.1)
def startFTPServer(FtpServerUsr,FtpServerPWD,FtpServerPath,FtpServerIP_list):
    FtpServerUsr=str(FtpServerUsr)
    FtpServerPWD=str(FtpServerPWD)
    FtpServerIP_list_arr=FtpServerIP_list.split(',')
    FtpServerIP_list_len=len(FtpServerIP_list_arr)
    spyFtpTaskList=[]
    ftpInstance_list=[]
    for FtpServerIP_list_arri in FtpServerIP_list_arr:
        #实例化虚拟用户，这是FTP验证首要条件
        authorizer = DummyAuthorizer()
        #添加用户权限和路径，括号内的参数是(用户名， 密码， 用户目录， 权限)
        authorizer.add_user(FtpServerUsr, FtpServerPWD, FtpServerPath, perm='elradfmw')
        #添加匿名用户 只需要路径
        authorizer.add_anonymous(FtpServerPath)
        #初始化ftp句柄
        handler = FTPHandler
        handler.authorizer = authorizer
        #添加被动端口范围
        handler.passive_ports = range(2000,3000)
        #监听ip 和 端口
        ftpInstance=FTPServer((FtpServerIP_list_arri, 21), handler)
        ftpInstance_list.append(ftpInstance)
    for FtpServerIP_list_arri in range(FtpServerIP_list_len):
        t=threading.Thread(target=ftpInstance_list[FtpServerIP_list_arri].serve_forever,args=(3,True,True))
        spyFtpTaskList.append(t)
    for FtpServerIP_list_arri in range(FtpServerIP_list_len):
        spyFtpTaskList[FtpServerIP_list_arri].start()
    #FTPServer((FtpServerIP, 2121), handler).serve_forever(timeout=3, blocking=True, handle_exit=True)
    #开始服务
    print('start ftpserver now!')
    #server.serve_forever(timeout=3, blocking=True, handle_exit=True)
    
    #server.close_all()#dosen't work
    #print('ftpserver has close !')
startFTPServer_muti(FtpServerUsr,FtpServerPWD,FtpServerPath,'192.166.36.52,192.168.23.81')
