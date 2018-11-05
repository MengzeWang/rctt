#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import os,shutil,time
from del_file import del_Dir
nmsDatabasePath="C:\NMS\NMS\PLATFORM\NNM5\MySQL5"
nmsPath="C:\NMS\NMS"

#step-1:停止网管和数据库服务
print(os.popen('net stop NMSServer').read())
print(os.popen('net stop Nms_database_engine').read())
#step-2:备份数据库
shutil.move(nmsDatabasePath,"C:\\MySQL5")
#step-3:卸载网管-qtp完成
print(u'step-3:卸载网管-qtp完成')
os.system('pause')
#step-4：删除原NMS残留文件
del_Dir(nmsPath)
#step-5:安装基线nms-qtp完成
print(u'step-5:安装基线nms-qtp完成')
os.system('pause')
#step-6:注销数据库服务
print(os.popen(nmsDatabasePath+'\\DelMysqlServer.bat').read())
print(os.popen('net stop NMSServer').read())
time.sleep(4)
print(os.popen('net stop Nms_database_engine').read())
time.sleep(4)
#step-7:删除新网管的MySQL5
del_Dir(nmsDatabasePath)
#step-8:拷贝备份MySQL5
print(u'step-8:准备移动备份MySQL5文件夹至新网管')
os.system('pause')
shutil.move("C:\\MySQL5",nmsDatabasePath)
#step-9:注册数据服务
print(os.popen(nmsDatabasePath+'\\RegMysqlServer.bat').read())
#step-10：检查数据库服务是否启动--跳过
print(u'step-11-12:安装pm及升级-qtp完成')
#step-11:安装性能PM-qtp完成
#step-12:升级-qtp完成