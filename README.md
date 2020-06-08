# py2so 内部使用版
## 背景

这个项目是为了加密用python编写的linux版桌面程序

原理是用`cython`把`py`转成`c`, 然后再用编译器把c代码转成动态链接库`.so` 文件

在github上开源的版本是用`gcc`编译`c`代码， 而现在这个这个内部版本，则是用`ollvm`编译

同时，会对中间`c`文件作进一步的脱敏处理

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
  注意 **.svn**,  **.git** , **__pycache__** 等可能存有源代码调试过程中临时文件或者代码库的文件夹会默认不被同步
2. cython把py转c, 有选项可指定哪些文件不被转换
3. 调用ollvm把c转成so


## 使用说明
```
  python py2so.py [选项] ...
```

## 选项:
```
    -h,  --help          显示帮助菜单
    -p,  --py            Python的子版本号, 默认值为 3。 次重要区别
                         例: -p 2  (比如你使用python2)
    -l,  --lib           指定要include的python库文件,必填。
    -d,  --directory     Python项目路 径 (如果使用-d参数, 将加密整个Python项目)
    -o,  --output        指定输出目录，如果不存在会自动建立。默认是当前目录下的.output文件夹
    -m,  --maintain      标记你不想加密的文件, 用逗号隔离
    -M,  --maintain_dir  标记你不想加密的文件夹, 用逗号隔离
    -e,  --exclude       rsync同步时不要同步的文件或者文件夹, 用逗号隔离
    -k,  --keep          **注意**测试时才用这个选项，不删除中间生成的`py`, `c`文件
    -D,  --delete        删除特定后缀的文件，比如`.ui`, `.proto`
```

## 例子
```
python py2so.py -l ~/anaconda3/include/python3.6m -d ~/deploy_package_new/Gastroscope/Server -o ~/Gastroscope/Server -m ManageServer.py -D ui,proto
python py2so.py -l ~/anaconda3/include/python3.6m -d ~/deploy_package_new/Gastroscope/Client -o ~/Gastroscope/Client -m ManageClient.py -D ui,proto
```

## py2so简介
1. py2so可以将python文件转化为so文件，达到加密python文件的目的
2. py2so加密一个py文件，也可以直接加密一整个python项目
3. 生成的.so文件可以被主文件通过 "from module import \*" 调用
4. 可以自动识别项目中的py文件,可以指定哪些文件或文件夹不被加密
5. 强制在目标文件夹删除加密过的py文件
6. 采用了把源文件目录同步到指定输出文件夹的方式，默认是 "./output"
7. 可以指定用python2或者python3，默认是 python3
8. 碰到无法编译的情况会退出





