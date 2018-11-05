# -*- coding: utf-8 -*- 
#sdTupu_file："st_xxxx" 
#config_file:"..\\config\\config.conf"
#<tag>
#priority:"1" (1-4)
#author: "XXX"
#modulename:"iTN8600_A_autoupgrade"
#</tag>
#casename:"iTN8600_A_autoupgrade"
#description:"每日自动构建版本更新检测及设备升级"
#productname:"iTN8600"
#createTime:"2018-05-12"
#topoMap:
#
__author__ = 'MengZe'
global shutil,GFFP3,dlFf,t2m,IGT,NewVersionCheck,NewVersionCheck_andUpgradeDev
import os,re,sys,shutil,time
reload(sys)
sys.setdefaultencoding('utf-8')
import Moudle_GetFileFtpPath3 as GFFP3
import downloadFlie_ftp2 as dlFf
import telnet2_mutiprocess as t2m
import ip_get_test as IGT

#1、检查路径下是否有更新，如果有，下载并返回文件名
def NewVersionCheck(CardName,versionType,local_path,ftp_serverip,UserName,PassWD,ftpFilePath,ftpFileName,MaxDirDeepLength=10):
    regex = re.compile('\s+')
    MonthMapping={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    change_log=''
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    if not os.path.isdir(local_path+'/'+CardName):
        os.mkdir(local_path+'/'+CardName)
    file_freshOnftp=GFFP3.findMostFreshFileBaseOn_SearchInDirListFor86_A_retrun([ftpFilePath],ftpFileName,0,MaxDirDeepLength,[ftp_serverip,21,30,UserName,PassWD])
    freshVersionTxt=local_path+'/'+CardName+'/'+CardName+'_'+versionType+'_fresh.txt'
    print(file_freshOnftp)
    if file_freshOnftp['onlyOneFreshFile']==1:
        freshVersionfile=local_path+'/'+CardName+'/'+'fresh_'+file_freshOnftp['FreshFile_Name']
        freshVersionfile_nopath='fresh_'+file_freshOnftp['FreshFile_Name']
        lastVersionfile=local_path+'/'+CardName+'/'+'last_'+file_freshOnftp['FreshFile_Name']
    elif file_freshOnftp['onlyOneFreshFile']==0:#找到了多个文件
        print('find more than one result,because mz is too busz,no time to do this past,quit')
        print('************************************')
        print(file_freshOnftp)
        print('************************************')
        return#退出func
    else:#没找到文件
        print('did not find any match result,quit')
        return#退出func
    local_fresh_date=''
    if os.path.isfile(freshVersionTxt):#有txt记录
        local_fresh_reader=open(freshVersionTxt,'a+')
        local_fresh_date=local_fresh_reader.read()
        local_fresh_reader.close()
        if local_fresh_date.strip(' ').strip('\n'):#本地记录不为空
            print('local:'+local_fresh_date.strip(' ').strip('\n'))
            ftp_fresh_date=file_freshOnftp['FreshFile_Date']
            if local_fresh_date!=ftp_fresh_date:#有新版本:存在隐藏bug，若上次ftp更新的文件被意外删除，又无更新文件，会认为上上次的版本是最新版本；解决办法：严格比较日期大小；本人测试进度紧张，此先处略
                print('find new version:old version date(%s),new version date(%s)' %(local_fresh_date,ftp_fresh_date))
                if os.path.isfile(freshVersionfile):#如果本地有fresh
                    if os.path.isfile(lastVersionfile):#如果本地有上次存档
                        os.remove(lastVersionfile)#移除上次存档
                        time.sleep(2)
                    shutil.move(freshVersionfile,lastVersionfile)#更新存档
                    time.sleep(2)
                if os.path.isfile(freshVersionfile):
                    os.remove(freshVersionfile)#移除fresh
                os.remove(freshVersionTxt)#移除txt
                change_log=local_fresh_date+'-->'+ftp_fresh_date
                local_fresh_date=ftp_fresh_date
            else:#没新版本
                print('local %s date is same with file on ftp' %(ftpFileName))
                print('change_log:none')
                return #退出func
    else:
        change_log='none-->'+file_freshOnftp['FreshFile_Date']
        local_fresh_date=file_freshOnftp['FreshFile_Date']
    #已确认无本地记录或为空
    if os.path.isfile(freshVersionfile):#如果本地有fresh
        os.remove(freshVersionfile)#移除fresh
    dlff_dlres=dlFf.downloadFtpFileBaseOn_fMFFile86_A_retrun(ftp_serverip,21,30,UserName,PassWD,file_freshOnftp,local_path,CardName,MaxDirDeepLength,localFilename=freshVersionfile_nopath)#更新fresh
    if local_fresh_date!='':
        local_fresh_reader=open(freshVersionTxt,'a+')
        local_fresh_reader.write(local_fresh_date)
        local_fresh_reader.close()
    print('change_log:'+change_log)
    print('new file ftp path:%s' %(dlff_dlres[0]['target_filepath_ftp']))
    return freshVersionfile_nopath

def NewVersionCheck_andUpgradeDev(versionType,ftp_serverip,local_path,UserName,PassWD,ftpFilePath,ftpFileName,CardName,Hostname_list,ftp3cd_usr,ftp3cd_pwd,reset_card=0):
    NewFileDetectRes=NewVersionCheck(CardName,versionType,local_path,ftp_serverip,UserName,PassWD,ftpFilePath,ftpFileName,2)
    multiprocessing_on=1
    ftpserver_ip_dict={}
    for Hostname_listi in Hostname_list.split(';'):
        Dev_list_arr=Hostname_listi.split('_')
        if int(Dev_list_arr[1]) not in ftpserver_ip_dict:
            ftpserver_ip_dict[int(Dev_list_arr[1])]=IGT.getSameSegmentIpOnComputerNetCard(Dev_list_arr[0],'255.255.255.0')
    print(ftpserver_ip_dict)
    if NewFileDetectRes:
        print('start upgrade device with:%s' %(NewFileDetectRes))
        t2m.download_svcfile_multi(Hostname_list,CardName,NewFileDetectRes,ftpserver_ip_dict,ftp3cd_usr,ftp3cd_pwd,reset_card,multiprocessing_on)
    else:
        print(CardName,versionType,'does not need to update,quit')


#======================取ftp上的版本，比较本地文件，若有更新则下载==========mx2==============
versiontype_mx2='sys'
ftp_serverip_mx2='172.16.1.123'
local_path_mx2='d:/py_ftp_download/'
username_mx2='test'
passwd_mx2='raisecom'
ftpfilepath_mx2='/itn8600-mx2/n_ritp_v76_br/'
ftpfilename_mx2='itn8600-mx2.z' 
cardname_mx2='itn8600-mx2'
reset_card_mx2=0
#======================取ftp上的版本，比较本地文件，若有更新则下载========nxu================
versiontype_nxu='sys'
ftp_serverip_nxu='172.16.1.123'
local_path_nxu='d:/py_ftp_download/'
username_nxu='test'
passwd_nxu='raisecom'
ftpfilepath_nxu='/itn8600-a-nxu-linux-make/n_ritp_v76_br/'
ftpfilename_nxu='itn8600-a-nxu.z' 
cardname_nxu='itn8600-nxu'
reset_card_nxu=0
#======================取ftp上的版本，比较本地文件，若有更新则下载========pg8================
versiontype_pg8='sys'
ftp_serverip_pg8='172.16.1.123'
local_path_pg8='d:/py_ftp_download/'
username_pg8='test'
passwd_pg8='raisecom'
ftpfilepath_pg8='/itn8600-a-nxu-linux-make/n_ritp_v76_br/'
ftpfilename_pg8='itn8600-a-nxu.z' 
cardname_pg8='itn8600-nxu'
reset_card_pg8=0
#=====================若有更新，下载至设备=================================================
hostname_list='192.168.34.2_1;192.168.34.3_1'#device-ip_ftpserver_ip_dict-index;
ftp3cd_usr='pydd'
ftp3cd_pwd='123456'
newversioncheck_andupgradedev(versiontype_mx2,ftp_serverip_mx2,local_path_mx2,username_mx2,passwd_mx2,ftpfilepath_mx2,ftpfilename_mx2,cardname_mx2,hostname_list,ftp3cd_usr,ftp3cd_pwd,reset_card_mx2)
newversioncheck_andupgradedev(versiontype_nxu,ftp_serverip_nxu,local_path_nxu,username_nxu,passwd_nxu,ftpfilepath_nxu,ftpfilename_nxu,cardname_nxu,hostname_list,ftp3cd_usr,ftp3cd_pwd,reset_card_nxu)
newversioncheck_andupgradedev(versiontype_nxu,ftp_serverip_nxu,local_path_nxu,username_nxu,passwd_nxu,ftpfilepath_nxu,ftpfilename_nxu,cardname_nxu,hostname_list,ftp3cd_usr,ftp3cd_pwd,reset_card_nxu)
