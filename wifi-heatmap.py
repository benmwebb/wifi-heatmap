#!/usr/bin/env python3

import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QScrollArea, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
import subprocess
import re
import csv
import collections
import operator

# Information on a single wireless AP
Signal = collections.namedtuple('Signal', ['ssid', 'bssid', 'rssi'])

class PointSignals(dict):
    """All signals for a given Cartesian point"""

    def add_signal(self, s):
        self[s.bssid] = s

    def get_text(self):
        """Get text suitable for a tooltip"""
        return "\n".join("%s %s %d" % (self[b].ssid, self[b].bssid,
                                       self[b].rssi)
                         for b in sorted(self.keys()))

    def get_all_rssi(self, bssids):
        """Get a list of RSSI values for the given BSSIDs.
           None is returned for any missing BSSID."""
        def get_rssi(sd, b):
            if b in sd:
                return sd[b].rssi
        return [get_rssi(self, b) for b in bssids]

class Signals(object):
    """All wireless AP signal information, sorted by bssid and position"""
    def __init__(self):
        self._signals = {}

    def add_point_signals(self, point, point_signals):
        self._signals[point] = point_signals

    def positions(self):
        return self._signals.items()

    def get_all_bssids(self):
        seen = {}
        for sd in self._signals.values():
            for signal in sd.values():
                seen[signal.bssid] = signal.ssid
        return sorted(seen.items(), key=operator.itemgetter(0))

    def write_csv(self, csvfile):
        w = csv.writer(csvfile)
        bssids = self.get_all_bssids()
        w.writerow(['X', 'Y'] + ["%s;%s" % b for b in bssids])
        bssids = [b[0] for b in bssids]
        for pos, ps in self.positions():
            p = list(pos) + ps.get_all_rssi(bssids)
            w.writerow(p)


class AirportQuery(object):
    def get_signals(self):
        out = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], universal_newlines=True)
        p = PointSignals()
        for ssid, bssid, rssi in re.findall(
                              '(\S+)\s+(..:..:..:..:..:..)\s+([\d-]+)', out):
            s = Signal(ssid=ssid, bssid=bssid, rssi=int(rssi))
            p.add_signal(s)
        return p

class FloorPlan(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        pixmap = QPixmap()
        self.setPixmap(pixmap)
        self.q = AirportQuery()
        self._signals = Signals()

        self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos()
            ps = self.q.get_signals()
            self._signals.add_point_signals((pos.x(), pos.y()), ps)
            label = QLabel('X', self)
            label.setToolTip(ps.get_text())
            label.move(pos)
            label.show()
 
class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'WiFi Heatmap'
        self.setWindowTitle(self.title)

        self.setup_menu()

        # Create widget
        self.plan = FloorPlan()

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.plan)
        self.setCentralWidget(self.scrollArea)
        self.show()

    def load_image(self, file_name):
        p = self.plan.pixmap()
        p.load(file_name)
        self.plan.setFixedSize(p.width(), p.height())
        self.setMaximumSize(QtCore.QSize(max(self.plan.width(), 400),
                                         max(self.plan.height(), 400)))

    def open_floor_plan_dialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select image file",
                       "","All Files (*);;Image Files (*.jpg)", options=options)
        if fileName:
            self.load_image(fileName)

    def save_survey(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Select CSV file",
                       "","All Files (*);;CSV Files (*.csv)", options=options)
        if file_name:
            with open(file_name, 'w', newline='') as csvfile:
                self.plan._signals.write_csv(csvfile)
            print('file saved as ' + file_name)

    def setup_menu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        b = QAction('Open Floor Plan...', self)
        b.triggered.connect(self.open_floor_plan_dialog)
        fileMenu.addAction(b)

        b = QAction('Save Survey...', self)
        b.triggered.connect(self.save_survey)
        fileMenu.addAction(b)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
