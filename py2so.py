#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : py2so.py
# Author            : leoatchina <leoatchina@outlook.com>
# Date              : 2021.01.07
# Last Modified Date: 2021.01.07
# Last Modified By  : leoatchina <leoatchina@outlook.com>

import re
import os
import sys
import getopt
import random
import string


def is_windows():
    return sys.platform.startswith('win')

def run_cmd(cmd):
    try:
        ret = os.system(cmd)
    except Exception as e:
        return e
    return ret

def transfer(file_noext, py_ver, lib_dir, keep = 0, delete_suffix = []):
    '''
    file_noext is the absolute path of the py file, without .py surfix
    it with compile to file_noext.c and compile to .so  or .dll file
    '''
    try:
        # cython to cpp
        cmd = 'cython -{py_ver} {file_noext}.py --cplus -D'.format(py_ver = py_ver, file_noext = file_noext)
        ret = run_cmd(cmd)

        # strip cpp file
        if ret == 0:
            # keep == 3   不对c 混淆，保留中间文件
            # keep == 2   对c 混淆，保留中间文件
            # keep == 1   不对c 混淆，不保留中间文件
            # keep == 0,  对c 混淆，不保留中间文件
            if keep % 2 == 1:
                pass
            else:
                with open('%s.cpp' % file_noext, 'r') as fp:
                    lines = fp.readlines()

                with open('%s.cpp' % file_noext, 'w') as fp:
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

        else:
            raise Exception('cython failed')

        # 把cpp 编译成so或者dll
        if ret == 0:
            if is_windows():
                cmd_template = "{clang} "
            else:
                cmd_template = "{clang} {file_noext}.cpp -fPIC -shared -I{lib_dir} `python{py_ver}-config --ldflags` -o {file_noext}.so -mllvm -fla"

            cmd = cmd_templete.format(clange = clang, py_ver = py_ver, file_noext = file_noext, lib_dir = lib_dir)
            ret = run_cmd(cmd)
        else:
            raise Exception('failed to replace strings in cpp files!')

        # tell if completed
        if ret == 0:
            if keep > 1:
                print('Completed %s, and keep the temp files' % file_noext)
            else:
                os.system('rm -f {file_noext}.py {file_noext}.cpp {file_noext}.o {file_noext}'.format(file_noext = file_noext))
                print('Completed %s, and deleted the temp files' % file_noext)
        else:
            raise Exception('Compile cpp to dynamic link file failed')

    except Exception as e:
        print('========================')
        print(cmd)
        print('========================')
        raise(e)

if __name__ == '__main__':
    help_show = '''
py2so is tool to change the .py to .so, you can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2so needs the environment of python2

Usage: python py2so.py [options] ...

Options:
  -h, --help          Show the help info
  -p, --py            Python version, default value is 3
                      Example: -p 2  (means you use python2)
  -l, --lib           python libray for compile, must be offered
  -f, --file          single file, -f supervised -d when offered at same time
  -d, --directory     Directory of your project (if use -d, you change the whole directory)
  -o, --output        Directory to store the compile results, default "./output"
  -e, --exclude       Directories or files that you do not want to sync to output file
                      dirs __pycache__, .vscode, .git, .idea will always not be synced
  -m, --maintain      list the file you don't want to transfer from py to so
                      example: -m __init__.py,setup.py
  -M, --maintaindir   like maintain, but dirs
  -D, --delete        files, dirs foreced to delete
  -k, --keep          if keep the compiled .c .o files, or do confuse the c file

example:
  python py2so.py -d test_dir -m __init__.py,setup.py
    '''
    keep         = 0
    py_ver       = '3'
    lib_dir      = ''
    source_dir   = ''
    origin_file  = ''
    output_dir   = './output'
    delete_list  = []
    exclude_list = []
    skipdir_list = []
    skipfil_list = []
    try:
        options, args = getopt.getopt(sys.argv[1:],
                "hp:l:f:o:d:m:M:e:k:D:",
                ["help", "py=", "lib=", "file=", "output=", "directory=", "maintain=", "maintaindir=", "exclude=", "keep=", "delete="])
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
        elif key in ['-f', '--file']:
            origin_file = value
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
            skipfil_list = value.split(",")
        # 要保留的dir
        elif key in ['-M', '--maintaindir']:
            tmp_list = value.split(",")
            for d in tmp_list:
                if d.startswith(r"./"):
                    d = d[2:]
                if d.endswith(r"/"):
                    d = d[:-1]
                skipdir_list.append(d)
    exclude_list = list(set(['.gitignore', '.git', '.svn', '.root', '.vscode', '.idea', '__pycache__', '.task'] + exclude_list))
    exclude_str = " --exclude=" + " --exclude=".join(exclude_list)
    # sys.exit(0)

    if lib_dir[-1] == r'/':
        lib_dir = lib_dir[:-1]

    if not os.path.isdir(lib_dir):
        print('lib_dir must be given, useing -l or --lib')
        sys.exit(1)
    try:
        if source_dir[-1] == r'/':
            source_dir = source_dir[-1]
    except Exception:
        pass

    if output_dir[-1] == r'/':
        output_dir = output_dir[-1]

    if os.path.abspath(source_dir) == os.path.abspath(output_dir):
        print("Source dir equals output dir!")
        sys.exit(1)

    if py_ver not in ['2', '3']:
        print('python version must be 2 or 3')
        sys.exit(1)

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # use rsync to transfer
        if origin_file:
            if not os.path.isfile(origin_file):
                print('No such File %s, please check or use the Absolute Path' % origin_file)
                sys.exit(1)
            try:
                os.system('cp %s %s' % (origin_file, output_dir))
                target_path = os.path.join(output_dir, os.path.basename(origin_file)).replace(r'.py', '')
                transfer(target_path, py_ver, lib_dir, keep)
            except Exception as e:
                raise e
        elif source_dir:
            if not os.path.exists(source_dir):
                print('No such Directory %s, please check or use the Absolute Path' % source_dir)
                sys.exit(1)
            rsync_cmd = 'rsync -azP --size-only %s --delete %s/ %s/' % (exclude_str, source_dir, output_dir)
            os.system(rsync_cmd)
            try:
                for root, dirs, files in os.walk(output_dir):
                    if root in skipdir_list or os.path.basename(root) in skipdir_list:
                        continue

                    for d in dirs:
                        if d in exclude_list or os.path.join(root, d) in exclude_list or os.path.join(os.path.basename(root), d) in exclude_list:
                            os.system('rm -rf %s' % os.path.join(root, d))

                    for fil in files:
                        if fil in skipfil_list or os.path.join(root, fil) in skipfil_list or os.path.join(os.path.basename(root), fil) in skipdir_list:
                            continue
                        elif fil in exclude_list:
                            os.system('rm -f %s' % os.path.join(root, fil))

                        pref = fil.split('.')[0]
                        file_noext = root + '/' + pref
                        if delete_list:
                            suffix = fil.split(r'.')[-1]
                            if suffix in delete_list:
                                os.system('rm -f %s' % os.path.join(root, fil))


                        # delete pyc which is easily to reverse
                        if fil.endswith('.pyc') or fil in exclude_list:
                            os.system('rm -f %s' % os.path.join(root, fil))
                        elif fil.endswith('.py'):
                            transfer(file_noext, py_ver, lib_dir, keep)
            except Exception as err:
                if 'ollvm' in str(err):
                    sys.exit(1)
                raise(err)
            else:
                print('%s to %s finished' % (source_dir, output_dir))
