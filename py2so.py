
import os
import sys
import getopt
import random
import string



########################### 老的混淆方式 ###########################################################3
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


######################################################################################
def strip_file(filename):
    # 去除了源代码信息,即使so文件报错,也看不出来代码
    os.system('cat {filename} | grep -v -E "^ \* " > {filename}.temp.cpp'.format(filename = filename))
    os.system('rm {filename}'.format(filename = filename))
    os.system('mv {filename}.temp.cpp {filename}'.format(filename = filename))


def run_cmd(cmd):
    try:
        ret = os.system(cmd)
    except Exception as e:
        return e
    return ret


# 核心函数
def transfer(full_basename, py_ver, lib_dir, keep = False, delete_suffix = []):
    '''
    full_basename is the absolute path of the py file, without .py surfix
    it with compile to full_basename.c and compile to .so file
    '''
    try:
        # cython to cpp
        cmd = 'cython -{py_ver} {full_basename}.py --cplus -D'.format(py_ver = py_ver, full_basename = full_basename)
        ret = run_cmd(cmd)

        # strip cpp file
        if ret == 0:
            strip_file("{full_basename}.cpp".format(full_basename = full_basename))
        else:
            raise Exception('cython failed')

        # .c to .so, with ollvm
        if ret == 0:
            cmd = "clang {full_basename}.cpp -fPIC -shared -I{lib_dir} `python{py_ver}-config --ldflags` -o {full_basename}.so -mllvm -fla".format(py_ver = py_ver, full_basename = full_basename, lib_dir = lib_dir)
            ret = run_cmd(cmd)
        else:
            raise Exception('strip failed')

        # print
        if ret == 0:
            if not keep:
                os.system('rm -f {full_basename}.py {full_basename}.cpp {full_basename}.o {full_basename}.cpp.temp.cpp {full_basename}'.format(full_basename = full_basename))
            print('Completed %s' % full_basename)
        else:
            raise Exception('ollvm to so failed')
    except Exception as e:
        print('========================')
        print(cmd)
        print('========================')
        raise e



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
  -d, --directory     Directory of your project (if use -d, you change the whole directory)
  -o, --output        Directory to store the compile results, default "./output"
  -e, --exclude       Directories or files that you do not want to sync to output file
                      dirs __pycache__, .vscode, .git, .idea will always not be synced
  -k, --keep          if keep the compiled .c .o files
  -m, --maintain      list the file you don't want to transfer from py to so
                      example: -m __init__.py,setup.py,[poc,resource,venv,interface]
  -M, --maintaindir   like maintain, but dirs

example:
  python py2so.py -d test_dir -m __init__.py,setup.py
    '''
    keep         = False
    py_ver       = '3'
    lib_dir      = ''
    source_dir   = ''
    output_dir   = './output'
    delete_list  = []
    exclude_list = []
    skipdir_list = []
    skipfil_list = []
    try:
        options, args = getopt.getopt(sys.argv[1:],
                "hp:l:o:d:f:m:M:e:k:D:",
                ["help", "py=", "lib=", "file=", "output=", "directory=", "maintain=", "maintaindir=", "exclude=", "keep=", "delete="])
    except getopt.getopterror:
        print('get options error')
        print(help_show)
        sys.exit(1)

    for key, value in options:
        if key in ['-h', '--help']:
            print(help_show)
            sys.exit(0)
        elif key in ['-p', '--py']:
            p_subv = value
        elif key in ['-l', '--lib']:
            lib_dir = value
        elif key in ['-o', '--output']:
            output_dir = value
        elif key in ['-d', '--directory']:
            source_dir = value
        elif key in ['-e', '--exclude']:
            exclude_list = value.split(",")
        elif key in ['-k', '--keep']:
            if value == '1':
                keep = True
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

    if source_dir[-1] == r'/':
        source_dir = source_dir[-1]

    if output_dir[-1] == r'/':
        output_dir = output_dir[-1]

    if os.path.abspath(source_dir) == os.path.abspath(output_dir):
        print("Source dir equals output dir!")
        sys.exit(1)

    if py_ver not in ['2', '3']:
        print('python version must be 2 or 3')
        sys.exit(1)

    if source_dir:
        if output_dir:
            if not os.path.exists(source_dir):
                print('No such Directory %s, please check or use the Absolute Path' % source_dir)
                sys.exit(1)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # use rsync to transfer
            rsync_cmd = 'rsync -azP --size-only %s --delete %s/ %s/' % (exclude_str, source_dir, output_dir)
            os.system(rsync_cmd)
            try:
                for root, dirs, files in os.walk(output_dir):
                    if root in skipdir_list or os.path.basename(root) in skipdir_list:
                        continue

                    for d in dirs:
                        if d in exclude_list:
                            os.system('rm -rf %s' % os.path.join(root, d))

                    for fil in files:
                        if fil in skipfil_list or os.path.join(root, fil) in skipfil_list or os.path.join(os.path.basename(root), fil) in skipdir_list:
                            continue

                        pref = fil.split('.')[0]
                        full_basename = root + '/' + pref
                        if delete_list:
                            suffix = fil.split(r'.')[-1]
                            if suffix in delete_list:
                                os.system('rm -f %s' % os.path.join(root, fil))
                        

                        # delete pyc which is easily to reverse
                        if fil.endswith('.pyc') or fil in exclude_list:
                            os.system('rm -f %s' % os.path.join(root, fil))
                        elif fil.endswith('.py'):
                            transfer(full_basename, py_ver, lib_dir, keep)
            except Exception as err:
                raise(err)
            else:
                print('%s to %s finished' % (source_dir, output_dir))
                print(rsync_cmd)
