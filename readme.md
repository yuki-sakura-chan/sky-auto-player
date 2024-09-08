# sky-auto-player

## 简介

sky-auto-player是一个自动演奏《sky·光遇》游戏中的乐器的程序，目前支持以下几种：

1. PC端《sky·光遇》音乐播放器

2. Android端《sky·光遇》音乐播放器 ~~使用adb实现，不是所有曲子效果都好~~

3. ~~iOS端《sky·光遇》音乐播放器~~

4. demo模式，用于在非游戏下试听曲子

当前仓库不提供海量曲谱，需要自行获取，仓库中提供了一些曲谱供玩家使用。

ios端暂时不支持，因为我没有mac，如果有人愿意提供mac的话，我会尽快支持。

## 下载

~~~shell
git clone https://github.com/caiyucong/sky-auto-player.git
~~~

安装第三方库

~~~shell
pip install PyDirectInput PyYAML chardet pygame pynput
~~~

## 使用方法

游戏中打开钢琴或其他15键乐器，运行`main.py`文件，选择曲谱即可，之后在游戏中按一下`F4`即可。

将配置文件的`player.type`设置为你需要的系统，目前支持的类型为`win`,`demo`,`android`。

目前安卓还不够完善，需要手动调整音符位置，手动设置adb路径。

`F4`可进行暂停

## 关于曲库

目前仅支持`json`格式的曲谱，未来可能会支持`midi`格式。

仓库自带一些曲子，更多曲子请在互联网获取。获取到曲子之后放在`config.yaml`文件中`file_path`配置的路径下。

未来可能会开发用户上传曲谱功能，如果有人愿意提供服务器的话。

## 关于发行

在制作出ui之后，我会将其打包成exe文件，方便大家使用。

## 关于手机端

本人专注于PC端，手机端的支持可能会有所延迟，如果有人愿意提供帮助，我会尽快支持。

## 关于项目

为什么项目包叫sakura？ 因为本人喜欢樱花。😜

## 项目灵感

此项目的灵感来自于@Tloml-Starry的项目：[SkyAutoMusic](https://github.com/Tloml-Starry/SkyAutoMusic)。感谢Ta的作品。

