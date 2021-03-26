#!/usr/bin/env python36
# -*- coding: utf-8 -*-
# File              : compile_gcc.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.01.14
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r"d:\msys2\mingw64\bin" + ';' + os.environ['PATH']

cmd = (
    r"c:\tools\anaconda3\python py2lib.py "
    r"-p c:\tools\anaconda3\python "
    r"-d c:\work\projects\aes_cypher "
    r"-o c:\work\projects\aes_cypher_c "
    r"-c config_gcc.ini "
    r"-m aes_cypher_gui.py "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
)
print(cmd)
os.system(cmd)

# cmd = (
#     r"d:\python36\python py2lib.py "
#     r"-f .\test\aaa.py "
#     r"-x "
#     r"-o D:\test "
#     r"-c config_gcc.ini "
#     r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
# )
# print(cmd)
# os.system(cmd)
