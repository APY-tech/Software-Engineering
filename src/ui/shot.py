# -*- coding: utf-8 -*-
"""用 Chrome 无头模式把所有界面 HTML 截成 PNG"""
import os, subprocess, glob, urllib.parse, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = os.path.join(BASE, "png")
os.makedirs(OUT, exist_ok=True)

DESKTOP = {"界面9", "界面10", "界面11", "界面12"}

files = sorted(glob.glob(os.path.join(BASE, "界面*.html")),
               key=lambda p: int("".join(c for c in os.path.basename(p) if c.isdigit())))
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    is_d = name in DESKTOP
    w, h, s = (1280, 820, 1.6) if is_d else (390, 844, 2)
    out = os.path.join(OUT, name + ".png")
    url = "file:///" + urllib.parse.quote(f.replace("\\", "/"))
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--force-device-scale-factor={s}", f"--window-size={w},{h}",
           f"--screenshot={out}", url, "--no-sandbox", "--virtual-time-budget=2500"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = os.path.exists(out)
    print(("OK  " if ok else "FAIL"), name, os.path.getsize(out) if ok else "", r.stderr.strip().splitlines()[-1:] if not ok else "")
