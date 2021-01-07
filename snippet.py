#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : snippet.py
# Author            : leoatchina <leoatchina@outlook.com>
# Date              : 2021.01.07
# Last Modified Date: 2021.01.07
# Last Modified By  : leoatchina <leoatchina@outlook.com>

# 这个文件里的代码体来是用 c代码宏去进一步进行加密，没能搞定


########################### c代码宏 ######################################################
keyword_list = ['cout','+=','-=','int ','goto','asm', 'do', 'if','[',']',
                'return', 'typedef', 'auto', 'double', 'inline','{','}',
                'short', 'typeid', 'bool', 'int ','(',')',
                'signed', 'typename', 'break', 'else','&gt;=','&lt;=',
                'sizeof', 'union', 'case', 'enum', 'mutable',';',
                'static', 'unsigned', 'catch', 'explicit', 'try',
                'namespace', 'using', 'char','main','const',
                'export', 'new', 'struct', 'class', 'switch',
                'false', 'private', 'long','::', 'void','endl',
                'float', 'protected', 'this', 'continue','++','--',
                'for', 'public', 'throw', 'while', 'default', 'friend',
                 'true','&lt;&lt;','cin','printf','==','&gt;&gt;','!=',]


def random_char():
    r = chr(random.randint(97,122))
    char,char_r,list_chr = [],[],[]
    for i in range(len(keyword_list)):
        char.append(r+str(i))
        char_r.append(keyword_list[i])
    random.shuffle(char)
    random.shuffle(char_r)
    for i in range(len(char)):
        list_chr.append([char[i],char_r[i]])
    return list_chr

def generate_define(list_chr):
    define = []
    for i in range(len(list_chr)):
        define.append('#define '+ list_chr[i][0] +' '+list_chr[i][1])
    return define

def replace(list_char, str, confusion):
    if confusion == ' /**/ ':
        confusion = ' /*' + ''.join(random.sample(string.hexdigits,6)) +'*/ '
    for i in list_char:
        if i[1] in str:
            str = str.replace(i[1],confusion+i[0]+confusion)
    return str

def obscure_file(filename, list_char):
    # confusion = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    # confusion = ' /*' + confusion + '*/ '
    with open(filename,'r') as f:
        with open(filename + ".temp.cpp", 'w') as m:
            define = generate_define(list_char)
            for i in define:
                m.write(i+'\n')
            for i in f.readlines():
                if '#' in i[0]:
                    m.write(i + '\n')
                    continue
                i = i.strip()
                m.write(i + '\n')
    os.system('rm %s' % filename)
    os.system('mv %s %s' % (filename + ".temp.cpp", filename))

