#!/usr/bin/env python3
"""
Username Availability Checker (GUI)
Checks username availability on: Snapchat, Twitter/X, Instagram, Telegram.
- Author: ViRuS-HaCkEr
- Note: This performs simple HTTP checks (HEAD/GET) and infers availability heuristically.
- Requirements: requests
"""

import threading
import requests
import time
import csv
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


BANNER_BG = "#063306"
WINDOW_BG = "#0b3a0b"
PANEL_BG = "#0f2f0f"
TEXT_FG = "#e8f5e9"
GOOD = "#3ad43a"
BAD = "#ff4242"
NEUTRAL = "#cccccc"

DEFAULT_TIMEOUT = 10
DEFAULT_DELAY = 0.6  
DEFAULT_WORKERS = 4
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UsernameChecker/1.0"

PLATFORMS = {
    "Twitter": {
        "url": "https://twitter.com/{u}",
        "method": "GET",
        "exists_status": 200,
        "not_found_signs": [404],
    },
    "Instagram": {
        "url": "https://www.instagram.com/{u}/",
        "method": "GET",
        "exists_status": 200,
        "not_found_signs": [404],
    },
    "Telegram": {
        "url": "https://t.me/{u}",
        "method": "GET",
        "exists_status": 200,
        "not_found_signs": [404],
    },
    "Snapchat": {
        "url": "https://www.snapchat.com/add/{u}",
        "method": "GET",
        "exists_status": 200,
       
        "not_found_signs": [404],
    },
}

def http_check(url, method="GET", timeout=DEFAULT_TIMEOUT, headers=None):
    headers = headers or {"User-Agent": USER_AGENT}
    try:
        if method.upper() == "HEAD":
            r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        else:
            r = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        return {"ok": True, "status_code": r.status_code, "text": r.text[:2000]}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": str(e)}

def evaluate_platform_response(platform_name, response):
    """
    Return one of: "taken", "available", "unknown"
    Uses status code rules and some content heuristics for Snapchat.
    """
    if not response.get("ok"):
        return "unknown", response.get("error")
    sc = response.get("status_code", 0)
    pf = PLATFORMS.get(platform_name)
    if not pf:
        return "unknown", "no rules for platform"
 
    if sc in pf.get("not_found_signs", []):
        return "available", f"status:{sc}"

    if sc == pf.get("exists_status"):
        
        if platform_name == "Snapchat":
            text = (response.get("text") or "").lower()
            
            if "couldn't find" in text or "not found" in text or "try again" in text:
                return "available", "snapchat page says not found"
            
            return "taken", f"status:{sc}"
        
        return "taken", f"status:{sc}"
    
    if sc in (301, 302):
        return "taken", f"redirect:{sc}"
   
    if sc == 403:
        return "taken", "forbidden/403"
    
    return "unknown", f"status:{sc}"


def check_username(username, platforms, delay_per_request=DEFAULT_DELAY, timeout=DEFAULT_TIMEOUT):
    """
    Check username across platforms dict (keys are platform names).
    Returns a dict of results per platform.
    """
    res = {
        "username": username,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": {}
    }
    for pname, pdata in platforms.items():
        url = pdata["url"].format(u=username)
        
        r = http_check(url, method=pdata.get("method", "GET"), timeout=timeout)
        verdict, reason = evaluate_platform_response(pname, r)
        res["results"][pname] = {
            "verdict": verdict,
            "reason": reason,
            "status_code": r.get("status_code") if r.get("ok") else None
        }
        time.sleep(delay_per_request)
    return res


class UsernameCheckerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Username Availability Checker — snap: ml-ftt")
        root.configure(bg=WINDOW_BG)
        root.geometry("920x640")

        
        banner = tk.Frame(root, bg=BANNER_BG, pady=10)
        banner.pack(fill=tk.X, padx=6, pady=6)
        tk.Label(
            banner,
            text="USERNAME AVAILABILITY",
            font=("Segoe UI Black", 20, "bold"),
            bg=BANNER_BG,
            fg="white"
        ).pack()
        tk.Label(
            banner,
            text="snap: ml-ftt",
            font=("Segoe UI", 10),
            bg=BANNER_BG,
            fg="#9fe59f"
        ).pack()

        
        ctrl = tk.Frame(root, bg=WINDOW_BG)
        ctrl.pack(fill=tk.X, padx=10, pady=(6, 6))

        tk.Label(
            ctrl,
            text="Enter username(s) (comma or newline separated):",
            bg=WINDOW_BG,
            fg=TEXT_FG
        ).grid(row=0, column=0, sticky="w")
        self.text_box = tk.Text(
            ctrl,
            height=6,
            width=70,
            bg=PANEL_BG,
            fg=TEXT_FG
        )
        self.text_box.grid(row=1, column=0, columnspan=4, padx=6, pady=6)

        tk.Label(ctrl, text="Workers:", bg=WINDOW_BG, fg=TEXT_FG).grid(row=2, column=0, sticky="e")
        self.workers_var = tk.IntVar(value=DEFAULT_WORKERS)
        tk.Spinbox(
            ctrl,
            from_=1,
            to=20,
            textvariable=self.workers_var,
            width=4
        ).grid(row=2, column=1, sticky="w")

        tk.Label(ctrl, text="Delay (s):", bg=WINDOW_BG, fg=TEXT_FG).grid(row=2, column=2, sticky="e")
        self.delay_var = tk.DoubleVar(value=DEFAULT_DELAY)
        tk.Spinbox(
            ctrl,
            from_=0.0,
            to=5.0,
            increment=0.1,
            textvariable=self.delay_var,
            width=6
        ).grid(row=2, column=3, sticky="w")

        self.start_btn = ttk.Button(ctrl, text="Start Check", command=self.start_check)
        self.start_btn.grid(row=3, column=0, pady=8)
        ttk.Button(ctrl, text="Clear Results", command=self.clear_results).grid(row=3, column=1, pady=8)
        ttk.Button(ctrl, text="Export CSV", command=self.export_csv).grid(row=3, column=2, pady=8)
        ttk.Button(ctrl, text="Export JSON", command=self.export_json).grid(row=3, column=3, pady=8)

        
        results_frame = tk.Frame(root, bg=WINDOW_BG)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        tk.Label(results_frame, text="Results:", bg=WINDOW_BG, fg=TEXT_FG).pack(anchor="w")
        self.tree = ttk.Treeview(
            results_frame,
            columns=("platform", "verdict", "reason"),
            show="headings"
        )
        self.tree.heading("platform", text="Platform")
        self.tree.heading("verdict", text="Verdict")
        self.tree.heading("reason", text="Reason")
        self.tree.column("platform", width=140)
        self.tree.column("verdict", width=120)
        self.tree.column("reason", width=520)
        self.tree.pack(fill=tk.BOTH, expand=True)

        
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            root,
            textvariable=self.status_var,
            bg=WINDOW_BG,
            fg=TEXT_FG
        ).pack(fill=tk.X, padx=10, pady=(0, 8))

        
        self.results = []  
        self._lock = threading.Lock()

    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []
        self.status_var.set("Cleared")

    def start_check(self):
        raw = self.text_box.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showinfo("Input required", "Enter at least one username.")
            return
        
        parts = [p.strip() for p in raw.replace(",", "\n").splitlines()]
        usernames = [p for p in parts if p]
        if not usernames:
            messagebox.showinfo("Input required", "Enter at least one username.")
            return

        workers = max(1, int(self.workers_var.get()))
        delay = float(self.delay_var.get())
        self.status_var.set(
            f"Starting checks for {len(usernames)} usernames with {workers} workers..."
        )
        self.start_btn.config(state="disabled")

        
        threading.Thread(
            target=self._run_checks_thread,
            args=(usernames, workers, delay),
            daemon=True
        ).start()

    def _run_checks_thread(self, usernames, workers, delay):
        self.results = []
        platforms = PLATFORMS
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {
                ex.submit(
                    check_username,
                    u,
                    platforms,
                    delay_per_request=delay
                ): u
                for u in usernames
            }
            for fut in as_completed(futures):
                u = futures[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    r = {"username": u, "error": str(e)}
                
                with self._lock:
                    self.results.append(r)
                    self._render_result(r)
        self.status_var.set("All checks completed.")
        self.start_btn.config(state="normal")

    def _render_result(self, result):
       
        uname = result.get("username")
        for platform, info in result.get("results", {}).items():
            verdict = info.get("verdict", "unknown")
            reason = info.get("reason", "")
            self.tree.insert(
                "",
                0,
                values=(f"{uname} - {platform}", verdict, reason)
            )
        self.status_var.set(f"Last checked: {uname}")

    def export_csv(self):
        if not self.results:
            messagebox.showinfo("No data", "No results to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="username_check.csv"
        )
        if not path:
            return
        rows = []
        for r in self.results:
            uname = r.get("username")
            for platform, info in r.get("results", {}).items():
                rows.append({
                    "username": uname,
                    "platform": platform,
                    "verdict": info.get("verdict"),
                    "reason": info.get("reason"),
                    "status_code": info.get("status_code")
                })
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["username", "platform", "verdict", "reason", "status_code"]
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        messagebox.showinfo("Saved", f"CSV saved to: {path}")

    def export_json(self):
        if not self.results:
            messagebox.showinfo("No data", "No results to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="username_check.json"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Saved", f"JSON saved to: {path}")


def main():
    root = tk.Tk()
    app = UsernameCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
