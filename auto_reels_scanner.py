# ponytail: fast pipeline using persistent ADB shell pipe and 0.45s UI snap delay.
import cv2
import glob
import numpy as np
import os
import subprocess
import sys
import time

ADB = r".\adb.exe"

class PersistentShell:
    def __init__(self):
        self.proc = subprocess.Popen([ADB, "shell"], stdin=subprocess.PIPE, text=True)

    def swipe_next(self):
        self.proc.stdin.write("input swipe 360 1250 360 250 90\n")
        self.proc.stdin.flush()

    def toggle_pause(self):
        self.proc.stdin.write("input tap 360 800\n")
        self.proc.stdin.flush()

    def close(self):
        try:
            self.proc.terminate()
        except Exception:
            pass

def capture_screen():
    res = subprocess.run([ADB, "exec-out", "screencap", "-p"], capture_output=True)
    if res.stdout and len(res.stdout) > 50000:
        arr = np.frombuffer(res.stdout, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return None

def is_friend_like_reel(img):
    if img is None:
        return False, None
        
    h, w, _ = img.shape
    if (w, h) != (720, 1604):
        img = cv2.resize(img, (720, 1604))
        
    bubble_zone = img[1180:1280, 35:140]
    hsv = cv2.cvtColor(bubble_zone, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([145, 130, 150]), np.array([179, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    heart_meta = None
    for c in contours:
        area = cv2.contourArea(c)
        if 480 <= area <= 650:
            x, y, cw, ch = cv2.boundingRect(c)
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            aspect = cw / float(ch)
            
            if solidity >= 0.78 and (34 <= cw <= 43) and (23 <= ch <= 32) and (1.20 <= aspect <= 1.65):
                if 50 <= x <= 85 and 28 <= y <= 65:
                    heart_meta = (35 + x, 1180 + y, cw, ch)
                    break
                    
    if not heart_meta:
        return False, None
        
    creator_zone = img[1300:1395, 35:140]
    gray = cv2.cvtColor(creator_zone, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    if cv2.countNonZero(edges) < 100:
        return False, None
        
    return True, heart_meta

def update_gallery():
    files = sorted(glob.glob("found_reels/reel_*.png"), key=lambda f: os.path.getmtime(f), reverse=True)
    cards = ""
    for f in files:
        name = os.path.basename(f)
        cards += f"""
        <div class="card" onclick="openModal('{f}')">
            <img src="{f}" alt="{name}" loading="lazy">
            <div class="meta">{name}</div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="5">
<title>Instagram Liked Reels Gallery</title>
<style>
  body {{ margin: 0; background: #121212; color: #fff; font-family: -apple-system, sans-serif; padding: 20px; }}
  h1 {{ font-size: 22px; margin-bottom: 8px; }}
  p {{ color: #aaa; margin-top: 0; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }}
  .card {{ background: #1e1e1e; border-radius: 12px; overflow: hidden; cursor: pointer; border: 1px solid #2a2a2a; transition: transform 0.15s; }}
  .card:hover {{ transform: scale(1.02); border-color: #e1306c; }}
  .card img {{ width: 100%; height: 360px; object-fit: cover; display: block; }}
  .card .meta {{ padding: 10px; font-size: 13px; font-weight: bold; color: #eee; text-align: center; }}
  #modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; z-index: 100; }}
  #modal img {{ max-height: 90vh; max-width: 90vw; border-radius: 8px; }}
</style>
</head>
<body>
<h1>Instagram Liked Reels ({len(files)} Terverifikasi)</h1>
<p>Auto-refresh setiap 5 detik.</p>
<div class="grid">
  {cards}
</div>
<div id="modal" onclick="this.style.display='none'"><img id="modal-img"></div>
<script>
function openModal(src) {{
  document.getElementById('modal-img').src = src;
  document.getElementById('modal').style.display = 'flex';
}}
</script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as out:
        out.write(html)

def main():
    max_reels = 100
    for arg in sys.argv[1:]:
        if arg.isdigit():
            max_reels = int(arg)
            
    os.makedirs("found_reels", exist_ok=True)
    update_gallery()
    shell = PersistentShell()
    
    print("=== Auto Reels Scanner (TURBO MODE) ===")
    print(f"Target: {max_reels} reels | Kecepatan: ~1.2s / reel | Gallery: http://localhost:8080/index.html\n")
    
    existing = glob.glob("found_reels/reel_*.png")
    found_total = len(existing)
    scanned = 0
    
    # Cek layar awal
    img = capture_screen()
    hit, bbox = is_friend_like_reel(img)
    if hit:
        found_total += 1
        shell.toggle_pause()
        save_path = f"found_reels/reel_{found_total}.png"
        cv2.imwrite(save_path, img)
        update_gallery()
        print(f"[KETEMU #{found_total}] Bubble teman valid di layar awal! Posisi: {bbox}")
        time.sleep(3.0)
        shell.toggle_pause()

    try:
        while scanned < max_reels:
            scanned += 1
            print(f"[{scanned}/{max_reels}] Fast scanning...", end="\r", flush=True)
            shell.swipe_next()
            time.sleep(0.45) # snap delay
            
            img = capture_screen()
            hit, bbox = is_friend_like_reel(img)
            if hit:
                found_total += 1
                shell.toggle_pause()
                save_path = f"found_reels/reel_{found_total}.png"
                cv2.imwrite(save_path, img)
                update_gallery()
                print(f"\n>>> [KETEMU #{found_total}] Bubble like teman terdeteksi! (Reel #{scanned})")
                print(f"-> Lokasi badge: {bbox}")
                print(f"-> Tersimpan: {save_path} | Web terupdate.")
                time.sleep(3.5)
                shell.toggle_pause()
    finally:
        shell.close()
            
    update_gallery()
    print(f"\nSelesai scan {scanned} reels. Total reels asli tersimpan: {found_total}.")

if __name__ == "__main__":
    main()
