import asyncio
import logging
import os
import re
import shutil
import tempfile
import winreg
from tkinter import Tk, filedialog, Label, StringVar, ttk

import pythoncom
import win32com.client
from pydub import AudioSegment
from pydub.utils import which

try:
    from edge_tts import Communicate
except ImportError:
    Communicate = None

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)

VOICE_ID_MAP = {}  # {显示名: voice.Id 或 TokenId}
BITRATE_MAP = {
    "高（320kbps）": "320k",
    "中（192kbps）": "192k",
    "低（128kbps）": "128k",
}

# Edge TTS 常用音色映射（可按需扩展）
EDGE_VOICE_MAP = {
    "Microsoft Xiaoxiao (Natural) - Chinese (Simplified, China)": "zh-CN-XiaoxiaoNeural",
    "Microsoft Yunxi (Natural) - Chinese (Simplified, China)": "zh-CN-YunxiNeural",
    "Microsoft Yunxia (Natural) - Chinese (Simplified, China)": "zh-CN-YunxiaNeural",
    "Microsoft Xiaoyi (Natural) - Chinese (Simplified, China)": "zh-CN-XiaoyiNeural",
    "Microsoft Jenny (Natural) - English (United States)": "en-US-JennyNeural",
    "Microsoft Aria (Natural) - English (United States)": "en-US-AriaNeural",
}


def load_voices():
    """枚举系统可用音色（包含 Desktop + OneCore），供下拉框使用。"""
    global VOICE_ID_MAP
    VOICE_ID_MAP.clear()
    try:
        pythoncom.CoInitialize()

        # 1) 经典 SAPI5 Desktop 声音（SpVoice 直接可见）
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        for i in range(voices.Count):
            v = voices.Item(i)
            name = v.GetDescription()
            VOICE_ID_MAP[name] = v.Id

        # 2) Windows 10/11 OneCore 语音（例如 Xiaoxiao / Yunxi 等）
        # 这里不用 COM Category，而是直接从注册表读取 Token 路径，
        # 再用 SpObjectToken.SetId 创建 Token，确保能拿到所有 Natural 音色。
        try:
            base = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as key:
                index = 0
                while True:
                    try:
                        sub_name = winreg.EnumKey(key, index)
                    except OSError:
                        break
                    index += 1

                    token_id = rf"HKEY_LOCAL_MACHINE\{base}\{sub_name}"
                    try:
                        token = win32com.client.Dispatch("SAPI.SpObjectToken")
                        token.SetId(token_id)
                        name = token.GetDescription()
                        if name not in VOICE_ID_MAP:
                            VOICE_ID_MAP[name] = token_id
                    except Exception as inner_e:
                        logging.warning("跳过 OneCore 语音 %s：%s", sub_name, inner_e)
        except Exception as e:
            logging.warning("加载 OneCore 语音失败，将仅使用 Desktop 语音：%s", e)

        logging.info("已发现 %d 个语音音色（包含 Desktop/OneCore）", len(VOICE_ID_MAP))
    except Exception as e:
        logging.exception("加载语音音色失败：%s", e)
    finally:
        # 不在这里 CoUninitialize，避免 COM 对象析构时出现 Win32 exception 提示
        pass


def preview_voice():
    """使用当前选中的音色播放一段示例文本。"""
    sample_text = "这是音色试听示例。"
    voice_name = voice_var.get().strip() if voice_var.get() else None
    engine = engine_var.get().strip()

    # Edge TTS 试听：用云端音色合成一小段到临时 mp3，然后用系统默认播放器播放
    if engine == "Edge TTS":
        try:
            if Communicate is None:
                raise RuntimeError("未安装 edge-tts，请先执行：pip install edge-tts")
            if not voice_name or voice_name not in EDGE_VOICE_MAP:
                raise RuntimeError("当前选中的音色不支持 Edge TTS。")

            preview_dir = os.path.join(os.getcwd(), "edge_preview_cache")
            os.makedirs(preview_dir, exist_ok=True)
            safe_name = re.sub(r"[^\w.-]+", "_", voice_name)
            tmp_mp3 = os.path.join(preview_dir, f"{safe_name}_preview.mp3")

            if os.path.exists(tmp_mp3) and os.path.getsize(tmp_mp3) > 0:
                logging.info("使用缓存的 Edge TTS 试听文件：%s", tmp_mp3)
            else:
                logging.info("开始 Edge TTS 音色试听生成：%s -> %s", voice_name, tmp_mp3)
                asyncio.run(edge_tts_async(sample_text, voice_name, tmp_mp3))

            try:
                os.startfile(tmp_mp3)  # 使用系统默认播放器播放
            except Exception as e:
                logging.warning("自动打开试听音频失败，请手动播放：%s", e)
                label.config(text=f"试听文件已生成：{tmp_mp3}")
        except Exception as e:
            logging.exception("Edge TTS 音色试听失败：%s", e)
            label.config(text=f"音色试听失败：{e}")
        return

    # 本地 SAPI 试听：沿用原逻辑
    try:
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        if voice_name and voice_name in VOICE_ID_MAP:
            try:
                token_id = VOICE_ID_MAP[voice_name]
                token = win32com.client.Dispatch("SAPI.SpObjectToken")
                token.SetId(token_id)
                speaker.Voice = token
            except Exception as e:
                logging.exception("设置试听音色失败，将使用默认音色：%s", e)
        logging.info("开始音色试听：%s", voice_name or "默认")
        speaker.Speak(sample_text)
    except Exception as e:
        logging.exception("音色试听失败：%s", e)
        label.config(text=f"音色试听失败：{e}")
    finally:
        pythoncom.CoUninitialize()


def select_file():
    root.filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=[("Text files", "*.txt")],
    )
    if root.filename:
        label.config(text=f"已选择文件：{os.path.basename(root.filename)}")
        logging.info("已选择文件：%s", root.filename)
    else:
        label.config(text="未选择文件，请重试。")
        logging.warning("未选择文件")


def ensure_ffmpeg():
    """确保 pydub 能找到 ffmpeg，否则提前提示用户。"""
    ffmpeg_path = which("ffmpeg") or which("ffmpeg.exe")
    if not ffmpeg_path:
        raise RuntimeError("未检测到 ffmpeg，可安装后重试（https://ffmpeg.org/）。")
    AudioSegment.converter = ffmpeg_path
    logging.info("ffmpeg 已找到：%s", ffmpeg_path)
    return ffmpeg_path


def split_text(text: str, max_len: int = 1500):
    """将长文本按句子拆分为较小片段，避免一次性传入 SAPI 失败。"""
    sentences = [s.strip() for s in re.split(r"(?<=[。！？.!?])\s*", text) if s.strip()]
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += sentence + " "
        else:
            if current:
                chunks.append(current.strip())
            if len(sentence) > max_len:
                for i in range(0, len(sentence), max_len):
                    chunks.append(sentence[i : i + max_len])
                current = ""
            else:
                current = sentence + " "
    if current:
        chunks.append(current.strip())
    logging.info("文本已拆分为 %d 段，每段最大长度 %d", len(chunks), max_len)
    return chunks if chunks else [text]


def speak_chunk_to_wav(text_chunk: str, wav_path: str, voice_name: str | None):
    """将单个文本片段合成为 wav 文件。"""
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    constants = win32com.client.constants

    try:
        # 直接使用 SpFileStream 默认格式（SAPI 支持且稳定），
        # 避免为不支持的格式赋值导致 COM 异常 (-2147201022)。
        stream.Open(wav_path, getattr(constants, "SSFMCreateForWrite", 3))

        # 根据用户选择设置音色（支持 Desktop + OneCore）
        if voice_name and voice_name in VOICE_ID_MAP:
            try:
                token_id = VOICE_ID_MAP[voice_name]
                token = win32com.client.Dispatch("SAPI.SpObjectToken")
                token.SetId(token_id)
                speaker.Voice = token
                logging.info("使用音色：%s", voice_name)
            except Exception as e:
                logging.exception("设置音色失败，将使用默认音色：%s", e)

        speaker.AudioOutputStream = stream
        speaker.Speak(text_chunk)
        logging.info("片段已生成 wav：%s，长度：%d 字符", wav_path, len(text_chunk))
    finally:
        try:
            stream.Close()
        except Exception:
            pass
        speaker.AudioOutputStream = None
        pythoncom.CoUninitialize()

def text_to_speech(text, output_filename, voice_name: str | None, bitrate_label: str):
    pythoncom.CoInitialize()
    temp_dir = tempfile.mkdtemp(prefix="tts_temp_")
    temp_files = []
    try:
        ensure_ffmpeg()
        text_chunks = split_text(text)
        total = len(text_chunks)
        logging.info("开始合成，共 %d 段，输出文件：%s", total, output_filename)

        bitrate = BITRATE_MAP.get(bitrate_label, "192k")
        logging.info("目标 MP3 比特率：%s（选项：%s）", bitrate, bitrate_label)

        combined_audio = None
        for idx, chunk in enumerate(text_chunks, start=1):
            wav_path = os.path.join(temp_dir, f"chunk_{idx}.wav")
            temp_files.append(wav_path)

            progress["value"] = 10 + int(50 * idx / total)
            root.update_idletasks()

            speak_chunk_to_wav(chunk, wav_path, voice_name)

            segment = AudioSegment.from_wav(wav_path)
            combined_audio = segment if combined_audio is None else combined_audio + segment
            logging.info("已完成第 %d/%d 段拼接", idx, total)

        progress["value"] = 70
        root.update_idletasks()

        combined_audio.export(output_filename, format="mp3", bitrate=bitrate)
        logging.info("MP3 导出完成：%s", output_filename)

        progress["value"] = 100
        root.update_idletasks()
        label.config(text=f"Speech saved to {os.path.basename(output_filename)}")
    finally:
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        shutil.rmtree(temp_dir, ignore_errors=True)
        pythoncom.CoUninitialize()
    
async def edge_tts_async(text: str, voice_label: str, output_path: str):
    """使用 Edge TTS 将文本直接保存为 MP3。"""
    if Communicate is None:
        raise RuntimeError("未安装 edge-tts，请先执行：pip install edge-tts")

    voice = EDGE_VOICE_MAP.get(voice_label)
    if not voice:
        raise RuntimeError(f"未找到对应的 Edge TTS 音色：{voice_label}")

    logging.info("使用 Edge TTS 音色：%s (%s) 输出到 %s", voice_label, voice, output_path)
    communicator = Communicate(text, voice=voice)
    await communicator.save(output_path)


def edge_text_to_speech(text: str, output_path: str, voice_label: str):
    """同步包装 Edge TTS 调用，便于在 Tk 事件中使用。"""
    progress["value"] = 10
    root.update_idletasks()
    asyncio.run(edge_tts_async(text, voice_label, output_path))
    progress["value"] = 100
    root.update_idletasks()
    label.config(text=f"Speech saved to {os.path.basename(output_path)}")


def convert_to_speech():
    progress["value"] = 0
    root.update_idletasks()
    try:
        if not getattr(root, "filename", None):
            label.config(text="请先选择文件。")
            return

        with open(root.filename, "r", encoding="utf-8") as file:
            text_content = file.read().strip()

        if not text_content:
            label.config(text="文件内容为空，无法转换。")
            return

        progress["value"] = 5
        root.update_idletasks()

        output_filename = os.path.splitext(os.path.basename(root.filename))[0] + ".mp3"
        output_dir = os.path.dirname(root.filename) or os.getcwd()
        output_path = os.path.join(output_dir, output_filename)

        voice_name = voice_var.get().strip() or None
        quality_label = quality_var.get().strip() or "中（192kbps）"
        engine = engine_var.get().strip()

        if engine == "Edge TTS":
            edge_text_to_speech(text_content, output_path, voice_name)
        else:
            text_to_speech(text_content, output_path, voice_name, quality_label)

    except RuntimeError as err:
        label.config(text=str(err))
        logging.error("运行时错误：%s", err)
    except Exception as err:
        hr = getattr(err, "hresult", None) or getattr(err, "excepinfo", [None]*6)[5]
        label.config(text=f"转换失败：{err}（HRESULT: {hr}）")
        logging.exception("转换失败，HRESULT=%s", hr)

# Set up Tkinter GUI
root = Tk()
root.title("Text to Speech Converter")
root.geometry("420x320")

label = Label(root, text="Welcome! Please select a .txt file.", font=("Arial", 12))
label.pack(pady=10)

voice_var = StringVar()
quality_var = StringVar(value="中（192kbps）")
engine_var = StringVar(value="本地 SAPI")

frame_opts = ttk.Frame(root)
frame_opts.pack(pady=5)

Label(frame_opts, text="引擎：").grid(row=0, column=0, padx=5, pady=2, sticky="e")
combo_engine = ttk.Combobox(
    frame_opts,
    textvariable=engine_var,
    values=["本地 SAPI", "Edge TTS"],
    state="readonly",
    width=15,
)
combo_engine.grid(row=0, column=1, padx=5, pady=2, sticky="w")


def refresh_voice_list(*_args):
    engine = engine_var.get().strip()
    if engine == "Edge TTS":
        values = list(EDGE_VOICE_MAP.keys())
    else:
        # 确保已加载本地语音
        if not VOICE_ID_MAP:
            load_voices()
        values = list(VOICE_ID_MAP.keys())

    combo_voice["values"] = values
    if values:
        voice_var.set(values[0])


Label(frame_opts, text="音色：").grid(row=1, column=0, padx=5, pady=2, sticky="e")
combo_voice = ttk.Combobox(
    frame_opts,
    textvariable=voice_var,
    values=[],
    state="readonly",
    width=25,
)
combo_voice.grid(row=1, column=1, padx=5, pady=2)

btn_preview = ttk.Button(frame_opts, text="试听", command=preview_voice)
btn_preview.grid(row=1, column=2, padx=5, pady=2)

combo_engine.bind("<<ComboboxSelected>>", refresh_voice_list)

# 初始化音色列表为本地 SAPI
load_voices()
refresh_voice_list()

Label(frame_opts, text="音质：").grid(row=2, column=0, padx=5, pady=2, sticky="e")
combo_quality = ttk.Combobox(
    frame_opts,
    textvariable=quality_var,
    values=list(BITRATE_MAP.keys()),
    state="readonly",
    width=25,
)
combo_quality.grid(row=2, column=1, padx=5, pady=2)
combo_quality.current(1)  # 默认中等 192kbps

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=5)

button_select = ttk.Button(root, text="Select File", command=select_file)
button_select.pack(pady=5)

button_convert = ttk.Button(root, text="Convert to Speech", command=convert_to_speech)
button_convert.pack(pady=5)

root.mainloop()
