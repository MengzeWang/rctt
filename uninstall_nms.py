#-*- encoding: utf8 -*-
__author__ = 'MengZe'
import os
import re
env_dist=os.environ
env_Path=env_dist.get('Path')
print env_Path
for x in env_Path.split(';'):
    print x
    nmp_path=re.match('(.*NNM5).*',x)
    if nmp_path:
        print 'nms_path:'+nmp_path.group(1)
        break
if nmp_path:
    os.chdir(os.path.join(nmp_path.group(1),'UnInstall'))
    print os.listdir('.')  
else:
    print 'not found nmp in os.environ'	