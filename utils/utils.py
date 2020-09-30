import shlex
import subprocess
import numpy as np


def get_console_output(raw_command, r=True, w=False):
    p = subprocess.Popen(shlex.split(raw_command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if r is True and w is False:
        return stdout.decode().strip("\n") if p.returncode == 0 else "Error\n" + stderr.decode().strip("\n")
    if w is True and r is False:
        return "successfully applied" if bool(p.returncode) is False else stderr.decode().strip("\n")


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def func_getter(_func, *args, **kwargs):
    return _func(*args, **kwargs)


list = []

"""
args [var1's value, var2's value, ...]
kwargs {"var1" : $(var1's value), "var2" : $(var2's value)...}
lambda_list [(lambda x,y:x+y) <-- for var1, lambda for var2, ...]
lambda_dict {"var1" : (lambda for var1), "var2" : (lambda for var2), ...}
==========================================================================
func :: function
func(  lambda_list[0](args[0]), lambda_list[1](args[1]),  ..)
func(  lambda_dict[kwargs[key]](kwargs[key]) , ..  )
==========================================================================
product_list
[var1  ]
product_dict
==========================================================================
for 문 
변수에 람다 적용한 뒤 func 호출
func() 
"""


def within_iteration(_func, iter_num, args_list, start=0, step=1, lambda_list=None, lambda_dict=None,
                     **args_dict):
    for i in range(start, iter_num, step):
        _func(*args_list, **args_dict)
        for idx, val in enumerate(args_list):
            args_list[idx] = lambda_list[idx](val)
        for key, val in args_dict.items():
            args_dict[key] = lambda_dict[key](val)


def temp(x, y, *args, **kwargs):
    print(x)
    print(y)
    print(args)
    print(kwargs)


if __name__ == '__main__':
    within_iteration(temp, 5, lambda_list=[(lambda x: x ** 2), (lambda y: y * 3)], args_list=[2, 4])
