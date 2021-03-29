#!/usr/bin/env python36
# -*- coding: utf-8 -*-
# File              : compile_ollvm.py
# Author            : taotao <taotao@myhexin.com>
# Date              : 2021.01.08
# Last Modified Date: 2021.03.29
# Last Modified By  : taotao <taotao@myhexin.com>

import os

os.environ['PATH'] = r'c:\python37;' + os.environ['PATH']

cmd = (
    r"c:\python37\python py2lib.py "
    r"-p c:\python37\python.exe "
    r"-d d:\work\projects\aes_cypher "
    r"-o d:\build\aes_cypher "
    r"-c config_ollvm.ini "
    r"-m aes_cypher_gui.py "
    r"-e test.py,.ini,.md,.txt,.sh,.lib,.obj,.so,.dll,.cmd,.bat,.exp "
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
