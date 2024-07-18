# sky-auto-palyer

PC端《sky·光遇》自动弹琴

Android端《sky·光遇》自动弹琴

~~Ios端《sky·光遇》自动弹琴~~

音频demo自动演奏

## 下载

~~~shell
git clone https://github.com/caiyucong/sky-auto-player.git
~~~

安装第三方库

~~~shell
pip install PyDirectInput PyYAML chardet pygame
~~~

## 使用方法

游戏中打开钢琴或其他15键乐器，运行`main.py`文件，选择曲谱即可，然后在2秒内点击游戏（懒得做自动捕捉窗口）。

将配置文件的`player.type`设置为你需要的系统，目前支持`win`,`demo`,`android`。

目前安卓还不够完善，需要手动调整音符位置，手动设置adb路径。

## 曲库

仓库自带一些曲子，更多曲子请在互联网获取。获取到曲子之后放在`config.yaml`文件中`file_path`配置的路径下。

## 项目灵感

此项目的灵感来自于@Tloml-Starry的项目：[https://github.com/Tloml-Starry/SkyAutoMusic](https://github.com/Tloml-Starry/SkyAutoMusic)。感谢Ta的作品。

