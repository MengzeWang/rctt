import telnetlib
import time
import re
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
    f=open(Hostname+'.txt','a+')
    tn=telnetlib.Telnet(Hostname,port=23,timeout=10)
    tn.set_debuglevel(0)
    #tn.read_all()
    tn.write('\r\n')
    tn.write(username+'\r\n')
    #time.sleep(5)
    a=tn.read_until('Login:')
    f.write(a+'\n')
    #a=tn.read_some()
    print_block(a,0)
    tn.write(password+'\r\n')
    a=tn.read_until('Password:')
    f.write(a+'\n')
    print_block(a,0)
    tn.write('ena\r\n')
    f.write(a+'\n')
    time.sleep(3)
    #a=tn.read_until('Raisecom>')
    print_block(a,0)
    tn.write(sudo_pssd+'\r\n')
    time.sleep(3)
    a=tn.read_very_eager()
    f.write(a+'\n')
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
    f.write(a+'\n')
    print_block(a,0)
    sh_ca_list=[]
    for show_card_result_row in a.split('\n'):
        print_block(show_card_result_row,0)
        if len(show_card_result_row.split())>2:
            sh_ca_list.append(show_card_result_row.split())
    #print sh_ca_list
    slot_col=sh_ca_list[0].index('Slot')
    stat_col=sh_ca_list[0].index('State')
    card_col=stat_col-1
    sh_ca_list_core=[]
    for card_info in sh_ca_list:
        if card_info[0]!='*':
            sh_ca_list_core.append([card_info[slot_col],card_info[card_col],card_info[stat_col]])
        else: 
            #print 'Master_Card:'
            sh_ca_list_core.append([card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]])	
    print sh_ca_list_core
    ver_result=[]
    if card_state=='all':
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            ver_result.append(multiline_infoprocess(get_cmdresult('show ver slot '+str(slot_verx[0]),cmdHostName)))
        print ver_result
    elif card_state=='working':
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            if slot_verx[2]=='working':
                ver_result.append(multiline_infoprocess(get_cmdresult('show ver slot '+str(slot_verx[0]),cmdHostName)))
            print ver_result
    else:
        for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
            if slot_verx[2]!='working':
                ver_result.append(multiline_infoprocess(get_cmdresult('show ver slot '+str(slot_verx[0]),cmdHostName)))
            print ver_result
    for ver_ri in ver_result:
        for ver_ri2 in ver_ri:
            f.write(ver_ri2+'\s')
        f.write('\n')
    f.close()
    return [cmdHostName,ver_result]
def download_svcfile(HostName,cmdHostName,slot_num,file_type,file_name,ftpserver_ip,ftp_usr,ftp_pwd,reset_card):#download svcfile system-boot ftp #startup-config/system-boot/fpga/mcu/bootrom/cpld/license
    tn.write('show interface snmp\r\n')
    time.sleep(2)
    print(tn.read_very_eager)
    tn.write('download svcfile '+file_type+' ftp\r\n')
    print tn.read_until('Please input location of service board : ',10)
    tn.write('slot '+str(slot_num)+'\r\n')
    print tn.read_until('Please input server IP Address    :',10)
    tn.write(ftpserver_ip+'\r\n')
    print tn.read_until('Please input FTP User name        :',10)
    tn.write(ftp_usr+'\r\n')
    print tn.read_until('Please input FTP Password         :',10)
    tn.write(str(ftp_pwd)+'\r\n')
    print tn.read_until('Please input FTP Server File Name :',10)
    tn.write(file_name+'\r\n')
    print tn.read_until('Are you sure[Y/N]:',10)
    tn.write('y\r\n')
    #time.sleep(5)
    #print tn.read_very_eager()
    dl_result='unknown'
    while True:
        time.sleep(5)
        #tn.write('\r\n')
        download_info=tn.read_very_eager()
        if not download_info:#no respond send enter
            tn.write('\r\n')
        print download_info
        for sg_line in download_info.split('\n'):
            if re.match('.*Copy file unsuccessfully!.*',sg_line):#Copy file unsuccessfully!/The upgrade is in processing!
                dl_result='failed'
            elif re.match('.*Copy file successfully!.*',sg_line):#Finished./Copy file successfully!
                dl_result='successful'
                print dl_result
        print 'downloading '+file_type+' to '+HostName+'-slot '+str(slot_num)+',filename:'+file_name+'......'
        #print multiline_infoprocess(download_info)[len(multiline_infoprocess(download_info))-1].strip()==cmdHostName
        if multiline_infoprocess(download_info)[len(multiline_infoprocess(download_info))-1].strip()==cmdHostName:
            print 'mz-info:download finished.download result '+dl_result
            if (dl_result=='successful')and(reset_card==1):
                tn.write('reset card '+str(slot_num)+'\r\n')
                time.sleep(2)
                print(tn.read_very_eager())
            break
    return dl_result
def GetCardSlotBase_GetDeviceAllCardInfo(CardName,GDAC_retrun):
    card_at=[]
    print GDAC_retrun[0]
    for x in GDAC_retrun[1]:
        print x
        if re.match('.*'+CardName,x[1],re.I):
            print 'match result:'+x[1]
            print x[1].split(' ')[1]
            card_at.append(x[1].split(' ')[1])#append slot number
    print card_at
    return card_at
def FileTpyeGuess(FileName):
    filePostrix=FileName.split('.')[len(FileName.split('.'))-1]
    print filePostrix
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
    else:
        return None

def download_svcfile_multi(Hostname_list,card_name,file_name_list,ftpserver_ip,ftp_usr,ftp_pwd,reset_card):#
    #init start
    
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    card_state='working'#'all/working/'
    Hostname_list=Hostname_list.split(';')
    file_name_list=file_name_list.split(';')
    for host_i in Hostname_list:#this 'for' can be modify to multiprocess
        GAC0=GetDeviceAllCardInfo(host_i,username,password,sudo_pssd,card_state)
        cmdHostName=GAC0[0]
        Card_slot=GetCardSlotBase_GetDeviceAllCardInfo(card_name,GAC0)
        for file_i in file_name_list:
            reset_card_now=0
            if (file_i==file_name_list[len(file_name_list)-1])and(reset_card==1):#the last file
                reset_card_now=1
            file_type=FileTpyeGuess(file_i)#startup-config/system-boot/fpga/mcu/bootrom/cpld/license
            if not file_type:
                print 'FileTpyeGuess failed'
                file_type='nan'
            #init end
            for sloti in Card_slot:#download svcfile to all same type card in one NE
                download_svcfile(host_i,cmdHostName,sloti,file_type,file_i,ftpserver_ip,ftp_usr,ftp_pwd,reset_card_now)			

Hostname_list1='192.168.67.10'
file_name_list1='iTN8600-SH2E_B.0_U27_FPGA_1.7_20180227.rbf;iTN8600-SH2E_B_BOOTROM_763bootrom.bin'
card_name1='sh2e'
ftpserver_ip1='192.168.67.52'

Hostname_list2='190.26.90.254;190.26.100.254'
file_name_list2='RA1428XV15_20171207.bin.rsh;itn8600-7616pg10.z'
card_name2='pg10'
ftpserver_ip2='10.0.1.52'

ftp_usr='pydd'
ftp_pwd='123456'
#download_svcfile_multi(Hostname_list1,card_name1,file_name_list1,ftpserver_ip1,ftp_usr,ftp_pwd)
#download_svcfile_multi(Hostname_list2,card_name2,file_name_list2,ftpserver_ip2,ftp_usr,ftp_pwd)
download_svcfile_multi(Hostname_list2,card_name2,file_name_list2,ftpserver_ip2,ftp_usr,ftp_pwd,1)