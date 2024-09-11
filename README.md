# sky-auto-player

English | [简体中文](./README.zh-CN.md)

## Introduction

`sky-auto-player` is an automated music-playing program specifically designed for the game *Sky: Children of the Light*. It allows players to automatically play instruments within the game. The current supported modes include:

1. **PC Music Player**: For the PC version of *Sky: Children of the Light*.
2. **Android Music Player**: Implemented via `adb` for the Android version, with varying performance depending on the song.
3. **iOS Music Player**: Currently not supported, pending future development.
4. **Demo Mode**: Allows you to preview songs outside the game environment.

**Note:** The repository does not include a large collection of music sheets; users need to obtain them on their own. Some sample music sheets are provided for use.

## Download and Installation

Clone the repository using Git:

```shell
git clone https://github.com/caiyucong/sky-auto-player.git
```

Install the required third-party libraries:

```shell
pip install -r requirements.txt
```

## Usage

1. Open the piano or any other 15-key instrument within the game.
2. Run the `main.py` file and select the desired music sheet.
3. Press the `F4` key in-game to start auto-playing.
4. Configure the `player.type` in the `config.yaml` file to suit your system (`win` for PC, `demo` for preview mode, `android` for Android).
5. Android users need to manually adjust note positions and set the `adb` path.

**Hotkey:** Press `F4` to pause or resume the performance.

## Music Library

Currently, the program supports `json` format music sheets, with possible future support for `midi` format. You can find more music sheets online and place them in the path specified by `file_path` in the `config.yaml` file.

There are plans to develop a feature for users to upload music sheets. If anyone is willing to provide server support, please contact me.

## Release Plans

Once the UI is complete, the project will be packaged into an executable (`exe`) file for ease of use.

## Mobile Support

The project currently focuses on PC development, with mobile support potentially delayed. If anyone is willing to help, mobile support will be expedited.

## About the Project

The project package is named `sakura` because I like cherry blossoms. 😜

## Project Inspiration

This project was inspired by @Tloml-Starry's [SkyAutoMusic](https://github.com/Tloml-Starry/SkyAutoMusic) project. Special thanks for the inspiration provided by their work.

## License

This project is licensed under the [MIT License](./LICENSE).
