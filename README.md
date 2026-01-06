## 文本转语音 MP3 工具（Windows）

这是一个基于 Python 的 **Windows 图形界面文本转语音工具**。  
它可以读取本地 `.txt` 文本文件，并通过 **本地 SAPI 语音引擎** 或 **Edge TTS 云端语音** 将文本转换为 MP3 音频文件。

### 功能特点

- **图形界面操作**：使用 `tkinter` 构建，支持文件选择、进度条提示。
- **多语音引擎**：
  - 本地 SAPI（包含 Desktop + OneCore 语音，如 Xiaoxiao / Yunxi 等）。
  - Edge TTS 云端语音（需安装 `edge-tts`，可选）。
- **音质可选**：支持高（320kbps）、中（192kbps）、低（128kbps）三档比特率。
- **长文本智能切分**：按句号/问号等标点切分，避免一次性传入导致合成失败。
- **自动清理临时文件**：合成完成后自动删除中间 WAV 片段。

### 环境要求

- 操作系统：**Windows 10/11**（需要支持 SAPI 和 OneCore 语音）
- Python 版本：建议 **Python 3.9 及以上**
- 已安装 **ffmpeg**（用于 `pydub` 处理音频）
  - 可到官网下载安装：`https://ffmpeg.org/`
  - 安装后需要将 `ffmpeg` 加入系统环境变量 `PATH`

### 安装步骤

1. **克隆或下载本项目代码**
   - 将代码放在任意目录，例如：`C:\Projects\texttomp3\`

2. **创建并激活虚拟环境（可选但推荐）**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

   > 说明：  
   > - `pywin32` 用于调用 Windows SAPI 语音接口。  
   > - `pydub` 用于拼接和导出 MP3 音频（依赖 ffmpeg）。  
   > - `edge-tts` 为可选依赖，用于 Edge TTS 云端语音。

4. **确保 ffmpeg 可用**
   - 在终端执行：

   ```bash
   ffmpeg -version
   ```

   能看到版本信息说明配置成功。

### 使用方法

1. 在项目目录下运行：

   ```bash
   python texttomp3.py
   ```

2. 在弹出的窗口中：
   - 点击 **“Select File”** 选择一个 UTF-8 编码的 `.txt` 文本文件。
   - 在 “引擎” 下拉框中选择：
     - `本地 SAPI`：使用本机安装的 Windows 语音。
     - `Edge TTS`：使用云端神经网络语音（需网络与 `edge-tts` 依赖）。
   - 在 “音色” 下拉框中选择具体音色（首次选择本地 SAPI 时会自动枚举系统语音）。
   - 在 “音质” 下拉框中选择目标 MP3 比特率。
   - 可点击 **“试听”** 按钮先听一小段示例。
   - 点击 **“Convert to Speech”** 开始转换，进度条会显示当前进度。

3. 合成完成后：
   - MP3 文件会保存在**原文本文件所在目录**，文件名与原文本相同，仅扩展名变为 `.mp3`。
   - 窗口底部标签会提示保存结果。

### 常见问题

- **提示未找到 ffmpeg**
  - 请确认已安装 ffmpeg，并将其加入系统 `PATH`。
- **Edge TTS 无法使用**
  - 确认已执行：
    ```bash
    pip install edge-tts
    ```
  - 并确保选择的音色在 Edge TTS 映射列表中。
- **本地语音列表为空或过少**
  - 请在 Windows 设置中安装相应的语音包（包含中文/英文语音），然后重新打开程序。

### 文件说明

- `texttomp3.py`：主程序文件，包含 GUI 与转换逻辑。
- `requirements.txt`：Python 依赖列表。
- `doc/`：变更记录与说明文档目录。

### 免责声明

本项目仅用于学习与个人使用。请确保在使用合成语音时遵守相关法律法规与服务条款，不得将合成语音用于违法或侵犯他人权益的场景。


