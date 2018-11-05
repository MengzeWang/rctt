#-*- encoding: utf-8 -*-
import os
import sys 
sys.path.append("..") 
import xiushiqi_test
path='D:\py_ftp_download\doc_based_download\iTN8600-V-NTU_SYSTEM_7.7.0_20180320\iTN8600-V-NTU_SYSTEM_7.7.0_20180320\\'
target_filename='iTN8600-V-NTU_SYSTEM_7.7.0_20180320.rar'
'''print os.getcwd()
print os.path.abspath('.')
print os.path.abspath(__file__)
print os.path.dirname(os.path.abspath(__file__))



def abcd(location_info=None):

    if location_info:
        print('UsingFunction:%s location is:%s' %(sys._getframe().f_code.co_name,os.path.abspath(__file__)))

class abc():
    def abcde(self,location_info=None):

        if location_info:
            print('UsingFunction:%s location is:%s' %(sys._getframe().f_code.co_name,os.path.abspath(__file__)))
abcd(location_info=0)
a=abc()
a.abcde(location_info=0)

@xiushiqi_test.printFuncLocation
def cba():
    pass

cba()'''
print os.path.isfile(path+target_filename)
print os.path.getsize(path+target_filename)