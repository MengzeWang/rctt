#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'MengZe'
from ftplib import FTP   
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def strip_posttrix(filename_str):
    possibel_postx=['rar','rsh','rbf','rsh','rbf','bin','doc','HEX','hex']
    tgt_sp_arr=filename_str.split('.')
    for px in possibel_postx:#remove postrix
        for tgt_sp_arri in tgt_sp_arr:
            if tgt_sp_arri==px:
                filename_str=filename_str.strip('.'+px)
    return filename_str
def SearchInDirList(dir_list,target_filename,stop_if_oneFile,*ftp_settings):
    print('searching_File:%s' %(target_filename))
    if ftp_settings:
        global ftp
        global target_may_in
        ftp=FTP()
        target_filename=strip_posttrix(target_filename)
        target_may_in=target_filename.replace('.','\.')
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
    hunt_get=[[],[]]
    dir_real_list=[]
    shoot_t=0
    for dir_i in dir_list:
        target_down=re.match('.*'+target_may_in+'.*',dir_i,re.I)
        #print('**************dir_i**************')
        #print(dir_i)#-rw-rw-rw-   1 user     group        2022 Mar 17  2017
                    #-rw-rw-rw-   1 user     group     1565074 Aug 21  2017 iTN8600-LEO2D_SYSTEM_7.6.5_20170821.rar		
        if target_down:
            shoot_t=shoot_t+1
            target_down_signal=1
            hunt_get0=[ftp.pwd(),dir_i[55:len(dir_i)]]
            print('hunt_get0:')
            print(hunt_get0)
            print('TARGET DWON!('+str(shoot_t)+')--'+ftp.pwd()+'/'+hunt_get0[1])
            hunt_get[0].append(hunt_get0[0])#zhongwen luan ma
            hunt_get[1].append(hunt_get0[1])
            if stop_if_oneFile==1:
                return hunt_get
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
        process_count=0
        for dir_i_real in dir_real_list:
            process_count=process_count+1
            #print("open:"+ftp.pwd()+'/'+dir_i_real)
            print str(process_count)+'/'+str(len(dir_real_list))
            ftp.cwd(dir_i_real)
            dir_subi_real=[]
            ftp.dir("",dir_subi_real.append)
            dir_i_real_reslut=SearchInDirList(dir_subi_real,target_filename,stop_if_oneFile)
            if dir_i_real_reslut[0][0]!='Failed':
                #if target_may_in==target_filename:
                print 'yeah~'
                print dir_i_real_reslut[1]
                target_down_signal=1
                hunt_get0=dir_i_real_reslut
                hunt_get[0]=hunt_get[0]+hunt_get0[0]
                hunt_get[1]=hunt_get[1]+hunt_get0[1]
                #else:
                if stop_if_oneFile==1:
                    #return [hunt_get,'yeah']
                    break
        ftp.cwd('..')
    if target_down_signal==0:
        return [['Failed'],['oh_no']]
    else:
        if ftp_settings:
            print 'searching finished.'
            print(hunt_get)
            ftp.quit()
        return hunt_get
def SearchInDirListFor86_A(dir_list,target_filename,stop_if_oneFile,goDeep=10,*ftp_settings):
    print('searching_File:%s' %(target_filename))
    if ftp_settings:
        global ftp
        global target_may_in
        ftp=FTP()
        target_filename=strip_posttrix(target_filename)
        target_may_in=target_filename.replace('.','\.')
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
    hunt_get=[[],[],[]]
    dir_real_list=[]
    shoot_t=0
    #print('%%%%%%%%%%%%%%%%')
    #print(dir_list)
    #print(ftp.dir())
    #print('%%%%%%%%%%%%%%%%')
    quik_search_res=0
    for dir_i in dir_list:
        target_down=re.match('.*'+target_may_in+'.*',dir_i)
        #print('**************dir_i**************')
        #print(dir_i)#-rw-rw-rw-   1 user     group        2022 Mar 17  2017
                    #-rw-rw-rw-   1 user     group     1565074 Aug 21  2017 iTN8600-LEO2D_SYSTEM_7.6.5_20170821.rar		
        if target_down:
            quik_search_res=1
            shoot_t=shoot_t+1
            target_down_signal=1
            hunt_get0=[ftp.pwd(),dir_i[55:len(dir_i)],dir_i[41:54].strip()]
            print('hunt_get0:')
            print(hunt_get0)
            print('TARGET DWON!('+str(shoot_t)+')--'+ftp.pwd()+'/'+hunt_get0[1])
            hunt_get[0].append(hunt_get0[0])#zhongwen luan ma
            hunt_get[1].append(hunt_get0[1])
            hunt_get[2].append(hunt_get0[2])
            if stop_if_oneFile==1:
                return hunt_get

    if (quik_search_res==0)and(goDeep>=0):
        for dir_i in dir_list:
            target_down=re.match('.*'+target_may_in+'.*',dir_i,re.I)
            #print('**************dir_i**************')
            #print(dir_i)#-rw-rw-rw-   1 user     group        2022 Mar 17  2017
                        #-rw-rw-rw-   1 user     group     1565074 Aug 21  2017 iTN8600-LEO2D_SYSTEM_7.6.5_20170821.rar		
            if target_down:
                shoot_t=shoot_t+1
                target_down_signal=1
                hunt_get0=[ftp.pwd(),dir_i[55:len(dir_i)],dir_i[41:54].strip()]
                print('hunt_get0:')
                print(hunt_get0)
                print('TARGET DWON!('+str(shoot_t)+')--'+ftp.pwd()+'/'+hunt_get0[1])
                hunt_get[0].append(hunt_get0[0])#zhongwen luan ma
                hunt_get[1].append(hunt_get0[1])
                hunt_get[2].append(hunt_get0[2])
                if stop_if_oneFile==1:
                    return hunt_get
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
        process_count=0
        for dir_i_real in dir_real_list:
            process_count=process_count+1
            #print("open:"+ftp.pwd()+'/'+dir_i_real)
            print(str(process_count)+'/'+str(len(dir_real_list)))
            print('open:'+dir_i_real)
            ftp.cwd(dir_i_real)
            dir_subi_real=[]
            ftp.dir("",dir_subi_real.append)
            dir_i_real_reslut=SearchInDirListFor86_A(dir_subi_real,target_filename,stop_if_oneFile,goDeep-1)
            if dir_i_real_reslut[0][0]!='Failed':
                #if target_may_in==target_filename:
                print 'yeah~'
                print dir_i_real_reslut[1]
                target_down_signal=1
                hunt_get0=dir_i_real_reslut
                hunt_get[0]=hunt_get[0]+hunt_get0[0]
                hunt_get[1]=hunt_get[1]+hunt_get0[1]
                hunt_get[2]=hunt_get[2]+hunt_get0[2]
                #else:
                if stop_if_oneFile==1:
                    #return [hunt_get,'yeah']
                    break
        ftp.cwd('..')
    if target_down_signal==0:
        return [['Failed'],['oh_no']]
    else:
        if ftp_settings:
            print 'searching finished.'
            print(hunt_get)
            ftp.quit()
        return hunt_get

#{'onlyOneFreshFile': 1, 'FreshFile_Name': 'N_RITP_V76_BR_741', 'FreshFile_path': '/itn8600-mx2/N_RITP_V76_BR', 'FreshFile_Date': 'May  8 11:46'}
def findMostFreshFileBaseOn_SearchInDirListFor86_A_retrun(dir_list,target_filename,stop_if_oneFile,goDeep=10,*ftp_settings):
    regex = re.compile('\s+')
    MonthMapping={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    allMatchresult=SearchInDirListFor86_A(dir_list,target_filename,stop_if_oneFile,goDeep,*ftp_settings)
    #print(allMatchresult)
    if allMatchresult[0][0]=='Failed':
        print('no result,quit')
        return {'onlyOneFreshFile':-1,'FreshFile_Name':target_filename,'FreshFile_path':None,'FreshFile_Date':None}
    onlyOneFreshFile=1
    FreshFile_Date='initial'
    File_index=0
    for match_namei in allMatchresult[1]:
        File_path=allMatchresult[0][File_index]
        File_name=match_namei
        File_date=allMatchresult[2][File_index]
        File_index=File_index+1
        File_date_arr=regex.split(File_date)
        if File_index==0:#如果是第一个文件，初始化文件日期和路径
            FreshFile_path=File_path
            FreshFile_Date=File_date
            FreshFile_Name=match_namei
            FreshFile_date_arr=regex.split(FreshFile_Date)
        else:#不是第一个文件，和当前已获得的文件日期比较，如果更新，则替换，继续遍历；否则继续遍历
            if (':' in FreshFile_Date)and(':' not in File_date):#FreshFile_Date是今年的文件，当前文件不是今年的文件，跳过
                pass
            elif (':' not in FreshFile_Date)and(':' in File_date):#当前文件是今年的文件，FreshFile_Date不是今年的文件，替换
                FreshFile_Date=File_date
                FreshFile_path=File_path
                FreshFile_Name=match_namei
                FreshFile_date_arr=regex.split(FreshFile_Date)
            else:#同年
                if (':' not in File_date):#最后信息不是小时分钟，而是年
                    if int(FreshFile_date_arr[2])>int(File_date_arr[2]):#FreshFile_Date年大
                        pass
                    elif int(FreshFile_date_arr[2])<int(File_date_arr[2]):#FreshFile_Date年小
                        FreshFile_Date=File_date
                        FreshFile_path=File_path
                        FreshFile_Name=match_namei
                        FreshFile_date_arr=regex.split(FreshFile_Date)
                    else:#同年
                        if MonthMapping[FreshFile_date_arr[0]]>MonthMapping[File_date_arr[0]]:#FreshFile_Date月份大
                            pass
                        elif MonthMapping[FreshFile_date_arr[0]]<MonthMapping[File_date_arr[0]]:#FreshFile_Date月份小
                            FreshFile_Date=File_date
                            FreshFile_path=File_path
                            FreshFile_Name=match_namei
                            FreshFile_date_arr=regex.split(FreshFile_Date)
                        else:#同年同月
                            if int(FreshFile_date_arr[1])>int(File_date_arr[1]):#FreshFile_Date日子大
                                pass
                            elif int(FreshFile_date_arr[1])<int(File_date_arr[1]):#FreshFile_Date日子小
                                FreshFile_Date=File_date
                                FreshFile_path=File_path
                                FreshFile_Name=match_namei
                                FreshFile_date_arr=regex.split(FreshFile_Date)
                            else:#同年同月同日，不知道谁更吊，都算上，用‘，’做分隔，FreshFile_Date不用变（因为一样）
                                print('warning!!!!more than one file in same year-month-day-hour-minute!')
                                onlyOneFreshFile=0
                                FreshFile_path=FreshFile_path+','+File_path
                                FreshFile_Name=FreshFile_Name+','+match_namei
                else:#最后信息是小时分钟，不是年
                        if MonthMapping[FreshFile_date_arr[0]]>MonthMapping[File_date_arr[0]]:#FreshFile_Date月份大
                            pass
                        elif MonthMapping[FreshFile_date_arr[0]]<MonthMapping[File_date_arr[0]]:#FreshFile_Date月份小
                            FreshFile_Date=File_date
                            FreshFile_path=File_path
                            FreshFile_Name=match_namei
                            FreshFile_date_arr=regex.split(FreshFile_Date)
                        else:#同年同月
                            if int(FreshFile_date_arr[1])>int(File_date_arr[1]):#FreshFile_Date日子大
                                pass
                            elif int(FreshFile_date_arr[1])<int(File_date_arr[1]):#FreshFile_Date日子小
                                FreshFile_Date=File_date
                                FreshFile_path=File_path
                                FreshFile_Name=match_namei
                                FreshFile_date_arr=regex.split(FreshFile_Date)
                            else:#同年同月同日
                                if int(FreshFile_date_arr[2].split(':')[0])>int(File_date_arr[2].split(':')[0]):#FreshFile_Date小时大
                                    pass
                                elif int(FreshFile_date_arr[2].split(':')[0])<int(File_date_arr[2].split(':')[0]):#FreshFile_Date小时小
                                    FreshFile_Date=File_date
                                    FreshFile_path=File_path
                                    FreshFile_Name=match_namei
                                else:#同年同月同日同时
                                    if int(FreshFile_date_arr[2].split(':')[1])>int(File_date_arr[2].split(':')[1]):#FreshFile_Date分钟大
                                        pass
                                    elif int(FreshFile_date_arr[2].split(':')[1])<int(File_date_arr[2].split(':')[1]):#FreshFile_Date分钟小
                                        FreshFile_Date=File_date
                                        FreshFile_path=File_path
                                        FreshFile_Name=match_namei
                                        FreshFile_date_arr=regex.split(FreshFile_Date)
                                    else:#同年同月同日同时同分，不知道谁更吊，都算上，用‘，’做分隔，FreshFile_Date不用变（因为一样）
                                        print('warning!!!!more than one file in same year-month-day-hour-minute!')
                                        onlyOneFreshFile=0
                                        FreshFile_path=FreshFile_path+','+File_path
                                        FreshFile_Name=FreshFile_Name+','+match_namei
        #print('++++++++++++++File_date:%s' %(File_date))
        #print('--------------FreshFile_Date:%s' %(FreshFile_Date))
    if FreshFile_Date=='initial':#ftp文件夹为空或未匹配到结果
        onlyOneFreshFile=-1
    return {'onlyOneFreshFile':onlyOneFreshFile,'FreshFile_Name':FreshFile_Name,'FreshFile_path':FreshFile_path,'FreshFile_Date':FreshFile_Date}

if __name__ == '__main__':
    target_filename='N_RITP_V76_BR_'
    target_filename2='itn8600-mx2.z'
    target_filename3='N_BSP_V76_MX2_BR_'
    mydir='/itn8600-mx2/N_RITP_V76_BR/'
    mydir2='/test1_test2/iTN8600/software/iTN8600-V-NXU_B_SYSTEM_7.6.23_20180111'
    stop_if_oneFile2=0
    #target_result=SearchInDirList([mydir],target_filename,stop_if_oneFile2,['172.16.1.123',21,30,'test','raisecom'])
    target_result=SearchInDirListFor86_A([mydir],target_filename,stop_if_oneFile2,['172.16.1.123',21,30,'test','raisecom'])#
    print('target_path:')
    print(target_result[0])
    print('match_name:')
    print(target_result[1])
    print('target_date:')
    print(target_result[2])
    target_result_latest=findMostFreshFileBaseOn_SearchInDirListFor86_A_retrun([mydir],target_filename,stop_if_oneFile2,2,['172.16.1.123',21,30,'test','raisecom'])
    print(target_result_latest)
else:
    print '__name__'+__name__
