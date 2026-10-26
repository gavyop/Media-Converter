import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'media_converter.pyw').read_text(encoding='utf-8')

class BrandingTests(unittest.TestCase):
    def test_gui_compiles(self):
        compile(SOURCE, 'media_converter.pyw', 'exec')

    def test_version_is_v2(self):
        self.assertIn("APP_VERSION = 'v2'", SOURCE)
        self.assertNotIn('v2.0.1', SOURCE)

    def test_copyright_and_github(self):
        self.assertIn("AUTHOR = 'GAVY_OP'", SOURCE)
        self.assertIn('© 2026', SOURCE)
        self.assertIn('https://github.com/gavyop', SOURCE)
        self.assertIn('https://github.com/gavyop/MP4-to-MP3-Track-Extractor', SOURCE)

    def test_clickable_browser_link(self):
        self.assertIn("link.bind('<Button-1>'", SOURCE)
        self.assertIn('webbrowser.open(url, new=2)', SOURCE)

    def test_docs(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('© 2026 GAVY_OP', readme)
        self.assertIn('Private', readme)
        self.assertIn('Media Converter v2', readme)
        self.assertNotIn('v2.0.1', readme)

if __name__ == '__main__':
    unittest.main()
