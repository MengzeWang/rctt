
ResetCard_array=ResetCard_array4
ps_checkport=ps_checkport4

def ResetPX4CheckNackplane(DUT_instance,ResetCard_array,ps_checkport):
    import re,inspect,os,time
    start_time=time.time()
    i=1
    loop_label=True
    while loop_label:
        print('#################')
        print('reset card round:%d' %(i))
        print('#################')
        time.sleep(8)
        DUT_instance.raisecom_WriteLog('info', 2, 'reset card round:'+str(i))
        DUT_instance.BackToSpecialModeFromAnymode()
        for ResetCard_arrayi in ResetCard_array:
            CardState=DUT_instance.getCardState(ResetCard_arrayi).get(ResetCard_arrayi)
            if CardState:#
                if CardState=='working':
                    print('card state is working,reset card '+str(ResetCard_arrayi))
                    DUT_instance.raisecom_dutMagCommand_RC_sendCommand('reset card '+str(ResetCard_arrayi),'#')
                else:
                    print('slot '+str(ResetCard_arrayi)+'state is:'+CardState+',will not be reset.')
            else:
                print(str(ResetCard_arrayi)+' slot is not exist')
        
        loop_label2=True
        while loop_label2:
            loop_label2=False
            time.sleep(10)#应该改成检测板卡working
            for ResetCard_arrayi in ResetCard_array:
                CardState=DUT_instance.getCardState(ResetCard_arrayi).get(ResetCard_arrayi)
                if CardState:#能正常获取到板卡状态
                    if CardState!='working':
                        loop_label2=True#任何一个不working都会导致等待
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('debug','#')
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('bcm shell','>')
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('ps '+ps_checkport,'>')
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('ps '+ps_checkport,'>')
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('ps '+ps_checkport,'>')
        ps_res=DUT_instance.raisecom_dutMagCommand_RC_sendCommand('ps '+ps_checkport,'>')
        for ps_resi in ps_res.split('\n'):
            print(ps_resi)
            if 'down' in ps_resi:
                os.system('pause')
                DUT_instance.raisecom_dutMagCommand_RC_sendCommand('exit','#')
                loop_label=False
                break
        i=i+1
        DUT_instance.raisecom_dutMagCommand_RC_sendCommand('exit','#')
    finish_time=time.time()
    total_s=finish_time-start_time
    print(total_s)
    usedTime_h=int(total_s/3600)#hour
    usedTime_m=int((total_s-3600*usedTime_h)/60)#min
    usedTime_s=total_s-3600*usedTime_h-60*usedTime_m#s

    print('Used_time:%d hour,%d minute,%d seconds' %(usedTime_h,usedTime_m,usedTime_s))