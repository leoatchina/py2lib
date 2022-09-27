#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : py2lib.py
# Author            : taotao
# Date              : 2021.01.07
# Last Modified Date: 2022.09.22
# Last Modified By  : taotao <taotao@myhexin.com>

from datetime import datetime
import getopt
import logging
import os
import re
import shutil
import sys


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# seed is for cypher seed
SEED = '0x' + datetime.today().strftime('%Y%m%d')
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
        return None
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
    else:
        lines = ["# -*- coding: utf-8 -*-\n"]
        # encoding = 'utf8'

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
                    line_strip = line_strip.split("as ")[0].strip()
                    line_strip = re.sub(r"\s{2,}", " ", line_strip)
                    import_raw = line_strip.replace("import ", "").split(",")
                    pyfile_imports.extend(import_raw)
                elif line_strip.startswith("from ") and "import " in line_strip:
                    try:
                        line_strip = re.sub(r"\s{2,}", " ", line_strip.split("as ")[0].replace(r")", "").replace(r"(", "").replace("from ", '')).strip()
                        pkg_import = line_strip.split(" ")[0]
                        targets    = line_strip.split("import ")[1].replace(" ", "")
                        # NOTE if one python file conatins 'from xxx import *', this file will not be compile to pyd
                        if r"*" in targets:
                            pyfile_imports.append(pkg_import)
                        else:
                            pyfile_imports.append(pkg_import)
                            targets = targets.replace(" ", "").split(",")
                            targets = [pkg_import + "." + target for target in targets]
                            pyfile_imports.extend(targets)
                    except Exception as e:
                        print(line_strip)
                        raise e

    # 没有找到python脚本
    if len(lines) <= 1:
        print(pyfile + ' has no workable python script!')
        return

    if wrtfile is None:
        wrtfile = pyfile

    with open(wrtfile, 'w') as fp:
        fp.writelines(lines)

    if pyfile_imports:
        for each_import in pyfile_imports:
            each_import = each_import.strip()
            if each_import in all_imports:
                pass
            else:
                try:
                    exec('import %s' % each_import)
                    all_imports.append(each_import)
                except Exception:
                    pass

def sync_dirs(source_dir, target_dir, exclude_list = [], overwrite_file = False, rm_target_dir = True):
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


def compile_file(pyfile_noext, template, b_py2lib = True, level = 0, print_cmd = False):
    '''
    pyfile_noext is the path of the py file without .py surfix
    it will be converted to c file and then compile to .so  or .dll file
    '''
    try:
        # cython to c file
        if b_py2lib:
            cmd = '{python} -m cython -3 {pyfile_noext}.py -D'.format(pyfile_noext = pyfile_noext, python = python)
        else:
            cmd = '{python} -m cython -3 {pyfile_noext}.py --embed -D'.format(pyfile_noext = pyfile_noext, python = python)
        ret = run_cmd(cmd)
        if ret is None:
            raise Exception('python file to c file with cython failed')

        # NOTE: 在奇数情况下,再混淆加密，但是现在暂时用不到
        if (level % 2) == 1:
            confuse(pyfile_noext + '.c')

        cmd = template.format(pyfile_noext = pyfile_noext, seed = SEED)
        if level > 3 and print_cmd:
            print(cmd)
        ret = run_cmd(cmd)

        if ret is None:
            if b_py2lib:
                raise Exception('Compile c file to dynamic link file failed')
            else:
                raise Exception('Compile c file to executable failed')

        # 在windows下，把.dll文件转.pyd
        if WINDOWS() and os.path.exists(pyfile_noext + ".dll") and b_py2lib:
            # NOTE: 有些情况下，用ollvm转dll会不成功，命令是对的，重启能解决问题。
            os.system("move {pyfile_noext}.dll {pyfile_noext}.pyd".format(pyfile_noext = pyfile_noext))
        # linux，change tarcget to 755
        else:
            if b_py2lib:
                os.system('chmod 644 ' + pyfile_noext + ".so")
            elif not b_py2lib and os.path.isfile(pyfile_noext):
                os.system('rm {}.so'.format(pyfile_noext))
                os.system('chmod 755 ' + pyfile_noext)

        # ########### delete temprary files
        temp_file_ext = ['.pyc', '.cpp', '.o', '.c', '.exp', '.obj', '.lib']

        if level > 3:
            if b_py2lib:
                print('Completed %s.py to library, and keep all temp files and py file' % pyfile_noext)
            else:
                print('Completed %s.py to execute, and keep all temp files and py file' % pyfile_noext)
        else:
            if level > 1:
                if b_py2lib:
                    print('Completed %s.py to library, and keep py file' % pyfile_noext)
                else:
                    print('Completed %s.py to execute, and keep py file' % pyfile_noext)
            else:
                if b_py2lib:
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
    if template is None:
        raise Exception('library_template is None')
    compile_file(pyfile_noext, template, b_py2lib = True, level = level)

def file_to_execute(pyfile_noext, template, level = 0):
    if template is None:
        raise Exception('execute_template is None')
    compile_file(pyfile_noext, template, b_py2lib = False, level = level)

# TODO, add delete_list to delete the unnecessary files or dirs during compile stage.
def dir_to_librarys(output_dir, library_template, level = 0, maintain_dirs = [], maintain_files = []):
    '''
    把原始的source，可能是file, 可能是dir， 同步到output_dir，并且根据library_template把py转成libray
    library_template: 写有转换模板里的文件里读出的转换模板语句
    maintain_dirs: 不要转的文件夹列表
    maintain_files:  不要转的文件列表
    '''
    for root, _, files in os.walk(output_dir):
        if root in maintain_dirs or os.path.basename(root) in maintain_dirs:
            continue

        for each_file in files:
            if each_file in maintain_files or \
                    each_file.startswith(r".") or \
                    os.path.join(root, each_file) in maintain_files or \
                    os.path.join(os.path.basename(root), each_file) in maintain_files:
                continue

            pyfile_noext = each_file.split('.')[0]
            pyfile_noext = os.path.join(root, pyfile_noext)
            pyfile       = os.path.join(root, each_file)
            # ######## compile
            if each_file.endswith('.py'):
                trim_pyfile(pyfile)
                file_to_library(pyfile_noext, library_template, level)



# MAIN
if __name__ == '__main__':
    help_show = '''
py2lib is tool to change the .py to .so or .pyd, you can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2lib needs the environment of python3 with cython installed

Usage: python py2lib.py [options] ...

Options:
  -h, --help        Show the help info
  -e, --execute     Compile to executable file
  -s, --sync        Sync only
  -c, --config      Set the compile template config file, must be offered if not sync_only
  -f, --file        Single file, -f supervised -d when offered at same time
  -d, --directory   Directory of your project (if use -d, you change the whole directory)
  -o, --output      Directory to store the compile results, must be different to source_dir
  -m, --maintain    The files you don't want to compile from py to library file
                    example: -m __init__.py,setup.py
  -M, --maintaindir like maintain, but dirs
  -x, --exclude     Directories or files that you do not want to sync to output dir.
                    __pycache__, .vscode, .git, .idea, .svn will always not be synced
  -l, --level       level == 5 confuse c files, keep c/o files and py file
                    level == 4 not confuse c files, keep c/o files and py file
                    level == 3 confuse c files, keep py files
                    level == 2 not confuse c files, keep py files
                    level == 1 confuse c files, not keep temp files
                    level == 0 not confuse c files, not keep temp files
  -D, --delete      Files, dirs foreced to delete in the output_dir
  -p, --python      Python executable file, default 'python'
  -i, --imports     hidden import, for pyinstaller/nuitka/etc.

example:
  python py2lib.py -d test_dir -o target_dir -m __init__.py,setup.py -c compile_template.ini
    '''

    # ########### basic ########################
    level         = 0
    py_lib_file   = None
    py_exe_file   = None
    source_dir    = None
    config        = None
    output_dir    = './output'
    sync_only     = False
    rm_target_dir = True
    python        = "python"
    # ########### list #######################
    delete_list  = []
    exclude_list = []
    maintain_dirs    = []
    maintain_files   = []
    # ########## template ########################
    library_template   = None
    execute_template   = None
    compile_command    = ''
    run_command        = ''
    addtional_commands = []

    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hskp:c:x:f:d:o:m:M:e:l:D:i:",
            ["help","sync", "keep",
             "python=", "config=", "file=", "execute=", "directory=", "output=", "maintain_files=", "maintain_dirs=", "exclude=", "level=", "delete=", "imports="]
        )
    except Exception as e:
        print('get options error', e)
        print(help_show)
        sys.exit(1)

    for key, value in options:
        if key in ['-h', '--help']:
            print(help_show)
            sys.exit(0)
        elif key in ['-s', '--sync']:
            sync_only = True
        elif key in ['-k', '--keep']:
            rm_target_dir = False
        elif key in ['-i', '--imports']:
            all_imports = value.replace(' ', '').split(",")
        elif key in ['-p', '--python']:
            python = value
        elif key in ['-e', '--execute']:
            py_exe_file = value
        elif key in ['-f', '--file']:
            py_lib_file = value
        elif key in ['-c', '--config']:
            config = value
        elif key in ['-o', '--output']:
            output_dir = value
        elif key in ['-d', '--directory']:
            source_dir = value
        elif key in ['-x', '--exclude']:
            exclude_list = value.split(",")
        elif key in ['-l', '--level']:
            level = int(value)
        elif key in ['-D', '--delete']:
            delete_list = value.split(",")
        # 要保留的file
        elif key in ['-m', '--maintain_files']:
            maintain_files = value.split(",")
        # 要保留的dir
        elif key in ['-M', '--maintain_dirs']:
            tmp_list = value.split(",")
            for d in tmp_list:
                if d.startswith(r"./"):
                    d = d[2:]
                if d.endswith(r"/"):
                    d = d[:-1]
                maintain_dirs.append(d)

    # clean maintain_files, exclude_list
    maintain_files = list(set(maintain_files))
    exclude_list = list(set(['.gitignore', '.git', '.svn', '.root', '.vscode', '.idea', '__pycache__', '.task', '.vim', '.gitlab-ci.yml', '.pyc'] + exclude_list))

    # source_dir and output_dir
    if len(source_dir) > 0:
        source_dir = re.sub(r"/+$", "", source_dir)

    if len(output_dir) > 0:
        output_dir = re.sub(r"/+$", "", output_dir)

    if os.path.abspath(source_dir) == os.path.abspath(output_dir):
        print("Source dir equals output dir!")
        sys.exit(1)

    # NOTE: main cause
    if sync_only:
        for source_file in [py_lib_file, py_exe_file]:
            if os.path.isfile(source_file):
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                shutil.copy(source_file, output_dir)
        if os.path.isdir(source_dir):
            sync_dirs(source_dir, output_dir, exclude_list, rm_target_dir=rm_target_dir)

    # Note, using config to create complile command
    elif os.path.isfile(config):
        with open(config) as fp:
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                if line != '':
                    if line.startswith("library_template"):
                        try:
                            library_template = r"=".join(line.split(r'=')[1:]).strip()
                        except Exception:
                            library_template = None
                    elif line.startswith("execute_template"):
                        try:
                            execute_template = r"=".join(line.split(r'=')[1:]).strip()
                        except Exception:
                            execute_template = None
                    elif line.startswith("compile_command"):
                        try:
                            compile_command = r"=".join(line.split(r'=')[1:]).strip()
                        except Exception:
                            compile_command = None
                    elif line.startswith('run_command'):
                        try:
                            run_command = line.split("=")[1].strip()
                        except Exception:
                            run_command = None
                    elif line.startswith('addtional_command'):
                        try:
                            addtional_command = "=".join(line.split("=")[1:])
                            addtional_commands.append(addtional_command)
                        except Exception:
                            pass

        # complile dirs first
        b_compiled = False
        if source_dir and os.path.isdir(source_dir) and not library_template is None:
            sync_dirs(source_dir, output_dir, exclude_list, rm_target_dir = rm_target_dir)
            # NOTE 只会全部编译成library, 不会编译成可执行程序
            dir_to_librarys(output_dir, library_template, level, maintain_dirs, maintain_files)
            b_compiled = True

        b_py2exe = False
        for source_file in [py_lib_file, py_exe_file]:
            if source_file and os.path.isfile(source_file):
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                shutil.copy(source_file, output_dir)
                exclude_list.append(source_file)
                pyfile_noext = os.path.join(output_dir, os.path.basename(source_file)).replace(r'.py', '')
                if b_py2exe:
                    file_to_execute(pyfile_noext, execute_template, level)
                else:
                    file_to_library(pyfile_noext, library_template, level)
                b_compiled = True
                # NOTE: b_py2exe -> True, 不过不一定编译
                b_py2exe = True
            else:
                b_py2exe = True

        if not b_compiled:
            print('None compiled, please check the template and command args')

    else:
        print(config)
        raise Exception("Please check the config exists")

    # =======================================================================
    # compile to pyd, use compile cmd to create executable file, and copy all pyd from souce_dir to target_dir
    # =======================================================================
    if compile_command:
        if all_imports and r"{hidden}" in compile_command:
            # print(all_imports)
            hidden_import = " --hidden-import=" + " --hidden-import=".join(all_imports)
        else:
            hidden_import = ""

        if source_dir:
            if compile_command:
                cmd = compile_command.format(hidden=hidden_import)
                print("================= pyinstaller_command ======================")
                print(cmd)
                print("============================================================")
                os.system(cmd)

            if addtional_commands:
                print("=================== addtional command ======================")
                for command in addtional_commands:
                    print(command)
                    os.system(command)
                print("============================================================")

            if run_command:
                print("================== run command ==============================")
                print(run_command)
                print("============================================================")
                os.system(run_command)
