# 把 py 文件转成动态链接库或可执行文件
## 背景

这个项目是为了加密用 python 编写的 linux 版桌面程序

就一个`compile_py.py`脚本

原理是用`cython`把`py`转成`c`, 然后再用编译器把 c 代码转成动态链接库`.so` 文件

在`github`上开源的版本是用`gcc`编译`c`代码， 而现在这个这个内部版本，则是用`ollvm`, 能保证在`ubuntu16.04`使用

同时，会对中间`c`文件作进一步的脱敏处理

**请更新下部署软件包**

## ollvm 介绍
~~请见[利用 ollvm 进行代码混淆](https://mabin004.github.io/2018/08/23/ollvm%E5%AD%A6%E4%B9%A0/)~~

## 生产环境下安装 ollvm

我在内网中编译上传了一个版本，在已经安装好`anaconda3`后
```
cd ~
wget http://10.10.52.61:8000/ollvm.tar.gz
tar xvzf ollvm
ln -s ~/ollvm/bin/clang ~/anaconda3/bin/clang
```
compile_py.py 在工作过程中会调用这个`clang`文件

## 基本过程
1. 利用 linux 的`rsync`命令把源代码同步到指定目录，其间会排除一些文件夹
  注意 **.svn**,  **.git** , **__pycache__** 等可能存有源代码调试过程中临时文件或者代码库的文件夹会**默认不被同步**
2. cython 把 py 转 c, 有选项可指定哪些文件不被转换
3. 调用 ollvm 把 c 转成 so
4. **注意**, 请部署同事在编译完毕后，检查下目标文件夹下有没有`__pycache__`, `.git`, `.svn`, `.idea`目录，有则删除。这些都是编写过程中产生的中间文件，**有泄密的危险性**

## 使用说明
```
  python compile_py.py 『选项』 ...
```

## 例子
基本可以用于生产环境
[编译 Gastroscope 项目](./compile.sh)
