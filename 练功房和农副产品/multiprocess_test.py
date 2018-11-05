from multiprocessing import Process
import os

def run_proc(name,name2):
    tr=['1','2','3','4','5','6','7','8','9','10']
    f=open(name+'.txt','a+')
    #print 'Run child process %s (%s)...\n' % (name, os.getpid())
    for i in tr:
        print('Run child process %s%s (%s) (%s)...\n' % (name, name2,os.getpid(),i))
        f.write('Run child process %s%s (%s) (%s)...\n' % (name, name2,os.getpid(),i))
    f.close()

if __name__=='__main__':
    print 'Parent process %s.' % os.getpid()
    p = Process(target=run_proc, args=('test','test',))
    p2 = Process(target=run_proc, args=('test2','test2',))
    p3 = Process(target=run_proc, args=('test3','test3',))
    print 'Process will start.'
    p.start()
    p2.start()
    p3.start()
    p.join()
    p2.join()
    p3.join()
    print 'Process end.'