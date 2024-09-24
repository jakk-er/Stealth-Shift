import os
import sys
import re
from PyQt5 import QtWidgets, QtGui, QtCore

class CloseableTab(QtWidgets.QWidget):
    """Custom widget for tabs with a close button."""
    def __init__(self, title, close_callback):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(title)
        self.close_button = QtWidgets.QPushButton("X")
        self.close_button.setFixedSize(20, 20)  # Size for close button
        self.close_button.clicked.connect(close_callback)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.close_button)

class VPNManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VPN Configuration Manager")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # OpenVPN and WireGuard tabs
        self.openvpn_tab = QtWidgets.QWidget()
        self.wireguard_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.openvpn_tab, "OpenVPN")
        self.tab_widget.addTab(self.wireguard_tab, "WireGuard")

        # Layouts for tabs
        self.setup_openvpn_tab()
        self.setup_wireguard_tab()

    def setup_openvpn_tab(self):
        layout = QtWidgets.QVBoxLayout(self.openvpn_tab)
        self.openvpn_list = QtWidgets.QListWidget()
        self.openvpn_list.itemClicked.connect(self.load_openvpn_config)
        layout.addWidget(self.openvpn_list)

        self.load_openvpn_files()

        self.openvpn_subtab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.openvpn_subtab_widget)

    def setup_wireguard_tab(self):
        layout = QtWidgets.QVBoxLayout(self.wireguard_tab)
        self.wireguard_list = QtWidgets.QListWidget()
        self.wireguard_list.itemClicked.connect(self.load_wireguard_config)
        layout.addWidget(self.wireguard_list)

        self.load_wireguard_files()

        self.wireguard_subtab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.wireguard_subtab_widget)

    def natural_sort(self, lst):
        """Sort a list using natural order (numeric values are taken into account)."""
        return sorted(lst, key=lambda x: [int(i) if i.isdigit() else i for i in re.split(r'(\d+)', x)])

    def load_openvpn_files(self):
        self.openvpn_dir = 'OP_VPNS'
        if not os.path.exists(self.openvpn_dir):
            QtWidgets.QMessageBox.warning(self, "Warning", f"OpenVPN directory '{self.openvpn_dir}' does not exist.")
            return

        filenames = [f for f in os.listdir(self.openvpn_dir) if f.endswith('.ovpn')]
        sorted_filenames = self.natural_sort(filenames)
        self.openvpn_list.addItems(sorted_filenames)

    def load_wireguard_files(self):
        self.wireguard_dir = 'WG_VPNS'
        if not os.path.exists(self.wireguard_dir):
            QtWidgets.QMessageBox.warning(self, "Warning", f"WireGuard directory '{self.wireguard_dir}' does not exist.")
            return

        filenames = [f for f in os.listdir(self.wireguard_dir) if f.endswith('.conf')]
        sorted_filenames = self.natural_sort(filenames)
        self.wireguard_list.addItems(sorted_filenames)

    def load_openvpn_config(self, item):
        filename = item.text()
        sub_tab = QtWidgets.QWidget()
        self.openvpn_subtab_widget.addTab(sub_tab, filename)

        layout = QtWidgets.QVBoxLayout(sub_tab)

        text_area = QtWidgets.QTextEdit()
        with open(os.path.join(self.openvpn_dir, filename), 'r') as f:
            content = f.read()
            text_area.setPlainText(content)
        layout.addWidget(text_area)

        save_button = QtWidgets.QPushButton("Save OpenVPN Config")
        save_button.clicked.connect(lambda: self.save_openvpn_config(filename, text_area))
        layout.addWidget(save_button)

        # Auth file handling
        auth_index = filename.split('-')[1].split('.')[0]
        auth_filename = f"auth-{auth_index}.txt"
        auth_file_path = os.path.join('AUTH', auth_filename)

        auth_filename_label = QtWidgets.QLabel(f"Auth File: {auth_filename}")
        layout.addWidget(auth_filename_label)

        auth_area = QtWidgets.QTextEdit()
        if os.path.isfile(auth_file_path):
            with open(auth_file_path, 'r') as f:
                auth_content = f.read()
                auth_area.setPlainText(auth_content)
        layout.addWidget(auth_area)

        auth_save_button = QtWidgets.QPushButton("Save Auth File")
        auth_save_button.clicked.connect(lambda: self.save_auth_file(auth_file_path, auth_area))
        layout.addWidget(auth_save_button)

        # Closeable tab
        closeable_tab = CloseableTab(filename, lambda: self.openvpn_subtab_widget.removeTab(self.openvpn_subtab_widget.indexOf(sub_tab)))
        self.openvpn_subtab_widget.setTabText(self.openvpn_subtab_widget.indexOf(sub_tab), "")
        self.openvpn_subtab_widget.tabBar().setTabButton(self.openvpn_subtab_widget.indexOf(sub_tab), QtWidgets.QTabBar.RightSide, closeable_tab)

    def load_wireguard_config(self, item):
        filename = item.text()
        sub_tab = QtWidgets.QWidget()
        self.wireguard_subtab_widget.addTab(sub_tab, filename)

        layout = QtWidgets.QVBoxLayout(sub_tab)

        text_area = QtWidgets.QTextEdit()
        with open(os.path.join(self.wireguard_dir, filename), 'r') as f:
            content = f.read()
            text_area.setPlainText(content)
        layout.addWidget(text_area)

        save_button = QtWidgets.QPushButton("Save WireGuard Config")
        save_button.clicked.connect(lambda: self.save_wireguard_config(filename, text_area))
        layout.addWidget(save_button)

        # Closeable tab
        closeable_tab = CloseableTab(filename, lambda: self.wireguard_subtab_widget.removeTab(self.wireguard_subtab_widget.indexOf(sub_tab)))
        self.wireguard_subtab_widget.setTabText(self.wireguard_subtab_widget.indexOf(sub_tab), "")
        self.wireguard_subtab_widget.tabBar().setTabButton(self.wireguard_subtab_widget.indexOf(sub_tab), QtWidgets.QTabBar.RightSide, closeable_tab)

    def save_openvpn_config(self, filename, text_area):
        file_path = os.path.join(self.openvpn_dir, filename)
        with open(file_path, 'w') as f:
            content = text_area.toPlainText().strip()
            f.write(content)
        QtWidgets.QMessageBox.information(self, "Info", f"Saved OpenVPN configuration: {filename}.")

    def save_auth_file(self, auth_file_path, auth_area):
        with open(auth_file_path, 'w') as f:
            auth_content = auth_area.toPlainText().strip()
            f.write(auth_content)
        QtWidgets.QMessageBox.information(self, "Info", f"Saved authentication file: {os.path.basename(auth_file_path)}.")

    def save_wireguard_config(self, filename, text_area):
        file_path = os.path.join(self.wireguard_dir, filename)
        with open(file_path, 'w') as f:
            content = text_area.toPlainText().strip()
            f.write(content)
        QtWidgets.QMessageBox.information(self, "Info", f"Saved WireGuard configuration: {filename}.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = VPNManager()
    window.show()
    sys.exit(app.exec_())
