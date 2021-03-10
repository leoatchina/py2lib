#!/usr/bin/env python36
# -*- coding: utf-8 -*-
# File              : compile_gcc.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.01.14
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r"D:\python36_GScopeGUI\scripts;d:\obfuscator-6.0-mingw-win32\bin" + ';' + os.environ['PATH']

cmd = (
    r"d:\python36_GScopeGUI\python py2lib.py "
    r"-d .\test "
    r"-o D:\test "
    r"-c config_ollvm.ini "
    r"-m aaa.py "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
)
print(cmd)
os.system(cmd)

os.system(r'D:\python36_GScopeGUI\scripts\pyinstaller --key ths@123 --distpath d:\test\compile --icon d:\test\126.ico d:\test\aaa.py -y')
