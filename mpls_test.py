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
def CreateTunnelEline(DeviceIp,port_num,Tunnel,LSP,Eline):
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
    print(tn.read_very_eager())
    tn.write('interface '+LSP['LSP_next_port']+'\r\n')
    time.sleep(0.5)
    print(tn.read_very_eager())
    tn.write('switchport trunk allowed vlan add '+LSP['LSP_id']+'\r\n')
    time.sleep(0.5)
    tn.write('y\r\n')
    print(tn.read_very_eager())
    time.sleep(0.5)
    print(tn.read_very_eager())
    tn.write('switchport mode trunk\r\n')
    time.sleep(0.5)
    print(tn.read_very_eager())
    tn.write('exit\r\n')
    time.sleep(0.5)
    print(tn.read_very_eager())
    tn.write('create vlan '+LSP['LSP_id']+' active\r\n')
    time.sleep(1)
    print(tn.read_very_eager())
    t_range_list=Tunnel['Tunnel_id'].split('-')
    l_range_list=LSP['LSP_id'].split('-')
    e_range_list=Eline['Eline_vlan'].split('-')
    et_range_list=Eline['Eline_tunnelid'].split('-')
    et_range=int(et_range_list[len(et_range_list)-1])-int(et_range_list[0])
    for tidi in range(int(t_range_list[0]),int(t_range_list[len(t_range_list)-1])+1):
        tn.write('interface tunnel '+str(tidi)+'\r\n')
        time.sleep(0.5)
        print(tn.read_very_eager())
        tn.write('destination '+str(Tunnel['Tunnel_dst_lsr'])+'\r\n')
        time.sleep(0.5)
        print(tn.read_very_eager())
        tn.write('mpls tunnel-id '+str(tidi)+'\r\n')
        time.sleep(0.5)
        print(tn.read_very_eager())
        tn.write('exit'+'\r\n')
        print(tn.read_very_eager())
    #a=tn.read_until(cmdHostName)
    if LSP['LSP_direction']=="ingress":
        for lidi in range(int(l_range_list[0]),int(l_range_list[len(l_range_list)-1])+1):
            tn.write('mpls bidirectional static-lsp ingress '+str(lidi)+' lsr-id '+LSP['LSP_dst_lsr']+' tunnel-id '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('forward '+LSP['LSP_dst_lsr']+' 255.255.255.255 nexthop-mac '+LSP['LSP_next_mac']+' vlan '+str(lidi)+' '+LSP['LSP_next_port']+' out-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('backward in-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('exit'+'\r\n')
    elif LSP['LSP_direction']=="egress":
        for lidi in range(int(l_range_list[0]),int(l_range_list[len(l_range_list)-1])+1):
            tn.write('mpls bidirectional static-lsp egress '+str(lidi)+' lsr-id '+LSP['LSP_dst_lsr']+' tunnel-id '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('backward '+LSP['LSP_dst_lsr']+' 255.255.255.255 nexthop-mac '+LSP['LSP_next_mac']+' vlan '+str(lidi)+' '+LSP['LSP_next_port']+' out-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('forward in-label '+str(lidi)+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
            tn.write('exit'+'\r\n')
            print(tn.read_very_eager())
    tn.write('interface '+Eline['Eline_port']+'\r\n')
    time.sleep(0.5)
    print(tn.read_very_eager())
    et_range_cout=0
    for eidi in range(int(e_range_list[0]),int(e_range_list[len(e_range_list)-1])+1):
        if et_range_cout<et_range:
            tn.write('mpls static-l2vc vlan '+str(eidi)+' destination '+Eline['Eline_dst_lsr']+' tagged vc-id '+str(eidi)+' in-label '+str(eidi)+' out-label '+str(eidi)+' tunnel-interface '+str(int(et_range_list[0])+et_range_cout)+'\r\n')
            et_range_cout=et_range_cout+1
            time.sleep(0.5)
            print(tn.read_very_eager())
        else:
            tn.write('mpls static-l2vc vlan '+str(eidi)+' destination '+Eline['Eline_dst_lsr']+' tagged vc-id '+str(eidi)+' in-label '+str(eidi)+' out-label '+str(eidi)+' tunnel-interface '+et_range_list[len(et_range_list)-1]+'\r\n')
            time.sleep(0.5)
            print(tn.read_very_eager())
    tn.write('exit'+'\r\n')
    time.sleep(0.5)
    tn.write('exit'+'\r\n')
    print(tn.read_very_eager())


Tunnel_90_254={'Tunnel_id':'103-199','Tunnel_dst_lsr':"190.26.100.254"}
LSP_90_254={'LSP_direction':"ingress",'LSP_id':"103-199",'LSP_dst_lsr':"190.26.100.254",'LSP_next_mac':"000E.5E32.CDBA",'LSP_next_port':"port 169"}
Eline_90_254={'Eline_port':"port 130",'Eline_vlan':"203-299",'Eline_tunnelid':"103-199",'Eline_dst_lsr':"190.26.100.254"}

Tunnel_100_254={'Tunnel_id':"103-199",'Tunnel_dst_lsr':"190.26.90.254"}
LSP_100_254={'LSP_direction':"egress",'LSP_id':"103-199",'LSP_dst_lsr':"190.26.90.254",'LSP_next_mac':"000E.5EBB.ACCC",'LSP_next_port':"port 221"}
Eline_100_254={'Eline_port':"port 178",'Eline_vlan':"203-299",'Eline_tunnelid':"103-199",'Eline_dst_lsr':"190.26.90.254"}

CreateTunnelEline(r'190.26.90.254',23,Tunnel_90_254,LSP_90_254,Eline_90_254)
CreateTunnelEline(r'190.26.100.254',23,Tunnel_100_254,LSP_100_254,Eline_100_254)


