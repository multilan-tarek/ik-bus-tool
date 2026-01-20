from PySide6.QtGui import QIcon, QPainter, QColor, qRgba, QFontDatabase
from PySide6.QtCore import QMargins, Signal, Qt, QTimer
from PySide6.QtWidgets import QDialog, QHBoxLayout, QGridLayout, QApplication, QScrollArea, QWidget
from gui.helper import get_logo
from gui.widgets.display import DisplayWidget


class DisplayWidgetWrapper(DisplayWidget):
    pressed_down = False
    mouse_hovering = False
    copied_overlay = False

    def hide_copied_overlay(self):
        self.copied_overlay = False
        self.repaint()

    def enter_event(self, event):
        self.mouse_hovering = True
        self.repaint()

    def leave_event(self, event):
        self.mouse_hovering = False
        self.repaint()

    def mouse_press_event(self, e):
        if e.button().name == "LeftButton" and not self.copied_overlay:
            self.pressed_down = True
            self.copied_overlay = True
            QTimer.single_shot(1500, self.hide_copied_overlay)
            QApplication.clipboard().set_text(self.data.hex().upper())
            self.repaint()

        super().mouse_press_event(e)

    def mouse_release_event(self, e):
        if e.button().name == "LeftButton":
            self.pressed_down = False
            self.repaint()

        super().mouse_press_event(e)

    def paint_event(self, event):
        super().paint_event(event)

        p = QPainter(self)
        p.set_render_hint(QPainter.RenderHint.Antialiasing, True)

        if self.copied_overlay or self.mouse_hovering:
            p.fill_rect(0, 0, self.width, self.height, QColor.from_rgba(qRgba(0, 0, 0, 80)))

            if self.copied_overlay:
                text = "Copied!"
                font_size = 11
            else:
                text = f"0x{self.data.hex().upper()}"
                font_size = 18

            font = QFontDatabase.system_font(QFontDatabase.SystemFont.FixedFont)
            font.set_point_size(font_size)

            p.set_font(font)
            p.set_pen(QColor(255, 255, 255))
            p.draw_text(self.rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter, text)


        if self.pressed_down:
            p.fill_rect(0, 0, self.width, self.height, QColor.from_rgba(qRgba(0, 0, 0, 40)))

        p.end()

class CharsetBrowser(QDialog):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window)

        self.window_title = "Charset Browser"
        self.window_icon = QIcon(get_logo())

        root_layout = QHBoxLayout(self)
        root_layout.contents_margins = QMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.widget_resizable = True
        root_layout.add_widget(scroll_area)
        self.content = QWidget()
        self.layout = QGridLayout(self.content)
        self.layout.set_horizontal_spacing(10)
        self.layout.set_vertical_spacing(18)
        scroll_area.set_widget(self.content)

        row = 0
        col = 0

        for byte in range(0xFF + 1):
            display = DisplayWidgetWrapper(char_count=1, pixel_size=10, padding=2)
            display.data = bytearray([byte])
            self.layout.add_widget(display, row, col)

            col += 1
            if col == 16:
                col = 0
                row += 1

        self.resize(0, 800)
        self.set_fixed_width(self.content.size_hint.width() + 40)
