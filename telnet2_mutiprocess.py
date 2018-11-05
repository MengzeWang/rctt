#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import telnetlib
import time,re,os
import multiprocessing
from multiprocessing import Pool
import ip_get_test as IGT
def print_block(a,*print_level):
    if (print_level)and(print_level[0]==0):
        return
    print '==============================='
    print 'type(a):'
    print type(a)
    print '\n'
    print 'a:'
    print a
    print '==============================='
def get_cmdresult(cmd,*end_until):
    tn.write(cmd+'\r\n')
    if end_until:
        return tn.read_until(end_until[0],10)
    else:
        time.sleep(5)
        return tn.read_very_eager()
def multiline_infoprocess(str_info):
    str_info_list=[]
    for str_info_row in str_info.split('\n'):
        str_info_list.append(str_info_row)
    return str_info_list
def GetDeviceAllCardInfo(Hostname,username,password,sudo_pssd,card_state):#card_state can be follows:all/working/non-working
    global tn
    #f=open(Hostname+'.txt','a+')
    tn=telnetlib.Telnet(Hostname,port=23,timeout=10)
    tn.set_debuglevel(0)
    #tn.read_all()
    tn.write('\r\n')
    tn.write(username+'\r\n')
    #time.sleep(5)
    a=tn.read_until('Login:')
    #a=tn.read_some()
    print_block(a,0)
    tn.write(password+'\r\n')
    a=tn.read_until('Password:')
    print_block(a,0)
    tn.write('ter time 0\r\n')
    time.sleep(3)
    tn.write('ena\r\n')
    time.sleep(3)
    #a=tn.read_until('Raisecom>')
    print_block(a,0)
    tn.write(sudo_pssd+'\r\n')
    time.sleep(3)
    a=tn.read_very_eager()
    #a=tn.read_until('Raisecom#')
    #print_block(a,0)
    #cmdHostName=''
    for recv_name in a.split():
        if re.match('.*#',recv_name):
            print '######host name#######'
            print recv_name
            cmdHostName=recv_name
            print '######host name#######'
            break
    tn.write('show card'+'\r\n')
    a=tn.read_until(cmdHostName)
    print_block(a,0)
    sh_ca_list=[]
    arrow_name_index=0
    arrow_index=0
    show_cols=0
    for show_card_result_row in a.split('\n'):
        print_block(show_card_result_row,0)
        if len(show_card_result_row.split())>6:
            sh_ca_list.append(show_card_result_row.split())
            if ('Slot' in show_card_result_row)and('State' in show_card_result_row)and('PowerType' in show_card_result_row):
                print('find arrow name:',show_card_result_row,'current index is:',arrow_index)
                show_cols=len(show_card_result_row.split())
                arrow_name_index=arrow_index
            arrow_index=arrow_index+1
    #print sh_ca_list
    slot_col=sh_ca_list[arrow_name_index].index('Slot')
    stat_col=sh_ca_list[arrow_name_index].index('State')
    PowerType_col=sh_ca_list[0].index('PowerType')
    card_col=stat_col-1
    sh_ca_list_core=[]
    for card_info in sh_ca_list:
        if card_info[0]!='*':
            if len(card_info)!=show_cols:#目前show card结果有7列，后续如果show card结果列数变化，可修改此处，但这里仅是个列数异常提示，不影响使用
                print('find a unexpected length line:',card_info,'consider this line is not show card valid info,drop it')
            else:
                sh_ca_list_core.append([card_info[slot_col],card_info[card_col],card_info[stat_col],card_info[PowerType_col]])
        else: 
            #print 'Master_Card:'
            sh_ca_list_core.append([card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1],card_info[PowerType_col+1]])
    #print sh_ca_list_core
    for sh_ca_list_corei in sh_ca_list_core:#sh_ca_list_core=[[card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]],[card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]]]
        print sh_ca_list_corei
    ver_result=[]
    if card_state=='all':
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            ver_result.append(multiline_infoprocess(get_cmdresult('show ver slot '+str(slot_verx[0]),cmdHostName)))
        #print ver_result
    elif card_state=='working':
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            if slot_verx[2]=='working':
                ver_result.append(multiline_infoprocess(get_cmdresult('show ver slot '+str(slot_verx[0]),cmdHostName)))
        #    print ver_result
    else:
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            if slot_verx[2]!='working':
                ver_result.append(Hostname+'--'+str(slot_verx[0])+'-'+str(slot_verx[1])+'-'+slot_verx[2])#['192.168.xx.xx',6,'iTN8600-sg8','offline']
        #    print ver_result
    return [cmdHostName,ver_result,sh_ca_list_core[1:len(sh_ca_list_core)]]#sh_ca_list_core:[card_info[slot_col],card_info[card_col],card_info[stat_col],card_info[PowerType_col]]
def download_svcfile(HostName,cmdHostName,slot_num,file_type,file_name,ftpserver_ip,ftp_usr,ftp_pwd,reset_card):#download svcfile system-boot ftp #startup-config/system-boot/fpga/mcu/bootrom/cpld/license
    #print HostName
    log_path=r'D:\py_ftp_download\upgrade_log\\'
    if not os.path.isdir(r'D:\py_ftp_download\\'):
        os.mkdir(r'D:\py_ftp_download\\')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    print(log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+HostName+'-detail-log.txt')
    f=open(log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+HostName+'-detail-log.txt','a+')
    print 'start-write'
    tn.write('show interface snmp\r\n')
    time.sleep(2)
    re_echo=tn.read_very_eager()
    print(re_echo)
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write('show card\r\n')
    time.sleep(2)
    re_echo=tn.read_very_eager()
    print(re_echo)
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write('download svcfile '+file_type+' ftp\r\n')
    re_echo=tn.read_until('Please input location of service board : ',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write('slot '+str(slot_num)+'\r\n')
    re_echo=tn.read_until('Please input server IP Address    :',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write(ftpserver_ip+'\r\n')
    re_echo=tn.read_until('Please input FTP User name        :',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write(ftp_usr+'\r\n')
    re_echo=tn.read_until('Please input FTP Password         :',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write(str(ftp_pwd)+'\r\n')
    re_echo=tn.read_until('Please input FTP Server File Name :',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write(file_name+'\r\n')
    re_echo=tn.read_until('Are you sure[Y/N]:',10)
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    tn.write('y\r\n')
    time.sleep(2)
    re_echo=tn.read_very_eager()
    print re_echo
    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+re_echo+'\n')
    #time.sleep(5)
    #print tn.read_very_eager()
    dl_result='unknown'
    print('initial_dl_result:'+dl_result)
    while True:
        time.sleep(5)
        #tn.write('\r\n')
        download_info=tn.read_very_eager()
        #if not download_info:#no respond send enter
        tn.write('\r\n')
        #print download_info
        for sg_line in download_info.split('\n'):
            print sg_line
            f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+sg_line+'\n')
            if re.match('.*Copy file unsuccessfully!.*',sg_line):#Copy file unsuccessfully!/The upgrade is in processing!
                dl_result='Failed'
            elif re.match('.*The upgrade is in processing!.*',sg_line):
                dl_result='DeviceBusy'
            elif re.match('.*Copy file successfully!.*',sg_line):#Finished./Copy file successfully!
                dl_result='Successful'
                print dl_result
        print 'downloading '+file_type+' to '+HostName+'-slot '+str(slot_num)+',filename:'+file_name+'......'
        #print multiline_infoprocess(download_info)[len(multiline_infoprocess(download_info))-1].strip()==cmdHostName
        device_print_detail=multiline_infoprocess(download_info)
        '''print('device_print_detail_start')
        print(device_print_detail)
        print('device_print_detail_end')'''
        #if device_print_detail[len(device_print_detail)-1].strip()==cmdHostName:
        job_done_label=False
        for device_print_detail_i in device_print_detail:
            if re.match('.*'+cmdHostName+'.*',device_print_detail_i):
                job_done_label=True
        if job_done_label:
            print 'mz-info:'+HostName+' download finished.download result '+dl_result
            if dl_result=='Successful':
                if reset_card==1:
                    tn.write('reset card '+str(slot_num)+'\r\n')
                    time.sleep(2)
                    sg_line=tn.read_very_eager()
                    print(sg_line)
                    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+sg_line+'\n')
                elif reset_card==3: 
                    tn.write('reset all \r\n')
                    time.sleep(1)
                    sg_line=tn.read_very_eager()
                    print(sg_line)
                    f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+sg_line+'\n')
                else:
                    print('dl_result:%s' %(dl_result))
                    print(tn.read_very_eager())
            else:
                print('dl_result:%s' %(dl_result))
                print(tn.read_very_eager())
            break
    f.close()
    return dl_result
def GetCardSlotBase_GetDeviceAllCardInfo(CardName,GDAC_retrun):
    card_at=[]
    CardName=str(CardName)
    print GDAC_retrun[0]
    #for x in GDAC_retrun[1]:
        #print x
     #   if re.match('.*'+CardName,x[1],re.I):
      #      print 'match result:'+x[1]
       #     print x[1].split(' ')[1]
        #    card_at.append(x[1].split(' ')[1])#append slot number
    for y in GDAC_retrun[2]:
        if (y[2]=='working')and(re.match('.*'+CardName+'$',y[1],re.I)):#card name 
            print 'match result:'+y[1]
            card_at.append(y[0])#append slot number
        elif (y[2]=='working')and(re.match('.*'+CardName,y[3],re.I)):#or PowerType
            print 'match result:'+y[3]
            card_at.append(y[0])#append slot number
    print card_at
    return card_at
def FileTpyeGuess(FileName,TailIsFiletype=0):
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
def download_svcfile_multi_part2(host_i2,username2,password2,sudo_pssd2,card_state2,card_name2,file_name_list2,reset_card2,ftpserver_ip2,ftp_usr2,ftp_pwd2):#have log
    reset_card2=int(reset_card2)
    log_path=r'D:\py_ftp_download\upgrade_log\\'
    if not os.path.isdir(r'D:\py_ftp_download\\'):
        os.mkdir(r'D:\py_ftp_download\\')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    print('Run child process %s %s (%s)...\n' % (host_i2, card_name2,os.getpid()))
    GAC0=GetDeviceAllCardInfo(host_i2,username2,password2,sudo_pssd2,card_state2)
    cmdHostName=GAC0[0]
    Card_slot=GetCardSlotBase_GetDeviceAllCardInfo(card_name2,GAC0)
    print(host_i2+' match card '+card_name2+' at:')
    print Card_slot
    download_result_logger=[]
    f=open(log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+host_i2+'.txt','a+')#log file 
    for file_i in file_name_list2:
        if not file_i:
            print('find empty filename!skip download.')
            continue
        reset_card_now=0
        if (file_i==file_name_list2[len(file_name_list2)-1])and(reset_card2==1):#the last file
            reset_card_now=1
        elif (file_i==file_name_list2[len(file_name_list2)-1])and(reset_card2==3):#the last file
            reset_card_now=3
        file_type=FileTpyeGuess(file_i)#startup-config/system-boot/fpga/mcu/bootrom/cpld/license
        if not file_type:
            print 'FileTpyeGuess failed'
            file_info_dict=FileTpyeGuess(file_i,TailIsFiletype=1)
            file_type=file_info_dict['FiletypeByGiven']
            file_i=file_info_dict['TrueFileName']
        #init end
        for sloti in Card_slot:#download svcfile to all same type card in one NE
            if reset_card_now==3:
                if (sloti==Card_slot[len(Card_slot)-1])and(reset_card_now==3):
                    reset_card_now2=3
                    print(u'准备升级最后一个槽位，下载完成后整机重启')
                else:
                    reset_card_now2=0
            else:
                reset_card_now2=reset_card_now
            print('process '+host_i2+' slot '+str(sloti)+',reset card state is:%s' %(reset_card_now2))
            dsrst=download_svcfile(host_i2,cmdHostName,sloti,file_type,file_i,ftpserver_ip2,ftp_usr2,ftp_pwd2,reset_card_now2)
            print(host_i2+'-slot-'+str(sloti)+'-done')
            download_result_logger.append([host_i2,sloti,file_i,dsrst])
            f.write(host_i2+'-'+str(sloti)+'-'+file_i+'-'+dsrst+'-('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')\n')
    f.close()
    print download_result_logger
    return download_result_logger
def download_svcfile_multi(Hostname_list,card_name,file_name_list,ftpserver_ip_dict,ftp_usr,ftp_pwd,reset_card,multiprocessing_on):#
    #init start
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    card_state='working'#'all/working/'
    Hostname_list=Hostname_list.split(';')
    file_name_list=file_name_list.split(';')
    #paramater check
    '''if type(ftpserver_ip_dict)!='<type '+'dict'+'>':
        print('ftpserver_ip_dict is %s,not a dict,quit' %(type(ftpserver_ip_dict)))
        return
    elif len(Hostname_list[0].split('_'))!=2:
        print('wrong format of Hostname_list,should be like:190.26.87.254_1,_1 mean ftpserver_ip_dict index')
        return
    else:
        pass'''
    if multiprocessing_on==1:
        print('Parent process %s.' % os.getpid())
        p=Pool(4)
        for host_ii_mix in Hostname_list:
            host_ii=host_ii_mix.split('_')[0]
            ftp_index=int(host_ii_mix.split('_')[1])
            ftpserver_ip=ftpserver_ip_dict[ftp_index]
            p_pool=p.apply_async(download_svcfile_multi_part2,args=(host_ii,username,password,sudo_pssd,card_state,card_name,file_name_list,reset_card,ftpserver_ip,ftp_usr,ftp_pwd,))
            #print ('p_pool.get'+host_ii+':%s' %(p_pool.get()))#use this make multi like a for
        print('Waiting for all device done...')
        p.close()
        p.join()
        print('All device download done.')
        return None 
def download_svcfile_multi2(DevIp,CardName,FileList_str,DevIpMask='255.255.255.0',FtpIp=None,FtpUsrName='pydd',FtpPWD=123456,ResetCard=0):
    #init start
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    card_state='working'#'all/working/'
    Hostname_list=DevIp.split(';')

    print('Parent process %s.' % os.getpid())
    p=Pool(4)
    for host_ii_mix in Hostname_list:
        if FtpIp:
            ftpserver_ip=FtpIp
        else:
            ftpserver_ip=getSameSegmentIpOnComputerNetCard(DevIp,DevIpMask)
        p_pool=p.apply_async(download_svcfile_multi_part2,args=(host_ii_mix,username,password,sudo_pssd,card_state,CardName,FileList_str,ResetCard,ftpserver_ip,FtpUsrName,FtpPWD,))
        time.sleep(1)
        #print ('p_pool.get'+host_ii+':%s' %(p_pool.get()))#use this make multi like a for
    print('Waiting for all device done...')
    p.close()
    p.join()
    print('All device download done.')
    return None
def downloadSvcfileMulti_forGUI(DevList_clear,CardList_clear,FtpSet,ResetAll):
    log_path=r'D:\py_ftp_download\upgrade_log\\'
    if not os.path.isdir(r'D:\py_ftp_download\\'):
        os.mkdir(r'D:\py_ftp_download\\')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    #init start
    #DevList_clear --['ip;mask;daiwai','ip;mask;dainei',...]
    #CardList_clear--['cardname_resetLabel:.boot;.sys;.fpga','cardname:.boot;.sys;.fpga',....]
    #FtpSet        --['inside server ip','3cd usrname','3cd password']
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    card_state='working'#'all/working/'
    print('Parent process %s.' % os.getpid())
    Failed_by_noServerip=''
    Failed_by_pingFailed=''
    nWorkingCard=[]
    print CardList_clear
    for Cardx in CardList_clear:#bian li ban ka['ss8_1:xx.bin;xx.sys;..','sg8_0:xx.bin;xx.fpga'...]
        Card_list_arr=Cardx.split(':')#['cardname','xx.bootrom;xx.system-boot;xx.fpga']
        print(u'当前主机CPU核数：'+str(multiprocessing.cpu_count()))
        try:
            if int(multiprocessing.cpu_count())<4:
                print(u'主机CPU核数小于4，初始化进程池最大容量：4')
                p=Pool(4)
            else:
                maxPro_num=int(multiprocessing.cpu_count())*2
                print(u'初始化进程池最大容量：%d' %(maxPro_num))
                p=Pool(maxPro_num)
        except Exception as e:
            print(u'初始化进程池失败！升级取消！')
            print(e)
        print(u'开始分配升级任务')
        for Devi in DevList_clear:#bian li she bei
            Dev_list_arr=Devi.split(';')#['devip','mask','1 or 0(dainei or daiwai)']
            if not IGT.deviceOnlineStateCheck(Dev_list_arr[0],PingPacksNum=5):
                print(Dev_list_arr[0],'ping failed,go next device')
                Failed_by_pingFailed=Failed_by_pingFailed+Devi+'-'
                continue
            if (Devi==DevList_clear[0])and(Cardx==CardList_clear[0]):#first round get all the non-working card info
                nWorkingCardinfo=GetDeviceAllCardInfo(Dev_list_arr[0],username,password,sudo_pssd,'non-working')#['no working card1','no working card2']
                if len(nWorkingCardinfo)>0:
                    nWorkingCard.append(nWorkingCardinfo)
            if Dev_list_arr[2]=='1':#dainei-zhiding ftp ip
                ftpserver_ip=FtpSet[0]
            else:#daiwai
                #ftpserver_ip=IGT.getSameSegmentIpOnComputerNetCard(Dev_list_arr[0],Dev_list_arr[1])#2018-05-30 abort
                ftpserver_ip=IGT.getPingSuccesIpOnComputerNetCard(Dev_list_arr[0],Dev_list_arr[1])
            if not ftpserver_ip:#do not find same segment ip address on local net card or inside server ip is blank
                Failed_by_noServerip=Failed_by_noServerip+Devi+'-'
            else:
                if ResetAll==1:
                    if Cardx==CardList_clear[len(CardList_clear)-1]:#the last card 
                        print(u'准备升级最后一种类型板卡，整机重启标志位置1')
                        print(u'增加子任务：'+Dev_list_arr[0]+'-'+Card_list_arr[0].split('_')[0])
                        try:
                            p_pool=p.apply_async(download_svcfile_multi_part2,args=(Dev_list_arr[0],username,password,sudo_pssd,card_state,Card_list_arr[0].split('_')[0],Card_list_arr[1].split(';'),3,ftpserver_ip,FtpSet[1],FtpSet[2],))
                        except Exception as e:
                            print(e)
                    else:
                        print(u'增加子任务：'+Dev_list_arr[0]+'-'+Card_list_arr[0].split('_')[0])
                        try:
                            p_pool=p.apply_async(download_svcfile_multi_part2,args=(Dev_list_arr[0],username,password,sudo_pssd,card_state,Card_list_arr[0].split('_')[0],Card_list_arr[1].split(';'),0,ftpserver_ip,FtpSet[1],FtpSet[2],))
                        except Exception as e:
                            print(e)
                else:#
                    print(u'增加子任务：'+Dev_list_arr[0]+'-'+Card_list_arr[0].split('_')[0])
                    try:
                        p_pool=p.apply_async(download_svcfile_multi_part2,args=(Dev_list_arr[0],username,password,sudo_pssd,card_state,Card_list_arr[0].split('_')[0],Card_list_arr[1].split(';'),Card_list_arr[0].split('_')[1],ftpserver_ip,FtpSet[1],FtpSet[2],))
                    except Exception as e:
                        print(e)
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
    for nWorkingCard_i in nWorkingCard:
        for nWorkingCard_ii in nWorkingCard_i[1]:
            print nWorkingCard_ii

    return 'ok.logFileIn---D:\py_ftp_download\upgrade_log'


def upLoadConfig(DevIP,DevMask,FtpIp=None,FtpUsrName='pydd',FtpPWD=123456,file_name=''):
    confFileName=file_name+'-'+DevIP+'-'+'.startup-config'#time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    if not FtpIp:
        FtpIp=IGT.getPingSuccesIpOnComputerNetCard(DevIP,DevMask)
    print('FtpIp',FtpIp)
    tn=telnetlib.Telnet(DevIP,port=23,timeout=10)
    tn.set_debuglevel(0)
    tn.write('\r\n')
    re_echo=tn.read_until('Login:')
    print(re_echo)
    tn.write('raisecom\r\n')
    re_echo=tn.read_until('Password:')
    print(re_echo)
    tn.write('raisecom\r\n')
    re_echo=tn.read_until('>')
    print(re_echo)
    tn.write('ter time 0\r\n')
    re_echo=tn.read_until('>')
    print(re_echo)
    tn.write('ena\r\n')
    re_echo=tn.read_until('Password:')
    print(re_echo)
    tn.write('raisecom\r\n')
    re_echo=tn.read_until('#')
    print(re_echo)
    tn.write('upload startup-config ftp\r\n')
    re_echo=tn.read_until('Please input server IP Address    :',10)
    print(re_echo)
    tn.write(str(FtpIp)+'\r\n')
    re_echo=tn.read_until('Please input FTP User name        :',10)
    print(re_echo)
    tn.write(str(FtpUsrName)+'\r\n')
    re_echo=tn.read_until('Please input FTP Password         :',10)
    print(re_echo)
    tn.write(str(FtpPWD)+'\r\n')
    re_echo=tn.read_until('Please input FTP Server File Name :',10)
    print(re_echo)
    tn.write(confFileName+'\r\n')
    re_echo=tn.read_until(':',10)
    print(re_echo)
    tn.write('y\r\n')
    re_echo=tn.read_until('#',10)
    print(re_echo)
    tn.close()

def upLoadConfigMutil_forGUI(DevList_clear):
    #DevList_clear --['ip;mask;daiwai','ip;mask;dainei',...]
    #DevList_clear=DevList_str.strip(',').split(',')
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
        print(u'初始化进程池失败！取消所有配置文件上传！--',str(e))
        return
    print(u'开始分配上传任务')
    timeMark=time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    for Devi in DevList_clear:#多进程实例化设备，每个设备单独跑自己的计划任务
        Devi_ip=Devi.split(';')[0]
        Devi_mask=Devi.split(';')[1]
        if not IGT.deviceOnlineStateCheck(Devi_ip,PingPacksNum=5):
            print(Devi_ip,'ping failed,go next device')
            continue
        try:
            p_pool=p.apply_async(upLoadConfig,args=(Devi_ip,Devi_mask,None,'pydd',123456,timeMark,))
        except Exception as e:
            print(u'创建多进程任务出现异常--',str(e))
    p.close()
    p.join()
    print('all subTask closed')
    return 'all subTask closed'

if __name__=='__main__':
    multiprocessing.freeze_support()
    Hostname_list='192.168.34.2_2;192.168.34.3_2'#device-IP_ftpserver_ip_dict-index;
    ftpserver_ip_dict={1:'10.0.2.52',2:'192.168.34.52',3:'192.168.23.81',4:'88.88.88.52'}
    ftp_usr='pydd'
    ftp_pwd='123456'
    reset_card=0
    multiprocessing_on=1

    sh2_version='iTN8600-A-SH2_A_SYSTEM_771_20180322__iTN8600-A_SH2.z;iTN8600-A-SH2_A_BOOTROM_770_20180321__bootrom.bin;iTN8600-A-SH2_A.0_U27_FPGA_1.0_20180321.rbf'
    ntu_version='iTN8600-V-NTU_A4_U155_FPGA_2.1_20180313.rbf.rsh;iTN8600-V-NTU_BOOTROM_761_20170918__bootrom.bin'#iTN8600-V-NTU_SYSTEM_770_20180320__itn8600-V-ntu.z;
    ss8_version='iTN8600-SS8_A_SYSTEM_771_20180322__iTN8600-V_SS8.z;iTN8600-SS8_A.0_U29_FPGA_1.7_20180227.rbf;iTN8600-SS8_A_BOOTROM_763_20180224__bootrom.bin'
    sg8_version='iTN8600-SG8_A_SYSTEM_770_20180329__iTN8600-SG8.z;iTN8600-SG8_A.0_U19_FPGA_1.0_20170807.bin.fpga;iTN8600-SG8_BOOTROM_765_20171012__bootrom.bin'

    #download_svcfile_multi(Hostname_list,'ss8',ss8_version,ftpserver_ip_dict,ftp_usr,ftp_pwd,reset_card,multiprocessing_on)
    download_svcfile_multi(Hostname_list,'sg8',sg8_version,ftpserver_ip_dict,ftp_usr,ftp_pwd,reset_card,multiprocessing_on)
    #download_svcfile_multi(Hostname_list,'sh2',sh2_version,ftpserver_ip_dict,ftp_usr,ftp_pwd,reset_card,multiprocessing_on)
    #download_svcfile_multi(Hostname_list,'ntu',ntu_version,ftpserver_ip_dict,ftp_usr,ftp_pwd,reset_card,multiprocessing_on)
else:
    multiprocessing.freeze_support()
