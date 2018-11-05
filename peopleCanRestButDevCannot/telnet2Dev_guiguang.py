#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import telnetlib
import time,re,os,sys,platform
import multiprocessing
from Tkinter import *
import tkMessageBox
import threading
if int(platform.python_version()[0])==3:
    py3=True
else:
    py3=False

class DevClass(object):
    def __init__(self,DevIp,DevTimeOut=600,log_path=''):#超时时间，单位s
        curDir=os.getcwd()#os.path.abspath('.')
        MainDir=curDir+r'\py_ftp_download\peopleCanRestButDevCannot\\'
        self.ip=DevIp
        self.DevTimeOut=DevTimeOut
        if log_path=='':
            self.log_path=MainDir
        else:
            self.log_path=log_path
        print(self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-log.txt')
        self.flog_str=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-log.txt'
        self.flog_error_str=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-error-log.txt'
        self.makeDir(self.log_path)
        if self.deviceOnlineStateCheckExtend(4,DevTimeOut):#超时时间内通过ping包测试则建立telnet连接，否则设置当前实例的可用状态为false
            self.goodState=True
            self.DevTelnetConnect()
            self.DevLogin()
        else:
            self.goodState=False
    #检查制定路径文件夹，若不存在则新建
    def makeDir(self,logdir):
        import re,os
        Disk=re.findall(r'\w:\\+',logdir)#盘符
        #logdir_list=re.findall(r'\\+(\w*)\\+',repr(logdir))#所有文件夹
        logdir_list=repr(logdir).split('\\')[1:]#获得文件夹列表并去除盘符
        temp_dir=Disk[0]
        for logdir_listi in logdir_list:#逐层建立文件夹
            if (logdir_listi)and(logdir_listi not in ['\'']):#不为空或纯符号’
                temp_dir=os.path.join(temp_dir,logdir_listi)
            if not os.path.isdir(temp_dir):
                print('dir:',temp_dir,'is not exist!now try to make one.')
                try:
                    os.mkdir(temp_dir)
                except Exception as e:
                    print('an error occured when try to make dir:'+temp_dir+'.reason:'+str(e))
    #王孟泽
    #PingPacksNum：ping包个数
    #不丢包返回true，丢包返回false
    def deviceOnlineStateCheck(self,PingPacksNum=5):
        dev_pingInfo=os.popen('ping '+self.ip+' -n '+str(PingPacksNum)).read()
        dev_pingInfo_arr=dev_pingInfo.split('\n')
        successPingCount=0
        for dev_pingInfo_arri in dev_pingInfo_arr:
            print(dev_pingInfo_arri)
            if 'TTL' in dev_pingInfo_arri:
                successPingCount=successPingCount+1
        if successPingCount==PingPacksNum:
            return True
        else:
            print(u'存在丢包，丢包率百分之：%d' %(100*(1-successPingCount/PingPacksNum)))
            return False
    def print_info(self,strInfo=''):
        print(u'设备网络存在异常，不能执行测试项：'+strInfo+u'，退出。')
    def logWriter(self,txt_pathfilename,str2write,printInfo=True):
        if printInfo:
            print(str2write)
        with open(txt_pathfilename,'a+') as myLog:
            myLog.write('('+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+')-'+str(str2write)+'\n')
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
                print('ping test with %d packes,round:%d' %(int(PingPacksNum),pingRound))
                if self.deviceOnlineStateCheck(PingPacksNum):
                    print('ping test with %d packes round:%d pass,exit function' %(int(PingPacksNum),pingRound))
                    self.logWriter(self.flog_error_str,'ping test with '+str(PingPacksNum)+' packes round:'+str(pingRound)+' pass,exit function')
                    devOnline=True
                    loop_lable=False
                else:
                    print('ping test with %d packes round:%d did not pass,go next' %(int(PingPacksNum),pingRound))
                    self.logWriter(self.flog_error_str,'ping test with '+str(PingPacksNum)+' packes round:'+str(pingRound)+' did not pass,go next')
                pingRound=pingRound+1
        else:
            start_time=time.time()
            used_time=0
            while used_time<ck_timeout:
                cur_time=time.time()
                print('ping test with %d packes,round:%d' %(int(PingPacksNum),pingRound))
                if self.deviceOnlineStateCheck(PingPacksNum):
                    print('ping test with %d packes round:%d pass,exit function' %(int(PingPacksNum),pingRound))
                    self.logWriter(self.flog_error_str,'ping test with '+str(PingPacksNum)+' packes round:'+str(pingRound)+' pass,exit function')
                    devOnline=True
                    break#满足退出条件
                else:
                    print('ping test with %d packes round:%d did not pass,go next' %(int(PingPacksNum),pingRound))
                    self.logWriter(self.flog_error_str,'ping test with '+str(PingPacksNum)+' packes round:'+str(pingRound)+' did not pass,go next')
                used_time=cur_time-start_time
        return devOnline
    #王孟泽
    #在指定时间内与设备建立telnet连接
    def DevTelnetConnect(self,reTryTimes_int=30):#如果能ping通,但60min都没成功telnet连接，任务返回失败
        reTryTimesMem=reTryTimes_int
        while reTryTimes_int>0:
            reTryTimes_int=reTryTimes_int-1
            if self.deviceOnlineStateCheckExtend(2):
                try:
                    self.tn=telnetlib.Telnet(self.ip,port=23,timeout=10)
                    self.tn.set_debuglevel(0)
                    print(self.ip+'--DevTelnetConnect success.')
                    return True
                except Exception as e:
                    print('DevTelnetConnect %d times failed,retry after 120 sec.' %(reTryTimesMem-reTryTimes_int))
                    self.logWriter(self.flog_error_str,self.ip+'--try DevTelnetConnect '+str(reTryTimesMem-reTryTimes_int)+' times failed!telnet failed')
                    time.sleep(120)
                    if reTryTimes_int==0:
                        self.logWriter(self.flog_error_str,self.ip+'--try DevTelnetConnect '+str(reTryTimesMem)+' times failed,quit!'+str(e))
                        self.goodState=False
                        return False
            else:
                print('DevTelnetConnect %d times ping result failed,retry after 120 sec.' %(reTryTimesMem-reTryTimes_int))
                self.logWriter(self.flog_error_str,self.ip+'--try DevTelnetConnect '+str(reTryTimesMem-reTryTimes_int)+' times failed!ping result failed.')
                time.sleep(120)
                if reTryTimes_int==0:
                    self.logWriter(self.flog_error_str,self.ip+'--try DevTelnetConnect '+str(reTryTimesMem)+' times failed,quit!'+str(e))
                    self.goodState=False
                    return False
    #王孟泽
    #输入：一般是下发命令的返回值，该函数作用是将返回值按行分割返回list
    def multiline_infoprocess(self,str_info):
        str_info_list=[]
        for str_info_row in str_info.split('\n'):
            str_info_list.append(str_info_row)
        return str_info_list
    #王孟泽
    #输入：在建立了telnet连接的前提下，登录设备
    def DevLogin(self,username='raisecom',password='raisecom',sudo_pssd='raisecom'):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        self.DevSendcmdUntil('\r\n','Login:')
        self.DevSendcmdUntil(username,'Password:')
        #self.DevSendcmdWaitSomeTimes('\r\n',1)
        #self.DevSendcmdWaitSomeTimes(username+'\r\n',1)
        #self.DevSendcmdWaitSomeTimes('ter time 0\r\n',1)
        self.DevSendcmdWaitSomeTimes(password,3)
        self.DevSendcmdWaitSomeTimes('ter time 0',1)
        self.DevSendcmdWaitSomeTimes('ena',1)
        self.DevSendcmdUntil(sudo_pssd,'#')
        self.DevSendcmdUntil('show in sn','#')
        print(self.ip+'--DevLogin success.')
    #王孟泽
    #输入：在登录设备前提下，发送命令并等待期望的回显终止符号（会自动写入log）
    def DevSendcmdUntil(self,str_cmd,str_expected_end,printInfo=True):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        if py3:
            str_cmd=str(str_cmd+'\r\n').encode('utf-8')
            str_expected_end=str(str_expected_end).encode('utf-8')
        else:
            str_cmd=str(str_cmd+'\r\n')
            str_expected_end=str(str_expected_end)
        print('start excute DevSendcmdUntil:',str_cmd,str_expected_end)
        try:
            self.tn.write(str_cmd)
            if py3:
                cmd_res=self.tn.read_until(str_expected_end).decode('utf-8')
            else:
                cmd_res=self.tn.read_until(str_expected_end)
            self.logWriter(self.flog_str,cmd_res,printInfo)
            return cmd_res
        except Exception as e:
            self.logWriter(self.flog_error_str,'an error occoured when excute cmd:'+str_cmd+'.error reason:'+str(e))
            self.logWriter(self.flog_error_str,'now try relogin and send again!')
            self.DevTelnetConnect()
            self.DevCmdCheck()
            self.DevSendcmdUntil(str_cmd,str_expected_end)
            return 'mz_info:an error occoured,cannot get cmd result'
    #王孟泽
    #输入：在登录设备前提下，发送命令并等待指定时间后读取返回（会自动写入log）
    def DevSendcmdWaitSomeTimes(self,str_cmd,waitTimes=5,printInfo=True):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        if py3:
            str_cmd=str(str_cmd+'\r\n').encode('utf-8')
        else:
            str_cmd=str(str_cmd+'\r\n')
        print('start excute DevSendcmdWaitSomeTimes:',str_cmd)
        try:
            self.tn.write(str_cmd)
            time.sleep(waitTimes)
            if py3:
                cmd_res=self.tn.read_very_eager().decode('utf-8')
            else:
                cmd_res=self.tn.read_very_eager()
            self.logWriter(self.flog_str,cmd_res,printInfo)
            return cmd_res
        except Exception as e:
            self.logWriter(self.flog_error_str,'an error occoured when excute cmd:'+str_cmd+'.error reason:'+str(e))
            self.logWriter(self.flog_error_str,'now try relogin and send again!')
            self.DevTelnetConnect()
            self.DevCmdCheck()
            self.DevSendcmdWaitSomeTimes(str_cmd)
            return 'mz_info:an error occoured,cannot get cmd result'
    #王孟泽
    #输入：在登录设备前提下，发送show card命令并返回处理后的结果
    def DevShowCard(self,card_state='working'):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        showC_res=self.DevSendcmdUntil('show card\r\n','#')
        sh_ca_list=[]
        arrow_name_index=0
        arrow_index=0
        show_cols=0
        for show_card_result_row in showC_res.split('\n'):
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
            print(sh_ca_list_corei)
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
    #王孟泽
    #输入：在登录设备前提下，从任意模式返回#模式下
    def BackToSpecialModeFromAnymode(self):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
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
    #王孟泽
    #输入：在登录设备前提下，获取当前主控盘信息
    #返回字典类型结果：
    #{'Slot':当前主控盘槽位号,'DevName':当前主控板卡名称,'ManagementCardCount':当前机框working态的主控盘个数}
    def getCurrentMasterCard(self):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
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
                print('Master_Card:'+card_info[slot_col+1]+'-'+card_info[card_col+1])
                MasterCard_dict={'Slot':card_info[slot_col+1],'DevName':card_info[card_col+1]}
                sh_ca_list_core.append([card_info[slot_col+1],card_info[card_col+1],card_info[stat_col+1]])
        try:
            MasterCard_slot=int(MasterCard_dict.get('Slot',0))#获取主盘盘号
        except Exception as e:
            print('an error occured when excute:int(MasterCard_dict.get("Slot",0))',e)
        if MasterCard_slot!=0:
            if MasterCard_slot%2==0:#当前主控槽位号为偶数
                for card_i in sh_ca_list_core[1:len(sh_ca_list_core)-1]:
                    if (int(card_i[0])==(MasterCard_slot-1))and(card_i[2]=='working'):#槽位号和状态都对的上
                        MasterCard_dict['ManagementCardCount']=2
                        MasterCard_dict['Slave_slot']=MasterCard_slot-1
                        break
                    else:
                        MasterCard_dict['ManagementCardCount']=1
            else:
                for card_i in sh_ca_list_core[1:len(sh_ca_list_core)-1]:
                    if (int(card_i[0])==(MasterCard_slot+1))and(card_i[2]=='working'):#槽位号和状态都对的上
                        MasterCard_dict['ManagementCardCount']=2
                        MasterCard_dict['Slave_slot']=MasterCard_slot+1
                        break
                    else:
                        MasterCard_dict['ManagementCardCount']=1
        return MasterCard_dict#MasterCard_dict={'Slot':当前主控盘槽位号,'DevName':当前主控板卡名称,'ManagementCardCount':当前机框working态的主控盘个数}
    #王孟泽
    #输入：在登录设备前提下，获取show card的信息
    #返回字典类型结果：
    #{'Slot':state,'Slot':state,...}
    def getCardState(self,CardSlot_list):#CardSlot_list='1,2,3,4'
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
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
                print('Master_Card:'+card_info[slot_col+1]+'-'+card_info[card_col+1])
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
    #王孟泽
    #输入：在登录设备前提下，通过conf模式下的slot x命令进入x单盘
    #返回字典类型结果：
    def goIntoSlotByConfMode(self,slot_num):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
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
    #王孟泽
    #输入：检测设备登录状态，如需要登录则登录
    def DevCmdCheck(self):#检查是否需要登录,如需则登录
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        if self.deviceOnlineStateCheckExtend(1):#能ping通
            try:
                cmd_return=self.DevSendcmdWaitSomeTimes('\r\n\r\n\r\n',3)
                for cmd_returni in cmd_return.split('\r\n'):
                    if 'Login:' in cmd_returni:
                        self.DevLogin()
                        return
            except Exception as e:
                self.DevTelnetConnect()
                self.DevLogin()
        return
    #王孟泽
    #一个可选输入：numberOfManagementCard（指定当前设备主控盘个数，默认为2）
    #默认是在'#'模式下开始，返回设备HA状态的字典，回到'#'模式下
    #{'HA_state':int型（可能值：2/4/6/8/10）,'HA_mode':str型（可能值：'LOCK SWITCH'/'FORCE SWITCH'/'MANUAL SWITCH'/'AUTO SWITCH'）}
    #示例返回值：{'HA_mode': 'MANUAL SWITCH', 'HA_state': 6}
    def showHaState(self,numberOfManagementCard=2):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        try:
            if int(numberOfManagementCard) not in [1,2]:
                print(u'输入的主控盘个数错误！-%d，当前可选主控盘个数为1或者2（默认2）' %(int(numberOfManagementCard)))
                return
            self.BackToSpecialModeFromAnymode()
            self.DevSendcmdUntil('debug', '#')
            ha_state=''
            ha_mode=''
            while not ha_state:#未匹配到任何结果则会持续尝试
                display_ha=self.DevSendcmdUntil('show ha sta', '#')
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
                    print(u'双主控时同步状态不为6:'+str(ha_state.split(r'(')[0])) #
                    self.logWriter(self.flog_str,'ha_state_abnormal:'+str(ha_state.split(r'(')[0]))
            else:
                if ha_state.split(r'(')[0]!='2':#单主控时同步状态不为2
                    print(u'单主控时同步状态不为2:'+ha_state.split(r'(')[0]) #
            return {'HA_state':int(ha_state.split(r'(')[0]),'HA_mode':ha_mode}
        except Exception as e:
            self.logWriter(self.flog_error_str,'showHaState mode failed!--'+str(e))
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
            self.print_info(sys._getframe().f_code.co_name)
            return
        pre_haState=self.showHaState(numberOfManagementCard)
        if (numberOfManagementCard==2)and(pre_haState['HA_state'] in [2,4,9]):#双主控且 未同步/同步过程中
            start_PreHaTime=time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time()))
            print(u'当前时间：%s\n当前HA状态：%d' %(start_PreHaTime,pre_haState['HA_state']))
            for time_stepi in range(40):
                time.sleep(60)
                after_haState=self.showHaState(numberOfManagementCard)
                if after_haState['HA_state']==6:
                    break
            if after_haState['HA_state']!=6:
                print(u'HA执行倒换等待同步超过40min，起始HA状态：'+str(pre_haState['HA_state'])+u',当前HA状态：'+str(after_haState['HA_state'])) #
                self.logWriter(self.flog_str,'non synce state over 40min:'+str(after_haState['HA_state']))
                return False
        elif pre_haState['HA_state'] in [1,3,5,7,8,10]:
            print(u'HA状态异常：'+str(pre_haState['HA_state'])) #
            self.logWriter(self.flog_str,'ha state abnormal:'+str(pre_haState['HA_state']))
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
            #zyh_ha=self.DevSendcmdWaitSomeTimes('debug',3)
            #zyh_ha=self.DevSendcmdUntil('show devm card-devinfo 12','#')
            #zyh_ha=self.DevSendcmdWaitSomeTimes('exit',3)
            display_ha=self.DevSendcmdWaitSomeTimes('reboot',3)#不匹配新的回显，只要命令下发即可
            display_ha=self.DevSendcmdWaitSomeTimes('Y',5)#不匹配新的回显，只要命令下发即可，后续引用ping包检测
            time.sleep(60)
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
                self.logWriter(self.flog_str,switchTpye+' Switch Failed--'+'oldMasterSlot:'+str(oldMasterSlot)+',newMasterSlot:'+str(newMasterSlot))
                return False
        elif switchTpye=='lock':#检测HA状态是否变化为锁定
            if newHAState=='LOCK SWITCH':
                print(switchTpye+' Switch succes')
                return True
            else:
                print(switchTpye+' Switch Failed')
                self.logWriter(self.flog_str,switchTpye+' Switch Failed')
                return False
        elif switchTpye=='clear':#检测HA倒换状态是否变化为自动倒换
            if newHAState=='AUTO SWITCH':
                print(switchTpye+' Switch succes')
                return True
            else:
                print('clear Switch Failed')
                self.logWriter(self.flog_str,'clear Switch Failed')
                return False
        else:#其他的暂时没用，后续需要用再细化（test/check）
            return True
    #王孟泽
    #用reset all命令重启设备（不做ha状态检查），等待900s再尝试登录
    def resetAll(self):
        if not self.goodState:
            self.print_info(sys._getframe().f_code.co_name)
            return
        self.BackToSpecialModeFromAnymode()
        self.DevSendcmdWaitSomeTimes('reset all', 5)
        time.sleep(900)
        self.deviceOnlineStateCheckExtend()
        self.DevTelnetConnect()
        self.DevLogin()
    def bcmShellShowcThenRecord_2U(self,portNum,Tx_range='0-any',Rx_range='0-any',timeStep=5):#阈值表示的是正常范围。不在此范围内的会被记录.采集的时间间隔默认是5s一次
        if not portNum:
            return
        portNum_list=[]
        if type(portNum) == str:
            portNum_list1=portNum.split(',')
        elif type(portNum) == list:
            portNum_list1=portNum
        else:
            return
        for portNum_list1i in portNum_list1:
            portNum_list.append(portNum_list1i)
        import os,re
        Tx_range_list=Tx_range.split('-')
        Rx_range_list=Rx_range.split('-')
        minTx=Tx_range_list[0]
        maxTx=Tx_range_list[1]
        minRx=Rx_range_list[0]
        maxRx=Rx_range_list[1]
        self.BackToSpecialModeFromAnymode()
        self.DevSendcmdUntil('debug', '#',False)
        log_path_showc=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-result-log.txt'
        log_path_showc2=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-result-clean-log.txt'
        try:
            self.DevSendcmdUntil('bcm shell','>',False)
            while True:
                roudi_res=[]
                roudi_res_clean=[]
                res=self.DevSendcmdUntil('show c ','>',False)
                for resi in res.splitlines():
                    #RPKT.ge26               :         6,319,014,831              +5,106           1,000/s
                    resi_l=resi.split()#根据空格分割，正常的数据应该有5列['RPKT.ge26', ':', '6,319,014,831', '+5,106', '1,000/s']
                    for porti in portNum_list:
                        rPort='RBYT.'+porti
                        tPort='TBYT.'+porti
                        if (rPort in resi)or(tPort in resi):
                            roudi_res.append(self.ip+' '+resi)#直接记录原始记录
                            if len(resi_l)==5:
                                PortSpeed=resi_l[-1].split('/')[0]#20181029新增，只记录速度,并去除/s
                            else:
                                PortSpeed='N/A'
                            roudi_res_clean.append(self.ip+'|'+resi_l[0]+'|'+str(PortSpeed))#20181029新增，只记录速度
                #self.DevSendcmdUntil('exit', '#',False)
                for roudi_res_cleani in roudi_res_clean:
                    self.logWriter(log_path_showc2,roudi_res_cleani)
                for roudi_resi in roudi_res:
                    self.logWriter(log_path_showc,roudi_resi)
                print(u'提示：当前可安全终止检测任务')
                time.sleep(int(timeStep))
        except KeyboardInterrupt:#接收到键盘ctrl+c
            self.DevSendcmdUntil('exit','#')#退出单盘的bcmshell
            print(u'提示:检测到键盘终止信号,退出bcm shell---'+self.ip)
    def bcmShellShowcThenRecord_2100(self,portNum,Tx_range='0-any',Rx_range='0-any',timeStep=5):#阈值表示的是正常范围。不在此范围内的会被记录.采集的时间间隔默认是5s一次
    #portNum='9_ge11,xe3;10_ge10,xe2'
        if not portNum:
            return
        import os,re
        Tx_range_list=Tx_range.split('-')
        Rx_range_list=Rx_range.split('-')
        minTx=Tx_range_list[0]
        maxTx=Tx_range_list[1]
        minRx=Rx_range_list[0]
        maxRx=Rx_range_list[1]
        self.DevSendcmdUntil('debug', '#',False)
        slot_num=portNum.split('_')[0]
        ck_port=portNum.split('_')[1]
        self.DevSendcmdWaitSomeTimes('slot '+str(slot_num),2,False)#进单盘
        self.DevSendcmdWaitSomeTimes('1',1,False)
        self.DevSendcmdWaitSomeTimes('1',1,False)
        self.DevSendcmdUntil('ena','#',False)
        self.DevSendcmdUntil('debug-hide 0906','#',False)#进入单盘debug下
        log_path_showc=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-result-log.txt'
        log_path_showc2=self.log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+self.ip+'-result-clean-log.txt'
        try:
            self.DevSendcmdUntil('bcmshell','>',False)
            while True:
                roudi_res=[]
                roudi_res_clean=[]
                #for sloti in portNum.split(';'):#槽位遍历-20181029-废弃，因为一个框只需在主槽查看所有信息
                
                res=self.DevSendcmdUntil('show c '+ck_port,'>',False)
                for resi in res.splitlines():#单槽位端口遍历
                    #RPKT.ge26               :         6,319,014,831              +5,106           1,000/s
                    resi_l=resi.split()#根据空格分割，正常的数据应该有5列['RPKT.ge26', ':', '6,319,014,831', '+5,106', '1,000/s']
                    for porti in ck_port.split(','):
                        rPort='RBYT.'+porti
                        tPort='TBYT.'+porti
                        if (rPort in resi)or(tPort in resi):
                            roudi_res.append(self.ip+' '+resi)
                            if len(resi_l)==5:
                                PortSpeed=resi_l[-1].split('/')[0]
                            else:
                                PortSpeed='N/A'
                            roudi_res_clean.append(self.ip+'|'+resi_l[0]+'|'+str(PortSpeed))#20181029新增，只记录速度
                #self.DevSendcmdUntil('exit','#',False)
                #self.DevSendcmdUntil('exit','#',False)#返回至2100的debug
                for roudi_res_cleani in roudi_res_clean:
                    self.logWriter(log_path_showc2,roudi_res_cleani)
                for roudi_resi in roudi_res:#将本次结果写入log
                    self.logWriter(log_path_showc,roudi_resi)
                print(u'提示：当前可安全终止检测任务')
                time.sleep(int(timeStep))
        except KeyboardInterrupt:#接收到键盘ctrl+c
            self.DevSendcmdUntil('exit','#')#退出单盘的bcmshell
            print(u'提示:检测到键盘终止信号,退出bcm shell---'+self.ip)


def doTaskSingle(devIp,portNum_list,devTpye='8600II'):#8600II/2100
    devInstance=DevClass(devIp)#实例化设备
    if str(devTpye)=='8600II':
        devInstance.bcmShellShowcThenRecord_2U(portNum_list,timeStep=3)#portNum_list格式'ge6,xe5'
    elif str(devTpye)=='2100':
        devInstance.bcmShellShowcThenRecord_2100(portNum_list,timeStep=3)#portNum_list格式'9_ge11,xe3;10_ge23'
    else:
        return
def doTaskMutil(devIP_port):#devIP_port的格式:devTpye,devIP-portlist#devTpye,devIP-portlist其中2100的portlist格式是slot_portlist,slot_portlist...
    #'8600II,192.166.35.3-xe3,ge26,ge34#2100,10.10.1.15-9_ge11,xe3;10_ge23'
    devIP_port_list=devIP_port.split('#')
    for curListLeni in devIP_port_list:
        devTpyei=curListLeni.split('-')[0].split(',')[0]
        devIpi=curListLeni.split('-')[0].split(',')[1]
        devPortListi=curListLeni.split('-')[1]
        p = multiprocessing.Process(target=doTaskSingle, args=(devIpi,devPortListi,devTpyei,))
        print(devIpi+':start do job')
        p.start()

def doTaskSingleDev2(devIP,taskList,bigLoopTimes=0):#'整机重启','主盘复位','备盘复位','清除倒换','强制倒换','人工倒换','等待主备同步'
    import os,time
    log_path=r'F:\py_ftp_download\peopleCanRestButDevCannot\\'
    flog_str=log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-'+devIP+'-LOOP-log.txt'
    devInstance=DevClass(devIP)
    taskList_list=taskList.split('->')
    bigLoopTimesCounter=1#大循环计数器
    while True:
        for taskList_listi in taskList_list:
            print(u'当前大循环次数：'+str(bigLoopTimesCounter))
            taskName=taskList_listi.split('_')[0]
            taskTime=taskList_listi.split('_')[1]
            if taskName==u'整机重启':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'resetAll-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    devInstance.resetAll()
            elif taskName==u'主盘复位':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'resetMaster-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    haSynce=devInstance.haSwitch('resetMaster')
                    if not haSynce:#同步异常
                        os.system('pause')
                        print(u'检测到同步异常，退出无限循环！')
                        return
            elif taskName==u'备盘复位':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'resetSlave-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    devInstance.haSwitch('resetSlave')
            elif taskName==u'清除倒换':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'clear-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    haSynce=devInstance.haSwitch('clear')
                    if not haSynce:#同步异常
                        os.system('pause')
                        print(u'检测到同步异常，退出无限循环！')
                        return
            elif taskName==u'锁定':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'lock-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    devInstance.haSwitch('lock')
                    
            elif taskName==u'强制倒换':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'force-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    haSynce=devInstance.haSwitch('force')
                    if not haSynce:#同步异常
                        os.system('pause')
                        print(u'检测到同步异常，退出无限循环！')
                        return
            elif taskName==u'人工倒换':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'manual-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    haSynce=devInstance.haSwitch('manual')
                    if not haSynce:#同步异常
                        os.system('pause')
                        print(u'检测到同步异常，退出无限循环！')
                        return
            elif taskName==u'等待主备同步':
                for i in range(int(taskTime)):
                    devInstance.logWriter(flog_str,'waitForSynce-'+str(bigLoopTimesCounter)+'-'+str(i+1))
                    haSynce=devInstance.haSwitch('waitForSynce')
                    if not haSynce:#同步异常
                        os.system('pause')
                        print(u'检测到同步异常，退出无限循环！')
                        return
            else:
                print(u'当前版本不支持该操作：'+taskName)
        if bigLoopTimesCounter==bigLoopTimes:
            print(devIP+u'---已达到指定执行次数：'+str(bigLoopTimesCounter)+u',任务结束')
            break
        bigLoopTimesCounter=bigLoopTimesCounter+1

def portMaps(devTpye,portNum_list):#8600II/2100
    iTN2100_snmp2sdk_slot9dict={'22': '26', '02': '03', '03': '16', '26': '25', '27': '20', '06': '02', '07': '17', '04': '07', '23': '11', '08': '05', '09': '21', '28': '10', '29': '00', '24': '12', '25': '13', '01': '14', '20': '24', '21': '27', '11': '22', '10': '09', '13': '18', '12': '06', '15': '15', '14': '08', '17': '28', '16': '04', '19': '23', '18': '29', '05': '19'}
    iTN2100_sdk2bcm_slot9dict={'24': 'ge22', '25': 'ge23', '26': 'xe0', '27': 'xe1', '20': 'ge18', '21': 'ge19', '22': 'ge20', '23': 'ge21', '28': 'xe2', '29': 'xe3', '3': 'ge1', '2': 'ge0', '5': 'ge3', '4': 'ge2', '7': 'ge5', '6': 'ge4', '9': 'ge7', '8': 'ge6', '11': 'ge9', '10': 'ge8', '13': 'ge11', '12': 'ge10', '15': 'ge13', '14': 'ge12', '17': 'ge15', '16': 'ge14', '19': 'ge17', '18': 'ge16'}
class GenerateSpyPort_UI(Frame):
    global window
    window=Tk()
    def __init__(self,master=None):
        Frame.__init__(self,master)
        curDir=os.getcwd()#os.path.abspath('.')
        self.MainDir=curDir+r'\py_ftp_download'
        print('workSpace:'+self.MainDir)
        self.conf_path=self.MainDir+r'\configDir_guiguang'
        self.conf_fresh_dev=self.conf_path+'\\'+'DevList_fresh.txt'
        self.conf_history_dev=self.conf_path+'\\'+'DevList_'+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'.txt'
        self.CreatepyddDir()
        self.pack()
        self.createWidgets()
    def addDevIpToList(self):
        DevIP=self.DevAddDevEntry.get().strip()
        DevIP_Mask=self.DevAddEntry2.get().strip()
        try:
            DevTpye=self.DevOPlistListbox.get(self.DevOPlistListbox.curselection()).strip()
            if not DevIP:
                tkMessageBox.showinfo('Message',u'设备ip为空！')
            elif not DevIP_Mask:
                tkMessageBox.showinfo('Message',u'设备端口为空！')
            elif not DevTpye:
                tkMessageBox.showinfo('Message',u'请选择设备类型！(左键单击选中一项)')
            else:
                self.DevListText.insert('end','\n'+DevTpye+','+DevIP+'-'+DevIP_Mask)
                self.defaultIp.set('')#clear ip entry
                self.defaultIpMask.set('')#clear mask entry
        except Exception as e:
            tkMessageBox.showinfo('Message',u'请选择设备类型！(左键单击选中一项)')



    def DownloadFileThroughTelnet(self):
        DevList=self.DevListText.get('1.0','end')
        DevList_clear_raw=DevList.encode('utf8').strip().split('\n')#['ip;mask;daiwai','ip;mask;dainei'....]
        DevList_clear_raw_str='#'.join(DevList_clear_raw)
        print(DevList_clear_raw_str)

        if (len(DevList_clear_raw_str)>0):
            #myTask2=multiprocessing.Process(target=telnetDownload.downloadSvcfileMulti_forGUI,args=(DevList_clear,CardList_clear,FtpSet,resetAllOption,))
            #myTask2.daemon=False#设置为非守护进程
            myTask3=threading.Thread(target=doTaskMutil,args=(DevList_clear_raw_str,))
            myTask3.daemon=False#设置为非守护线程
            time.sleep(1)
            #myTask2.start()
            myTask3.start()
            #myTask3.join()
            #downloadState=telnetDownload.downloadSvcfileMulti_forGUI(DevList_clear,CardList_clear,FtpSet,resetAllOption)
            #tkMessageBox.showinfo('Message',downloadState)

    def UpLoadDevConfig(self):
        DevList=self.DevListText.get('1.0','end')
        DevList_clear_raw=DevList.encode('utf8').strip().split('\n')#['ip;mask;daiwai','ip;mask;dainei'....]
        DevList_str_raw=''
        for DevList_clear_rawi in DevList_clear_raw:
            if DevList_clear_rawi:
                DevList_str_raw+=DevList_clear_rawi.split(';')[0]+','
        telnetDownload.upLoadConfig_mutil(DevList_str_raw)
        
    def openUpgradeLogDir(self):
        os.system(r'start F:\py_ftp_download\peopleCanRestButDevCannot\\')
    
    def CreatepyddDir(self):
        if not os.path.isdir(self.MainDir):
            os.mkdir(self.MainDir)
        if not os.path.isdir(self.conf_path):
            os.mkdir(self.conf_path)

    def saveDevList(self):#save ftp setting too
        if os.path.isfile(self.conf_fresh_dev):
            os.remove(self.conf_fresh_dev)
        print('save DevList into:'+self.conf_fresh_dev)
        if not self.DevListText.get('1.0','end'):#当前列表为空则不覆盖
            return
#open
        conf_fresh_writer=open(self.conf_fresh_dev,'a+')
        conf_history_writer=open(self.conf_history_dev,'a+')
#write
        conf_fresh_writer.write(self.DevListText.get('1.0','end'))
        conf_history_writer.write(self.DevListText.get('1.0','end'))
#close
        conf_fresh_writer.close()
        conf_history_writer.close()
    def loadDevList(self):
        if os.path.isfile(self.conf_fresh_dev):#text exist
        # load dev list
            self.DevListText.delete(1.0,'end')#clear 
            conf_fresh_reader=open(self.conf_fresh_dev,'a+')
            self.DevListText.insert('end',conf_fresh_reader.read())
            conf_fresh_reader.close()
        else:
            if py3:
                tkinter.messagebox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)
            else:
                tkMessageBox.showinfo('Message',u'未找到配置:'+self.conf_fresh_dev)

    def createWidgets(self):
        self.Menubar=Menu(self)
        self.fileMenu=Menu(self.Menubar,tearoff=0)
        self.Menubar.add_cascade(label=u'工具配置管理',menu=self.fileMenu)
        self.fileMenu.add_command(label=u'保存当前列表',command=self.saveDevList)
        self.fileMenu.add_command(label=u'加载上次列表',command=self.loadDevList)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=u'退出',command=self.quit)
        window.config(menu=self.Menubar)
#============add device to list
        self.DevAddDeviceLabel_Father=Label(self,width=100,height=3)#width=15, height=5
        self.DevAddDeviceLabel_Father.pack(side=TOP,expand='no',anchor='nw')
        self.DevAddLabel0=Label(self.DevAddDeviceLabel_Father,text=u'设备类型(单击选中):',width=15,height=1)#width=15, height=5
        self.DevAddLabel0.pack(side=TOP,expand='no')
        self.DevOPListStr=StringVar()
        self.DevOPlistListbox=Listbox(self.DevAddDeviceLabel_Father,listvariable=self.DevOPListStr,width=20,height=2)
        self.DevOPListStr.set((' '*12+'8600II',' '*12+'2100'))
        #self.DevOPlistListbox.bind('<Double-Button-1>',self.addOPIntoTempList)
        self.DevOPlistListbox.pack(side=TOP,expand='no')
        self.DevAddDevLabel=Label(self.DevAddDeviceLabel_Father,text=u'设备IP地址:',width=15,height=1)#width=15, height=5
        self.DevAddDevLabel.pack(side=TOP,expand='no')
        self.defaultIp = StringVar()
        self.DevAddDevEntry=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIp)
        self.DevAddDevEntry.pack(side=TOP,expand='no')
        self.DevAddLabel2=Label(self.DevAddDeviceLabel_Father,text=u'监测端口列表(用英文,隔开):',width=25,height=1)#width=15, height=5
        self.DevAddLabel2.pack(side=TOP,expand='no')
        self.defaultIpMask = StringVar()
        self.DevAddEntry2=Entry(self.DevAddDeviceLabel_Father,textvariable = self.defaultIpMask)
        self.defaultIpMask.set('')
        self.DevAddEntry2.pack(side=TOP,expand='no')
        self.addDevButton=Button(self.DevAddDeviceLabel_Father,text=u'添加至监测设备列表',command=self.addDevIpToList)
        self.addDevButton.pack(side=TOP,expand='no')
#============device list
        self.DevListLabel=Label(self.DevAddDeviceLabel_Father,width=75,height=5)#width=15, height=5
        self.DevListLabel.pack(side=LEFT,expand='no',anchor='nw')
        self.DevListLabel_top=Label(self.DevListLabel,text=u'监测设备及端口列表',font=('Arial', 12),width=30,height=1)#width=15, height=5
        self.DevListLabel_top.pack()
        self.DevListText=Text(self.DevListLabel,width=30,height=21)
        self.DevListText.pack()

#============Run
        self.RunButton=Button(self.DevListLabel,text=u'开始监测',width=13,height=2,command=self.DownloadFileThroughTelnet)
        self.RunButton.pack(side=TOP)
        self.RunButton=Button(self.DevListLabel,text=u'打开log文件夹',width=13,height=2,command=self.openUpgradeLogDir)
        self.RunButton.pack(side=TOP)
if __name__=='__main__':
    multiprocessing.freeze_support()
    #log_path=r'F:\py_ftp_download\peopleCanRestButDevCannot\\'
    #flog_str=log_path+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'-result-log.txt'
    #a=DevClass('192.168.23.51',15)
    #a.DevLogin()
    #a.bcmShellShowcThenRecord_2U('xe2,ge26')
    #doTaskMutil('8600II,192.168.23.51-xe3,ge26,ge34#8600II,192.168.23.52-xe2,ge34')
    #doTaskMutil('8600II,10.68.250.227-ge6,xe5#8600II,10.68.250.229-ge20,xe0,xe3#8600II,10.68.250.242-ge27,xe0,xe1#8600II,10.68.250.226-xe1#2100,10.105.255.22-10_ge21,xe3#2100,10.105.255.24-9_ge22;10_xe0')#现网-II和21
    #a=DevClass('10.10.1.15',15)
    #a.bcmShellShowcThenRecord_2100('9_ge11,xe3;10_ge23',flog_str)
    #doTaskMutil('2100,10.10.1.15-9_ge11,xe3;10_ge23#2100,10.10.1.13-9_ge23,xe3')
    app=GenerateSpyPort_UI()
    app.master.title(u'端口流量记录工具')
    app.master.geometry('450x650')
    app.mainloop()

else:
    multiprocessing.freeze_support()
