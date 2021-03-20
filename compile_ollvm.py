#!/usr/bin/env python36
# -*- coding: utf-8 -*-
# File              : compile_gcc.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.01.14
# Last Modified By  : taotao <taotao@myhexin.com>

import os
import time

os.environ['PATH'] = r"D:\python36_GScopeGUI\scripts;" + os.environ['PATH']

# os.system(r'D:\python36_GScopeGUI\scripts\pyinstaller -y --key ths@123 --distpath d:\build\compile --icon .\test\126.ico .\test\aaa.py')

cmd = (
    r"d:\python36_GScopeGUI\python py2lib.py "
    r"-d .\test "
    r"-o d:\test "
    r"-c config_ollvm.ini "
    r"-m aaa.py "
    r"-e .ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
)
print(cmd)
os.system(cmd)



# cmd = (
#     r"d:\python36_GScopeGUI\python py2lib.py "
#     r"-S "
#     r"-d d:\test "
#     r"-o D:\build\compile\aaa "
#     r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
# )
# print(cmd)
# os.system(cmd)
