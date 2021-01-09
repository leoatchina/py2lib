#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : py2so.py
# Author            : taotao
# Date              : 2021.01.07
# Last Modified Date: 2021.01.09
# Last Modified By  : taotao

import re
import os
import sys
import getopt
import random
import string
import shutil


def is_windows():
    return sys.platform.startswith('win')

def run_cmd(cmd):
    try:
        ret = os.system(cmd)
    except Exception as e:
        return 1
    return ret

def inexclude_list(filename, exclude_list):
    if os.sep in filename:
        base_name = os.path.basename(filename)
        if inexclude_list(base_name, exclude_list):
            return True

    if filename in exclude_list:
        return True

    file_noext, file_ext = os.path.splitext(filename)
    if file_ext in exclude_list:
        return True

    return False

def sync_dirs(source_dir, output_dir, exclude_list = [], del_output = True):
    '''
    同步source_dir 和 targe_dir, 并排除exclude_list
    exclude_list 由basename, 以及相应的后缀组成
    '''
    if os.path.basename(source_dir) in exclude_list:
        return
    if os.path.abspath(source_dir) in exclude_list:
        return
    try:
        if r"." + os.path.split(r".")[1] in exclude_list:
            return
    except Exception as e:
        pass

    if os.path.isdir(output_dir) and del_output:
        shutil.rmtree(output_dir, ignore_errors = True)
        os.makedirs(output_dir, exist_ok = True)
    else:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

    for filename in os.listdir(source_dir):
        if inexclude_list(filename, exclude_list):
            continue

        file_s = source_dir + os.sep + filename
        file_t = output_dir + os.sep + filename
        if os.path.isdir(file_s):
            if not os.path.exists(file_t):
                print('mkdir %s' % os.path.abspath(file_t))
                os.makedirs(file_t, exist_ok = True)
            sync_dirs(file_s, file_t, exclude_list, del_output = False)
        else:
            with open(file_s,'rb') as f_s:
                with open(file_t,'wb') as f_t:
                    print('copy %s to %s' % (file_s, file_t))
                    f_t.write(f_s.read())


def trasfer_to_dynamic(file_noext, lib_dir, compile_template, keep = 0, delete_suffix = []):
    '''
    file_noext is the absolute path of the py file without .py surfix
    it with compile to file_noext.c and compile to .so  or .dll file
    '''
    try:
        # cython to cpp
        cmd = 'cython -3 {file_noext}.py -D'.format(file_noext = file_noext)
        ret = run_cmd(cmd)

        if ret > 0:
            raise Exception('cython to cpp file failed')
        # keep == 3   对cpp进一步替换，保留中间文件
        # keep == 2   不对cpp进一步替换，保留中间文件
        # keep == 1   对cpp进一步替换，不保留中间文件
        # keep == 0,  不对cpp进一步替换，不保留中间文件
        if (keep % 2) == 1:
            with open('%s.c' % file_noext, 'r') as fp:
                lines = fp.readlines()
            with open('%s.c' % file_noext, 'w') as fp:
                re_PYX_ERR = r'__PYX_ERR\(\d+,\s*\d+,(\s*\w+)\)'
                re_PYX_ERR_if = r';\s*if[\s\S]+__PYX_ERR[\S\s]*\n'
                found_pyx_err_define = False
                for line in lines:
                    if line.startswith('#define'):
                        fp.write(line)
                        if '__PYX_ERR' in line and not found_pyx_err_define:
                            found_pyx_err_define = True
                    elif found_pyx_err_define and line.strip == '':
                        # 写入一个假的行
                        found_pyx_err_define = False
                        fp.write(r" / * %s.py:0\n * /\n" % file_noext)
                    elif line.startswith(r' * '):
                        pass
                    elif re.search(re_PYX_ERR, line):
                        if re.search(re_PYX_ERR_if, line):
                            line = re.sub(re_PYX_ERR_if, ';\n', line)
                        else:
                            words = re.search(re_PYX_ERR, line).group(1)
                            line = re.sub(re_PYX_ERR, r'__PYX_ERR(0, 0, %s)' % words, line)
                        fp.write(line)
                    else:
                        fp.write(line)
        # 把cpp 编译成so或者dll
        cmd = compile_template.format(file_noext = file_noext, lib_dir = lib_dir)
        ret = run_cmd(cmd)

        # tell if completed
        if ret > 0:
            raise Exception('Compile cpp to dynamic link file failed')
        else:
            if keep > 1:
                print('Completed %s, and keep the temp files' % file_noext)
            else:
                remove_list = [file_noext + ext for ext in ['.py', '.pyc', '.cpp', '', '.o', '.c']]
                for each in remove_list:
                    try:
                        os.remove(each)
                    except Exception as e:
                        pass
                print('Completed %s, and deleted the temp files' % file_noext)

    except Exception as e:
        print('========================')
        print(cmd)
        print('========================')
        raise(e)


def compile(source, output_dir, compile_template, keep = 0, mdir_list = [], mfile_list = []):
    '''

    '''
    if os.path.isfile(source):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.system('cp %s %s' % (source, output_dir))
        target_path = os.path.join(output_dir, os.path.basename(source)).replace(r'.py', '')
        trasfer_to_dynamic(target_path, lib_dir, compile_template, keep)
    else:
        sync_dirs(source, output_dir, exclude_list)

        for root, dirs, files in os.walk(output_dir):
            if root in mdir_list or os.path.basename(root) in mdir_list:
                continue

            for each_file in files:
                if each_file in mfile_list or \
                        os.path.join(root, each_file) in mfile_list or \
                        os.path.join(os.path.basename(root), each_file) in mfile_list:
                    continue

                file_noext = each_file.split('.')[0]
                file_noext = root + os.sep + file_noext
                if delete_list:
                    suffix = each_file.split(r'.')[-1]
                    if suffix in delete_list:
                        os.system('rm -f %s' % os.path.join(root, each_file))

                # delete pyc which is easily to reverse
                if each_file.endswith('.pyc'):
                    os.system('rm -f %s' % os.path.join(root, each_file))
                elif each_file.endswith('.py'):
                    trasfer_to_dynamic(file_noext, lib_dir, compile_template, keep)

if __name__ == '__main__':
    help_show = '''
py2so is tool to change the .py to .so, you can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2so needs the environment of python2

Usage: python py2so.py [options] ...

Options:
  -h, --help          Show the help info
  -c, --commandfile   Set the command template file
  -l, --lib           python libray for compile, must be offered
  -f, --file          single file, -f supervised -d when offered at same time
  -d, --directory     Directory of your project (if use -d, you change the whole directory)
  -o, --output        Directory to store the compile results, default "./output"
  -e, --exclude       Directories or files that you do not want to sync to output dir.
                      __pycache__, .vscode, .git, .idea, .svn will always not be synced
  -m, --maintain      list the file you don't want to trasfer_to_dynamic from py to dynamic link file
                      example: -m __init__.py,setup.py
  -M, --maintaindir   like maintain, but dirs
  -k, --keep          if keep the compiled .c .o files, or do confuse the c file
  -D, --delete        files, dirs foreced to delete in the output_dir

example:
  python py2so.py -d test_dir -m __init__.py,setup.py
    '''

    keep        = 0
    lib_dir     = ''
    source_file = ''
    source_dir  = ''
    output_dir  = ''

    delete_list  = []
    exclude_list = []
    mdir_list    = []
    mfile_list   = []


    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hc:l:f:d:o:m:M:e:k:D:",
            ["help", "commandfile=", "lib=", "file=", "directory=", "output=", "maintain=", "maintaindir=", "exclude=", "keep=", "delete="]
        )
    except getopt.getopterror:
        print('get options error')
        print(help_show)
        sys.exit(1)

    for key, value in options:
        if key in ['-h', '--help']:
            print(help_show)
            sys.exit(0)
        elif key in ['-l', '--lib']:
            lib_dir = value
        elif key in ['-c', '--compilefile']:
            commandfile = value
        elif key in ['-f', '--file']:
            source_file = value
        elif key in ['-o', '--output']:
            output_dir = value
        elif key in ['-d', '--directory']:
            source_dir = value
        elif key in ['-e', '--exclude']:
            exclude_list = value.split(",")
        elif key in ['-k', '--keep']:
            try:
                keep = int(value)
            except Exception:
                keep = 0
        elif key in ['-D', '--delete']:
            delete_list = value.split(",")
        # 要保留的file
        elif key in ['-m', '--maintain']:
            mfile_list = value.split(",")
        # 要保留的dir
        elif key in ['-M', '--maintaindir']:
            tmp_list = value.split(",")
            for d in tmp_list:
                if d.startswith(r"./"):
                    d = d[2:]
                if d.endswith(r"/"):
                    d = d[:-1]
                mdir_list.append(d)
    exclude_list = list(set(['.gitignore', '.git', '.svn', '.root', '.vscode', '.idea', '__pycache__', '.task'] + exclude_list))

    ##########  python library dir
    if len(lib_dir) and lib_dir[-1] == r'/':
        lib_dir = lib_dir[:-1]
    if not os.path.isdir(lib_dir):
        print('lib_dir must be given, useing -l or --lib')
        sys.exit(1)
    ############# source_dir
    if len(source_dir) > 0 and source_dir[-1] == r'/':
        source_dir = source_dir[-1]

    ######## output_dir
    if len(output_dir) > 0 and output_dir[-1] == r'/':
        output_dir = output_dir[-1]

    if os.path.abspath(source_dir) == os.path.abspath(output_dir):
        print("Source dir equals output dir!")
        sys.exit(1)
    ###### commandfile
    if "commandfile" in globals() and os.path.isfile(commandfile):
        with open(commandfile) as fp:
            lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if line != '':
                compile_template = line
                break
        if "compile_template" not in globals():
            raise Exception("Please check the commandfile", commandfile)
    else:
        if is_windows():
            compile_template = "cl.exe {file_noext}.c -fPIC -shared -I{lib_dir} `python3-config --ldflags` -o {file_noext}.dll -mllvm -fla"
        else:
            compile_template = ""

    ###### 最终要compile
    if os.path.isdir(source_dir):
        compile(source_dir, output_dir, compile_template, keep, mdir_list, mfile_list)
    elif os.path.isfile(source_file):
        compile(source_file, output_dir, compile_template, keep)
