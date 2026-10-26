"""Media Converter v2 - simple Windows GUI. © 2026 GAVY_OP."""
from __future__ import annotations

import threading
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from media_core import AUDIO_FORMATS, MEDIA_INPUT_EXTENSIONS, VIDEO_FORMATS, locate_tools, run_conversion

BASE = Path(__file__).resolve().parent
APP_VERSION = 'v2'
AUTHOR = 'GAVY_OP'
GITHUB_PROFILE_URL = 'https://github.com/gavyop'
GITHUB_PROJECT_URL = 'https://github.com/gavyop/MP4-to-MP3-Track-Extractor'


class MediaConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f'Media Converter {APP_VERSION} — {AUTHOR}')
        root.geometry('690x490')
        root.minsize(600, 470)
        self.source = tk.StringVar()
        self.operation = tk.StringVar(value='Extract audio tracks')
        self.output_format = tk.StringVar(value='mp3')
        self.status = tk.StringVar(value='Choose a video or audio file to begin.')
        self.ffmpeg_file = None
        self.running = False

        container = ttk.Frame(root, padding=20)
        container.pack(fill='both', expand=True)
        ttk.Label(container, text=f'Media Converter {APP_VERSION}', font=('Segoe UI', 19, 'bold')).pack(anchor='w', pady=(0, 14))
        row = ttk.Frame(container)
        row.pack(fill='x')
        ttk.Entry(row, textvariable=self.source).pack(side='left', expand=True, fill='x')
        self.browse_button = ttk.Button(row, text='Choose File', command=self.choose_source)
        self.browse_button.pack(side='left', padx=(8, 0))

        ttk.Label(container, text='Operation').pack(anchor='w', pady=(16, 3))
        self.operation_input = ttk.Combobox(container, textvariable=self.operation,
                                            values=['Extract audio tracks', 'Convert audio', 'Convert video'], state='readonly')
        self.operation_input.pack(fill='x')
        self.operation_input.bind('<<ComboboxSelected>>', lambda _evt: self.update_formats())

        ttk.Label(container, text='Output format').pack(anchor='w', pady=(15, 3))
        self.format_input = ttk.Combobox(container, textvariable=self.output_format, state='readonly')
        self.format_input.pack(fill='x')
        self.update_formats()

        self.convert_button = ttk.Button(container, text='Convert / Extract', command=self.start)
        self.convert_button.pack(fill='x', pady=(18, 12))
        self.progress = ttk.Progressbar(container, mode='indeterminate')
        self.progress.pack(fill='x')
        ttk.Label(container, textvariable=self.status, wraplength=630).pack(anchor='w', pady=(12, 0))
        ttk.Label(container, text='Output files are saved beside the input. Existing files are never replaced.',
                  foreground='#666').pack(anchor='w', pady=(18, 0))

        # Copyright and GitHub links are clickable directly inside the app.
        footer = ttk.Frame(container)
        footer.pack(side='bottom', anchor='w', fill='x', pady=(16, 0))
        ttk.Label(footer, text=f'© 2026 {AUTHOR} — All Rights Reserved  |  Media Converter {APP_VERSION}',
                  foreground='#555').pack(anchor='w')
        links = ttk.Frame(footer)
        links.pack(anchor='w', pady=(5, 0))
        self._add_link(links, 'GAVY_OP on GitHub', GITHUB_PROFILE_URL)
        ttk.Label(links, text='  •  ').pack(side='left')
        self._add_link(links, 'Project repository', GITHUB_PROJECT_URL)

    @staticmethod
    def _add_link(parent, text, url):
        link = tk.Label(parent, text=text, fg='#0969da', cursor='hand2',
                        font=('Segoe UI', 9, 'underline'))
        link.pack(side='left')
        link.bind('<Button-1>', lambda _event: webbrowser.open(url, new=2))
        return link

    def choose_source(self):
        filter_str = ' '.join('*' + suffix for suffix in sorted(MEDIA_INPUT_EXTENSIONS))
        chosen = filedialog.askopenfilename(title='Choose video or audio file',
                                             filetypes=[('Video and audio files', filter_str), ('All files', '*.*')])
        if chosen:
            self.source.set(chosen)

    def update_formats(self):
        formats = VIDEO_FORMATS if self.operation.get() == 'Convert video' else AUDIO_FORMATS
        self.format_input['values'] = formats
        if self.output_format.get() not in formats:
            self.output_format.set(formats[0])

    def select_ffmpeg(self):
        tools = locate_tools(BASE, self.ffmpeg_file)
        if tools:
            return tools
        messagebox.showinfo('Choose FFmpeg', 'FFmpeg and FFprobe were not found. Select ffmpeg.exe in the FFmpeg bin folder. Both files must be in the same folder.')
        selection = filedialog.askopenfilename(title='Select ffmpeg.exe', filetypes=[('FFmpeg executable', 'ffmpeg.exe'), ('All files', '*.*')])
        if not selection:
            return None
        self.ffmpeg_file = selection
        tools = locate_tools(BASE, selection)
        if not tools:
            messagebox.showerror('FFmpeg missing', 'Could not find ffprobe.exe beside ffmpeg.exe. Download both from the same FFmpeg package.')
        return tools

    def start(self):
        if self.running:
            return
        src = Path(self.source.get().strip().strip('"'))
        if not src.is_file():
            messagebox.showerror('Missing file', 'Please choose an existing video or audio file.')
            return
        tools = self.select_ffmpeg()
        if not tools:
            self.status.set('Cancelled — FFmpeg/FFprobe not selected.')
            return
        self.running = True
        self.convert_button.state(['disabled'])
        self.browse_button.state(['disabled'])
        self.operation_input.state(['disabled'])
        self.format_input.state(['disabled'])
        self.progress.start(12)
        self.status.set('Converting... This may take a while for large files.')
        thread = threading.Thread(target=self._convert, args=(src, self.operation.get(), self.output_format.get(), tools), daemon=True)
        thread.start()

    def _convert(self, src, mode, fmt, tools):
        try:
            output_files = run_conversion(src, mode, fmt, *tools)
        except Exception as exc:
            msg = str(exc)
            self._schedule(lambda: self._finished(error=msg))
        else:
            self._schedule(lambda: self._finished(files=output_files))

    def _schedule(self, callback):
        try:
            self.root.after(0, callback)
        except RuntimeError:
            pass

    def _finished(self, files=None, error=None):
        self.running = False
        self.progress.stop()
        self.convert_button.state(['!disabled'])
        self.browse_button.state(['!disabled'])
        self.operation_input.state(['!disabled'])
        self.format_input.state(['!disabled'])
        if error:
            self.status.set('Conversion failed. See error details.')
            messagebox.showerror('Conversion failed', error)
        else:
            self.status.set('Created: ' + ', '.join(p.name for p in files))
            messagebox.showinfo('Success', 'Created:\n' + '\n'.join(str(p) for p in files))


if __name__ == '__main__':
    app_root = tk.Tk()
    MediaConverterApp(app_root)
    app_root.mainloop()
