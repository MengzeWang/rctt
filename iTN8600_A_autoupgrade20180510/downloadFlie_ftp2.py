#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from ftplib import FTP   
import os
import Moudle_GetFileFtpPath3 as GFFP3
import unpack_rar_toCurrentDir as URCD
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def downloadFtpFile2(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename,stop_if_oneFile,local_path):#target_filename must cannot have postrix
    target_filename=GFFP3.strip_posttrix(target_filename)
    if not target_filename:
        print('invalid target_filename,quit')
        return None
    ftp = FTP() 
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    ftp.connect(ftp_serverip,port,timeout) # connect ftp server 
    ftp.login(UserName,PassWD) # login  
    print ftp.getwelcome()  # print welcome info 
    target_filepath_raw=GFFP3.SearchInDirList([file_path],target_filename,stop_if_oneFile,[ftp_serverip,port,timeout,UserName,PassWD])
    if target_filepath_raw[0][0]=='Failed':
        print('cannot find (%s) in (%s),quit.' %(target_filename,file_path))
        ftp.quit()# quit
        return None
    else:
        print 'target_filepath_raw'
        print target_filepath_raw
        #pass
    i=0
    download_state_label=[]
    for path_i in target_filepath_raw[0]:
        dir_check=GFFP3.strip_posttrix(target_filepath_raw[1][i])
        if dir_check==target_filepath_raw[1][i]:#use this to know if current target_filepath_raw[1][i] is a file
            target_filepath_ftp=path_i+'/'+target_filepath_raw[1][i]#have no postrix,so join to ftp-dir path
        else:
            target_filepath_ftp=path_i#have postrix,so do not join to ftp-dir path
        print('try to open ftp dir:%s' %(target_filepath_ftp))
        try:
            ftp.cwd(target_filepath_ftp)    # set FTP path
            file_list = ftp.nlst()       # get file list
        except:
            #pass
            print('error happened when try to open ftp dir:%s' %(target_filepath_ftp))
            download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'failed'})
        else:
#            path = local_path + target_filename+'/'+target_filepath_raw[1][i]+'/'  # set local path file
            path = local_path +dir_check+'/'  # set local path file
            if not os.path.isdir(path):
#                if not os.path.isdir(local_path + target_filename+'/'):
#                    os.mkdir(local_path + target_filename+'/')	
                os.mkdir(path)
            for name in file_list:
                print(name)# print all file  
                path_file=path+'/'+name
                f = open(path_file,'wb')         # create a temp file   
                filename = 'RETR ' + name    
                ftp.retrbinary(filename,f.write) # download file  
                f.close()
                if name[-3:]=='rar':
                    unrar_file_list=URCD.unpack_rar_toCurrentDir(path,name)
                    for unrar_file_list_i in unrar_file_list:
                        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':unrar_file_list_i})
                elif name[-3:] in ['bin','rbf','rsh']:
                    download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
                elif name[-1:] in ['z']:
                    download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
        i=i+1
    ftp.quit()# quit

    for dl_resulti in download_state_label:
        print('Download---%s--%s' %(dl_resulti['target_filepath_ftp'],dl_resulti['result']))
    print('local_path----------'+local_path)
    return download_state_label#a list,contain many dict,each dict should represent ether a file(if succes) or a dir(if failed)


def downloadFtpFileUse_fMFFile86_A_retrun(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename,local_path,CardName,goDeep=10,localFilename=None):
    stop_if_oneFile=0
    target_filename=GFFP3.strip_posttrix(target_filename)
    if not target_filename:
        print('invalid target_filename,quit')
        return None
    ftp = FTP() 
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    ftp.connect(ftp_serverip,port,timeout) # connect ftp server 
    ftp.login(UserName,PassWD) # login  
    print ftp.getwelcome()  # print welcome info 
    target_filepath_raw=GFFP3.findMostFreshFileBaseOn_SearchInDirListFor86_A_retrun([file_path],target_filename,stop_if_oneFile,goDeep,[ftp_serverip,port,timeout,UserName,PassWD])
    if target_filepath_raw['onlyOneFreshFile']==-1:
        print('cannot find (%s) in (%s),quit.' %(target_filename,file_path))
        ftp.quit()# quit
        return None
    else:
        print 'target_filepath_raw'
        print target_filepath_raw
        #pass
    i=0
    download_state_label=[]
    file_index=0
    for path_i in target_filepath_raw['FreshFile_path'].split(','):
        #dir_check=GFFP3.strip_posttrix(target_filepath_raw['FreshFile_path'])
        #if dir_check==target_filepath_raw[1][i]:#use this to know if current target_filepath_raw[1][i] is a file
        #    target_filepath_ftp=path_i+'/'+target_filepath_raw[1][i]#have no postrix,so join to ftp-dir path
        #else:
        target_filepath_ftp=path_i#have postrix,so do not join to ftp-dir path
        print('try to open ftp dir:%s' %(target_filepath_ftp))
        try:
            ftp.cwd(target_filepath_ftp)    # set FTP path
            file_list = ftp.nlst()       # get file list
        except:
            #pass
            print('error happened when try to open ftp dir:%s' %(target_filepath_ftp))
            download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'failed'})
        else:
#            path = local_path + target_filename+'/'+target_filepath_raw[1][i]+'/'  # set local path file
            path = local_path +'/'+CardName+'/'  # set local path file
            if not os.path.isdir(path):
#                if not os.path.isdir(local_path + target_filename+'/'):
#                    os.mkdir(local_path + target_filename+'/')	
                os.mkdir(path)
            for name in file_list:
                #print(name)# print all file
                if name==target_filepath_raw['FreshFile_Name'].split(',')[file_index]:
                    if localFilename:#如果指定文件名
                        path_file=path+'/'+localFilename
                    else:
                        path_file=path+'/'+name
                    f = open(path_file,'wb')         # create a temp file   
                    filename = 'RETR ' + name    
                    ftp.retrbinary(filename,f.write) # download file  
                    f.close()
                    if name[-3:]=='rar':
                        unrar_file_list=URCD.unpack_rar_toCurrentDir(path,name)
                        for unrar_file_list_i in unrar_file_list:
                            download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':unrar_file_list_i})
                    elif name[-3:] in ['bin','rbf','rsh']:
                        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
                    elif name[-1:] in ['z']:
                        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
        i=i+1
        file_index=file_index+1
    ftp.quit()# quit
    for dl_resulti in download_state_label:
        print('Download---%s--%s' %(dl_resulti['target_filepath_ftp'],dl_resulti['result']))
    print('local_path----------'+local_path)
    return download_state_label#a list,contain many dict,each dict should represent ether a file(if succes) or a dir(if failed)

def downloadFtpFileBaseOn_fMFFile86_A_retrun(ftp_serverip,port,timeout,UserName,PassWD,fMFFile86_A_retrun,local_path,CardName,goDeep=10,localFilename=None):
    stop_if_oneFile=0
    target_filename=fMFFile86_A_retrun['FreshFile_Name']
    target_filepath_raw=fMFFile86_A_retrun
    ftp = FTP() 
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    ftp.connect(ftp_serverip,port,timeout) # connect ftp server 
    ftp.login(UserName,PassWD) # login  
    print ftp.getwelcome()  # print welcome info 

    if target_filepath_raw['onlyOneFreshFile']==-1:
        print('cannot find (%s) in,quit.' %(target_filename))
        ftp.quit()# quit
        return None
    else:
        print 'target_filepath_raw'
        print target_filepath_raw
        #pass
    i=0
    download_state_label=[]
    file_index=0
    for path_i in target_filepath_raw['FreshFile_path'].split(','):
        target_filepath_ftp=path_i#have postrix,so do not join to ftp-dir path
        print('try to open ftp dir:%s' %(target_filepath_ftp))
        try:
            ftp.cwd(target_filepath_ftp)    # set FTP path
            file_list = ftp.nlst()       # get file list
        except:
            #pass
            print('error happened when try to open ftp dir:%s' %(target_filepath_ftp))
            download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'failed'})
        else:
#            path = local_path + target_filename+'/'+target_filepath_raw[1][i]+'/'  # set local path file
            path = local_path +'/'+CardName+'/'  # set local path file
            if not os.path.isdir(path):
#                if not os.path.isdir(local_path + target_filename+'/'):
#                    os.mkdir(local_path + target_filename+'/')	
                os.mkdir(path)
            for name in file_list:
                #print(name)# print all file
                if name==target_filepath_raw['FreshFile_Name'].split(',')[file_index]:
                    if localFilename:#如果指定文件名
                        path_file=path+'/'+localFilename
                    else:
                        path_file=path+'/'+name
                    f = open(path_file,'wb')         # create a temp file   
                    filename = 'RETR ' + name    
                    ftp.retrbinary(filename,f.write) # download file  
                    f.close()
                    #if name[-3:]=='rar':
                    #    unrar_file_list=URCD.unpack_rar_toCurrentDir(path,name)
                    #    for unrar_file_list_i in unrar_file_list:
                    #        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':unrar_file_list_i})
                    if name[-3:] in ['bin','rbf','rsh']:
                        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
                    elif name[-1:] in ['z']:
                        download_state_label.append({'target_filename':target_filename,'target_filepath_ftp':target_filepath_ftp,'result':'success','local_path':path,'filename':name})
        i=i+1
        file_index=file_index+1
    ftp.quit()# quit
    for dl_resulti in download_state_label:
        print('Download---%s--%s' %(dl_resulti['target_filepath_ftp'],dl_resulti['result']))
    print('local_path----------'+local_path)
    return download_state_label#a list,contain many dict,each dict should represent ether a file(if succes) or a dir(if failed)

if __name__ == '__main__':
    ftp_serverip='172.16.1.182'
    timeout = 30  
    port = 21
    UserName='dev'
    PassWD='dev'
    file_path='/test1_test2/iTN8600/software/'
    #file_path=''
    target_filename='iTN167A_SDN_1.0.11_20171129' 
    target_filename2='iTN8600-V-NXU_B_SYSTEM_7.6.25_20180301' 
    local_path='d:/py_ftp_download/'
    stop_if_oneFile=1
    #downloadFtpFile2(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename2,stop_if_oneFile,local_path)
    ftp_serverip2='172.16.1.123'
    UserName2='test'
    PassWD2='raisecom'
    file_path2='/itn8600-mx2/N_RITP_V76_BR/'
    target_filename='svc_ibc.a' 
    downloadFtpFileUse_fMFFile86_A_retrun(ftp_serverip2,port,timeout,UserName2,PassWD2,file_path2,target_filename,local_path,'iTN8600_A_MX2')