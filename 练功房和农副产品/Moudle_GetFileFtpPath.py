#!/usr/bin/env python
# -*- coding: utf-8 -*-
' a test module '

__author__ = 'MengZe'
from ftplib import FTP   
import os
import re
def SearchInDirList(dir_list,target_filename,*ftp_settings):
    if ftp_settings:
        global ftp
        global target_may_in
        ftp=FTP()
        dot_searcher=0
        while dot_searcher!=len(target_filename):
            dot_searcher=dot_searcher+1
            if target_filename[len(target_filename)-dot_searcher]=='.':
                target_may_in=target_filename[0:len(target_filename)-dot_searcher]
                dot_searcher=len(target_filename)
        print 'First Initialize settings'
        print 'target_may_in:'+target_may_in
        #print ftp_settings
        for ftpsx in ftp_settings[0]:
            #print type(ftpsx)
            print ftpsx
        ftp.connect(ftp_settings[0][0],ftp_settings[0][1],ftp_settings[0][2])
        ftp.login(ftp_settings[0][3],ftp_settings[0][4])
        print ftp.getwelcome()  # print welcome info
        if not dir_list:#if first dir input is empty,initial dirlist to root dir list 
            ftp.dir("",dir_list.append)
        else:#have give a path to search
            ftp.cwd(dir_list[0])
            dir_list=[]
            ftp.dir("",dir_list.append)
    bottom_dir=1
    target_down_signal=0
    dir_real_list=[]
	
    for dir_i in dir_list:
        target_down=re.match('.*'+target_filename+'.*',dir_i)
        target_may_down=re.match('.*'+target_may_in+'$',dir_i)
        #print dir_i#-rw-rw-rw-   1 user     group        2022 Mar 17  2017 
        if target_down:
            print('TARGET DWON!--'+ftp.pwd())
            target_down_signal=1
            return ftp.pwd()
        elif target_may_down:
            cur_dir_e=dir_i[55:len(dir_i)]
            try:
                ftp.cwd(ftp.pwd()+'/'+cur_dir_e)
            except:
                print ('line 46 error:('+ftp.pwd()+'/'+cur_dir_e+') is not a dir')
            print('TARGET maybe DWON!--'+ftp.pwd())
            target_down_signal=1
            return ftp.pwd()
        else:
            cur_dir=dir_i[55:len(dir_i)]
            #print cur_dir
            cur_dir_attribute=dir_i.split(' ')[0]
            if (re.match(r'd.*',cur_dir_attribute))and(cur_dir!='.')and(cur_dir!='..'):#can modify to use rematch instead of '.'and'..'
                bottom_dir=0
                dir_real_list.append(cur_dir)
                #print(cur_dir)
                #print cur_dir_attribute
                #re.match(r'd.*',cur_dir_attribute).group(0)
    if bottom_dir==1:#current dir is  bottom layer
        #print ("bottom--"+ftp.pwd())
        ftp.cwd('..')
    else:#bottom_dir=0 current dir is not bottom layer
        for dir_i_real in dir_real_list:
            ftp.cwd(dir_i_real)
            print("open:"+ftp.pwd()+'/'+dir_i_real)
            dir_subi_real=[]
            ftp.dir("",dir_subi_real.append)
            dir_i_real_reslut=SearchInDirList(dir_subi_real,target_filename)
            if dir_i_real_reslut!='Failed':
                print 'yeah~'
                return dir_i_real_reslut
        ftp.cwd('..')
    if target_down_signal==0:
        return 'Failed'
    if ftp_settings:
        ftp.quit()
if __name__ == '__main__':
    target_filename='iTN8600-V-NXU_B_SYSTEM_7.6.23_20180111.rar'
    target_filename2='RA1302AV23_20170401.rbf.rsh'
    mydir='/test1_test2/iTN8600/software'
    mydir2='/test1_test2/iTN8600/software/iTN8600-V-NXU_B_SYSTEM_7.6.23_20180111'
    target_path=SearchInDirList([mydir2],target_filename,['172.16.1.182',21,30,'dev','dev'])
    print 'target_path:'+target_path
else:
    print '__name__'+__name__