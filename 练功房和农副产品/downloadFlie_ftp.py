#-*- encoding: utf8 -*-
__author__ = 'MengZe'
from ftplib import FTP   
import os
import Moudle_GetFileFtpPath as GFFP


def downloadFtpFile(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename,local_path):
    ftp = FTP() 
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    target_filepath=GFFP.SearchInDirList([file_path],target_filename,[ftp_serverip,port,timeout,UserName,PassWD])
    ftp.connect(ftp_serverip,port,timeout) # connect ftp server 
    ftp.login(UserName,PassWD) # login  
    print ftp.getwelcome()  # print welcome info 
    ftp.cwd(target_filepath)    # set FTP path  
    #file_list = ftp.nlst()       # get file list 
    #for name in file_list:  
    #    print(name)             # print all file  
    path = local_path + target_filename    # set local path file

    f = open(path,'wb')         # create a temp file   
    filename = 'RETR ' + target_filename    
    ftp.retrbinary(filename,f.write) # download file  
    f.close() 
    ftp.quit()# quit
    print('Download_finished---'+target_filename)
    print('local_path----------'+local_path)

if __name__ == '__main__':
    ftp_serverip='172.16.1.182'
    timeout = 30  
    port = 21
    UserName='dev'
    PassWD='dev'
    file_path='/test1_test2/iTN8600/software/iTN167A_SDN_1.0.11_20171129/'
    #file_path=''
    target_filename='iTN167A_SDN_1.0.11_20171129.rar' 
    local_path='d:/py_ftp_download/'
    downloadFtpFile(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename,local_path)