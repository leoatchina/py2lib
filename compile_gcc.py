#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : compile_gcc.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.01.14
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r"d:\mingw\bin" + ';' + os.environ['PATH']

cmd = (
    r"d:\Anaconda3\python py2lib.py "
    r"-d .\check "
    r"-o D:\test "
    r"-c config_gcc.ini "
    r"-m aaa.py "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
)
print(cmd)
os.system(cmd)

cmd = (
    r"d:\Anaconda3\python py2lib.py "
    r"-f .\check\aaa.py "
    r"-x "
    r"-o D:\test "
    r"-c config_gcc.ini "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
    r"-k 2"
)
print(cmd)
os.system(cmd)
