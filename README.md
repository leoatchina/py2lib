# py2so 内部使用版
## 背景

这个项目是为了加密用python编写的linux版桌面程序

就一个`py2so.py`脚本

原理是用`cython`把`py`转成`c`, 然后再用编译器把c代码转成动态链接库`.so` 文件

在`github`上开源的版本是用`gcc`编译`c`代码， 而现在这个这个内部版本，则是用`ollvm`, 能保证在`ubuntu16.04`使用

同时，会对中间`c`文件作进一步的脱敏处理

**请更新下部署软件包**

## ollvm介绍
请见[利用ollvm进行代码混淆](https://mabin004.github.io/2018/08/23/ollvm%E5%AD%A6%E4%B9%A0/)

## 生产环境下安装ollvm

我在内网中编译上传了一个版本, 在已经安装好`anaconda3`后
```
cd ~
wget http://10.10.52.61:8000/ollvm.tar.gz
tar xvzf ollvm
ln -s ~/ollvm/bin/clang ~/anaconda3/bin/clang
```
py2so.py在工作过程中会调用这个`clang`文件

## 基本过程
1. 利用linux的`rsync`命令把源代码同步到指定目录, 其间会排除一些文件夹
  注意 **.svn**,  **.git** , **__pycache__** 等可能存有源代码调试过程中临时文件或者代码库的文件夹会**默认不被同步**
2. cython把py转c, 有选项可指定哪些文件不被转换
3. 调用ollvm把c转成so
4. **注意**, 请部署同事在编译完毕后，检查下目标文件夹下有没有`__pycache__`, `.git`, `.svn`, `.idea`目录，有则删除。这些都是编写过程中产生的中间文件，**有泄密的危险性**

## 使用说明
```
  python py2so.py [选项] ...
```

## 选项:
```
    -h,  --help          显示帮助菜单
    -p,  --py            Python的子版本号, 默认值为 3。
                         例: -p 2  (使用python2)
    -l,  --lib           指定要include的python库文件,必填。
    -d,  --directory     Python项目路径
    -o,  --output        指定输出目录，如果不存在会自动建立。默认是当前目录下的./output文件夹
    -m,  --maintain      标记你不想加密的文件, 用逗号隔离
    -M,  --maintain_dir  标记你不想加密的文件夹, 用逗号隔离
    -e,  --exclude       rsync同步时不要同步的文件或者文件夹, 用逗号隔离
    -k,  --keep          值为2时，保留编译出来的.c， .py文件，不对.c文件进行进一步修改
                         值为1时，保留编译出来的.c， .py文件，对.c文件进行进一步修改
                         值为0时，不保留编译出来的.c， .py文件
    -D,  --delete        删除特定后缀的文件，比如.ui, .proto
```

## 例子
基本可以用于生产环境
[编译Gastroscope项目](./run.sh)