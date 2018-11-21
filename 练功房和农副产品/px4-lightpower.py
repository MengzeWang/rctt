import telnetlib,time,os
Hostname='192.167.36.3'
tn=telnetlib.Telnet(Hostname,port=23,timeout=10)
tn.set_debuglevel(0)
tn.write('\r\n')
tn.write('raisecom\r\n')
a=tn.read_until('Login:')
print a
tn.write('raisecom\r\n')
a=tn.read_until('Password:')
print a
tn.write('ena\r\n')
a=tn.read_until('Raisecom>')
print a
tn.write('raisecom\r\n')
time.sleep(2)
a=tn.read_very_eager()
print a
while True:
    tn.write('conf'+'\r\n')
    time.sleep(1)
    a=tn.read_very_eager()
    print a
    tn.write('slot 11\r\n')
    a=tn.read_very_eager()
    print a
    tn.write('\r\n')
    tn.write('\r\n')
    time.sleep(3)
    a=tn.read_very_eager()
    print a
    tn.write('show_tr 1 ddm')
    time.sleep(1)
    tn.write('\r\n')
    time.sleep(3)
    show_transceiver_res=tn.read_very_eager()
    for show_transceiver_resi in show_transceiver_res.split('\n'):
        print('show_transceiver_resi:',show_transceiver_resi)
        if 'transceiver temperature: 0.000 centigrade' in show_transceiver_resi:
            os.system('pause')
    tn.write('exit')
    time.sleep(1)
    tn.write('\r\n')
    time.sleep(1)
    a=tn.read_very_eager()#raisecom(conf)#
    print a
    tn.write('exit')
    time.sleep(1)
    tn.write('\r\n')
    time.sleep(1)
    a=tn.read_very_eager()#raisecom#
    print a
    tn.write('reset card 11')
    time.sleep(1)
    tn.write('\r\n')
    time.sleep(1)
    a=tn.read_until('Slot 11 plugged in.')
    #a=tn.read_very_eager()#Slot 11 plugged in.
    print a
    time.sleep(10)