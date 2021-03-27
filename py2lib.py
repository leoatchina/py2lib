#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : py2lib.py
# Author            : taotao
# Date              : 2021.01.07
# Last Modified Date: 2021.03.27
# Last Modified By  : leoatchina <leoatchina@outlook.com>

import re
import os, sys
import getopt
import shutil
import logging
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# seed is for cypher seed
seed = '0x' + datetime.today().strftime('%Y%m%d')
chs_regex = "[\u4e00-\u9fa5]"

all_imports = []
all_pyfiles = []

def WINDOWS():
    return sys.platform.startswith('win')

def run_cmd(cmd):
    try:
        ret = os.system(cmd)
    except Exception as e:
        print('================================')
        print('The command ' + cmd + ' not work')
        print(e)
        print('================================')
        return 1
    return ret

def check_in_exclude_list(filename, exclude_list):
    if os.sep in filename:
        base_name = os.path.basename(filename)
        if check_in_exclude_list(base_name, exclude_list):
            return True
    if filename in exclude_list:
        return True
    _, file_ext = os.path.splitext(filename)
    if file_ext in exclude_list:
        return True
    return False


def trim_pyfile(pyfile, wrtfile = None):
    """trim a pyfile """
    docstring_found = False
    if WINDOWS():
        lines = ["# -*- coding: gbk -*-\n"]
        encoding = 'gbk'
    else:
        lines = ["# -*- coding: utf-8 -*-\n"]
        encoding = 'utf8'

    global all_imports

    pyfile_imports = []
    with open(pyfile, 'r', encoding= 'utf8') as fp:
        continue_import = True
        for line in fp.readlines():
            line_strip = line.strip()
            if docstring_found:
                if r"'''" in line_strip:
                    docstring_found = False
                continue
            if r"'''" in line_strip:
                docstring_found = True
                continue
            if line_strip == '' or line_strip.startswith("#"):
                continue
            # 去除chinese
            line = re.sub(chs_regex, '', line)
            lines.append(line)

            if continue_import:
                if line_strip.startswith('import '):
                    line_strip = re.sub(r"\s{2,}", " ", line_strip)
                    line_strip = line_strip.split("as")[0].strip()
                    line_strip = line_strip.replace("import ", "").replace(" ", "")
                    import_raw = line_strip.replace(" ", "").replace("import", "").split(",")
                    pyfile_imports.extend(import_raw)
                elif line_strip.startswith("from "):
                    line_strip = re.sub(r"\s{2,}", " ", line_strip.replace("from ", ''))
                    pkg_import = line_strip.split(" ")[0]
                    targets    = line_strip.split(" ")[2]
                    # NOTE if one python file conatins 'from xxx import *', this file will not be compile to pyd
                    if r"*" in targets:
                        pyfile_imports  = []
                        convert_to_pyd  = False
                        continue_import = False
                    else:
                        targets = targets.replace(" ", '').split(",")
                        # pyfile_imports.append(pkg_import.split(r".")[0])
                        pyfile_imports.extend([pkg_import + "." + target for target in targets])

    # 没有找到python脚本
    if len(lines) <= 1:
        print(pyfile + ' has no workable python script!')
        return

    if wrtfile is None:
        wrtfile = pyfile

    with open(wrtfile, 'w') as fp:
        fp.writelines(lines)

    if pyfile_imports:
        for each in pyfile_imports:
            if each in all_imports:
                pass
            else:
                all_imports.append(each)

def sync_dirs(source_dir, target_dir, exclude_list = [], overwrite_file = False, rm_target_dir = True, sync_pyd = False):
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
    except Exception:
        pass
    if os.path.isdir(target_dir) and rm_target_dir:
        shutil.rmtree(target_dir, ignore_errors = True)
    os.makedirs(target_dir, exist_ok = True)
    for filename in os.listdir(source_dir):
        if check_in_exclude_list(filename, exclude_list):
            continue
        source = source_dir + os.sep + filename
        target = target_dir + os.sep + filename
        if os.path.isdir(source):
            if not os.path.exists(target):
                print('mkdir %s' % os.path.abspath(target))
                os.makedirs(target, exist_ok = True)
            sync_dirs(source, target, exclude_list, rm_target_dir = False)
        else:
            if sync_pyd and not source.endswith(r'pyd'):
                continue
            if overwrite_file:
                pass
            elif not os.path.exists(target):
                pass
            elif os.path.isfile(target):
                if os.path.getsize(target) == os.path.getsize(source):
                    continue
            else:
                continue
            shutil.copy(source, target_dir)


def confuse(c_source_file):
    '''
    对cython转换出来的c文件进行进一步的正则替换
    目的是为了不被强行调用时，爆出execption的详细情况
    '''
    with open(c_source_file, 'r') as fp:

        lines = fp.readlines()

    with open(c_source_file, 'w') as fp:
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
                fp.write(r" / * %s.py:0\n * /\n" % pyfile_noext)
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


def compile_file(pyfile_noext, template, compile_to_library = True, level = 0, print_cmd = False):
    '''
    pyfile_noext is the path of the py file without .py surfix
    it with compile to c_file and compile to .so  or .dll file
    '''
    try:
        # cython to c file
        if compile_to_library:
            cmd = '{python} -m cython -3 {pyfile_noext}.py -D'.format(pyfile_noext = pyfile_noext, python = python)
        else:
            cmd = '{python} -m cython -3 {pyfile_noext}.py --embed -D'.format(pyfile_noext = pyfile_noext, python = python)
        ret = run_cmd(cmd)
        if ret > 0:
            raise Exception('python file to c file with cython failed')
        # 再混淆加密，XXX 但是现在暂时用不到
        if (level % 2) == 1:
            confuse(pyfile_noext + '.c')
        # 把c 编译成so或者dll或者可执行
        # NOTE seed is a global value
        if level > 5:
            if compile_to_library:
                print('Completed %s.py to library, and keep all temp files and py file' % pyfile_noext)
            else:
                print('Completed %s.py to execute, and keep all temp files and py file' % pyfile_noext)

        cmd = template.format(pyfile_noext = pyfile_noext, seed = seed)
        if level > 3 and print_cmd:
            print(cmd)
        ret = run_cmd(cmd)

        if ret > 0:
            if compile_to_library:
                raise Exception('Compile c file to dynamic link file failed')
            else:
                raise Exception('Compile c file to executable failed')
        # 在windows下，把.dll文件转.pyd
        # 有些情况下，用ollvm转dll会不成功，命令是对的，重启能解决问题。
        if WINDOWS() and os.path.exists(pyfile_noext + ".dll") and compile_to_library:
            # print(pyfile_noext + ".dll")
            os.system("move {pyfile_noext}.dll {pyfile_noext}.pyd".format(pyfile_noext = pyfile_noext))
        # linux，change tarcget to 755
        elif not WINDOWS() and not compile_to_library and os.path.exists(pyfile_noext):
            os.system('chmod 755 ' + pyfile_noext)

        ############ delete temprary files
        temp_file_ext = ['.pyc', '.cpp', '.o', '.c', '.exp', '.obj', '.lib']

        if level > 3:
            if compile_to_library:
                print('Completed %s.py to library, and keep all temp files and py file' % pyfile_noext)
            else:
                print('Completed %s.py to execute, and keep all temp files and py file' % pyfile_noext)
        else:
            if level > 1:
                if compile_to_library:
                    print('Completed %s.py to library, and keep py file' % pyfile_noext)
                else:
                    print('Completed %s.py to execute, and keep py file' % pyfile_noext)
            else:
                if compile_to_library:
                    print('Completed %s.py to library, and delete all temp files' % pyfile_noext)
                else:
                    print('Completed %s.py to execute, and delete all temp files' % pyfile_noext)
                temp_file_ext.append('.py')

            files_to_remove = [pyfile_noext + ext for ext in temp_file_ext]
            for each_file in files_to_remove:
                try:
                    os.remove(each_file)
                except Exception:
                    pass

    except Exception as e:
        print('========================')
        try:
            print(cmd)
        except Exception:
            print("no command")
        print('========================')
        raise(e)


def file_to_library(pyfile_noext, template, level = 0):
    compile_file(pyfile_noext, template, compile_to_library = True, level = level)

def file_to_execute(pyfile_noext, template, level = 0):
    compile_file(pyfile_noext, template, compile_to_library = False, level = level)


# TODO, add delete_list to delete the unnecessary files or dirs during compile stage.
def dir_to_librarys(output_dir, library_template, level = 0, mdir_list = [], mfile_list = []):
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

            pyfile_noext = each_file.split('.')[0]
            pyfile_noext = os.path.join(root, pyfile_noext)
            pyfile       = os.path.join(root, each_file)
            ######### compile
            if each_file.endswith('.py'):
                trim_pyfile(pyfile)
                file_to_library(pyfile_noext, library_template, level)



if __name__ == '__main__':
    help_show = '''
py2lib is tool to change the .py to .so or .pyd, you can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2lib needs the environment of python3 with cython installed

Usage: python py2lib.py [options] ...

Options:
  -h, --help        Show the help info
  -x, --execute     Compile to executable file
  -s, --sync        Sync only
  -S, --syncpyd     Sync pyd only
  -c, --commandcfg  Set the command template config file, must be offered if not sync_only
  -f, --file        Single file, -f supervised -d when offered at same time
  -d, --directory   Directory of your project (if use -d, you change the whole directory)
  -o, --output      Directory to store the compile results, must be different to source_dir
  -m, --maintain    The files you don't want to compile from py to library file
                    example: -m __init__.py,setup.py
  -M, --maintaindir like maintain, but dirs
  -e, --exclude     Directories or files that you do not want to sync to output dir.
                    __pycache__, .vscode, .git, .idea, .svn will always not be synced
  -l, --level       level == 5 confuse c file, keep temp files and py file
                    level == 4 not confuse c file, keep temp files and py file
                    level == 3 confuse c file, keep py file only
                    level == 2 not confuse c file, keep py file only
                    level == 1 confuse c file, not keep temp files
                    level == 0 not confuse c file, not keep temp files
  -D, --delete      Files, dirs foreced to delete in the output_dir
  -p, --python      Python executable file, default python
  -i, --imports     Pyinstaller hidden import

example:
  python py2lib.py -d test_dir -o target_dir -m __init__.py,setup.py -c config.ini
    '''

    ############ basic ########################
    level         = 0
    to_library    = True
    source_file   = ''
    source_dir    = ''
    commandcfg    = ''
    output_dir    = './output'
    sync_only     = False
    sync_pyd      = False
    rm_target_dir = True
    python        = "python"
    pyinst_imports = []
    ############ list #######################
    delete_list  = []
    exclude_list = []
    mdir_list    = []
    mfile_list   = []
    ########### template ########################
    library_template = ''
    execute_template = ''
    pyinst_command = ''

    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hxsSkp:c:f:d:o:m:M:e:l:D:",
            ["help", "execute", "sync", "sync_pyd", "keep" \
             "python=", "commandcfg=", "file=", "directory=", "output=", "maintain=", "maintaindir=", "exclude=", "level=", "delete="]
        )
    except Exception as e:
        print('get options error', e)
        print(help_show)
        sys.exit(1)

    for key, value in options:
        if key in ['-h', '--help']:
            print(help_show)
            sys.exit(0)
        elif key in ['-i', '--imports']:
            pyinst_imports = value.replace(' ', '').split(",")
        elif key in ['-p', '--python']:
            python = value
        elif key in ['-x', '--execute']:
            to_library = False
        elif key in ['-s', '--sync']:
            sync_only = True
        elif key in ['-S', '--syncpyd']:
            sync_only = True
            sync_pyd  = True
        elif key in ['-k', '--keep']:
            rm_target_dir = False
        elif key in ['-c', '--commandcfg']:
            commandcfg = value
        elif key in ['-f', '--file']:
            source_file = value
        elif key in ['-o', '--output']:
            output_dir = value
        elif key in ['-d', '--directory']:
            source_dir = value
        elif key in ['-e', '--exclude']:
            exclude_list = value.split(",")
        elif key in ['-l', '--level']:
            level = int(value)
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
    exclude_list = list(set(['.gitignore', '.git', '.svn', '.root', '.vscode', '.idea', '__pycache__', '.task', '.vim', '.gitlab-ci.yml', '.pyc'] + exclude_list))

    ############# source_dir
    if len(source_dir) > 0 and source_dir[-1] == r'/':
        source_dir = source_dir[-1]

    ######## output_dir
    if len(output_dir) > 0 and output_dir[-1] == r'/':
        output_dir = output_dir[-1]

    if os.path.abspath(source_dir) == os.path.abspath(output_dir):
        print("Source dir equals output dir!")
        sys.exit(1)
    if sync_only:
        if os.path.isfile(source_file):
            if not sync_pyd or sync_pyd and source_file.endswith(r'.pyd'):
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                shutil.copy(source_file, output_dir)
        elif os.path.isdir(source_dir):
            if sync_pyd:
                sync_dirs(source_dir, output_dir, exclude_list, rm_target_dir = False, sync_pyd = True)
            else:
                sync_dirs(source_dir, output_dir, exclude_list, rm_target_dir = rm_target_dir)
    elif os.path.isfile(commandcfg):
        # check the template
        with open(commandcfg) as fp:
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                if line != '':
                    if line.startswith("library_template"):
                        library_template = r"=".join(line.split(r'=')[1:]).strip()
                    elif line.startswith("execute_template"):
                        execute_template = r"=".join(line.split(r'=')[1:]).strip()
                    elif line.startswith("pyinst_command"):
                        pyinst_command = r"=".join(line.split(r'=')[1:]).strip()

        if library_template == '' and to_library:
            raise Exception("Please check the commandcfg if library_template exists")
        elif execute_template == '' and not to_library:
            raise Exception("Please check the commandcfg if execute_template exists")

        ############# XXX do compile
        if os.path.isfile(source_file):
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            shutil.copy(source_file, output_dir)
            pyfile_noext = os.path.join(output_dir, os.path.basename(source_file)).replace(r'.py', '')
            # NOTE file可能会编译成library或者executable
            if to_library:
                file_to_library(pyfile_noext, library_template, level)
            else:
                file_to_execute(pyfile_noext, execute_template, level)
        elif os.path.isdir(source_dir):
            sync_dirs(source_dir, output_dir, exclude_list, rm_target_dir = rm_target_dir)
            # NOTE 只会全部编译成library
            dir_to_librarys(output_dir, library_template, level, mdir_list, mfile_list)
        else:
            print('neither source file nor source dir offered, please check!!!')
    # if not command file offered, raise the exception
    else:
        raise Exception("Please check the commandcfg exists")
    if pyinst_command:
        all_imports.extend(pyinst_imports)
        if all_imports and r"{hidden}" in pyinst_command:
            # print(all_imports)
            hidden_import = " --hidden-import=" + " --hidden-import=".join(all_imports)
        else:
            hidden_import = ""
        cmd = pyinst_command.format(hidden = hidden_import)
        logger.info(cmd)
        print(cmd)
        os.system(cmd)

