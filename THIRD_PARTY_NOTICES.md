# Third-party notices

發行版（壓縮版與安裝程式）內含下列第三方元件，各自適用其授權。

| 元件 | 用途 | 授權 | 來源 |
|---|---|---|---|
| yt-dlp | 影片解析與下載 | The Unlicense | https://github.com/yt-dlp/yt-dlp |
| FFmpeg (LGPL, shared build) | 影音合併與轉檔 | LGPL v2.1+ | https://github.com/BtbN/FFmpeg-Builds |
| PySide6 / Qt for Python | 使用者介面 | LGPL v3 | https://www.qt.io/qt-for-python |
| Python | 執行環境 | PSF License | https://www.python.org |

FFmpeg 以動態連結（DLL）方式隨附，可自行以相容版本替換 `_internal\bin` 內的 ffmpeg.exe、ffprobe.exe 與 DLL。FFmpeg 原始碼可由上述來源取得。
PySide6 同樣為動態連結，可替換其 DLL。完整授權文字請參閱各專案網站。
