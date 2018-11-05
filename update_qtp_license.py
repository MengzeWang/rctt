import os
import re
rmdir_path='C:\Documents and Settings\All Users\Application Data\SafeNet Sentinel'
rmdir_path_win7='C:\ProgramData\SafeNet Sentinel'
instdemo=r'"C:\software1\HP_UFT\bin\instdemo.exe"'
env_dist=os.environ
env_Path=env_dist.get('Path')
for x in env_Path.split(';'):
    #print(x)
    qtp_path=re.match('(.*QTP).*',x)
    if qtp_path:
        print('qtp_match:'+qtp_path.group(0))
        print('qtp_path:'+qtp_path.group(1))
        break
def remove_dir(dir):
#    dir = dir.replace('\\', '/')
    if(os.path.isdir(dir)):
        for p in os.listdir(dir):
            remove_dir(os.path.join(dir,p))
        if(os.path.exists(dir)):
            os.rmdir(dir)
    else:
        if(os.path.exists(dir)):
            os.remove(dir)
if os.path.isdir(rmdir_path):
    #os.chdir(rmdir_path)
    #print(os.getcwd())
    remove_dir(rmdir_path)
    os.system(instdemo)
elif os.path.isdir(rmdir_path_win7):
    remove_dir(rmdir_path_win7)
    os.system(instdemo)
else:
    os.system(instdemo)