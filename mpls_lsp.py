#-*- encoding: utf8 -*-
__author__ = 'MengZe'
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
def CreateEline(DeviceIp,port_num,Tunnel,LSP,Eline):
    username='raisecom'
    password='raisecom'
    sudo_pssd='raisecom'
    tn=telnetlib.Telnet(DeviceIp,port=port_num,timeout=10)
    tn.set_debuglevel(0)
    tn.write('\r\n')
    tn.write(username+'\r\n')
    a=tn.read_until('Login:')
    print_block(a,0)
    tn.write(password+'\r\n')
    a=tn.read_until('Password:')
    print_block(a,0)
    tn.write('ena\r\n')
    time.sleep(3)
    print_block(a,0)
    tn.write(sudo_pssd+'\r\n')
    time.sleep(3)
    a=tn.read_very_eager()
    for recv_name in a.split():
        if re.match('.*#',recv_name):
            print '######host name#######'
            print recv_name
            cmdHostName=recv_name
            print '######host name#######'
            break
    tn.write('conf\r\n')
    time.sleep(0.5)
    tn.write('interface '+LSP['LSP_next_port']+'\r\n')
    time.sleep(0.5)
    tn.write('switchport trunk allowed vlan '+LSP['LSP_id']+'\r\n')
    time.sleep(0.5)
    tn.write('switchport mode trunk\r\n')
    time.sleep(0.5)
    tn.write('exit\r\n')
    time.sleep(0.5)
    tn.write('create vlan '+LSP['LSP_id']+' active\r\n')
    time.sleep(1)
    t_range_list=Tunnel['Tunnel_id'].split('-')
    l_range_list=LSP['LSP_id'].split('-')
    e_range_list=Eline['Eline_vlan'].split('-')
    et_range_list=Eline['Eline_tunnelid'].split('-')
    et_range=int(et_range_list[len(et_range_list)-1])-int(et_range_list[0])
    et_range_cout=0
    for tidi in range(int(t_range_list[0]),int(t_range_list[len(t_range_list)-1])):
        tn.write('interface tunnel '+str(tidi)+'\r\n')
        time.sleep(0.5)
        tn.write('destination '+str(Tunnel['Tunnel_dst_lsr'])+'\r\n')
        time.sleep(0.5)
        tn.write('mpls tunnel-id '+str(tidi)+'\r\n')
        time.sleep(0.5)
        tn.write('exit'+'\r\n')
    #a=tn.read_until(cmdHostName)
    if LSP['LSP_direction']=="ingress":
        for lidi in range(int(l_range_list[0]),int(l_range_list[len(l_range_list)-1])):
            tn.write('mpls bidirectional static-lsp ingress '+str(lidi)+' lsr-id '+LSP['LSP_dst_lsr']+' tunnel-id '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('forward '+LSP['LSP_dst_lsr']+' 255.255.255.255 nexthop-mac '+LSP['LSP_next_mac']+' vlan '+str(lidi)+' '+LSP['LSP_next_port']+' out-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('backward in-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('exit'+'\r\n')
    elif LSP['LSP_direction']=="egress":
        for lidi in range(int(l_range_list[0]),int(l_range_list[len(l_range_list)-1])):
            tn.write('mpls bidirectional static-lsp egress '+str(lidi)+' lsr-id '+LSP['LSP_dst_lsr']+' tunnel-id '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('backward '+LSP['LSP_dst_lsr']+' 255.255.255.255 nexthop-mac '+LSP['LSP_next_mac']+' vlan '+str(lidi)+' '+LSP['LSP_next_port']+' out-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('forward in-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            tn.write('exit'+'\r\n')
    tn.write('interface '+Eline['Eline_port']+'\r\n')
    time.sleep(0.5)
    for eidi in range(int(e_range_list[0]),int(e_range_list[len(e_range_list)-1])):
        if et_range_cout<et_range:
            tn.write('mpls static-l2vc vlan '+str(eidi)+' destination '+Eline['Eline_dst_lsr']+' tagged vc-id '+str(eidi)+' in-label '+str(eidi)+' out-label '+str(eidi)+' tunnel-interface '+str(int(et_range_list[0]+et_range_i)+'\r\n')
            et_range_cout=et_range_cout+1
            time.sleep(0.5)
        else:
            tn.write('mpls static-l2vc vlan '+str(eidi)+' destination '+Eline['Eline_dst_lsr']+' tagged vc-id '+str(eidi)+' in-label '+str(eidi)+' out-label '+str(eidi)+' tunnel-interface '+et_range_list[len(et_range_list)-1]+'\r\n')
            time.sleep(0.5)

Tunnel_90_254={'Tunnel_id':'4201-4250','Tunnel_dst_lsr':"192.167.36.3"}
LSP_90_254={'LSP_direction':"ingress",'LSP_id':"4201-4250",'LSP_dst_lsr':"192.167.36.3",'LSP_next_mac':"0018.0518.0004",'LSP_next_port':"port 89"}
Eline_90_254={'Eline_port':"port 99",'Eline_vlan':"5201-5250",'Eline_tunnelid':"4201-4250",'Eline_dst_lsr':"192.167.36.3"}

Tunnel_100_254={'Tunnel_id':"4201-4250",'Tunnel_dst_lsr':"192.168.36.4"}
LSP_100_254={'LSP_direction':"egress",'LSP_id':"4201-4250",'LSP_dst_lsr':"192.168.36.4",'LSP_next_mac':"0018.0518.0007",'LSP_next_port':"port 97"}
Eline_100_254={'Eline_port':"port 94",'Eline_vlan':"5201-5250",'Eline_tunnelid':"4201-4250",'Eline_dst_lsr':"192.168.36.4"}

CreateEline(r'190.26.90.254',23,Tunnel_90_254,LSP_90_254,Eline_90_254)

