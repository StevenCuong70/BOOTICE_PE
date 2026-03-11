#!/usr/bin/env python3
"""Fido - Windows ISO Downloader (Simplified)"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import re
import uuid
import time
import threading
import os
import sys
from datetime import datetime, timezone

# ============================================================================
# Config
# ============================================================================
APP_TITLE = "ISO Downloader Fido MS link"
TIMEOUT = 30
PROFILE_ID = "606624d44113"
INSTANCE_ID = "560dc9f3-1aa5-4a2f-b63c-9e18f8d0e175"
ORG_ID = "y6jn8c31"
LOCALE = "en-US"
session_ids = [None, None]

VERSIONS = [
    {
        "name": "Windows 11", "page": "windows11",
        "releases": [{
            "name": "25H2 (Build 26200.6584 - 2025.10)",
            "editions": [
                {"name": "Windows 11 Home/Pro/Edu", "ids": [3262, 3265]},
            ],
        }]
    },
    {
        "name": "Windows 10", "page": "Windows10ISO",
        "releases": [{
            "name": "22H2 v1 (Build 19045.2965 - 2023.05)",
            "editions": [
                {"name": "Windows 10 Home/Pro/Edu", "ids": [2618]},
            ]
        }]
    },
]

# ============================================================================
# API Functions
# ============================================================================
def api_get(url, **kw):
    """GET request wrapper."""
    return requests.get(url, timeout=TIMEOUT, allow_redirects=False, **kw)

def api_get_json(url, **kw):
    """GET request returning JSON."""
    r = requests.get(url, timeout=TIMEOUT, **kw)
    return r.json()

def fetch_languages(edition_ids):
    """Fetch available languages from Microsoft."""
    global session_ids
    languages = {}

    for si, eid in enumerate(edition_ids):
        sid = str(uuid.uuid4())
        session_ids[si] = sid

        # 1) Whitelist session
        api_get(f"https://vlscppe.microsoft.com/tags?org_id={ORG_ID}&session_id={sid}")

        # 2) Get ov-df params
        r = api_get(f"https://ov-df.microsoft.com/mdt.js?instanceId={INSTANCE_ID}&PageId=si&session_id={sid}")
        w = re.search(r'[?&]w=([A-F0-9]+)', r.text)
        rt = re.search(r'rticks\=\"\+?(\d+)', r.text)
        if not w or not rt:
            raise Exception("Cannot extract ov-df data")

        # 3) Reply ov-df
        mdt = int(datetime.now(timezone.utc).timestamp() * 1000)
        api_get(f"https://ov-df.microsoft.com/?session_id={sid}&CustomerId={INSTANCE_ID}"
                f"&PageId=si&w={w[1]}&mdt={mdt}&rticks={rt[1]}")

        # 4) Get SKU info
        url = (f"https://www.microsoft.com/software-download-connector/api/"
               f"getskuinformationbyproductedition?profile={PROFILE_ID}"
               f"&productEditionId={eid}&SKU=undefined&friendlyFileName=undefined"
               f"&Locale={LOCALE}&sessionID={sid}")

        for attempt in range(3):
            if attempt: time.sleep(2)
            data = api_get_json(url)
            if data.get("Errors"):
                if attempt < 2: continue
                raise Exception(data["Errors"][0].get("Value", "API Error"))
            for sku in data.get("Skus", []):
                lang = sku["Language"]
                if lang not in languages:
                    languages[lang] = {"display": sku["LocalizedLanguage"], "data": []}
                languages[lang]["data"].append({"si": si, "sku": sku["Id"]})
            if languages: break

    if not languages:
        raise Exception("No languages found")

    # Filter: only English and Vietnamese
    filtered = {}
    for k, v in languages.items():
        kl = k.lower()
        if "english" in kl or "vietnam" in kl or "tiếng việt" in v["display"].lower():
            filtered[k] = v

    return filtered if filtered else languages

def fetch_links(selected_lang):
    """Fetch download links for selected language."""
    links = []
    for entry in selected_lang["data"]:
        sid = session_ids[entry["si"]]
        url = (f"https://www.microsoft.com/software-download-connector/api/"
               f"GetProductDownloadLinksBySku?profile={PROFILE_ID}"
               f"&productEditionId=undefined&SKU={entry['sku']}"
               f"&friendlyFileName=undefined&Locale={LOCALE}&sessionID={sid}")

        data = api_get_json(url, headers={"Referer": "https://www.microsoft.com/software-download/windows11"})

        if data.get("Errors"):
            etype = data["Errors"][0].get("Type", 0)
            if etype == 9:
                raise Exception("IP banned by Microsoft (code 715-123130). Try later.")
            raise Exception(data["Errors"][0].get("Value", "API Error"))

        for opt in data.get("ProductDownloadOptions", []):
            arch_map = {0: "x86", 1: "x64", 2: "ARM64"}
            links.append({
                "arch": arch_map.get(opt["DownloadType"], "Unknown"),
                "url": opt["Uri"]
            })

    if not links:
        raise Exception("No download links found")
    return links

def human_size(n):
    """Convert bytes to human readable."""
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

# ============================================================================
# Download with progress
# ============================================================================
def download_file(url, filepath, progress_cb=None, done_cb=None, error_cb=None):
    """Download file with progress callback."""
    try:
        r = requests.get(url, stream=True, timeout=TIMEOUT * 10)
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb and total:
                        progress_cb(downloaded, total)

        if done_cb:
            done_cb(filepath, total)
    except Exception as e:
        if error_cb:
            error_cb(str(e))

# ============================================================================
# GUI Application
# ============================================================================
class FidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.resizable(False, False)
        self.root.geometry("420x200")
        self._center()

        self.stage = 0
        self.rows = []       # dynamic combo rows
        self.data = {}       # stored selections
        self.downloading = False

        self._build()

    def _center(self):
        self.root.update_idletasks()
        w, h = 420, 200
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        self.frame = tk.Frame(self.root, padx=12, pady=8)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Version row (always visible)
        self._add_label(self.frame, "Version")
        self.ver_combo = self._add_combo(self.frame, [v["name"] for v in VERSIONS])

        # Dynamic rows container
        self.dyn_frame = tk.Frame(self.frame)
        self.dyn_frame.pack(fill=tk.X)

        # Progress bar (hidden)
        self.progress_frame = tk.Frame(self.frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var,
                                             maximum=100, length=390)
        self.progress_bar.pack(fill=tk.X, pady=(4, 0))
        self.progress_label = tk.Label(self.progress_frame, text="", font=("Segoe UI", 9), fg="gray")
        self.progress_label.pack(fill=tk.X)

        # Buttons
        self.btn_frame = tk.Frame(self.frame)
        self.btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_ok = tk.Button(self.btn_frame, text="Continue", font=("Segoe UI", 10),
                                width=18, command=self._next)
        self.btn_ok.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_back = tk.Button(self.btn_frame, text="Close", font=("Segoe UI", 10),
                                  width=18, command=self._back)
        self.btn_back.pack(side=tk.LEFT)

        # Status
        self.status = tk.Label(self.root, text="", font=("Segoe UI", 8), fg="gray", anchor="w")
        self.status.pack(fill=tk.X, padx=12, pady=(0, 4))

    def _add_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 10), anchor="w").pack(fill=tk.X)

    def _add_combo(self, parent, values, idx=0):
        c = ttk.Combobox(parent, values=values, state="readonly", font=("Segoe UI", 10))
        c.pack(fill=tk.X, pady=(2, 6))
        if values: c.current(min(idx, len(values) - 1))
        return c

    def _add_row(self, label, values, idx=0):
        """Add dynamic combo row."""
        f = tk.Frame(self.dyn_frame)
        f.pack(fill=tk.X)
        self._add_label(f, label)
        combo = self._add_combo(f, values, idx)
        self.rows.append({"frame": f, "combo": combo, "values": values})
        self._grow()
        return combo

    def _pop_row(self):
        """Remove last dynamic row."""
        if self.rows:
            r = self.rows.pop()
            r["frame"].destroy()
            self._shrink()

    DH = 52

    def _grow(self):
        g = self.root.geometry().split("+")[0]
        w, h = map(int, g.split("x"))
        self.root.geometry(f"{w}x{h + self.DH}")

    def _shrink(self):
        g = self.root.geometry().split("+")[0]
        w, h = map(int, g.split("x"))
        self.root.geometry(f"{w}x{max(200, h - self.DH)}")

    def _set_busy(self, busy, msg=""):
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_ok.config(state=state)
        self.btn_back.config(state=state)
        self.status.config(text=msg)
        self.root.update_idletasks()

    def _error(self, msg):
        self._set_busy(False)
        messagebox.showerror("Error", msg)

    # ---- Navigation ----
    def _next(self):
        self.stage += 1
        if self.stage == 1:   self._s1_version()
        elif self.stage == 2: self._s2_release()
        elif self.stage == 3: self._s3_edition()
        elif self.stage == 4: self._s4_language()
        elif self.stage == 5: self._s5_download()

    def _back(self):
        if self.downloading:
            return
        if self.stage == 0:
            self.root.destroy()
            return

        self._pop_row()

        # Re-enable previous combo
        if self.rows:
            self.rows[-1]["combo"].config(state="readonly")
        else:
            self.ver_combo.config(state="readonly")

        self.stage -= 1
        self.btn_ok.config(text="Continue")
        self.btn_back.config(text="Close" if self.stage == 0 else "Back")

        # Hide progress if going back from download
        self.progress_frame.pack_forget()
        self.status.config(text="")

    # ---- Stages ----
    def _s1_version(self):
        """Version -> Releases."""
        vi = self.ver_combo.current()
        self.data["vi"] = vi
        self.ver_combo.config(state="disabled")

        releases = VERSIONS[vi]["releases"]
        self._add_row("Release", [r["name"] for r in releases])
        self.btn_back.config(text="Back")

    def _s2_release(self):
        """Release -> Editions."""
        ri = self.rows[0]["combo"].current()
        self.data["ri"] = ri
        self.rows[0]["combo"].config(state="disabled")

        eds = VERSIONS[self.data["vi"]]["releases"][ri]["editions"]
        self._add_row("Edition", [e["name"] for e in eds])

    def _s3_edition(self):
        """Edition -> Languages (async)."""
        ei = self.rows[1]["combo"].current()
        self.data["ei"] = ei
        self.rows[1]["combo"].config(state="disabled")

        eds = VERSIONS[self.data["vi"]]["releases"][self.data["ri"]]["editions"]
        self.data["eids"] = eds[ei]["ids"]

        self._set_busy(True, "Fetching languages...")

        def work():
            try:
                langs = fetch_languages(self.data["eids"])
                self.root.after(0, lambda: self._s3_done(langs))
            except Exception as e:
                self.root.after(0, lambda: self._s3_err(str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _s3_done(self, langs):
        self.data["langs"] = langs
        keys = list(langs.keys())
        displays = [langs[k]["display"] for k in keys]

        # Auto-select: prefer English
        idx = 0
        for i, k in enumerate(keys):
            if "english" in k.lower():
                idx = i
                break

        self._add_row("Language", displays, idx)
        self._set_busy(False)

    def _s3_err(self, msg):
        self.stage -= 1
        self.rows[-1]["combo"].config(state="readonly")
        self._error(msg)

    def _s4_language(self):
        """Language -> Arch links (async)."""
        li = self.rows[2]["combo"].current()
        self.rows[2]["combo"].config(state="disabled")

        keys = list(self.data["langs"].keys())
        self.data["lang"] = self.data["langs"][keys[li]]

        self._set_busy(True, "Fetching download links...")

        def work():
            try:
                links = fetch_links(self.data["lang"])
                self.root.after(0, lambda: self._s4_done(links))
            except Exception as e:
                self.root.after(0, lambda: self._s4_err(str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _s4_done(self, links):
        self.data["links"] = links
        archs = [l["arch"] for l in links]

        # Auto-select x64
        idx = 0
        import platform
        pa = platform.machine().lower()
        prefer = "x64" if pa in ("x86_64", "amd64") else ("ARM64" if pa in ("aarch64", "arm64") else "x86")
        for i, a in enumerate(archs):
            if a == prefer:
                idx = i
                break

        self._add_row("Architecture", archs, idx)
        self.btn_ok.config(text="Download")
        self._set_busy(False)

    def _s4_err(self, msg):
        self.stage -= 1
        self.rows[-1]["combo"].config(state="readonly")
        self._error(msg)

    def _s5_download(self):
        """Start download."""
        ai = self.rows[3]["combo"].current()
        self.rows[3]["combo"].config(state="disabled")
        link = self.data["links"][ai]
        url = link["url"]

        # Extract filename
        m = re.search(r'/([^/?]+\.iso)', url)
        default_name = m.group(1) if m else "windows.iso"

        # Ask save location
        filepath = filedialog.asksaveasfilename(
            title="Save ISO",
            initialfile=default_name,
            defaultextension=".iso",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )

        if not filepath:
            self.stage -= 1
            self.rows[-1]["combo"].config(state="readonly")
            return

        # Show progress
        self.progress_frame.pack(fill=tk.X, pady=(6, 0), before=self.btn_frame)
        self._grow()
        self.progress_var.set(0)
        self.progress_label.config(text="Starting download...")
        self.downloading = True
        self._set_busy(True, "Downloading...")

        def on_progress(done, total):
            pct = done / total * 100
            self.root.after(0, lambda: self._update_progress(done, total, pct))

        def on_done(path, total):
            self.root.after(0, lambda: self._download_done(path, total))

        def on_error(msg):
            self.root.after(0, lambda: self._download_error(msg))

        threading.Thread(target=download_file, args=(url, filepath, on_progress, on_done, on_error),
                         daemon=True).start()

    def _update_progress(self, done, total, pct):
        self.progress_var.set(pct)
        self.progress_label.config(text=f"{human_size(done)} / {human_size(total)} ({pct:.1f}%)")
        self.root.update_idletasks()

    def _download_done(self, path, total):
        self.downloading = False
        self.progress_var.set(100)
        self.progress_label.config(text=f"Done! {human_size(total)}")
        self._set_busy(False, "Download complete!")
        messagebox.showinfo("Done", f"Downloaded successfully!\n\n{path}\n{human_size(total)}")

    def _download_error(self, msg):
        self.downloading = False
        self._set_busy(False)
        self._error(f"Download failed: {msg}")

# ============================================================================
# Main
# ============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = FidoApp(root)
    root.mainloop()