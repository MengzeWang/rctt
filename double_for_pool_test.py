from multiprocessing import Pool
import os,time,random




def print_aaa(a):
    time.sleep(random.random() * 3)
    print(a+'b')
    print('child process %s.' % os.getpid())

def muti_p1(a1,a2):

    print('Parent process %s.' % os.getpid())
    a12=''
    for a1_i in a1:
        p=Pool(4)
        for a2_j in a2:
            a12=a1_i+a2_j
            p_pool=p.apply_async(print_aaa, args=(a12,))
        p.close()
        p.join()


if __name__=='__main__':#attention:must use this way to run function,otherwise will occur weird loop print and cmd will die,if not ctrl+c ,and your computer also will also die
    a3=['a6','a7']
    a4=['a8','a9']
    muti_p1(a3,a4)

