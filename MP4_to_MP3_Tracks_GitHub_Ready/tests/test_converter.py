import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from converter_core import ConversionError, audio_track_count, convert_all_tracks, make_output_directory


class ExtractorTests(unittest.TestCase):
    def test_output_directory_never_overwrites(self):
        with tempfile.TemporaryDirectory() as t:
            v = Path(t) / "βίντεο.mp4"
            a, b = make_output_directory(v), make_output_directory(v)
            self.assertNotEqual(a, b)
            self.assertTrue(a.is_dir() and b.is_dir())

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ConversionError):
                convert_all_tracks(Path(t) / "missing.mp4", Path(t) / "ffmpeg")

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe required")
    def test_extract_two_real_audio_tracks(self):
        with tempfile.TemporaryDirectory() as t:
            temp = Path(t)
            source = temp / "Δοκιμή.mp4"
            exe = Path(shutil.which("ffmpeg"))
            args = [str(exe), "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=400:duration=0.7", "-f", "lavfi", "-i", "sine=frequency=900:duration=0.7", "-map", "0:a", "-map", "1:a", "-c:a", "aac", "-y", str(source)]
            subprocess.run(args, check=True, capture_output=True)
            self.assertEqual(audio_track_count(source, exe), 2)
            files = convert_all_tracks(source, exe)
            self.assertEqual([p.name for p in files], ["Track_1.mp3", "Track_2.mp3"])
            self.assertTrue(all(p.is_file() and p.stat().st_size > 1000 for p in files))
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
