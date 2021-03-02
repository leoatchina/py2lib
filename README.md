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
  -h, --help          帮助
  -s, --sync          只同步不编译
  -c, --commandfile   在需要编译的情况下，必须提供，为编译模板 
  -f, --file          单文件模式， -f 优先 级大于 -d 
  -d, --directory     源文件夹 
  -o, --output        目标文件夹 
  -x, --execute       指定编译为可执行文件的文件， 用逗号隔开 
  -m, --maintain      指定不被编译的文件，用逗号隔开
                      example: -m __init__.py,setup.py
  -M, --maintaindir   不被编译的文件上，其下所有文件夹都不会被编译 
  -e, --exclude       不被同步的文件夹， __pycache__, .vscode, .git, .idea, .svn 等肯定不被同步 
  -k, --keep          keep == 3 对c文件进一步混淆，保持临时文件（o文件等） 
                      keep == 2 不对c文件进一步混淆, 保持临时文件 
                      keep == 1 对c文件进一步混淆, 不保持临时文件 
                      keep == 0 不对c文件进一步混淆, 不保持临时文件
  -D, --delete        在编译结束后要删除的文件 

example:
  python py2lib.py -d test_dir -o target_dir -m __init__.py,setup.py -c config.ini

```

## 关于编译模板
### 需要掌握的知识
你所用的编译器的用法、参数等，如`gcc`的用法

### 模板文件
commandfile即`使用说明`里提到的`-c `参数需要提供， 在里面视编译需要写入`library_template`及`execute_template`。
其中`{path_noext}`代表着无后缀的各个文件，**必须要提供**。不明白什么意思 ？ 一个py文件，会经过 {path_noext}.py -> {path_noext}.c -> {path_noext}.o -> {path_noext}.so 或者 {path_noext}.exe 或者 {path_noext}.dll 或者 {path_noext}.pyd
```
library_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -s -shared {path_noext}.c -o {path_noext}.dll -Wl,--subsystem,windows -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
execute_template = d:/mingw64/bin/gcc.exe -DMS_WIN64 -municode {path_noext}.c -o {path_noext}.exe -I d:\Anaconda3\include -L "d:\Anaconda3\libs" -lpython36
```


## 建议使用ollvm编译器 
请见[利用 ollvm 进行代码混淆](https://mabin004.github.io/2018/08/23/ollvm%E5%AD%A6%E4%B9%A0/)

我在内网中编译上传了一个版本，可执行文件是 `clang`
```
cd ~
wget http://10.10.52.61:8000/ollvm.tar.gz
tar xvzf ollvm
```
在模板里写入这个clang
```
library_template = /path/to/clang {path_noext}.c -fPIC -shared -I /path/to/python/include `python3-config --ldflags` -o {path_noext}.so -mllvm -fla
```