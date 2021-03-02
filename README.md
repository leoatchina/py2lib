# 把 py 文件转成动态链接库或可执行文件

## 背景
这个项目是为了加密用 python 编写的 py, 核心就一个`py2lib.py`脚本，原理是用`cython`把`py`转成`c`, 然后再用编译器把 c 代码转成动态链接库`so`或者`dll` 文件
**请更新下部署软件包**
```
pip install cython
```
## 基本过程
1. 先把源代码同步到目录目录，其间会排除一些文件夹
  注意 **.svn**,  **.git** , **__pycache__** , **.idea** 等可能存有源代码调试过程中临时文件或者代码库的文件夹会**默认不被同步**
2. cython 把 py 转 c, 有选项可指定哪些文件不被转换
3. 调用编译工具把 c 转成 静态库 
4. **注意**, 请部署同事在编译完毕后，检查下目标文件夹下有没有`__pycache__`, `.git`, `.svn`, `.idea`目录，有则删除。这些都是编写过程中产生的中间文件，**有泄密的危险性**

## 使用说明
```
Usage: python py2lib.py [options] ...

Options:
  -h, --help          Show the help info
  -s, --sync          sync only, donot do compile
  -c, --commandfile   Set the command template file, must be offered
  -f, --file          single file, -f supervised -d when offered at same time
  -d, --directory     Directory of your project (if use -d, you change the whole directory)
  -o, --output        Directory to store the compile results, must be different to source_dir
  -x, --execute       The files, compile to executable file
  -m, --maintain      list the file you don't want to compile from py to library file
                      example: -m __init__.py,setup.py
  -M, --maintaindir   like maintain, but dirs
  -e, --exclude       Directories or files that you do not want to sync to output dir.
                      __pycache__, .vscode, .git, .idea, .svn will always not be synced
  -k, --keep          keep == 3 confuse c file, keep temp files
                      keep == 2 not confuse c file, keep temp files
                      keep == 1 confuse c file, not keep temp files
                      keep == 0 not confuse c file, not keep temp files
  -D, --delete        files, dirs foreced to delete in the output_dir

example:
  python py2lib.py -d test_dir -o target_dir -m __init__.py,setup.py -c config.ini
  python py2lib.py 『选项』 ...

```
commandfile一定要提供，里面格式如下下
```
library_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -s -shared {path_noext}.c -o {path_noext}.dll -Wl,--subsystem,windows -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
execute_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -municode {path_noext}.c -o {path_noext}.exe -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
```

## 编译器选择

请见[利用 ollvm 进行代码混淆](https://mabin004.github.io/2018/08/23/ollvm%E5%AD%A6%E4%B9%A0/)

在`github`上开源的版本是用`gcc`编译`c`代码， 而现在这个这个内部版本，则是用在`ubuntu16.04`下编译安装的 `ollvm`
同时，会对中间`c`文件作进一步的脱敏处理

我在内网中编译上传了一个版本，在已经安装好`anaconda3`后
```
cd ~
wget http://10.10.52.61:8000/ollvm.tar.gz
tar xvzf ollvm
ln -s ~/ollvm/bin/clang ~/anaconda3/bin/clang
```

