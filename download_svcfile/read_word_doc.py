#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import win32com,re
from win32com.client import Dispatch,constants
#import downloadFlie_ftp2 as dlFf
import os,shutil
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def file_type_filter(filename_str):
    filename_str.replace('.','\.')
    not_intrerest_type=[r'.doc',r'.docx',r'.rar']
    for bad_file in not_intrerest_type:
        if re.match('.*'+bad_file+'$',filename_str):
            return None
    return filename_str
def strip_chinese_word(unicode_tpye_str):
    #print(unicode_tpye_str)
    #print('type(unicode_tpye_str):%s' %(type(unicode_tpye_str)))
    #unicode_tpye_str=unicode_tpye_str.decode('utf-8')
    unicode_tpye_str_new=u''
    for char_x_index in unicode_tpye_str:
        if u'\u4e00' <= char_x_index.decode('utf-8') <= u'\u9fff':
            print(u'drop out:'+char_x_index)
        elif char_x_index.decode('utf-8')==u' ':
            print(u'drop out:space')
        else:
            unicode_tpye_str_new=unicode_tpye_str_new+char_x_index
    return unicode_tpye_str_new
def right_arrow_right(str_input):#iTN8600-SH2E_B.0_U27_FPGA_1.5_20171219->\riTN8600-SH2E_B.0_U27_FPGA_1.6_20180109'
    str_input.decode('utf-8')
    str_arr=str_input.split(u'->\r')
    return str_arr[len(str_arr)-1]
def extract_version_from_doc(file_path,file_name):
    #filename_txt=r'D:\pyS\iTN8600-V-NXU_B_SYSTEM_7.6.24_20180206.txt'
    filenamein=file_path+'\\'+file_name+'.doc'
    filename_txt=filenamein[0:len(filenamein)-4]+r'.txt'
    word=win32com.client.Dispatch('word.application')
    word.displayalerts=0
    word.visible=0
    #countdoc=word.Documents.Count
    #print(countdoc)
    try:
        doc=word.Documents.Open(filenamein)
    except:
        print('Cannot find '+filenamein)
        return []
    t=doc.Tables[0]
    #t_number=doc.Tables.Count
    #r_table=t.rows
    #print('type(t):%s' %(type(t)))
    #print('table counts:%s' %(t_number))
    #print('table row counts:%s' %(r_table))
    #name = t.Cell(10,4).Range.Text
    #print('type(name):%s' %(type(name)))
    #print(str(name).decode('utf-8'))
    #doc.SaveAs(r'D:\pyS\test', 4)
    version_collect_arr=[]
    f=open(filename_txt,'a+')  
    for table_row_try in range(1,30):
        try:
            txt = t.Cell(table_row_try,4).Range.Text
            #print('%s,4:%s' %(table_row_try,str(txt).decode('utf-8'))
        except Exception as e:
            #print('invalid-row:%s' %(table_row_try))
            pass
        else:
            txt_name = t.Cell(table_row_try,3).Range.Text
            filetype_x=str(txt_name).decode('utf-8')
            filename_x=str(txt).decode('utf-8')
            #print(filetype_x)
            #print('(%s,4):%s\n' %(table_row_try,filename_x))
            if (filetype_x[0:len(filetype_x)-2]==u'FPGA')or(filetype_x[0:len(filetype_x)-2]==u'公司自主芯片'):
                filetype_x_only_eng=strip_chinese_word(filename_x[0:len(filename_x)-2])
                print(filetype_x_only_eng)
                #version_collect_arr.append(['FPGA:'+filename_x[0:len(filename_x)-2].encode('utf-8')])
                filetype_x_right=right_arrow_right(filetype_x_only_eng)
                #print('filetype_x_right')
                #print(filetype_x_right)
                version_collect_arr.append(['fpga:'+filetype_x_right.encode('utf-8')])
                f.write('fpga:'+filetype_x_right.encode('utf-8'))
                f.write('\n')
            elif (filetype_x[0:len(filetype_x)-2]==u'系统软件'):
                filetype_x_only_eng=strip_chinese_word(filename_x[0:len(filename_x)-2])
                print(filetype_x_only_eng)
                filetype_x_right=right_arrow_right(filetype_x_only_eng)
                version_collect_arr.append(['system-boot:'+filetype_x_right.encode('utf-8')])
                f.write('system-boot:'+filetype_x_right.encode('utf-8'))
                f.write('\n')
            elif (filetype_x[0:len(filetype_x)-2]==u'Bootrom'):
                filetype_x_only_eng=strip_chinese_word(filename_x[0:len(filename_x)-2])
                print(filetype_x_only_eng)
                filetype_x_right=right_arrow_right(filetype_x_only_eng)
                version_collect_arr.append(['bootrom:'+filetype_x_right.encode('utf-8')])
                f.write('bootrom:'+filetype_x_right.encode('utf-8'))
                f.write('\n')
    print  version_collect_arr
    f.close()       
    doc.Close()
    word.Quit()
    return version_collect_arr

def GetDoc_version(doc_path,wordfile_name,downloadTo_path,CardName=None):
    import downloadFlie_ftp2 as dlFf
    ftpServer_setting_path=r'D:\py_ftp_download'
    if not os.path.isdir(ftpServer_setting_path):
        os.mkdir(ftpServer_setting_path)
    if not os.path.isdir(downloadTo_path):
        os.mkdir(downloadTo_path)
    version_info=extract_version_from_doc(doc_path,wordfile_name)
    wanted_type='system-boot,bootrom,fpga'#fpga;system-boot;bootrom;
#==========
    ftp_serverip='172.16.1.182'
    timeout = 30  
    port = 21
    UserName='dev'
    PassWD='dev'
    #file_path=''
    local_path=downloadTo_path+'/'+wordfile_name+'/'
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    file_is_unique=1
    download_file_detail=[]
    download_file_brief=[]
    download_file_detail_for_telDwload=[]
    for wanted_type_i in wanted_type.split(','):
        if wanted_type_i=='fpga':
            file_path=['/test1_test2/iTN8600/hardware/','/test1_test2/FPGA/','/test1_test2/iTN8600/']
        else:
            file_path=['/test1_test2/iTN8600/software/','/test1_test2/iTN8600/']
        for version_info_i in version_info:
            if wanted_type_i==version_info_i[0].split(':')[0]:
                target_filename=version_info_i[0].split(':')[1]
                #print target_filename
                for file_path_sub in file_path:
                    if target_filename:
                        dld_result=dlFf.downloadFtpFile2(ftp_serverip,port,timeout,UserName,PassWD,file_path_sub,target_filename,file_is_unique,local_path)
                        if dld_result:
                            for dldt in dld_result:
                                if (dldt['result']=='success')and(file_type_filter(dldt['filename'])):
                                    download_file_detail.append([wanted_type_i,dldt['local_path']+'\\'+dldt['filename']])
                                    download_file_brief.append([wanted_type_i,dldt['filename']])#filename or unrar filename,maybe have garbage file
                                    if CardName:
                                        download_file_detail_for_telDwload.append([CardName,dldt['filename']+r'.'+wanted_type_i])
                            break
    result_show_for_GUI=''
    for download_file_detail_i in download_file_detail:
        print download_file_detail_i
        result_show_for_GUI=result_show_for_GUI+download_file_detail_i[1]+'\n\n\n\n'
        shutil.copy(download_file_detail_i[1],ftpServer_setting_path)
    if CardName:
        return [result_show_for_GUI,download_file_detail_for_telDwload,download_file_brief]
    else:
        return [result_show_for_GUI,download_file_brief]#[[bootrom,xxx.bin],[system-boot,xxx.z],[fpga,xxx.xxx],....]
        
#==========
    
if __name__ == '__main__':
    file_abspath=r'D:\py_ftp_download\test_doc_collect'
    file_nodoc_name='iTN8600-V-NXU_B_SYSTEM_7.6.24_20180206'
    version_info=extract_version_from_doc(file_abspath,file_nodoc_name)
    wanted_type='system-boot,bootrom,fpga'#fpga;system-boot;bootrom
#==========
    ftp_serverip='172.16.1.182'
    timeout = 30  
    port = 21
    UserName='dev'
    PassWD='dev'
    #file_path=''
    local_path='d:/py_ftp_download/doc_based_download/'+file_nodoc_name+'/'
    file_is_unique=1
    for wanted_type_i in wanted_type.split(','):
        if wanted_type_i=='fpga':
            file_path='/test1_test2/FPGA/'
        else:
            file_path='/test1_test2/iTN8600/software/'
        for version_info_i in version_info:
            print(version_info_i)
            if wanted_type_i==version_info_i[0].split(':')[0]:
                target_filename=version_info_i[0].split(':')[1]
                print target_filename
                dlFf.downloadFtpFile2(ftp_serverip,port,timeout,UserName,PassWD,file_path,target_filename,file_is_unique,local_path)
#==========