## Text to Speech (TTS) to MP3 Tool for Windows

This is a **Python-based graphical Text to Speech (TTS) tool for Windows**.  
It reads local `.txt` files and converts the text into **MP3 audio files** using either the **local Windows SAPI voices** or **Edge TTS cloud voices**.

> Keywords (for better GitHub discoverability):  
> `python` / `text to speech` / `tts` / `text to mp3` / `text2speech` / `speech synthesis` / `audio` / `mp3`

---

### Features

- **GUI-based operation**: Built with `tkinter`, supports file selection, progress bar and status hints.
- **Multiple TTS engines**:
  - Local SAPI (Desktop + OneCore voices, e.g. Xiaoxiao, Yunxi, etc.).
  - Edge TTS cloud voices (optional, requires `edge-tts` and internet connection).
- **Configurable MP3 quality**: 3 bitrates – High (320 kbps), Medium (192 kbps), Low (128 kbps).
- **Smart long-text splitting**: Splits text by punctuation (period, question mark, etc.) to avoid synthesis failures when sending very long text at once.
- **Automatic temp file cleanup**: Removes intermediate WAV segments after MP3 generation to save disk space.

---

### Requirements

- OS: **Windows 10 / 11** (with SAPI & OneCore voice support)
- Python: **3.9+** recommended
- **ffmpeg** installed (used by `pydub` to process audio)
  - Download from the official website: `https://ffmpeg.org/`
  - Add `ffmpeg` to the system `PATH` environment variable after installation.

---

### Installation

1. **Clone or download this repository**
   - Place the code in any directory, e.g. `C:\Projects\texttomp3\`

2. **(Optional but recommended) Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   > Notes:  
   > - `pywin32` is used to access the Windows SAPI voice API.  
   > - `pydub` is used to concatenate and export MP3 audio (depends on ffmpeg).  
   > - `edge-tts` is optional, used for Edge TTS cloud voices.

4. **Verify ffmpeg is available**
   - Run in terminal:

   ```bash
   ffmpeg -version
   ```

   If you see version info, `ffmpeg` is configured correctly.

---

### Usage

1. Run the program in the project directory:

   ```bash
   python texttomp3.py
   ```

2. In the GUI window:
   - Click **“Select File”** to choose a UTF-8 encoded `.txt` file.
   - In the **Engine** dropdown:
     - `Local SAPI`: Use Windows built-in / installed voices.
     - `Edge TTS`: Use cloud neural voices (requires `edge-tts` and internet).
   - In the **Voice** dropdown: choose a specific voice.  
     For local SAPI, voices will be enumerated automatically on first selection.
   - In the **Quality** dropdown: choose the target MP3 bitrate.
   - (Optional) Click **“Preview”** to listen to a short sample before full conversion.
   - Click **“Convert to Speech”** to start conversion.  
     The progress bar will show the approximate progress.

3. After conversion:
   - The MP3 file will be saved in the **same directory as the source `.txt` file**.  
     The file name will be the same as the text file, with the `.mp3` extension.
   - A status label at the bottom of the window will show the final result.

---

### FAQ

- **ffmpeg not found**
  - Please make sure `ffmpeg` is installed and added to the system `PATH`.

- **Edge TTS does not work**
  - Make sure you have installed:

    ```bash
    pip install edge-tts
    ```

  - And verify that the selected voice exists in the Edge TTS voice list.

- **Local voice list is empty or very limited**
  - Install additional language packs / voices in Windows Settings (e.g. Chinese, English voices), then reopen the program.

---

### Project Structure

- `texttomp3.py`: Main script, includes the GUI and text-to-speech / audio export logic.
- `requirements.txt`: Python dependencies.
- `doc/`: Change logs and additional documentation.
- `README.md`: Chinese README.
- `README.en.md`: English README (this file).

---

### Typical Use Cases

- Convert ebooks / online articles to MP3 to listen on phones or in the car.
- Generate narration audio for videos / short videos.
- Create spoken versions of study materials (e.g. vocabulary lists, texts).
- Use as a base for automation scripts that batch-convert text to speech.

---

### Disclaimer

This project is for learning and personal use only.  
Please comply with all applicable laws, regulations, and service terms when using synthesized speech, and **do not** use the generated audio for illegal activities or to infringe others’ rights.  
The author assumes no responsibility for any legal issues arising from misuse of this project.


