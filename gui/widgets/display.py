import json
import os.path
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import  QPainter,  QColor


class DisplayWidget(QWidget):
    def __init__(self, char_count=20, pixel_size=8, pixel_spacing=1, padding=40, check_control=False):
        from __feature__ import snake_case, true_property  # noqa
        QWidget.__init__(self)

        charset_path = os.path.join(os.getcwd(), "gui", "assets", "charset.json")
        with open(charset_path, "r") as charset_file:
            self.charset = json.loads(charset_file.read())

        self.check_control = check_control
        self.char_count = char_count
        self.padding = padding
        self.data_value = bytearray()

        self.pixel_width = pixel_size
        self.pixel_height = pixel_size
        self.pixel_spacing = pixel_spacing

        self.display_padding = self.pixel_width * 2

        self.char_width = (self.pixel_width * 5) + (self.pixel_spacing * 4)
        self.char_height = (self.pixel_height * 7) + (self.pixel_spacing * 6)

        self.arrow_width = 0

        self.display_width = self.display_padding + (self.char_width * self.char_count) + (self.pixel_width * (self.char_count - 1))
        self.display_height = self.char_height + self.display_padding

        if self.check_control:
            self.arrow_width = self.char_width + (self.pixel_width * 2) + int(self.display_padding / 2)

            self.display_width += (self.pixel_width * 2) + (self.arrow_width * 2)

        self.set_fixed_size(self.display_width + self.padding, self.display_height + self.padding)

    @property
    def data(self):
        return self.data_value

    @data.setter
    def data(self, value):
        self.data_value = value
        self.repaint()

    def paint_char(self, painter, char, x, y, color):
        char_data = self.charset.get(f"{char:x}")

        if char_data is None:
            return

        for row_i, row in enumerate(char_data):
            for col_i, col in enumerate(row):
                pixel_x = x + (col_i * (self.pixel_width + self.pixel_spacing))
                pixel_y = y + (row_i * (self.pixel_height + self.pixel_spacing))

                if not col:
                    continue

                painter.fill_rect(pixel_x, pixel_y, self.pixel_width, self.pixel_height, color)

    def draw_char(self, painter, index, char):
        start_x = (index * (self.char_width + self.pixel_width)) + (self.padding / 2) + self.arrow_width +  int(self.display_padding / 2)
        start_y = int(self.padding / 2) + int(self.display_padding / 2)
        color = QColor.from_rgb(255, 127, 92)

        self.paint_char(painter, char, start_x, start_y, color)

    def draw_arrows(self, painter):
        start_x = int(self.padding / 2) - self.pixel_width + int(self.display_padding / 2)
        start_y = int(self.padding / 2) + int(self.display_padding / 2)
        color = QColor.from_rgb(240, 97, 106)

        self.paint_char(painter, 0xbc, start_x, start_y, color)

        start_x = self.width - (self.padding / 2) - self.char_width + self.pixel_width - int(self.display_padding / 2)
        self.paint_char(painter, 0xbd, start_x, start_y, color)

    def paint_event(self, event):
        p = QPainter(self)
        p.set_render_hint(QPainter.RenderHint.Antialiasing, True)

        padding_offset = int(self.padding / 2)
        p.fill_rect(0, 0, self.width, self.height, QColor.from_rgb(0, 0, 0))
        p.fill_rect(padding_offset, padding_offset, self.display_width, self.display_height, QColor.from_rgb(171, 72, 61))

        if self.check_control:
            p.fill_rect(padding_offset, padding_offset, self.arrow_width, self.display_height, QColor.from_rgb(149, 41, 53))
            p.fill_rect(self.width - self.arrow_width - padding_offset, padding_offset, self.arrow_width, self.display_height, QColor.from_rgb(149, 41, 53))

        for i, byte in enumerate(self.data_value):
            if i >= self.char_count:
                break

            self.draw_char(p, i, byte)

        if self.check_control:
            self.draw_arrows(p)

        p.end()
