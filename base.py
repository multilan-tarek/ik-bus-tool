import sys
import PySide6  # noqa
from PySide6.QtCore import Signal
from __feature__ import snake_case, true_property  # noqa
from PySide6.QtWidgets import QApplication
from config import Config
from gui.base import GUI


class Main(QApplication):
    quit_event = Signal()

    def __init__(self, args):
        super().__init__(args)
        self.aboutToQuit.connect(self.on_quit_event)
        self.config = Config()
        self.gui = GUI(self)

    def on_quit_event(self):
        self.quit_event.emit()
        self.config.write_config()

main = Main(sys.argv)
sys.exit(main.exec())
