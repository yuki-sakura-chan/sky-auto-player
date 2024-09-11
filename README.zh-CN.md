# sky-auto-player

[English](./README.md) | 简体中文

## 简介

`sky-auto-player` 是一个专为《Sky·光遇》设计的自动演奏程序，旨在帮助玩家自动演奏游戏中的乐器。当前支持以下几种模式：

1. **PC 端音乐播放器**：适用于《Sky·光遇》PC 版本。
2. **Android 端音乐播放器**：通过 `adb` 实现，支持《Sky·光遇》Android 版本，但效果可能因曲子而异。
3. **iOS 端音乐播放器**：当前暂不支持，等待后续开发。
4. **Demo 模式**：可以在非游戏环境中试听曲子。

**注意：** 项目中不包含海量曲谱，用户需自行获取。仓库中提供了一些示例曲谱供使用。

### 下载与安装

使用 Git 克隆仓库：

```shell
git clone https://github.com/caiyucong/sky-auto-player.git
```

安装所需的第三方库：

```shell
pip install -r requirements.txt
```

### 使用方法

1. 在游戏中打开钢琴或其他 15 键乐器。
2. 运行 `main.py` 文件，选择所需的曲谱。
3. 在游戏中按下 `F4` 键以开始自动演奏。
4. 可在 `config.yaml` 文件中配置 `player.type` 为 `win`（PC 端）、`demo`（试听模式）、`android`（安卓端）等不同系统。
5. 安卓版需要手动调整音符位置及设置 `adb` 路径。

**快捷键说明：** 按下 `F4` 键可暂停或恢复演奏。

### 曲库说明

目前支持 `json` 格式的曲谱，未来可能会支持 `midi` 格式。更多曲谱可以在互联网上获取，并将其放置于 `config.yaml` 文件中指定的 `file_path` 路径下。

未来计划开发用户上传曲谱的功能，有志愿提供服务器支持者可与我联系。

### 发行计划

在 UI 完成后，项目将打包为 `exe` 文件，方便用户直接使用。

### 手机端支持

本项目目前主要专注于 PC 端的开发，手机端支持可能会有所延迟。如果有人愿意提供帮助，手机端的支持将会加速推进。

### 关于项目

项目包名为 `sakura`，因为本人喜欢樱花。😜

### 项目灵感

本项目的灵感来源于 @Tloml-Starry 的项目：[SkyAutoMusic](https://github.com/Tloml-Starry/SkyAutoMusic)。特别感谢他的作品为本项目提供了启发。

### License

本项目采用 [MIT 许可证](./LICENSE)。
