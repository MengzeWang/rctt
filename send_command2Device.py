#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import telnetlib
import time
import re
from multiprocessing import Pool
import os
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
def Connect2Device(DeviceIp):
    global tn
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    #f=open(Hostname+'.txt','a+')
    tn=telnetlib.Telnet(DeviceIp,port=23,timeout=10)
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
    return [tn,cmdHostName]

def send_command2Device(Hostname,username,password,sudo_pssd,cmd_str):#
    global tn
    #f=open(Hostname+'.txt','a+')
    tn=telnetlib.Telnet(Hostname,port=20006,timeout=10)
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
	#mpls bidirectional static-lsp ingress 5 lsr-id 190.26.100.35 tunnel-id 5
	#forward 190.26.100.35 255.255.255.255 nexthop-mac 000E.5E10.1112 vlan 5 line 1 out-label 16
	#backward in-label 16
	#interface tunnel 1
    #destination 190.26.100.35
    #mpls tunnel-id 5
    a=tn.read_until(cmdHostName)

	
if __name__=='__main__':
    Hostname_list2='190.26.87.254;190.26.87.130;190.26.100.254'
    file_name_list2='iTN8600-7617SG8.z'
    card_name2='sg8'
    ftpserver_ip2='10.0.1.52'
    ftp_usr='pydd'
    ftp_pwd='123456'
#download_svcfile_multi(Hostname_list1,card_name1,file_name_list1,ftpserver_ip1,ftp_usr,ftp_pwd)
#download_svcfile_multi(Hostname_list2,card_name2,file_name_list2,ftpserver_ip2,ftp_usr,ftp_pwd)
    download_svcfile_multi(Hostname_list2,card_name2,file_name_list2,ftpserver_ip2,ftp_usr,ftp_pwd,1,1)