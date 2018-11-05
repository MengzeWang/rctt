#coding=utf-8  
import os,sys,time
def start3CD():
    print(u'尝试关闭已经开启的3CD')
    os.system('taskkill -f -im 3CDaemon.EXE')
    print(u'当前运行路径：'+os.getcwd())
    os.system('.\\3cd\\3CDaemon.EXE')
if __name__=='__main__':
    start3CD()