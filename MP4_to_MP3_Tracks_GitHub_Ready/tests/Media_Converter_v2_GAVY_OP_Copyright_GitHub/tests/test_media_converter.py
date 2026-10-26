import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_core import locate_tools, run_conversion, streams_for, build_command, unique_output


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg and FFprobe are required')
class MediaConverterIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='media_converter_test_')
        cls.root = Path(cls.tmp.name)
        cls.ffmpeg, cls.ffprobe = locate_tools(cls.root)
        cls.video = cls.root / 'βίντεο_δύο_ήχοι.mp4'
        subprocess.run([cls.ffmpeg, '-v', 'error', '-y',
                        '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=10:duration=0.8',
                        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.8',
                        '-f', 'lavfi', '-i', 'sine=frequency=880:duration=0.8',
                        '-map', '0:v:0', '-map', '1:a:0', '-map', '2:a:0',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                        str(cls.video)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_detect_two_audio_streams(self):
        self.assertEqual(sum(s.get('codec_type') == 'audio' for s in streams_for(self.video, self.ffprobe)), 2)

    def test_02_two_distinct_mp3_outputs(self):
        outputs = run_conversion(self.video, 'Extract audio tracks', 'mp3', self.ffmpeg, self.ffprobe)
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(p.stat().st_size > 1000 for p in outputs))
        self.assertNotEqual(outputs[0].read_bytes(), outputs[1].read_bytes())

    def test_03_audio_to_flac(self):
        input_mp3 = self.root / 'βίντεο_δύο_ήχοι_track_1.mp3'
        if not input_mp3.exists():
            run_conversion(self.video, 'Extract audio tracks', 'mp3', self.ffmpeg, self.ffprobe)
        outputs = run_conversion(input_mp3, 'Convert audio', 'flac', self.ffmpeg, self.ffprobe)
        self.assertEqual(len(outputs), 1)
        self.assertGreater(outputs[0].stat().st_size, 1000)

    def test_04_mkv_video_conversion(self):
        outputs = run_conversion(self.video, 'Convert video', 'mkv', self.ffmpeg, self.ffprobe)
        stream_kinds = [s['codec_type'] for s in streams_for(outputs[0], self.ffprobe)]
        self.assertEqual(stream_kinds.count('video'), 1)
        self.assertEqual(stream_kinds.count('audio'), 2)

    def test_05_webm_video_conversion(self):
        outputs = run_conversion(self.video, 'Convert video', 'webm', self.ffmpeg, self.ffprobe)
        self.assertEqual(len(outputs), 1)
        self.assertGreater(outputs[0].stat().st_size, 1000)

    def test_06_unique_output(self):
        base = self.root / 'existing.mp3'
        base.write_bytes(b'x')
        newer = unique_output(self.root, 'existing', 'mp3')
        self.assertEqual(newer.name, 'existing_2.mp3')

    def test_07_missing_video_errors(self):
        mp3 = run_conversion(self.video, 'Extract audio tracks', 'mp3', self.ffmpeg, self.ffprobe)[0]
        with self.assertRaisesRegex(ValueError, 'no video'):
            run_conversion(mp3, 'Convert video', 'mp4', self.ffmpeg, self.ffprobe)

    def test_08_selected_ffmpeg_requires_matching_ffprobe(self):
        fake = self.root / 'selected_ffmpeg.exe'
        fake.write_bytes(b'file')
        self.assertIsNone(locate_tools(self.root, str(fake)))

    def test_09_invalid_format_errors(self):
        with self.assertRaises(ValueError):
            build_command(self.ffmpeg, self.video, self.root / 'broken.mp4', 'Convert audio', 'mp4')


if __name__ == '__main__':
    unittest.main()
