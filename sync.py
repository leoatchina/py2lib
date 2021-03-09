#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : sync.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.14
# Last Modified Date: 2021.01.14
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r"d:\mingw\bin" + ';' + os.environ['PATH']

cmd = (
    r"d:\python36\python py2lib.py "
    r"-s "
    r"-d .\test "
    r"-o d:\test "
)
print(cmd)
os.system(cmd)
