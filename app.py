# -*- coding: utf-8 -*-
"""🎃 阿威相片 👻 — 萬聖節風格本機相片管理 (Flask)

讀取/寫入 D:\照片，嚴格防止路徑遍歷攻擊。
啟動:  python app.py  →  http://127.0.0.1:5000
"""
import re
from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, jsonify, render_template, request, send_file

# ── 設定 ─────────────────────────────────────────────
PHOTOS_DIR = Path(r"D:\照片")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)          # 不存在則自動建立
PHOTOS_DIR_RESOLVED = PHOTOS_DIR.resolve()

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mov"}
MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".mov": "video/quicktime",
}

app = Flask(__name__, template_folder=".")  # index.html 放在專案根目錄（兼作 GitHub Pages 首頁）
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB


# ── 安全性工具 ────────────────────────────────────────
def sanitize_filename(name: str):
    """清洗上傳檔名：剝離任何路徑成分、保留中文、移除 Windows 非法字元。"""
    if not name:
        return None
    name = name.replace("\\", "/").split("/")[-1]        # 只取 basename
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name)   # 非法字元 → _
    name = name.strip().strip(".").strip()
    if not name or name in (".", ".."):
        return None
    return name


def resolve_photo(name: str):
    """將名稱解析到 D:\照片 內的真實檔案；任何路徑遍歷一律拒絕 (回傳 None)。"""
    if not name or "\x00" in name:
        return None
    candidate = (PHOTOS_DIR / name).resolve()
    try:
        candidate.relative_to(PHOTOS_DIR_RESOLVED)       # 必須仍落在 D:\照片 內
    except (ValueError, OSError):
        return None
    if not candidate.is_file():
        return None
    if candidate.suffix.lower() not in ALLOWED_EXTS:
        return None
    return candidate


def unique_path(filename: str) -> Path:
    """同檔名重複上傳時自動加 (1)、(2)… 避免覆蓋。"""
    target = PHOTOS_DIR / filename
    if not target.exists():
        return target
    if "." in filename:
        stem, suffix = filename.rsplit(".", 1)
    else:
        stem, suffix = filename, ""
    i = 1
    while True:
        new_name = f"{stem} ({i}).{suffix}" if suffix else f"{stem} ({i})"
        target = PHOTOS_DIR / new_name
        if not target.exists():
            return target
        i += 1


# ── 路由 ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/photos")
def api_photos():
    """列出 D:\照片 內（含所有子資料夾）的支援圖片。

    回傳欄位: name(檔名)、rel(相對路徑, 正斜線)、folder(子資料夾, 根目錄為 "")、
    size、mtime、url。排序: 先資料夾(根目錄優先)、再新檔優先。
    """
    items = []
    if not PHOTOS_DIR.exists():
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    for p in PHOTOS_DIR.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in ALLOWED_EXTS:
            continue
        rel = p.relative_to(PHOTOS_DIR).as_posix()
        st = p.stat()
        items.append({
            "name": p.name,
            "rel": rel,
            "folder": rel.rsplit("/", 1)[0] if "/" in rel else "",
            "kind": "video" if p.suffix.lower() == ".mov" else "image",
            "size": st.st_size,
            "mtime": st.st_mtime,
            "url": "/photo/" + quote(rel),
        })
    items.sort(key=lambda x: x["mtime"], reverse=True)
    items.sort(key=lambda x: x["folder"])
    return jsonify({"count": len(items), "photos": items})


@app.route("/api/folders")
def api_folders():
    """列出 D:\照片 下所有資料夾（含沒有照片的子資料夾）。

    回傳欄位: rel(相對路徑, 根目錄為 "")、name(資料夾名)、depth(深度)、
    count(該資料夾「直接」底下的支援圖片數)。
    """
    if not PHOTOS_DIR.exists():
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    dirs = [PHOTOS_DIR]
    for d in PHOTOS_DIR.rglob("*"):
        if d.is_dir():
            dirs.append(d)
    items = []
    for d in dirs:
        rel = d.relative_to(PHOTOS_DIR).as_posix()
        if rel == ".":
            rel = ""
        count = sum(
            1 for f in d.iterdir()
            if f.is_file() and f.suffix.lower() in ALLOWED_EXTS
        )
        items.append({
            "rel": rel,
            "name": d.name if rel else "",
            "depth": len(rel.split("/")) if rel else 0,
            "count": count,
        })
    items.sort(key=lambda x: x["rel"])
    return jsonify({"count": len(items), "folders": items})


@app.route("/photo/<path:name>")
def photo(name):
    """顯示圖片（僅限 D:\照片 內）。"""
    p = resolve_photo(name)
    if not p:
        abort(404)
    return send_file(
        p,
        mimetype=MIME.get(p.suffix.lower(), "application/octet-stream"),
        conditional=True,
    )


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """接收多檔上傳 (multipart 欄位名: files)，存入 D:\照片。"""
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "no files"}), 400
    created, errors = [], []
    for f in files:
        raw = f.filename or ""
        name = sanitize_filename(raw)
        if not name:
            errors.append(f"invalid filename: {raw!r}")
            continue
        if Path(name).suffix.lower() not in ALLOWED_EXTS:
            errors.append(f"unsupported type: {name}")
            continue
        target = unique_path(name)
        f.save(target)
        created.append(target.name)
    return jsonify({"created": created, "errors": errors})


if __name__ == "__main__":
    print(f"🎃 阿威相片伺服器已啟動: http://127.0.0.1:5000  (照片目錄: {PHOTOS_DIR})")
    app.run(host="0.0.0.0", port=5000, debug=False)
