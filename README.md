# 🎃 阿威相片 👻

萬聖節恐怖風格的**本機相片 / 影片管理網頁**（Flask）。
深夜的破碎老城街上，骷髏人、紅眼死神與巫婆不規則地穿行——而你的照片，就在牠們身旁展出。

![theme](https://img.shields.io/badge/theme-Halloween%20Horror-a1122c)
![stack](https://img.shields.io/badge/stack-Flask%20%2B%20HTML%2FCSS%2FJS-c94f0d)

## ✨ 功能

- 📁 左側資料夾導覽，右側相片牆（递归掃描所有子資料夾）
- 🖼️ 支援 jpg / jpeg / png / gif / webp / **mov 影片**（影片可在格內直接播放）
- 🔍 燈箱放大檢視（圖片全幅 / 影片全畫面播放，鍵盤 ← → Esc 操作）
- 🎃 拖曳上傳或點按多選上傳（中文檔名完整支援，同名自動加 ` (n)`）
- 🔒 路徑遍歷攻擊防護：所有檔案存取被鎖定在照片根目錄內

## 🚀 本機執行

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 啟動（預設監聽 http://127.0.0.1:5000）
python app.py
```

照片目錄預設為 `D:\照片`（不存在會自動建立）。
若要改用其他路徑，修改 `app.py` 頂部的 `PHOTOS_DIR` 即可。

## ⚠️ 關於本儲存庫的 GitHub Pages 版本

GitHub Pages 只能託管**靜態檔案**，無法執行 Python/Flask 後端。
因此線上版本是**離線展示模式**：可以看到完整的萬聖節老街場景與妖怪動畫，
但照片牆為空（無法讀取本機檔案）。要使用完整的瀏覽 / 上傳功能，請在本機執行 `python app.py`。

## 📁 專案結構

```
awei_photos_app/
├── app.py               # Flask 後端（清單/圖片/影片/上傳 API + 安全檢查）
├── requirements.txt     # flask, werkzeug
└── templates/
    └── index.html       # 前端單檔（HTML/CSS/JS 全整合，含 SVG 場景動畫）
```

## 🛡️ 安全設計

- 上傳檔名清洗：剝離路徑成分、移除 Windows 非法字元、保留中文
- `resolve_photo()`：`resolve()` 後必須仍位於照片目錄內（`relative_to` 包含檢查）
- 副檔名白名單：jpg / jpeg / png / gif / webp / mov
- 僅監聽 `127.0.0.1`（預設不对外开放網路）

## 📄 License

MIT
