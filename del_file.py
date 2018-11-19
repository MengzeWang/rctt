#-*- encoding: utf8 -*-
import os,shutil
def del_file(path):
    ls = os.listdir(path)
    print('---',ls)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
            
#shutil.move("C:\\wmz1","D:\\wmz1")
def del_Dir(path):
    if os.path.isdir(path):
        ls = os.listdir(path)
    else:
        print(u'未找到文件夹:%s,退出function' %(path))
        return
    #print(u'当前文件夹包含内容---')
    #print(ls)
    if not ls:
        os.rmdir(path)
        return
    else:
        for i in ls:
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                try:
                    del_Dir(c_path)
                except Exception as e:
                    print(u'%s非空或无权限删除,尝试进入该文件夹' %(c_path))
                    del_Dir(c_path)
            else:
                try:
                    print(u'删除文件---'+c_path)
                    os.remove(c_path)
                except Exception as e:
                    print(u'删除文件%s出现错误，退出function' %(c_path))
                    return

    if os.path.isdir(path):
        print(u'删除文件夹---'+path)
        os.rmdir(path)
if __name__=='__main__':
    #del_file(CUR_PATH)
    CUR_PATH = "D:\\wmz1"
    del_Dir(CUR_PATH)
    #os.rmdir(CUR_PATH)