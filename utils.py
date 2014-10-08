import ctypes

match = (100,100)
xs = [10,54]
ys = [1,9]

arr = lambda x: (ctypes.c_int * len(x))(*x)


utils = ctypes.CDLL('utils.dylib')
ret = utils.checkNewPoint(arr(match),arr(xs),arr(ys),len(xs))
print ret