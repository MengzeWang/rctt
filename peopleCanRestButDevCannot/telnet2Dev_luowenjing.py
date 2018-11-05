#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import telnetlib
import time,re,os
import multiprocessing
from multiprocessing import Pool


class DevClass():
    def __init__(self,DevIp,DevTimeOut=600):#超时时间，单位s
        self.ip=DevIp
        self.DevTimeOut=DevTimeOut
        if self.deviceOnlineStateCheckExtend(4,DevTimeOut):#超时时间内通过ping包测试则建立telnet连接，否则设置当前实例的可用状态为false
            self.DevTelnetConnect()
            self.goodState=True
            self.log_path=r'D:\py_ftp_download\\'
            if not os.path.isdir(self.log_path):
                os.mkdir(self.log_path)
            print(self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-log.txt')
            self.f=open(self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-log.txt','a+')
        else:
            self.goodState=False
    #王孟泽
    #PingPacksNum：ping包个数
    #不丢包返回true，丢包返回false
    def deviceOnlineStateCheck(self,PingPacksNum=5):
        dev_pingInfo=os.popen('ping '+self.ip+' -n '+str(PingPacksNum)).read()
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
    #王孟泽
    #PingPacksNum：期望连续PingPacksNum个ping包不出现丢包，返回true
    #ck_timeout：超时时间，单位s。
    #默认ck_timeout=0，代表死循环，除非满足条件，否则持续进行ping包测试；
    #若ck_timeout为正数，则在限时ck_timeout秒内进行ping包测试，若达到限时仍未通过ping包测试，退出循环返回false
    def deviceOnlineStateCheckExtend(self,PingPacksNum=5,ck_timeout=0):
        devOnline=False
        pingRound=1
        if ck_timeout==0:
            loop_lable=True
            while loop_lable:
                print('ping test with 5 packes,round:%d' %(pingRound))
                if self.deviceOnlineStateCheck(PingPacksNum):
                    print('ping test with 5 packes round:%d pass,exit function' %(pingRound))
                    devOnline=True
                    loop_lable=False
                else:
                    print('ping test with 5 packes round:%d did not pass,go next' %(pingRound))
                pingRound=pingRound+1
        else:
            start_time=time.time()
            used_time=0
            while used_time<ck_timeout:
                cur_time=time.time()
                print('ping test with 5 packes,round:%d' %(pingRound))
                if self.deviceOnlineStateCheck(PingPacksNum):
                    print('ping test with 5 packes round:%d pass,exit function' %(pingRound))
                    devOnline=True
                    break#满足退出条件
                else:
                    print('ping test with 5 packes round:%d did not pass,go next' %(pingRound))
                used_time=cur_time-start_time
        return devOnline
    def DevTelnetConnect(self):
        if self.deviceOnlineStateCheck(2):
            global tn
            tn=telnetlib.Telnet(self.ip,port=23,timeout=10)
            tn.set_debuglevel(0)
            print(self.ip+'--DevTelnetConnect success.')
            return True
        else:
            return False
    def get_cmdresult(self,cmd,*end_until):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        tn.write(cmd+'\r\n')
        if end_until:
            return tn.read_until(end_until[0],10)
        else:
            time.sleep(5)
            return tn.read_very_eager()
    def multiline_infoprocess(self,str_info):
        str_info_list=[]
        for str_info_row in str_info.split('\n'):
            str_info_list.append(str_info_row)
        return str_info_list
    def DevLogin(self,username='raisecom',password='raisecom',sudo_pssd='raisecom'):#card_state can be follows:all/working/non-working
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        #f=open(Hostname+'.txt','a+')
        #tn.read_all()
        tn.write('\r\n')
        a=tn.read_until('Login:')
        #a=tn.read_some()
        print(a)
        tn.write(username+'\r\n')
        a=tn.read_until('Password:')
        print(a)
        tn.write(password+'\r\n')
        time.sleep(1)
        tn.write('ter time 0\r\n')
        time.sleep(1)
        tn.write('ena\r\n')
        time.sleep(1)
        tn.write(sudo_pssd+'\r\n')
        time.sleep(1)
        a=tn.read_very_eager()
        print(a)
        #a=tn.read_until('Raisecom#')
        for recv_name in a.split():
            if re.match('.*#',recv_name):
                print '######host name#######'
                print recv_name
                cmdHostName=recv_name
                print '######host name#######'
                break
        tn.write('show in sn'+'\r\n')
        a=tn.read_until('Raisecom#')
        print(a)
        print(self.ip+'--DevLogin success.')
    def DevSendcmdUntil(self,str_cmd,str_expected_end):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        tn.write(str_cmd+'\r\n')
        cmd_res=tn.read_until(str_expected_end)
        self.f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+cmd_res+'\n')
        print(cmd_res)
        return cmd_res
    def DevSendcmdWaitSomeTimes(self,str_cmd,waitTimes=5):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        print('start excute DevSendcmdWaitSomeTimes')
        tn.write(str_cmd+'\r\n')
        time.sleep(waitTimes)
        try:
            cmd_res=tn.read_very_eager()
            self.f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+cmd_res+'\n')
            print(cmd_res)
            return cmd_res
        except Exceptoin as e:
            print('an error occoured')
            return 'mz_info:an error occoured,cannot get cmd result '
    def DevShowCard(self,card_state='working'):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        tn.write('show card'+'\r\n')
        a=tn.read_until('#')
        self.f.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+a+'\n')
        print(a)
        sh_ca_list=[]
        arrow_name_index=0
        arrow_index=0
        show_cols=0
        for show_card_result_row in a.split('\n'):
            print(show_card_result_row)
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
                ver_result.append(slot_verx[0])
            #print ver_result
        elif card_state=='working':
            for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
                if slot_verx[2]=='working':
                    ver_result.append(slot_verx[0])
        else:
            for slot_verx in sh_ca_list_core[1:len(sh_ca_list_core)]:
                if slot_verx[2]!='working':
                    ver_result.append(slot_verx[0])
            #    print ver_result
        return [ver_result,sh_ca_list_core[1:len(sh_ca_list_core)]]#sh_ca_list_core:[card_info[slot_col],card_info[card_col],card_info[stat_col],card_info[PowerType_col]]
    def BackToSpecialModeFromAnymode(self):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        display_test=self.DevSendcmdWaitSomeTimes('test_curMode', 1)#获取当前所在模式
        display_test_arr=display_test.split('\r\n')
        for display_test_arr_i in display_test_arr:
            if re.match('.*#.*',display_test_arr_i):
                print('current in (%s) mode' %(display_test_arr_i))
                if ('(' in display_test_arr_i)or(')' in display_test_arr_i)or('>' in display_test_arr_i):
                    print('not in special mode')
                    display_test=self.DevSendcmdUntil('exit','#')
                    self.BackToSpecialModeFromAnymode()
                else:
                    return
            elif re.match('.*>.*',display_test_arr_i):
                print('current in (%s) mode' %(display_test_arr_i))
                if ('(' in display_test_arr_i)or(')' in display_test_arr_i)or('>' in display_test_arr_i):
                    print('not in special mode')
                    display_test=self.DevSendcmdWaitSomeTimes('exit',1)
                    self.BackToSpecialModeFromAnymode()
                else:
                    return
    def getCurrentMasterCard(self):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        self.BackToSpecialModeFromAnymode()
        show_card_raw=self.DevSendcmdUntil('show card', '#')
        sh_ca_list=[]
        arrow_name_index=0#假设列名称所在行为0行
        arrow_index=0
        for show_card_result_row in show_card_raw.split('\n'):
            if len(show_card_result_row.split())>6:
                sh_ca_list.append(show_card_result_row.split())
                if ('Slot' in show_card_result_row)and('State' in show_card_result_row):
                    print('find arrow name:',show_card_result_row,'current index is:',arrow_index)
                    arrow_name_index=arrow_index#列名称所在行真实值
                arrow_index=arrow_index+1
        slot_col=sh_ca_list[arrow_name_index].index('Slot')
        stat_col=sh_ca_list[arrow_name_index].index('State')
        card_col=stat_col-1
        sh_ca_list_core=[]
        MasterCard_dict={}
        for card_info in sh_ca_list:
            if card_info[0]!='*':
                if len(card_info)!=7:#目前show card结果有7列，后续如果show card结果列数变化，可修改此处，但这里仅是个列数异常提示，不影响使用
                    print('find a unexpected length line:',card_info,'consider this line is not show card valid info,drop it')
                else:
                    sh_ca_list_core.append([card_info[slot_col],card_info[card_col],card_info[stat_col]])
            else: 
                print 'Master_Card:'+card_info[slot_col+1]+'-'+card_info[card_col+1]
                MasterCard_dict={'Slot':card_info[slot_col+1],'DevName':card_info[card_col+1]}
                sh_ca_list_core.append([card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]]) 
        if int(MasterCard_dict['Slot'])%2==0:#当前主控槽位号为偶数
            for card_i in sh_ca_list_core[1:len(sh_ca_list_core)-1]:
                if (int(card_i[0])==(int(MasterCard_dict['Slot'])-1))and(card_i[2]=='working'):#槽位号和状态都对的上
                    MasterCard_dict['ManagementCardCount']=2
                    break
                else:
                    MasterCard_dict['ManagementCardCount']=1
        else:
            for card_i in sh_ca_list_core[1:len(sh_ca_list_core)-1]:
                if (int(card_i[0])==(int(MasterCard_dict['Slot'])+1))and(card_i[2]=='working'):#槽位号和状态都对的上
                    MasterCard_dict['ManagementCardCount']=2
                    break
                else:
                    MasterCard_dict['ManagementCardCount']=1
        return MasterCard_dict#MasterCard_dict={'Slot':当前主控盘槽位号,'DevName':当前主控板卡名称,'ManagementCardCount':当前机框working态的主控盘个数}
    def getCardState(self,CardSlot_list):#CardSlot_list='1,2,3,4'
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        CardSlot_list=str(CardSlot_list)
        CardSlot_list_arr=CardSlot_list.split(',')
        self.BackToSpecialModeFromAnymode()
        show_card_raw=self.DevSendcmdUntil('show card', '#')
        sh_ca_list=[]
        arrow_name_index=0#假设列名称所在行为0行
        arrow_index=0
        for show_card_result_row in show_card_raw.split('\n'):
            #print(show_card_result_row)
            if len(show_card_result_row.split())>6:
                sh_ca_list.append(show_card_result_row.split())
                if ('Slot' in show_card_result_row)and('State' in show_card_result_row):
                    print('find arrow name:',show_card_result_row,'current index is:',arrow_index)
                    arrow_name_index=arrow_index#列名称所在行真实值
                arrow_index=arrow_index+1
        slot_col=sh_ca_list[arrow_name_index].index('Slot')
        stat_col=sh_ca_list[arrow_name_index].index('State')
        card_col=stat_col-1
        #print('slot_col',slot_col,'stat_col',stat_col)
        sh_ca_list_core=[]
        for card_info in sh_ca_list:
            if card_info[0]!='*':
                #print('len(card_info)',len(card_info))
                if len(card_info)!=7:
                    print(card_info)
                sh_ca_list_core.append([card_info[slot_col],card_info[card_col],card_info[stat_col]])
            else: 
                print 'Master_Card:'+card_info[slot_col+1]+'-'+card_info[card_col+1]
                sh_ca_list_core.append([card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]]) 
        #print sh_ca_list_core
        CardSlot_list_state_dict={}
        for sh_ca_list_corei in sh_ca_list_core:
            #print sh_ca_list_corei
            for CardSlot_list_arri in CardSlot_list_arr:
                if str(CardSlot_list_arri)==str(sh_ca_list_corei[0]):
                    CardSlot_list_state_dict[int(CardSlot_list_arri)]=sh_ca_list_corei[2]
                    CardSlot_list_arr.remove(CardSlot_list_arri)
        if len(CardSlot_list_arr)!=0:
            print(u'注意,部分槽位未查询到工作状态：')
            print(CardSlot_list_arr)
        return CardSlot_list_state_dict#CardSlot_list_state_dict={'Slot':state,'Slot':state}
    def goIntoSlotByConfMode(self,slot_num):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        self.BackToSpecialModeFromAnymode()
        self.DevSendcmdUntil('config', '#')
        TryGoIntoSlotx=self.DevSendcmdUntil('slot '+str(slot_num), '.*')
        TryGoIntoSlotx=self.DevSendcmdUntil('\r', '#')
        TryGoIntoSlotx=self.DevSendcmdUntil('\r', '#')
        TryGoIntoSlotx=self.DevSendcmdUntil('\r', '#')
        print('****TryGoIntoSlotx*****')
        print(TryGoIntoSlotx)
        print('***********************')
        #'Raisecom(config-slot/7)#'
        #'Raisecom#'
        #'Raisecom(config-sfp/1)# '
        #'Raisecom(config-stm4-opt/1)#'
        #'Svc board do not support to enter slot mode.'
        #'Card in null state can not config.'
        for TryGoIntoSlotx_row in TryGoIntoSlotx.split('\n'):
            if 'config-' in TryGoIntoSlotx_row:
                print('go into slot success')
                return True
                self.DevSendcmdUntil('end\r\n', '#')#防止在sfp/stm port模式下
                print('pass', 1, '进入slot'+str(slot_num)+'成功')
                break
            elif 'Raisecom#' in TryGoIntoSlotx_row:
                testCurConfMode=self.DevSendcmdUntil('show card\r\n', '#')
                for testCurConfMode_row in testCurConfMode:#% " card "  Unknown command.
                    if 'Unknown command' in testCurConfMode_row:
                        #return True
                        self.DevSendcmdUntil('conf\r\n', '#')#进入单盘下的config模式
                        print('pass', 1, '进入slot'+str(slot_num)+'成功')
                        break
                    else:
                        print('pass', 1, '进入slot'+str(slot_num)+'失败')
                        return False
            elif 'debug' in TryGoIntoSlotx_row:
                testCurConfMode=self.DevSendcmdUntil('show card\r\n', '#')
                for testCurConfMode_row in testCurConfMode:#% " card "  Unknown command.
                    if 'Unknown command' in testCurConfMode_row:
                        #return True
                        self.DevSendcmdUntil('end', '#')#进入单盘下的config模式
                        print('pass', 1, '进入slot'+str(slot_num)+'成功')
                        break
                    else:
                        print('pass', 1, '进入slot'+str(slot_num)+'失败')
                        return False
            elif 'do not support to enter' in TryGoIntoSlotx_row:
                print('warning', 1, 'do not support to enter!')
                return False
            else:#无效行，略（存在隐藏bug：单盘bcmshell下或其他未知模式，认为是无效信息）
                pass
        getCardInfo=self.DevSendcmdUntil('show info', '#')
        activeStaus=''
        selfStmMode=''
        selfProtectMode=''
        for getCardInfoi in getCardInfo:
            if 'active status is' in getCardInfoi:
                activeStaus=getCardInfoi.split('')[len(getCardInfoi.split(''))-1]
            if 'self stm mode is' in getCardInfoi:
                selfStmMode=getCardInfoi.split('')[len(getCardInfoi.split(''))-1]
            if 'self protect mode is' in getCardInfoi:
                selfProtectMode=getCardInfoi.split('')[len(getCardInfoi.split(''))-1]
        return {'activeStaus':activeStaus,'selfStmMode':selfStmMode,'selfProtectMode':selfProtectMode}

    def DevCmdCheck(self):#检查是否需要登录,如需则登录
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        self.deviceOnlineStateCheckExtend(1)
        self.DevTelnetConnect()
        cmd_return=self.DevSendcmdWaitSomeTimes('\r\n\r\n\r\n',3)
        for cmd_returni in cmd_return.split('\r\n'):
            if 'Login:' in cmd_returni:
                self.DevLogin()
                return
        return
    #王孟泽
    #一个可选输入：numberOfManagementCard（指定当前设备主控盘个数，默认为2）
    #默认是在'#'模式下开始，返回设备HA状态的字典，回到'#'模式下
    #{'HA_state':int型（可能值：2/4/6/8/10）,'HA_mode':str型（可能值：'LOCK SWITCH'/'FORCE SWITCH'/'MANUAL SWITCH'/'AUTO SWITCH'）}
    #示例返回值：{'HA_mode': 'MANUAL SWITCH', 'HA_state': 6}
    def showHaState(self,numberOfManagementCard=2):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        try:
            if int(numberOfManagementCard) not in [1,2]:
                print(u'输入的主控盘个数错误！-%d，当前可选主控盘个数为1或者2（默认2）' %(int(numberOfManagementCard)))
                return
            self.BackToSpecialModeFromAnymode()
            self.DevSendcmdUntil('debug', '#')
            display_ha=self.DevSendcmdUntil('show ha sta', '#')
            ha_state=''
            ha_mode=''
            for display_ha_line in display_ha.split('\r\n'):
                #print('line:%s' %(display_ha_line))
                display_ha_line_arr=display_ha_line.split(r':')
                if re.match('.*HA fsm state.*',display_ha_line_arr[0]):#匹配HA状态
                    #print('HA fsm state:%s' %(display_ha_line_arr[1]))
                    ha_state=display_ha_line_arr[1].strip()
                if re.match('.*HA switch mode.*',display_ha_line_arr[0]):#匹配HA倒换模式
                    #print('HA fsm state:%s' %(display_ha_line_arr[1]))
                    ha_mode=display_ha_line_arr[1].strip()
                if len(display_ha_line_arr)>1:#排除无效行，根据':'分割后得到的list元素个数是否大于1
                    if re.match('.*state',display_ha_line_arr[1]):#检查每个模块的状态
                        if not re.match('0',display_ha_line_arr[2][0]):#如果有模块的状态为非0
                            print('bad Module:' %(display_ha_line_arr[3]))#打印问题模块详情
            self.DevSendcmdUntil('exit', '#')
            #print ha_state.split(r'(')
            if numberOfManagementCard==2:#双主控时同步状态不为6
                if ha_state.split(r'(')[0]!='6':
                    print(u'双主控时同步状态不为6:'+ha_state.split(r'(')[0]) #
            else:
                if ha_state.split(r'(')[0]!='2':#单主控时同步状态不为2
                    print(u'单主控时同步状态不为2:'+ha_state.split(r'(')[0]) #
            return {'HA_state':int(ha_state.split(r'(')[0]),'HA_mode':ha_mode}
        except:
            info = traceback.format_exc()
            print('info', 2, info, 'display') #回显异常log，统一都是info，因为info只是个形式，没有作用
    #王孟泽
    #注意：需要提前导入time模块
    #'#'模式下开始，视情况进行HA倒换操作，返回倒换结果，最后返回'#'
    #目前支持的倒换输入:clear/lock/force/manual/test/check/resetMaster/waitForSynce
    #进入debug检查HA状态是否为同步，若同步状态则执行给定倒换命令；若指定只有一块主控，直接执行倒换操作
    #若非同步,首先判断非同步状态倒换标志：async_switch
    ##   若async_switch==True则直接执行倒换；
    ##   若async_switch==False(默认),则状态为8/10直接返回倒换失败；状态为2/4共计持续40min返回倒换失败
    def haSwitch(self,switchTpye,async_switch=False,numberOfManagementCard=2):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        pre_haState=self.showHaState(numberOfManagementCard)
        if (numberOfManagementCard==2)and(pre_haState['HA_state']<6):#双主控且 未同步/同步过程中
            start_PreHaTime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
            print(u'当前时间：%s\n当前HA状态：%d' %(start_PreHaTime,pre_haState['HA_state']))
            for time_stepi in range(40):
                time.sleep(60)
                after_haState=self.showHaState(numberOfManagementCard)
                if after_haState['HA_state']==6:
                    break
            if after_haState['HA_state']!=6:
                print(u'HA执行倒换等待同步超过40min，起始HA状态：'+pre_haState['HA_state']+'，当前HA状态：'+after_haState['HA_state']) #
                return False
        elif pre_haState['HA_state'] in [8,10]:
            print(u'HA状态异常：'+str(pre_haState['HA_state'])) #
            return False
        else:
            after_haState=pre_haState

        if switchTpye=='waitForSynce':#私人模式，用于等待主备同步，能走到这一步说明已经同步，直接返回true
            return True
        #获取倒换前Master信息 槽位、倒换状态
        oldMasterSlot=self.getCurrentMasterCard()['Slot']
        oldHAState=after_haState['HA_mode']
        cmdend='#'
        cmdend2='.*reboot the device?(Y/N)'
        cmdend3='Login:'
        if switchTpye=='resetMaster':#目前存在问题：当前主盘为插网线的盘时，执行主盘复位后会导致网元长时间托管，平台自带的离线重连功能超时时间较短；需新开发设备在/离线检测功能
            display_ha=self.DevSendcmdWaitSomeTimes('reboot',3)#不匹配新的回显，只要命令下发即可
            display_ha=self.DevSendcmdWaitSomeTimes('Y',5)#不匹配新的回显，只要命令下发即可，后续引用ping包检测
        else:#进入conf模式
            display_ha=self.DevSendcmdUntil('conf', cmdend)
        if switchTpye=='clear':
            display_ha=self.DevSendcmdUntil('ha clear-switch', cmdend)
        elif switchTpye=='lock':
            display_ha=self.DevSendcmdUntil('ha lock-switch on', cmdend)
        elif switchTpye=='force':
            display_ha=self.DevSendcmdWaitSomeTimes('ha force-switch', 5)#不匹配新的回显，只要命令下发即可，后续引用ping包检测
        elif switchTpye=='manual':
            display_ha=self.DevSendcmdWaitSomeTimes('ha manual-switch', 5)#不匹配新的回显，只要命令下发即可，后续引用ping包检测
        elif switchTpye=='test':
            display_ha=self.DevSendcmdUntil('ha test-switch', cmdend)
        elif switchTpye=='check':
            display_ha=self.DevSendcmdUntil('ha check-version', cmdend)
        elif switchTpye=='mz_check':#用于递归调用自身，检查HA状态，返回执行倒换命令后当前主盘信息
            curMasterSlot=self.getCurrentMasterCard()['Slot']
            return curMasterSlot
        elif switchTpye=='resetMaster':
            pass
        else:
            print(u'注意！错误的倒换类型输入:%s:(目前支持的倒换输入:clear/lock/force/manual/resetMaster)' %(switchTpye))
        self.deviceOnlineStateCheckExtend()#ping包检测，每轮ping5个包，除非丢包率为0，否则不会退出ping循环
        self.DevCmdCheck()#检测是否需要登录
        newMasterSlot=self.haSwitch('mz_check',async_switch,numberOfManagementCard)#递归调用自身
        newHAState=self.showHaState(numberOfManagementCard)['HA_mode']
        if switchTpye in ['resetMaster','force','manual']:#这些操作需检查HA后主控槽位是否变化，变化则返回倒换成功
            if oldMasterSlot!=newMasterSlot:
                print('oldMasterSlot:%s\nnewMasterSlot:%s' %(oldMasterSlot,newMasterSlot))
                print(switchTpye+' Switch succes')
                return True
            else:
                print('oldMasterSlot:%s\nnewMasterSlot:%s' %(oldMasterSlot,newMasterSlot))
                print(switchTpye+' Switch Failed')
                return False
        elif switchTpye=='lock':#检测HA状态是否变化为锁定
            if newHAState=='LOCK SWITCH':
                print(switchTpye+' Switch succes')
                return True
            else:
                print(switchTpye+' Switch Failed')
                return False
        elif switchTpye=='clear':#检测HA倒换状态是否变化为自动倒换
            if newHAState=='AUTO SWITCH':
                print(switchTpye+' Switch succes')
                return True
            else:
                print('clear Switch Failed')
                return False
        else:#其他的暂时没用，后续需要用再细化（test/check）
            return True

    def resetAll(self):
        if not self.goodState:
            print(u'设备网络存在异常，不能执行测试，退出。')
            return
        self.BackToSpecialModeFromAnymode()
        self.DevSendcmdWaitSomeTimes('reset all', 5)
        time.sleep(30)
        self.deviceOnlineStateCheckExtend()
        self.DevTelnetConnect()
        self.DevLogin()



if __name__=='__main__':
    a=DevClass('172.16.66.227')
    a.DevLogin()
    while True:
        a.haSwitch('waitForSynce')
        a.haSwitch('manual')#目前支持的倒换输入:clear/lock/force/manual/test/check/resetMaster/waitForSynce
        a.haSwitch('manual')#目前支持的倒换输入:clear/lock/force/manual/test/check/resetMaster/waitForSynce
        a.DevSendcmdUntil('ping 172.30.1.25','#')
        a.resetAll()
