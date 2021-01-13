#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : compile_gcc.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.01.13
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r"d:\mingw\bin" + ';' + os.environ['PATH']

os.system(
    r"d:\Anaconda3\python py2so.py "
    r"-d C:\Work\Projects\py2so_ollvm "
    r"-o C:\Users\taotao\Desktop\test "
    r"-c config_gcc.ini "
    r"-m aaa.py "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
)

os.system(
    r"d:\Anaconda3\python py2so.py "
    r"-f C:\Work\Projects\py2so_ollvm\debug\aaa.py "
    r"-x "
    r"-o C:\Users\taotao\Desktop\test\debug "
    r"-c config_gcc.ini "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
    r"-k 2"
)
