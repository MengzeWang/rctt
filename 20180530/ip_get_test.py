#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import os
import re
'''
p=os.popen('ipconfig').read()
p2=p.split(':')
a=[]
for p2_i in p2:
    ftp_ip=re.match('.*'+r'192.168.34'+'.*',p2_i)
    if ftp_ip:
        print ftp_ip.group(0)
        a.append(ftp_ip.group(0).strip())
print a'''

def deviceOnlineStateCheck(devIp):
    PingPacksNum=10
    dev_pingInfo=os.popen('ping '+devIp+' -n '+str(PingPacksNum)).read()
    dev_pingInfo_arr=dev_pingInfo.split('\n')
    successPingCount=0
    for dev_pingInfo_arri in dev_pingInfo_arr:
        print dev_pingInfo_arri
        if 'TTL' in dev_pingInfo_arri:
            successPingCount=successPingCount+1

    if successPingCount==PingPacksNum:
        return True
    else:
        print(u'存在丢包，丢包率百分之：%d' %(100*(1-successPingCount/PingPacksNum)))
        return False

def ip_net_computer(ip_ip,ip_mask):#return valid ip range:[first_valid_ip,last_valid_ip,ip_aftermask_segment,ip_aftermask_brodcast]
    ip_arr=ip_ip.split(r'.')
    mask_arr=ip_mask.split(r'.')
    i=0
    ip_aftermask_arr=[]
    valid_ip_max_arr=[]
    ip_aftermask_first=''
    ip_aftermask_last=''
    ip_aftermask_segment=''
    ip_aftermask_brodcast=''
    avalibe_num=0
    for ip_arri in ip_arr:
        ip_arri_bin=bin(int(ip_arri))
        mask_arri_bin=bin(int(mask_arr[i]))
        bin_ip=str(ip_arri_bin)[2:len(str(ip_arri_bin))]
        bin_mask=str(mask_arri_bin)[2:len(str(mask_arri_bin))]
        if len(bin_ip)<8:
            for high_position_miss_ip in range(8-int(len(bin_ip))):
                bin_ip='0'+bin_ip
        if len(bin_mask)<8:
            for high_position_miss_mask in range(8-int(len(bin_mask))):
                bin_mask='0'+bin_mask
        #print 'bin_ip:'+bin_ip
        #print 'bin_mask:'+bin_mask
        valid_ip=''
        valid_ip_max=''
        for bin_ip_i in range(len(bin_ip)):
            valid_ip=valid_ip+str(int(bin_ip[bin_ip_i])&int(bin_mask[bin_ip_i]))
            if bin_mask[bin_ip_i]=='0':
                avalibe_num=avalibe_num+1
                valid_ip_max=valid_ip_max+'1'
            else:
                valid_ip_max=valid_ip_max+bin_ip[bin_ip_i]
        #print 'valid_ip:'+valid_ip
        #print int(str(valid_ip),2)
        #print int(str(valid_ip_max),2)
        ip_aftermask_arr.append(str(int(str(valid_ip),2)))
        valid_ip_max_arr.append(str(int(str(valid_ip_max),2)))
        i=i+1
    #print ip_aftermask_arr
    #print valid_ip_max_arr
    avalibe_num_oc=1
    for j in range(avalibe_num):
        avalibe_num_oc=avalibe_num_oc*2
    #print 'avalibe_num_oc:'+str(avalibe_num_oc-2)#print total avaliable ip number 
    index_i=0
    for ip_aftermask_arri in ip_aftermask_arr:
        ip_aftermask_segment=ip_aftermask_segment+ip_aftermask_arri+r'.'
        ip_aftermask_brodcast=ip_aftermask_brodcast+valid_ip_max_arr[index_i]+r'.'
        if ip_aftermask_arri==ip_aftermask_arr[3]:
            ip_aftermask_first=ip_aftermask_first+str(int(ip_aftermask_arri)+1)+r'.'
            ip_aftermask_last=ip_aftermask_last+str(int(valid_ip_max_arr[index_i])-1)+r'.'
        else:
            ip_aftermask_first=ip_aftermask_first+ip_aftermask_arri+r'.'
            ip_aftermask_last=ip_aftermask_last+valid_ip_max_arr[index_i]+r'.'
        index_i=index_i+1
    ip_aftermask_first=ip_aftermask_first.strip(r'.')
    ip_aftermask_last=ip_aftermask_last.strip(r'.')
    ip_aftermask_segment=ip_aftermask_segment.strip(r'.')
    ip_aftermask_brodcast=ip_aftermask_brodcast.strip(r'.')
    return [ip_aftermask_first,ip_aftermask_last,ip_aftermask_segment,ip_aftermask_brodcast]

def ip_samenet_judge(ipv4_1_ip,ipv4_1_mask,ipv4_2_ip):#judge ipv4_2_ip is or is't in ip1 net
    range_ipv41=ip_net_computer(ipv4_1_ip,ipv4_1_mask)
    range_ipv42=ip_net_computer(ipv4_2_ip,ipv4_1_mask)
    if (range_ipv41[0]==range_ipv42[0])and(range_ipv41[1]==range_ipv42[1]):
        if (range_ipv41[2]!=ipv4_2_ip)and(range_ipv41[3]!=ipv4_2_ip):
            return True
        elif (range_ipv41[2]==ipv4_2_ip):
            print('warning:%s is invalid ip,valid ip range is %s to %s' %(ipv4_2_ip,range_ipv41[0],range_ipv41[1]))
            return False
        else:
            print('warning:'+ipv4_2_ip+' is brodcast ip in this net segment')
            return True
    else:
        return False

def getSameSegmentIpOnComputerNetCard(ip_ip,ip_mask):
    ipconfigInfo=os.popen('ipconfig').read()
    ipConfArr=ipconfigInfo.split(':')
    ipConfArr_clean=[]
    for ipConfArr_i in ipConfArr:
        #ftp_ip=re.match('.*'+r'192.168.34'+'.*',ipConfArr_i)
        ftp_ip=re.match('.*\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.*',ipConfArr_i)
        if ftp_ip:
     #       print ftp_ip.group(0)
            ipConfArr_clean.append(ftp_ip.group(0).strip())
    #print a
    for ipConfArr_clean_i in ipConfArr_clean:
        if ip_samenet_judge(ip_ip,ip_mask,ipConfArr_clean_i):
            print('same_segment_local_ip:'+ipConfArr_clean_i)
            return ipConfArr_clean_i
            
def getPingSuccesIpOnComputerNetCard(Dev_ip,dev_mask):
    regex = re.compile('\s+')
    ip_valid_check=getSameSegmentIpOnComputerNetCard(Dev_ip,dev_mask)
    if ip_valid_check:
        return ip_valid_check

    routePrintInfo=os.popen('route print').read()
    routePrintArr=routePrintInfo.split('\n')
    default_ip_line=''
    pingSuccessKeyLine=''
    routePrintArr_clean=[]
    ipMaskInterface_info_arr=[]
    active_route_list=True
    for routePrintArri in routePrintArr:
        if ('0.0.0.0' in routePrintArri)and(active_route_list):#active route list
            default_ip_line=routePrintArri#record the default ip interface
            active_route_list=False
        routePrintArri_ip=re.match('\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*',routePrintArri)
        if (routePrintArri_ip)and('0.0.0.0' not in routePrintArri):#valid value start
            #print('ip:',routePrintArri_ip.group(1))
            #print('mask:',routePrintArri_ip.group(2))
            if ip_samenet_judge(routePrintArri_ip.group(1),routePrintArri_ip.group(2),Dev_ip):
                #print('find valid route in route list',Dev_ip,routePrintArri_ip.group(1),routePrintArri_ip.group(2))
                pingSuccessKeyLine=routePrintArri
                break#find same segment quit for loop immediately
    if not pingSuccessKeyLine:
        pingSuccessKeyLine=default_ip_line
    print(Dev_ip,'pingSuccessKeyLine is:',pingSuccessKeyLine)
    
    for ipMaskInterface_infoi in pingSuccessKeyLine.split(' '):
        ipMaskInterface_info=re.match('\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*',ipMaskInterface_infoi)
        if ipMaskInterface_info:
            ipMaskInterface_info_arr.append(ipMaskInterface_info.group(1))
    #print('ipMaskInterface_info_arr:',ipMaskInterface_info_arr)
    if len(ipMaskInterface_info_arr)==3:#probably find in permanent route list,but alse may in active route list(have chinese word in gateway column)
        if '0.0.0.0' in ipMaskInterface_info_arr:
            return ipMaskInterface_info_arr[2]
        return ipMaskInterface_info_arr[2]
    elif len(ipMaskInterface_info_arr)==4:#probably find in active route list,the last one column is interface
        if '0.0.0.0' in ipMaskInterface_info_arr:#0.0.0.0,retrun interface
            return ipMaskInterface_info_arr[3]
        return ipMaskInterface_info_arr[2]
    else:
        print('function getPingSuccesIpOnComputerNetCard hava an unexpected error,please contact WangMengZe for support^_^')
        return False

if __name__=='__main__':
    #print ip_net_computer('190.26.90.66','255.255.255.224')
    #print ip_samenet_judge('190.26.90.66','255.255.255.224','190.26.90.95')

    #getSameSegmentIpOnComputerNetCard('192.168.34.2','255.255.255.0')
    #getSameSegmentIpOnComputerNetCard('190.26.100.254','255.255.255.224')
    #deviceOnlineStateCheck('192.168.34.4')
    a=getPingSuccesIpOnComputerNetCard('172.16.66.54','255.255.255.0')
    a1=getPingSuccesIpOnComputerNetCard('192.168.36.2','255.255.255.0')
    print(a,a1)