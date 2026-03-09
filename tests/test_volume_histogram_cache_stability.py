import unittest

import numpy as np
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QImage, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QStyleOptionGraphicsItem

import os
import sys

# Allow `import ui.*` like the app does when running `python app/main.py`.
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
APP_DIR = os.path.join(REPO_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from ui.charts.volume_histogram import VolumeHistogramItem


class TestVolumeHistogramCacheStability(unittest.TestCase):
    def test_chunk_cache_survives_y_range_changes(self) -> None:
        _ = QApplication.instance() or QApplication([])

        n = 1200
        x = np.arange(n, dtype=np.float64)
        vol = (np.sin(np.linspace(0.0, 50.0, n)) + 1.1) * 100.0
        is_up = (np.arange(n) % 2) == 0

        item = VolumeHistogramItem(
            up_color=QColor("#22C55E"),
            down_color=QColor("#EF5350"),
            base_color=QColor("#64748B"),
            bar_width=0.8,
            volume_height_ratio=0.15,
            chunk_size=300,
        )
        item.set_arrays(x, vol, is_up)

        img = QImage(800, 400, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)

        opt = QStyleOptionGraphicsItem()
        opt.exposedRect = QRectF(0.0, -100.0, float(n - 1), 200.0)
        painter = QPainter(img)
        try:
            item.paint(painter, opt, None)
        finally:
            painter.end()

        cache_keys_1 = set(getattr(item, "_chunk_cache", {}).keys())
        self.assertGreater(len(cache_keys_1), 0)

        # Change only the y-range; x-range stays identical.
        opt.exposedRect = QRectF(0.0, -1000.0, float(n - 1), 2000.0)
        painter = QPainter(img)
        try:
            item.paint(painter, opt, None)
        finally:
            painter.end()

        cache_keys_2 = set(getattr(item, "_chunk_cache", {}).keys())
        self.assertEqual(cache_keys_1, cache_keys_2)


if __name__ == "__main__":
    unittest.main()
