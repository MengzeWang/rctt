#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import time,re,os,sys
import multiprocessing
sys.path.append('D:\pyS\peopleCanRestButDevCannot\\')
import telnet2Dev
import ip_get_test as IGT

class DevClass_BD(telnet2Dev.DevClass):
    def __init__(self,DevIp,DevIpMask='255.255.255.0',FtpIp_usr=None):#超时时间，单位s
        self.log_path_deviceUpgradeLog=r'D:\py_ftp_download\\deviceUpgradeLog\\'
        self.ip=DevIp
        self.download_result_str=self.log_path_deviceUpgradeLog+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-download_result.txt'
        super(DevClass_BD,self).__init__(DevIp,log_path=self.log_path_deviceUpgradeLog)#继承父类的初始化
        if self.goodState:
            if FtpIp_usr:
                self.FtpIp=FtpIp_usr
            else:
                self.FtpIp=IGT.getPingSuccesIpOnComputerNetCard(DevIp,DevIpMask)
                print('self.FtpIp',self.FtpIp)
#必有key：CardInfo，list中的每个元素都是一块卡，每块卡的信息都是一个dict，包含的key值有；视输入参数可能有的key：versionInfo，card_at
    def GetDeviceAllCardInfo(self,card_name_PowerType='all',card_state='working',cardVersionGet=False):#card_state can be follows:all/working/non-working
        infoRes={}
        showCard_dict={}
        sh_ca_list=[]
        arrow_name_index=0
        arrow_index=0
        show_cols=0
        showCard_raw=self.DevSendcmdUntil('show card','#')
        print('showCard_raw',showCard_raw.encode('utf-8'))
        for show_card_result_row in showCard_raw.split('\r\n'):
            if len(show_card_result_row.split())>6:
                sh_ca_list.append(show_card_result_row.split())
                if ('Slot' in show_card_result_row)and('State' in show_card_result_row)and('PowerType' in show_card_result_row):
                    print('find arrow name:',show_card_result_row,'current index is:',arrow_index)
                    show_cols=len(show_card_result_row.split())
                    arrow_name_index=arrow_index
                arrow_index=arrow_index+1
        print('sh_ca_list',sh_ca_list)
        slot_col=sh_ca_list[arrow_name_index].index('Slot')
        stat_col=sh_ca_list[arrow_name_index].index('State')
        PowerType_col=sh_ca_list[arrow_name_index].index('PowerType')
        PowerName_col=sh_ca_list[arrow_name_index].index('PowerName')
        sh_ca_list_core=[]
        shCaListCore_collectByDict=[]
        for card_info in sh_ca_list:
            if card_info[0]!='*':
                if len(card_info)!=show_cols:#目前show card结果有7列，后续如果show card结果列数变化，可修改此处，但这里仅是个列数异常提示，不影响使用
                    print('find a unexpected length line:',card_info,'consider this line is not show card valid info,drop it')
                else:
                    sh_ca_list_core.append([card_info[slot_col],card_info[PowerName_col],card_info[stat_col],card_info[PowerType_col]])
                    shCaListCore_collectByDict.append({'Slot':card_info[slot_col],'State':card_info[stat_col],'PowerType':card_info[PowerType_col],'PowerName':card_info[PowerName_col]})
            else: 
                sh_ca_list_core.append([card_info[slot_col+1],card_info[PowerName_col+1],card_info[stat_col+1],card_info[PowerType_col+1]])
                shCaListCore_collectByDict.append({'Slot':card_info[slot_col+1],'State':card_info[stat_col+1],'PowerType':card_info[PowerType_col+1],'PowerName':card_info[PowerName_col+1]})
        infoRes['CardInfo']=shCaListCore_collectByDict#list中的每个元素都是一块卡，每块卡的信息都是一个dict，包含的key值有
        if cardVersionGet:
            ver_result=[]
            if card_state=='all':
                for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
                    ver_result.append(self.multiline_infoprocess(self.DevSendcmdUntil('show ver slot '+str(slot_verx[0]),'#')))
            elif card_state=='working':
                for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
                    if slot_verx[2]=='working':
                        ver_result.append(self.multiline_infoprocess(self.DevSendcmdUntil('show ver slot '+str(slot_verx[0]),'#')))
            else:
                for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
                    if slot_verx[2]!='working':
                        ver_result.append(self.ip+'--'+str(slot_verx[0])+'-'+str(slot_verx[1])+'-'+slot_verx[2])#['192.168.xx.xx',6,'iTN8600-sg8','offline']
            infoRes['versionInfo']=ver_result
        if card_name_PowerType!='all':
            card_at=[]
            for cardi in shCaListCore_collectByDict:
                if (cardi.get('State')=='working')and(re.match('.*'+card_name_PowerType+'$',cardi.get('PowerName'),re.I)):#card name 
                    print('match result:',cardi.get('PowerName'))
                    card_at.append(cardi.get('Slot'))#append slot number
                elif (cardi.get('State')=='working')and(re.match('.*'+card_name_PowerType,cardi.get('PowerType'),re.I)):#or PowerType
                    print('match result:'+cardi.get('PowerType'))
                    card_at.append(cardi.get('Slot'))#append slot number
            infoRes['card_at']=card_at
        print('infoRes',infoRes)
        return infoRes#必有key：CardInfo，list中的每个元素都是一块卡，每块卡的信息都是一个dict，包含的key值有；视输入参数可能有的key：versionInfo，card_at
    def FileTpyeGuess(self,FileName,TailIsFiletype=0):
        filePostrix=FileName.split('.')[len(FileName.split('.'))-1]
        #print filePostrix
        if TailIsFiletype==1:#file name have filetye in the end,such as 1.z.system-boot,this is used for receive read_word_doc return
            return {'FiletypeByGiven':filePostrix,'TrueFileName':FileName.strip(filePostrix).strip(r'.')}
        if filePostrix=='z':
            return 'system-boot'
        elif filePostrix=='bin':
            return 'bootrom'
        elif (filePostrix=='rsh')or(filePostrix=='rbf'):
            return 'fpga'
        elif filePostrix=='dat':
            return 'license'
        elif filePostrix=='startup-config':
            return 'startup-config'
        elif filePostrix=='HEX':
            return 'mcu'
        else:
            return None
    def downloadSvcfileSlotx(self,slot_num,file_type,file_name,ftpserver_ip,ftp_usr,ftp_pwd,reset_card=0):#download svcfile system-boot ftp #startup-config/system-boot/fpga/mcu/bootrom/cpld/license
        self.DevSendcmdUntil('show interface snmp','#')
        self.DevSendcmdUntil('show card','#')
        self.DevSendcmdUntil('download svcfile '+file_type+' ftp','Please input location of service board : ')
        self.DevSendcmdUntil('slot '+str(slot_num),'Please input server IP Address    :')
        self.DevSendcmdUntil(ftpserver_ip,'Please input FTP User name        :')
        self.DevSendcmdUntil(str(ftp_usr),'Please input FTP Password         :')
        self.DevSendcmdUntil(str(ftp_pwd),'Please input FTP Server File Name :')
        self.DevSendcmdUntil(str(file_name),'Are you sure[Y/N]:')
        self.DevSendcmdWaitSomeTimes('y')
        dl_result='unknown'
        print('initial_dl_result:'+dl_result)
        while True:
            time.sleep(1)
            download_info=self.DevSendcmdWaitSomeTimes('')
            for sg_line in download_info.split('\n'):
                if re.match('.*Copy file unsuccessfully!.*',sg_line):#Copy file unsuccessfully!/The upgrade is in processing!
                    dl_result='Failed'
                elif re.match('.*The upgrade is in processing!.*',sg_line):
                    dl_result='DeviceBusy'
                elif re.match('.*Copy file successfully!.*',sg_line):#Finished./Copy file successfully!
                    dl_result='Successful'
                    print(dl_result)
            print('downloading '+file_type+' to '+self.ip+'-slot '+str(slot_num)+',filename:'+file_name+'......')
            #print multiline_infoprocess(download_info)[len(multiline_infoprocess(download_info))-1].strip()==cmdHostName
            device_print_detail=self.multiline_infoprocess(download_info)
            '''print('device_print_detail_start')
            print(device_print_detail)
            print('device_print_detail_end')'''
            #if device_print_detail[len(device_print_detail)-1].strip()==cmdHostName:
            job_done_label=False
            for device_print_detail_i in device_print_detail:
                if re.match('.*Raisecom#.*',device_print_detail_i):
                    job_done_label=True
            if job_done_label:
                print('mz-info:'+self.ip+' download finished.download result '+dl_result)
                if dl_result=='Successful':
                    if str(reset_card)==1:
                        sg_line=self.DevSendcmdWaitSomeTimes('reset card '+str(slot_num))
                    elif str(reset_card)==3: 
                        sg_line=self.DevSendcmdWaitSomeTimes('reset all ')
                    else:
                        print('dl_result:%s' %(dl_result))
                else:
                    print('dl_result:%s' %(dl_result))
                break
        self.logWriter(self.download_result_str,str(slot_num)+'-'+str(file_name)+'-'+dl_result)
        return dl_result
    def downloadSvcfile_CardAndFileList(self,card_fileList_list,FtpIp=None,FtpUsrName='pydd',FtpPWD=123456):
    #example:card_fileList_list=['PG8_resetLabel:PG8.boorom;PG8.system.z,PX4_resetLabel:PX4.boorom;PX4.system.z']
        if not FtpIp:
            FtpIp=self.FtpIp
        print('FtpIp',FtpIp)
        for card_fileList_listi in card_fileList_list:
            try:
                cardi_info_str=card_fileList_listi.split(':')[0]
                fileList_info_list=card_fileList_listi.split(':')[1].split(';')
                card_name=cardi_info_str.split('_')[0]
                card_reset_label=cardi_info_str.split('_')[1]
            except Exception as e:
                print('input card_fileList_listi invalid:',card_fileList_listi,'--',str(e))
            slot_list=self.GetDeviceAllCardInfo(card_name).get('card_at')
            if len(slot_list)>0:#存在匹配的板卡
                print(slot_list)
                print(fileList_info_list)
                for slot_listi in slot_list:#逐个槽位下载
                    for fileList_listii in fileList_info_list:#逐个文件下载
                        if not fileList_listii:#为空则跳过
                            continue
                        file_type=self.FileTpyeGuess(fileList_listii)#startup-config/system-boot/fpga/mcu/bootrom/cpld/license
                        if not file_type:
                            print('FileTpyeGuess failed')
                            file_info_dict=self.FileTpyeGuess(fileList_listii,TailIsFiletype=1)
                            file_type=file_info_dict['FiletypeByGiven']
                            fileList_listii=file_info_dict['TrueFileName']
                        if (fileList_listii==fileList_info_list[-1]):#x槽位下载的最后一个文件,填入真实的重启标志
                            self.downloadSvcfileSlotx(slot_listi,file_type,fileList_listii,FtpIp,FtpUsrName,FtpPWD,card_reset_label)
                        else:#不是x槽位下载的最后一个文件,不填入真实的重启标志
                            self.downloadSvcfileSlotx(slot_listi,file_type,fileList_listii,FtpIp,FtpUsrName,FtpPWD)
            else:
                self.logWriter(self.download_result_str,self.ip+'-'+'does not have card-'+str(cardList_listi))
        return
    def upLoadConfig(self,FtpIp=None,FtpUsrName='pydd',FtpPWD=123456,file_name=''):
        if not FtpIp:
            FtpIp=self.FtpIp
        print('FtpIp',FtpIp)
        confFileName=time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'-'+self.ip+'-'+file_name+'.startup-config'
        self.DevSendcmdUntil('upload startup-config ftp','Please input server IP Address    :')
        self.DevSendcmdUntil(FtpIp,'Please input FTP User name        :')
        self.DevSendcmdUntil(str(FtpUsrName),'Please input FTP Password         :')
        self.DevSendcmdUntil(str(FtpPWD),'Please input FTP Server File Name :')#Please input FTP Server File Name :
        self.DevSendcmdUntil(confFileName,':')#
        self.DevSendcmdUntil('y','#')#


def downloadSvcfileMulti_forGUI_BD(DevList_clear,CardList_clear,FtpSet,ResetAll=0):
#DevList_clear=
#example:CardList_clear='PG8_resetLabel:PG8.boorom,PG8.system.z;PX4_resetLabel:PX4.boorom,PX4.system.z'
    if type(DevList_clear)==str:#兼容C#界面输入
        DevList_clear=DevList_clear.strip(',').split(',')
        CardList_clear=CardList_clear.strip(',').split(',')
        FtpSet=FtpSet.strip(',').split(',')
        for CardList_clear_listi in CardList_clear:
            if CardList_clear_listi.split('_')[1]=='3':
                ResetAll=1
    log_path=r'D:\py_ftp_download\deviceUpgradeLog\\'
    if not os.path.isdir(r'D:\py_ftp_download\\'):
        os.mkdir(r'D:\py_ftp_download\\')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    #init start
    #DevList_clear --['ip;mask;daiwai','ip;mask;dainei',...]
    #CardList_clear--['cardname_resetLabel:.boot;.sys;.fpga','cardname_resetLabel:.boot;.sys;.fpga',....]
    #FtpSet        --['inside server ip','3cd usrname','3cd password']
    print('Parent process %s.' % os.getpid())
    Failed_by_noServerip=''
    Failed_by_pingFailed=''
    print(CardList_clear)
    try:
        print(u'当前主机CPU核数：'+str(multiprocessing.cpu_count()))
        if int(multiprocessing.cpu_count())<4:
            print(u'主机CPU核数小于4，初始化进程池最大容量：4')
            p=multiprocessing.Pool(4)
        else:
            maxPro_num=int(multiprocessing.cpu_count())*2
            print(u'初始化进程池最大容量：%d' %(maxPro_num))
            p=multiprocessing.Pool(maxPro_num)
    except Exception as e:
        print(u'初始化进程池失败！升级取消！--',str(e))
        return
    print(u'开始分配升级任务')
    for Devi in DevList_clear:#多进程实例化设备，每个设备单独跑自己的计划任务
        Devi_info=Devi.split(';')
        Devi_ip=Devi_info[0]
        Devi_mask=Devi_info[1]
        Devi_ftp_set=int(Devi_info[2])
        if not IGT.deviceOnlineStateCheck(Devi_ip,PingPacksNum=5):
            print(Devi_ip,'ping failed,go next device')
            Failed_by_pingFailed=Failed_by_pingFailed+Devi_ip+'-'
            continue
        Devi_instance=DevClass_BD(Devi_ip,Devi_mask)
        try:
            if Devi_ftp_set:#使用指定ftp
                if len(FtpSet)!=3:
                    Failed_by_noServerip=Failed_by_noServerip+Devi_ip+'-'
                    print(Devi_ip,u'指定的ftp配置非法！跳过！')
                    continue
                p_pool=p.apply_async(Devi_instance.downloadSvcfile_CardAndFileList,args=(CardList_clear,FtpSet[0],FtpSet[1],FtpSet[2],))
            else:
                p_pool=p.apply_async(Devi_instance.downloadSvcfile_CardAndFileList,args=(CardList_clear,))
        except Exception as e:
            print(u'创建多进程任务出现异常--',str(e))
    p.close()
    p.join()
    f=open(log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+'download_fail_log'+'.txt','a+')#log file
    print(u'所有进程已结束,升级结果请见py_ftp_download\\upgrade_log文件夹下log')
    print(u'未能找到本地同网段ip导致未能升级的设备有：'+Failed_by_noServerip.strip('-'))#Failed_by_pingFailed
    print(u'未能ping通或存在丢包导致未能升级的设备有：'+Failed_by_pingFailed.strip('-'))
    print(u'检测到板卡状态为非工作态的有：')
    f.write('Failed_by_noServerip:'+Failed_by_noServerip.strip('-')+'-('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')\n')
    f.write('Failed_by_pingFailed:'+Failed_by_pingFailed.strip('-')+'-('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')\n')
    f.close()

def upLoadConfig_mutil(DevList_str):
    DevList_clear=DevList_str.strip(',').split(',')
    try:
        print(u'当前主机CPU核数：'+str(multiprocessing.cpu_count()))
        if int(multiprocessing.cpu_count())<4:
            print(u'主机CPU核数小于4，初始化进程池最大容量：4')
            p=multiprocessing.Pool(4)
        else:
            maxPro_num=int(multiprocessing.cpu_count())*2
            print(u'初始化进程池最大容量：%d' %(maxPro_num))
            p=multiprocessing.Pool(maxPro_num)
    except Exception as e:
        print(u'初始化进程池失败！升级取消！--',str(e))
        return
    print(u'开始分配上传任务')
    for Devi in DevList_clear:#多进程实例化设备，每个设备单独跑自己的计划任务
        if not IGT.deviceOnlineStateCheck(Devi,PingPacksNum=5):
            print(Devi,'ping failed,go next device')
            Failed_by_pingFailed=Failed_by_pingFailed+Devi+'-'
            continue
        Devi_instance=DevClass_BD(Devi)
        try:
            p_pool=p.apply_async(Devi_instance.upLoadConfig)
        except Exception as e:
            print(u'创建多进程任务出现异常--',str(e))
    p.close()
    p.join()
if __name__=='__main__':
    multiprocessing.freeze_support()
    #a=DevClass_BD('192.168.36.4')
    #a.downloadSvcfile_CardAndFileList('PG8;PX4','iTN8600-A-PG8_A.1_U7_MCU_1.6_20180907.HEX;iTN8600-A-PX4_A.1_U8_MCU_1.6_20180831.HEX','0;0')
    #b=DevClass_BD('192.167.36.3')
    #c=DevClass_BD('192.166.36.2')
    #a.upLoadConfig()
    #b.upLoadConfig()
    #c.upLoadConfig()
    #downloadSvcfileMulti_forGUI_BD('192.166.36.2;255.255.255.0;0,192.167.36.3;255.255.255.0;0,','nxu_0:iTN8600-A-NXU_A_BOOTROM_780_20180906__bootrom.bin.bootrom,','1;1;123')
    upLoadConfig_mutil('192.166.36.2,192.167.36.3,192.168.36.4')

else:
    multiprocessing.freeze_support()
