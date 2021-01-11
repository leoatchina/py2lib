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
        print(e)
        return 1
    return ret

def inexclude_list(filename, exclude_list):
    if os.sep in filename:
        base_name = os.path.basename(filename)
        if inexclude_list(base_name, exclude_list):
            return True

    if filename in exclude_list:
        return True

    _, file_ext = os.path.splitext(filename)

    if file_ext in exclude_list:
        return True

    return False

def sync_dirs(source_dir, target_dir, exclude_list = [], del_output = True):
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

    if os.path.isdir(target_dir) and del_output:
        shutil.rmtree(target_dir, ignore_errors = True)

    os.makedirs(target_dir, exist_ok = True)

    for filename in os.listdir(source_dir):
        if inexclude_list(filename, exclude_list):
            continue

        file_s = source_dir + os.sep + filename
        file_t = target_dir + os.sep + filename
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


def compile_file(path_noext, template, to_library = True, keep = 0):
    '''
    path_noext is the path of the py file without .py surfix
    it with compile to path_noext.cpp and compile to .so  or .dll file
    '''
    try:
        # cython to cpp
        cmd = 'cython -3 {path_noext}.py --cplus -D'.format(path_noext = path_noext)
        ret = run_cmd(cmd)

        if ret > 0:
            raise Exception('python file to cpp file with cython failed')

        if (keep % 2) == 1:
            with open('%s.cpp' % path_noext, 'r') as fp:
                lines = fp.readlines()
            with open('%s.cpp' % path_noext, 'w') as fp:
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
                        fp.write(r" / * %s.py:0\n * /\n" % path_noext)
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
        # 把cpp 编译成so或者dll或者可执行
        cmd = template.format(path_noext = path_noext)
        ret = run_cmd(cmd)

        if ret > 0:
            if to_library:
                raise Exception('Compile cpp to dynamic link file failed')
            else:
                raise Exception('Compile cpp to executable failed')
        # 对文件作一些修改
        if is_windows() and os.path.exists(path_noext + ".dll") and to_library:
            os.system("move {path_noext}.dll {path_noext}.pyd".format(path_noext = path_noext))
        elif not is_windows and not to_library and os.path.exists(path_noext):
            os.system('chmod 755 ' + path_noext)

        ############ delete temprary files
        if keep > 1:
            print('Completed %s, and keep the temp files' % path_noext)
        else:
            remove_list = [path_noext + ext for ext in ['.py', '.pyc', '.cpp', '.o', '.c', '.exp', '.obj', '.lib']]
            for each in remove_list:
                try:
                    os.remove(each)
                except Exception:
                    pass
            print('Completed %s, and has deleted the temp files' % path_noext)

    except Exception as e:
        if "cmd" in globals():
            print('========================')
            print(cmd)
            print('========================')
        else:
            print('======== no command ============')
        raise(e)


def file_to_library(path_noext, library_template, keep = 0):
    compile_file(path_noext, library_template, to_library = True, keep = keep)

def file_to_execute(path_noext, execute_template, keep = 0):
    compile_file(path_noext, library_template, to_library = False, keep = keep)



# TODO, add delete_list
def dir_to_librarys(output_dir, library_template, keep = 0, mdir_list = [], mfile_list = []):
    '''
    把原始的source，可能是file, 可能是dir， 同步到output_dir，并且根据library_template把py转成libray
    library_template: 写有转换模板里的文件里读出的转换模板语句
    mdir_list: 不要转的文件夹列表
    mfile_list:  不要转的文件列表
    '''
    for root, _, files in os.walk(output_dir):
        if root in mdir_list or os.path.basename(root) in mdir_list:
            continue

        for each_file in files:
            if each_file in mfile_list or \
                    each_file.startswith(r".") or \
                    os.path.join(root, each_file) in mfile_list or \
                    os.path.join(os.path.basename(root), each_file) in mfile_list:
                continue

            path_noext = each_file.split('.')[0]
            path_noext = root + os.sep + path_noext
            ######### compile
            if each_file.endswith('.py'):
                file_to_library(path_noext, library_template, keep)


if __name__ == '__main__':
    help_show = '''
py2so is tool to change the .py to .so or .pyd, you can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2so needs the environment of python2

Usage: python py2so.py [options] ...

Options:
  -h, --help          Show the help info
  -c, --commandfile   Set the command template file, must be offered
  -f, --file          single file, -f supervised -d when offered at same time
  -d, --directory     Directory of your project (if use -d, you change the whole directory)
  -o, --output        Directory to store the compile results, must be different to source_dir
  -m, --maintain      list the file you don't want to compile from py to library file
                      example: -m __init__.py,setup.py
  -M, --maintaindir   like maintain, but dirs
  -e, --exclude       Directories or files that you do not want to sync to output dir.
                      __pycache__, .vscode, .git, .idea, .svn will always not be synced
  -k, --keep          keep == 3 confuse cpp file, keep temp files
                      keep == 2 not confuse cpp file, keep temp files
                      keep == 1 confuse cpp file, not keep temp files
                      keep == 0 not confuse cpp file, not keep temp files
  -D, --delete        files, dirs foreced to delete in the output_dir

example:
  python py2so.py -d test_dir -m __init__.py,setup.py
    '''

    ############ basic ########################
    keep        = 0
    source_file = ''
    source_dir  = ''
    output_dir  = ''
    commandfile = ''
    ############ list #######################
    delete_list  = []
    exclude_list = []
    mdir_list    = []
    mfile_list   = []
    ########### template ########################
    library_template  = ''
    execute_template = ''

    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hc:f:d:o:m:M:e:k:D:",
            ["help", "commandfile=", "file=", "directory=", "output=", "maintain=", "maintaindir=", "exclude=", "keep=", "delete="]
        )
    except getopt.getopterror:
        print('get options error')
        print(help_show)
        sys.exit(1)

    for key, value in options:
        if key in ['-h', '--help']:
            print(help_show)
            sys.exit(0)
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
            keep = int(value)
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
    if os.path.isfile(commandfile):
        with open(commandfile) as fp:
            lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if line != '':
                if line.startswith("library_template"):
                    library_template = line.split(r'=')[1].strip()
                elif line.startswith("execute_template"):
                    execute_template = line.split(r'=')[1].strip()

    if library_template == '':
        raise Exception("Please check the commandfile")

    ###### 最终要compile
    ########## TODO  编译executable file
    if os.path.isfile(source_file):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.system('cp %s %s' % (source_file, output_dir))
        path_noext = os.path.join(output_dir, os.path.basename(source_file)).replace(r'.py', '')
        if execute_template != '':
            file_to_execute(path_noext, execute_template, keep)
        else:
            file_to_library(path_noext, library_template, keep)
    elif os.path.isdir(source_dir):
        sync_dirs(source_dir, output_dir, exclude_list)
        dir_to_librarys(output_dir, library_template, keep, mdir_list, mfile_list)
