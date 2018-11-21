import inspect
def printFuncLocation(func):
    def wrapped():
        print('******UsingFunction:%s location is:%s******' %(func.__name__,inspect.getsourcefile(func)))
        return func()
    return wrapped

if __name__!='__main__':
    print('haha')