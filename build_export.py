"""Build the published site from haiduongholic.html.

Writes:
  docs/index.html                     the page served by GitHub Pages (images in docs/img/)
  docs/HaiDuongHolic-Portfolio.html   one self-contained file with every image embedded, for download

Usage: python build_export.py
"""
import base64
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
MIME = {".jpg": "image/jpeg", ".webp": "image/webp", ".png": "image/png"}

HEAD = "\n".join([
    "<!doctype html>", '<html lang="vi">', "<head>", '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
    '<meta name="theme-color" content="#F4EDE3">', '<meta name="color-scheme" content="light">',
    '<meta name="description" content="Portfolio review TikTok của kênh Hải Dương Holic, số liệu tự cập nhật.">',
    "<style>html{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>", ""])


def uri(p: pathlib.Path) -> str:
    return "data:" + MIME[p.suffix] + ";base64," + base64.b64encode(p.read_bytes()).decode()


def wrap(body: str) -> str:
    """Move the page's <title>/<style> into <head> and wrap the rest in <body>."""
    i = body.index("</style>") + len("</style>")
    return HEAD + body[:i] + "\n</head>\n<body>\n" + body[i:] + "\n</body>\n</html>\n"


def build() -> None:
    src = (ROOT / "haiduongholic.html").read_text(encoding="utf-8")
    DOCS.mkdir(exist_ok=True)

    # 1) Site page: same relative image paths, images copied next to it.
    shutil.copytree(ROOT / "img", DOCS / "img", dirs_exist_ok=True)
    (DOCS / "index.html").write_text(wrap(src), encoding="utf-8")

    # 2) Standalone download: every image embedded as a data URI.
    out = re.sub(r"img/[a-z0-9]+\.(?:jpg|webp|png)",
                 lambda m: uri(ROOT / m.group(0)) if (ROOT / m.group(0)).exists() else m.group(0), src)
    imgs = {p.stem[1:]: uri(p) for p in (ROOT / "img").glob("v*.jpg")}
    out = out.replace('function src(x) { return "img/v" + x.img + ".jpg"; }',
                      "function src(x) { return IMG[x.img]; }")
    out = out.replace("(function () {\n  var U", "var IMG = " + json.dumps(imgs) + ";\n(function () {\n  var U", 1)
    assert "img/" not in out.replace("data:image/", ""), "an image path was left unembedded"
    (DOCS / "HaiDuongHolic-Portfolio.html").write_text(wrap(out), encoding="utf-8")


if __name__ == "__main__":
    build()
    print("Built docs/index.html and docs/HaiDuongHolic-Portfolio.html")
