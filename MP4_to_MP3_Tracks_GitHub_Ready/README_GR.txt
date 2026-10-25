FFmpeg MP4 -> SEPARATE MP3 AUDIO TRACKS (Windows)
================================================

TI KANEI:
Anoigeis to START_HERE.bat -> Emfanizetai "Choose MP4" -> Dialexe to video.
To programma vriskei OLA ta audio tracks kai ftiaxnei 1 MP3 gia to kathena.
An exeis 2 tracks, tha pareis Track_1.mp3 kai Track_2.mp3.
Den allazei to video sou. Ta arxeia pane sto <onoma_video>_MP3_Tracks.

PROAPAITOUNTA:
1. Python 3 (yparxei idi ston ypologisti sou apo to proigoumeno script).
2. FFmpeg sto PC sou. Official downloads: https://ffmpeg.org/download.html
   Gia Windows, pare ena trusted Windows build apo ta links tis official page.
   Apothikeuse to "ffmpeg.exe" dipla sto START_HERE.bat, i bale ton sto PATH.
   An to FFmpeg exe den vrethei, to app tha se rotisei na to epilexeis.

POS TO XREISIMOPOIEIS:
1. Extract All to ZIP.
2. Balto "ffmpeg.exe" ston idio fakelo an den exeis idi FFmpeg.
3. Kane DIPLO KLIK sto START_HERE.bat.
4. Sto File dialog epilexe MP4 (kai MKV/MOV/M4V).
5. Perimene mexri na vgalei DONE.
6. Pata "Open MP3 Folder" gia na deis ta arxeia.

NOTES:
- MP3 320 kbps: to conversion den mporei na veltiwsei tin arxiki poiotita audio.
- Den anemazei ta videos sto internet. Ola ginontai sto PC sou.
- Einai ena mikro Python GUI (oxi exe). Den xreiazetai na grafeis entoles.
- An den aniksei, dokimase na anoixeis me Python 3 (tkinter built in).
