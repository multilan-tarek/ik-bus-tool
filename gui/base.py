from PySide6.QtCore import QMargins
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QGroupBox, QTableWidget, \
    QAbstractItemView, QCheckBox, QProgressBar, QTableWidgetItem, QHBoxLayout, QHBoxLayout, QComboBox
from gui.helper import get_logo
from gui.ike_simulation import IkeSimulation
from gui.serial import SerialManager
from gui.transmit_area import TransmitArea


class GUI(QMainWindow):
    def __init__(self, application):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = application.config

        self.table = None

        self.serial_manager = SerialManager(self.config)
        self.serial_manager.frame_received.connect(self.frame_received)
        application.quit_event.connect(self.serial_manager.stop)

        self.ike_simulation = IkeSimulation(self)






        self.window_title = "I/K-Bus Tool"
        self.window_icon = QIcon(get_logo())

        main_widget = QWidget()
        self.set_central_widget(main_widget)
        main_layout = QVBoxLayout(main_widget)



        main_layout.add_widget(TransmitArea(self.config, self.serial_manager))
        main_layout.add_spacing(8)
        main_layout.add_widget(self.init_filter_area())
        main_layout.add_spacing(8)
        main_layout.add_widget(self.init_receive_area())

        self.init_menu_bar()
        self.init_status_bar()

        #self.minimum_size = main_layout.size_hint()
        self.set_fixed_width(1200)
        self.set_fixed_height(900)
        self.show()

    def frame_received(self, frame):
        table_row = self.table.row_count
        decoded_data = frame.data.replace(b"\n", b"").replace(b"\r", b"").decode("ascii", errors="ignore")

        self.table.insert_row(table_row)
        self.table.set_row_height(table_row, 18)
        self.table.set_item(table_row, 0, QTableWidgetItem(frame.source_str))
        self.table.set_item(table_row, 1, QTableWidgetItem(frame.dest_str))
        self.table.set_item(table_row, 2, QTableWidgetItem(frame.cmd_str))
        self.table.set_item(table_row, 3, QTableWidgetItem(decoded_data))
        self.table.set_item(table_row, 4, QTableWidgetItem(str(frame)))

        self.table.scroll_to_bottom()

    def init_receive_area(self):
        self.table = QTableWidget()

        self.table.style_sheet = "QTableView{border: 1px solid #d8d8d8;}"
        #self.table.horizontal_header().style_sheet = "border: none; border-bottom: 1px solid #d8d8d8;"
        self.table.horizontal_header().stretch_last_section = True
        self.table.vertical_header().hide()
        self.table.edit_triggers = QAbstractItemView.EditTrigger.NoEditTriggers

        self.table.column_count = 5
        self.table.set_horizontal_header_labels(["Source", "Destination", "Type", "Decoded", "Hex"])

        return self.table

    def init_filter_area(self):
        area = QGroupBox("Filter")


        return area

    def init_menu_bar(self):
        menu_bar = self.menu_bar()

        menu_file = menu_bar.add_menu("&File")
        menu_file_open_bin = menu_file.add_action("Open Binary")

        menu_file.add_separator()

        menu_file_save_bin = menu_file.add_action("Save as Binary")
        menu_file_save_text = menu_file.add_action("Save as Text")
        menu_file_save_hex = menu_file.add_action("Save as HEX")

        menu_file.add_separator()

        menu_file_clear = menu_file.add_action("Clear")

        menu_file.add_separator()

        menu_file_close = menu_file.add_action("Close")
        menu_file_close.triggered.connect(lambda: exit())


        self.serial_manager.init_menu(menu_bar)
        menu_sim = menu_bar.add_menu("&Simulation")
        menu_tools = menu_bar.add_menu("&Tools")
        menu_help = menu_bar.add_menu("&Help")

        menu_tools_text_conv = menu_tools.add_action("Text Conversion")

        menu_ike_sim = menu_sim.add_action("IKE/KMB")
        menu_ike_sim.triggered.connect(lambda: self.ike_simulation.open())

    def init_status_bar(self):
        status_bar = self.status_bar()

        #self.read_buffer_fill = QProgressBar()
        #self.read_buffer_fill.set_range(0, 100)
        #self.read_buffer_fill.value = 0
        #self.read_buffer_fill.text_visible = False
        #self.read_buffer_fill.fixed_height = 10
        #status_bar.add_permanent_widget(self.read_buffer_fill)
#
        #self.write_buffer_fill = QProgressBar()
        #self.write_buffer_fill.set_range(0, 100)
        #self.write_buffer_fill.value = 0
        #self.write_buffer_fill.text_visible = False
        #status_bar.add_permanent_widget(self.write_buffer_fill)