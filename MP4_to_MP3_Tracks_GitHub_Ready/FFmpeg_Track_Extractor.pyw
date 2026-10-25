"""Windows-friendly FFmpeg audio track extractor with an MP4 file chooser."""
from __future__ import annotations

import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter_core import ConversionError, convert_all_tracks, locate_ffmpeg


APP_DIR = Path(__file__).resolve().parent


class TrackExtractor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MP4 → Separate MP3 Audio Tracks")
        self.geometry("540x300")
        self.minsize(490, 280)
        self.resizable(True, False)
        self.configure(bg="#121927")
        self.ffmpeg = None
        self.output_directory: Path | None = None
        self.is_busy = False
        self._create_ui()
        # Open native File dialog as soon as the app is launched.
        self.after(350, self.choose_file)

    def _create_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#273042", background="#38bdf8", borderwidth=0)
        wrap = tk.Frame(self, bg="#121927", padx=27, pady=17)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text="🎧 MP4 → MP3 TRACKS", bg="#121927", fg="white",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(2, 8))
        tk.Label(wrap, text="Select one MP4. Every embedded audio track becomes a separate MP3 (320 kbps).",
                 bg="#121927", fg="#b7c4d4", wraplength=465, justify="left",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

        self.status_var = tk.StringVar(value="Choose an MP4 file to begin.")
        self.status = tk.Label(wrap, textvariable=self.status_var, bg="#121927", fg="#e5ecf6",
                               wraplength=470, justify="left", font=("Segoe UI", 10))
        self.status.pack(anchor="w", pady=(0, 8))
        self.progress = ttk.Progressbar(wrap, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 16))
        actions = tk.Frame(wrap, bg="#121927")
        actions.pack(fill="x")
        self.pick_btn = tk.Button(actions, text="📁  Choose MP4", command=self.choose_file,
                                  bg="#0284c7", fg="white", activebackground="#0369a1",
                                  font=("Segoe UI", 10, "bold"), relief="flat", padx=18, pady=10)
        self.pick_btn.pack(side="left", padx=(0, 10))
        self.open_btn = tk.Button(actions, text="Open MP3 Folder", command=self.open_output,
                                  bg="#354154", fg="white", activebackground="#475569",
                                  font=("Segoe UI", 10), relief="flat", padx=12, pady=10,
                                  state="disabled")
        self.open_btn.pack(side="left")
        tk.Label(wrap, text="No video is changed or deleted. Separate audio files are saved next to your MP4.",
                 bg="#121927", fg="#8294ab", wraplength=480, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(15, 0))

    def _resolve_ffmpeg(self):
        if self.ffmpeg and self.ffmpeg.is_file():
            return self.ffmpeg
        self.ffmpeg = locate_ffmpeg(APP_DIR)
        if self.ffmpeg:
            return self.ffmpeg
        answer = messagebox.askyesno(
            "FFmpeg is required",
            "Couldn't find ffmpeg.exe.\n\n"
            "Download FFmpeg from ffmpeg.org/download.html, unzip it, and put "
            "ffmpeg.exe next to this app.\n\nDo you want to locate ffmpeg.exe manually?",
            parent=self)
        if not answer:
            return None
        chosen = filedialog.askopenfilename(parent=self, title="Locate ffmpeg.exe",
                        filetypes=[("FFmpeg executable", "ffmpeg.exe"), ("All files", "*.*")])
        if chosen:
            self.ffmpeg = Path(chosen)
        return self.ffmpeg

    def choose_file(self):
        if self.is_busy:
            return
        path = filedialog.askopenfilename(
            parent=self, title="Choose MP4 file containing multiple audio tracks",
            filetypes=[("Video files", "*.mp4 *.mkv *.mov *.m4v"), ("All files", "*.*")]
        )
        if not path:
            self.status_var.set("No file selected. Click Choose MP4 to try again.")
            return
        ffmpeg = self._resolve_ffmpeg()
        if not ffmpeg:
            self.status_var.set("FFmpeg is needed. Choose MP4 to try again after installing it.")
            return
        self.is_busy = True
        self.output_directory = None
        self.pick_btn.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.status_var.set(f"Converting tracks from: {Path(path).name}")
        self.progress.start(14)
        threading.Thread(target=self._worker, args=(Path(path), ffmpeg), daemon=True).start()

    def _worker(self, video: Path, ffmpeg: Path):
        try:
            tracks = convert_all_tracks(video, ffmpeg,
                                        on_progress=lambda n, total: self.after(0, self._progress, n, total))
            self.after(0, self._success, tracks)
        except (ConversionError, OSError, subprocess.SubprocessError) as exc:
            self.after(0, self._failure, str(exc))
        except Exception as exc:
            self.after(0, self._failure, f"Unexpected error: {exc}")

    def _progress(self, n: int, total: int):
        self.status_var.set(f"Converted {n}/{total} audio tracks ...")

    def _finish(self):
        self.is_busy = False
        self.progress.stop()
        self.pick_btn.config(state="normal")

    def _success(self, tracks: list[Path]):
        self._finish()
        self.output_directory = tracks[0].parent
        self.open_btn.config(state="normal")
        self.status_var.set(f"✅ DONE! Exported {len(tracks)} MP3 track(s) at 320 kbps.")
        messagebox.showinfo("MP3 export complete",
                            f"Created {len(tracks)} MP3 file(s):\n" +
                            "\n".join(p.name for p in tracks) +
                            f"\n\nSaved in:\n{self.output_directory}", parent=self)

    def _failure(self, text: str):
        self._finish()
        self.status_var.set("Error. See the message and try again.")
        messagebox.showerror("Could not extract tracks", text, parent=self)

    def open_output(self):
        if not self.output_directory:
            return
        if os.name == "nt":
            os.startfile(str(self.output_directory))
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(self.output_directory)])


if __name__ == "__main__":
    TrackExtractor().mainloop()
