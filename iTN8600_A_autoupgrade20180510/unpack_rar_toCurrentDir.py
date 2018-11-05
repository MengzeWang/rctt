# -*- coding: utf-8 -*-
import rarfile 
import sys
import os,shutil
#print(sys.path)
def unpack_rar_toCurrentDir(file_path,file_name):
    print(os.path.abspath(__file__)+'functoin:unpack_rar_toCurrentDir')
    if not os.path.isdir(file_path):
        print('invalid path,quit')
        return
    inside_files=[]  
    if os.path.isfile(file_path+'/'+file_name):
        rf = rarfile.RarFile(file_path+'/'+file_name)  
        os.chdir(file_path)
        #print os.getcwd()
        #print os.listdir('.')
        for f in rf.infolist():
            print('%s,%s' %(f.filename, f.file_size))
            rf.extract(f.filename)
            shutil.move(f.filename,file_name[0:len(file_name)-4].replace('.','')+'__'+f.filename)
            inside_files.append(file_name[0:len(file_name)-4].replace('.','')+'__'+f.filename)
        #rf.extractall()  
        rf.close()
    else:
        print('no such file %s,quit' %(file_name))
        return
    return inside_files
#path=r'D:\py_ftp_download\doc_based_download\iTN8600-SH2E_B_SYSTEM_7.6.33_20180320\iTN8600-SH2E_B_SYSTEM_7.6.33_20180320'

#file_name=r'iTN8600-SH2E_B_SYSTEM_7.6.33_20180320.rar'
#rar = rarfile.RarFile(file_name) 
#rar.extractall('D:\pyS\\')  
#print os.path.isfile(file_name)
#print os.path.isdir(file_name2)

#a=unpack_rar_toCurrentDir(path,file_name)
#print a

