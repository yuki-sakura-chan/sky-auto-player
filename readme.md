# sky-auto-player

PC端《sky·光遇》音乐播放器

Android端《sky·光遇》音乐播放器 ~~使用adb实现，不是所有曲子效果都好~~

~~iOS端《sky·光遇》音乐播放器~~

demo播放

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

将配置文件的`player.type`设置为你需要的系统，目前支持`win`,`demo`,`android`。

目前安卓还不够完善，需要手动调整音符位置，手动设置adb路径。

`F4`可进行暂停

## 曲库

仓库自带一些曲子，更多曲子请在互联网获取。获取到曲子之后放在`config.yaml`文件中`file_path`配置的路径下。

## 项目灵感

此项目的灵感来自于@Tloml-Starry的项目：[SkyAutoMusic](https://github.com/Tloml-Starry/SkyAutoMusic)。感谢Ta的作品。

