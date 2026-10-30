# 萬用影片下載器 (Video Downloader)

以 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 為核心的 Windows 桌面下載器，介面使用 PySide6。支援 YouTube、TikTok、Bilibili，以及 yt-dlp 支援的其他網站。

## 功能

- 貼上網址，自動解析標題、時長與可用畫質
- 選擇畫質，或僅下載音訊（mp3 / m4a）
- 播放清單、下載佇列、進度、取消、開啟檔案位置
- cookies.txt 與代理設定（程式只使用 cookies.txt 的暫存複本，不會改動原檔）
- 內附 ffmpeg，不需另外安裝

## 開發

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m app.main
.venv\Scripts\python -m pytest
```

打包需要把 ffmpeg 放進 `bin/`（ffmpeg.exe、ffprobe.exe 與其 DLL，建議 LGPL shared 版），然後：

```bash
.venv\Scripts\python -m PyInstaller build/ytdlpgui.spec --noconfirm --distpath dist --workpath build/work
```

安裝程式用 Inno Setup 6 編譯 `build/installer.iss`。

## 已知限制

- Bilibili 的 CDN 會對整檔請求回 HTTP 567，程式對 Bilibili 改用分段（Range）下載。
- YouTube 可能要求登入確認，需要匯出 cookies.txt。
- 安裝程式與執行檔沒有程式碼簽章，Windows SmartScreen 可能顯示警告。

## 使用須知

僅供下載你自己的內容或已獲授權的內容。下載他人影片可能違反平台條款或著作權，責任由使用者自行承擔。cookies.txt 等同登入憑證，請勿分享或提交到版本庫。

## 授權

本專案採用 [The Unlicense](LICENSE)（與 yt-dlp 相同），釋出為公眾領域。第三方元件與其授權見 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
