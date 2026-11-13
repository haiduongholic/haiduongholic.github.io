"""Refresh the TikTok numbers shown on the Hải Dương Holic portfolio.

Reads each tracked video's public TikTok page, takes its view count and the channel's
follower / like / post counts, writes them into the data block of haiduongholic.html,
then rebuilds the standalone export. A video that cannot be read keeps its last value.

Usage: python update_stats.py   (run from this folder)
Exit code 1 means nothing could be read, so the page was left unchanged.
"""
import datetime
import json
import pathlib
import re
import sys
import time
import urllib.request

import build_export

ROOT = pathlib.Path(__file__).resolve().parent
PAGE = ROOT / "haiduongholic.html"
URL = "https://www.tiktok.com/@haiduongholic/video/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
BLOCK = re.compile(r'(<script type="application/json" id="hdh-data">)(.*?)(</script>)', re.S)
STATE = re.compile(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', re.S)


def fetch(video_id: str):
    req = urllib.request.Request(URL + video_id, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = STATE.search(html)
    if not m:
        return None
    item = json.loads(m.group(1))["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
    return int(item["stats"]["playCount"]), item.get("authorStats") or {}


def main() -> int:
    page = PAGE.read_text(encoding="utf-8")
    m = BLOCK.search(page)
    data = json.loads(m.group(2))
    ok, author = 0, {}
    for vid in list(data["views"]):
        got = None
        for attempt in range(4):  # TikTok sometimes serves a page without data; wait and retry
            try:
                got = fetch(vid)
            except Exception as e:  # network error, TikTok block, changed page layout
                print("retry", vid, type(e).__name__, e)
            if got:
                break
            time.sleep(4 + attempt * 6)
        if got:
            data["views"][vid] = got[0]
            author = author or got[1]
            ok += 1
        else:
            print("skip", vid, "(kept last value)")
        time.sleep(3)
    if not ok:
        print("No video could be read; page left unchanged.")
        return 1
    if author.get("followerCount"):
        data["followers"] = int(author["followerCount"])
        data["likes"] = int(author.get("heartCount") or author.get("heart") or data["likes"])
        data["posts"] = int(author.get("videoCount") or data["posts"])
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    data["updated"] = now.strftime("%H:%M %d/%m/%Y")
    blob = json.dumps(data, ensure_ascii=False)
    page = page[:m.start(2)] + blob + page[m.end(2):]
    PAGE.write_text(page, encoding="utf-8")
    build_export.build()
    print(f"Updated {ok}/{len(data['views'])} videos; followers {data['followers']}, "
          f"likes {data['likes']}, posts {data['posts']}, at {data['updated']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
