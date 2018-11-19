#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import os,re
import del_file
target_path=r'D:\新建文件夹\TestCaseExecute\Script\EMS\iTN8600-QTP'

def deleteResDir(target_path):
    ls = os.listdir(target_path)
    for lsi in ls:
        c_path = os.path.join(target_path, lsi)#获取文件列表
        if os.path.isdir(c_path):#逐个进入，有Res文件夹的话则删除
            os.chdir(c_path)
            ls2 = os.listdir('.')
            for lsi2 in ls2:
                if re.match('^Res\d+$',lsi2):
                    delete_targetDir=os.path.join(c_path, lsi2)
                    print(delete_targetDir)
                    del_file.del_Dir(delete_targetDir)
if __name__=='__main__':
    deleteResDir(target_path)