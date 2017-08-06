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

class Signals(object):
    """All wireless AP signal information, sorted by bssid and position"""
    def __init__(self):
        self._signals = {}

    def add_signal(self, pos, signal):
        if pos not in self._signals:
            self._signals[pos] = {}
        self._signals[pos][signal.bssid] = signal

    def positions(self):
        return self._signals.items()

    def get_all_bssids(self):
        seen = {}
        for sd in self._signals.values():
            for signal in sd.values():
                seen[signal.bssid] = signal.ssid
        return sorted(seen.items(), key=operator.itemgetter(0))

    def get_text(self, pos):
        """Get text suitable for a tooltip"""
        sd = self._signals[pos]
        return "\n".join("%s %s %d" % (sd[b].ssid, sd[b].bssid, sd[b].rssi)
                         for b in sorted(sd.keys()))

class AirportQuery(object):
    def get_signals(self):
        out = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], universal_newlines=True)
        for ssid, bssid, rssi in re.findall(
                              '(\S+)\s+(..:..:..:..:..:..)\s+([\d-]+)', out):
            s = Signal(ssid=ssid, bssid=bssid, rssi=int(rssi))
            yield s

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
            for signal in self.q.get_signals():
                self._signals.add_signal((pos.x(), pos.y()), signal)
            print("mouse pressed at", pos)
            label = QLabel('X', self)
            label.setToolTip(self._signals.get_text((pos.x(), pos.y())))
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

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select image file",
                       "","All Files (*);;Image Files (*.jpg)", options=options)
        if fileName:
            self.load_image(fileName)

    def save_points(self):
        def get_rssi(sd, b):
            if b in sd:
                return sd[b].rssi
        bssids = self.plan._signals.get_all_bssids()
        with open('out.csv', 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(['X', 'Y'] + ["%s:%s" % b for b in bssids])
            for pos, sd in self.plan._signals.positions():
                p = list(pos) + [get_rssi(sd, b[0]) for b in bssids]
                w.writerow(p)
        print('file saved as out.csv')

    def setup_menu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        openButton = QAction('Open File...', self)
        openButton.triggered.connect(self.openFileDialog)
        fileMenu.addAction(openButton)

        saveButton = QAction('Save points...', self)
        saveButton.triggered.connect(self.save_points)
        fileMenu.addAction(saveButton)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
