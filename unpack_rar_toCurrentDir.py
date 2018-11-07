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
            try:
                rf.extract(f.filename)
                shutil.move(f.filename,file_name[0:len(file_name)-4].replace('.','')+'__'+f.filename)
                inside_files.append(file_name[0:len(file_name)-4].replace('.','')+'__'+f.filename)
            except:
                print('an error occured when process unpack,skip this file:%s' % (f.filename))
        #rf.extractall()  
        rf.close()
    else:
        print('no such file %s,quit' %(file_name))
        return
    return inside_files
if __name__=='__main__':
    path=r'D:\py_ftp_download\doc_based_download\iTN8600-A-SH2_A_SYSTEM_7.7.20_20181105\iTN8600-A-SH2_A_SYSTEM_7.7.20_20181105'

    file_name=u'iTN8600-A-SH2试产配置文件和命令.rar'
    #rar = rarfile.RarFile(file_name) 
    #rar.extractall('D:\pyS\\')  
    #print os.path.isfile(file_name)
    #print os.path.isdir(file_name2)

    a=unpack_rar_toCurrentDir(path,file_name)
    #print a

