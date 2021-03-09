#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : compile_cl_pyd.py
# Author            : taotao
# Date              : 2021.01.08
# Last Modified Date: 2021.01.11
# Last Modified By  : taotao

import os

os.environ['PATH'] = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\HostX64\x64" + ';' + os.environ['PATH']
os.system(
    r"python py2lib.py "
    r"-d C:\Work\Projects\py2lib "
    r"-o C:\Users\taotao\Desktop\test "
    r"-c config_cl.ini "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
    r"-k 2"
)
