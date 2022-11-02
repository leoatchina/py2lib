# 把 py 文件转成动态链接库或可执行文件

## 需求
这个项目是为了加密用 python 编写的 py, 核心就是`py2lib.py`脚本，原理是用`cython`把`py`文件转成`cpp`文件, 然后再用编译器转成动态链接库`so`或者`dll`或者可执行文件
**请安装cython**
```
pip install cython
```
早期的脚本需要把编译器的参数等都写入到此文件的调用参数里，现在都放到`模板文件`里

## 基本过程
1. 先把源代码同步到目录目录，可以指定排除一些文件夹。**.svn**,  **.git** , **__pycache__** , **.idea** 等可能存有源代码调试过程中临时文件或者代码库的文件夹会**默认不被同步**
2. 读取`模板文件`，组装出可以的编译命令
3. cython 把 py 转 c
4. 调用编译工具把 c 转成 静态库或可执行文件。
5. **注意**, 请部署同事在编译完毕后，检查下目标文件夹下有没有`__pycache__`, `.git`, `.svn`, `.idea`目录，有则删除。这些都是编写过程中产生的中间文件，**有泄密的危险性**

## 使用说明
```
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
  python py2lib.py -d test_dir -o target_dir -m __init__.py,setup.py -c config.ini

```

## 关于编译模板
### 需要掌握的知识
你所用的编译器的用法、参数等，如`gcc`, `ollvm`,`cl`, `clang`的用法

### 模板文件
commandfile即`使用说明`里提到的`-c `参数需要提供， 在里面视编译需要写入`library_template` `execute_template`。
其中`{pyfile_noext}`代表着无后缀的各个文件，**必须要提供**。
一个py文件，会经过 {pyfile_noext}.py -> {pyfile_noext}.c -> {pyfile_noext}.o -> {pyfile_noext}.so 或者 {pyfile_noext}.exe 或者 {pyfile_noext}.dll 或者
{pyfile_noext}.pyd

下面是一些典型的模板文件
```mingw64 in WINDOWS
library_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -s -shared {pyfile_noext}.c -o {pyfile_noext}.dll -Wl,--subsystem,windows -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
execute_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -municode {pyfile_noext}.c -o {pyfile_noext}.exe -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
```

```linux
library_template=gcc -fPIC -s -shared {pyfile_noext}.c -o {pyfile_noext}.so -I ~/miniconda3/envs/py3.8/include -I/usr/include/python3.8 `python3-config --ldflags`
execute_template=gcc -fPIC {pyfile_noext}.c -o {pyfile_noext} -I ~/miniconda3/envs/py3.8/include -I/usr/include/python3.8 `python3-config --ldflags` -lpython3.8
```

## 建议使用ollvm编译器
请见[利用 ollvm 进行代码混淆](https://mabin004.github.io/2018/08/23/ollvm%E5%AD%A6%E4%B9%A0/)
在模板里写入这个clang
```
library_template = /path/to/clang {pyfile_noext}.c -fPIC -shared -I /path/to/python/include `python3-config --ldflags` -o {pyfile_noext}.so -mllvm -fla
```
如果是windows版本的ollvm 文件，注意把对应目录加入到系统的PATH里去
