## 文本转语音 MP3 工具（Windows）Text to Speech (TTS) to MP3

这是一个基于 **Python** 的 **Windows 图形界面文本转语音（Text to Speech, TTS）工具**。  
它可以读取本地 `.txt` 文本文件，并通过 **本地 SAPI 语音引擎** 或 **Edge TTS 云端语音** 将文本转换为 **MP3 音频文件**，适合有批量朗读、听书、语音内容制作等需求的用户。

> 关键词（方便在 GitHub 上搜索到本项目）：  
> `python` / `text to speech` / `tts` / `text to mp3` / `text2speech` / `speech synthesis` / `audio` / `mp3`

### 多语言 README

- 🇨🇳 当前文件：**中文 README（推荐中文用户）**
- 🇬🇧 英文版本：请查看 `README.en.md`

---

### 功能特点（Features）

- **图形界面操作（GUI）**：使用 `tkinter` 构建，支持文件选择、进度条提示，零命令行基础也能使用。
- **多语音引擎（Local TTS + Cloud TTS）**：
  - 本地 SAPI（包含 Desktop + OneCore 语音，如 Xiaoxiao / Yunxi 等）。
  - Edge TTS 云端语音（需安装 `edge-tts`，可选）。
- **音质可选（MP3 Bitrate）**：支持高（320kbps）、中（192kbps）、低（128kbps）三档比特率。
- **长文本智能切分（Smart Split）**：按句号 / 问号等标点切分，避免一次性传入导致合成失败。
- **自动清理临时文件**：合成完成后自动删除中间 WAV 片段，避免占用磁盘空间。

---

### 环境要求（Requirements）

- 操作系统：**Windows 10/11**（需要支持 SAPI 和 OneCore 语音）
- Python 版本：建议 **Python 3.9 及以上**
- 已安装 **ffmpeg**（用于 `pydub` 处理音频）
  - 可到官网下载安装：`https://ffmpeg.org/`
  - 安装后需要将 `ffmpeg` 加入系统环境变量 `PATH`

---

### 安装步骤（Installation）

1. **克隆或下载本项目代码**
   - 将代码放在任意目录，例如：`C:\Projects\texttomp3\`

2. **创建并激活虚拟环境（可选但推荐）**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **安装依赖（Install dependencies）**

   ```bash
   pip install -r requirements.txt
   ```

   > 说明：  
   > - `pywin32` 用于调用 Windows SAPI 语音接口。  
   > - `pydub` 用于拼接和导出 MP3 音频（依赖 ffmpeg）。  
   > - `edge-tts` 为可选依赖，用于 Edge TTS 云端语音。

4. **确保 ffmpeg 可用（Check ffmpeg）**
   - 在终端执行：

   ```bash
   ffmpeg -version
   ```

   能看到版本信息说明配置成功。

---

### 使用方法（Usage）

1. 在项目目录下运行：

   ```bash
   python texttomp3.py
   ```

2. 在弹出的窗口中（GUI 操作流程）：
   - 点击 **“Select File”** 选择一个 UTF-8 编码的 `.txt` 文本文件。
   - 在 “引擎” 下拉框中选择：
     - `本地 SAPI`：使用本机安装的 Windows 语音。
     - `Edge TTS`：使用云端神经网络语音（需网络与 `edge-tts` 依赖）。
   - 在 “音色” 下拉框中选择具体音色（首次选择本地 SAPI 时会自动枚举系统语音）。
   - 在 “音质” 下拉框中选择目标 MP3 比特率。
   - 可点击 **“试听”** 按钮先听一小段示例。
   - 点击 **“Convert to Speech”** 开始转换，进度条会显示当前进度。

3. 合成完成后（输出结果）：
   - MP3 文件会保存在**原文本文件所在目录**，文件名与原文本相同，仅扩展名变为 `.mp3`。
   - 窗口底部标签会提示保存结果。

---

### 常见问题（FAQ）

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

---

### 文件说明（Project Structure）

- `texttomp3.py`：主程序文件，包含 GUI 与文本转语音 / 音频导出逻辑。
- `requirements.txt`：Python 依赖列表。
- `doc/`：变更记录与说明文档目录。
- `README.md`：中文使用说明与项目介绍。
- `README.en.md`：英文使用说明与项目介绍。

---

### 适用场景（Use Cases）

- 将电子书 / 网文转换为 MP3，在手机 / 车机上听书。
- 为视频 / 短视频生成旁白音频。
- 制作学习资料的朗读音频（例如单词、课文）。
- 需要批量转换文本为语音的自动化脚本场景（可在此 GUI 基础上扩展）。

---

### 免责声明（Disclaimer）

本项目仅用于学习与个人使用。请确保在使用合成语音时遵守相关法律法规与服务条款，不得将合成语音用于违法或侵犯他人权益的场景。作者不对因使用本项目产生的任何法律风险承担责任。

