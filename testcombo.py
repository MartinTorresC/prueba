'''
Created on Jul 9, 2018

@author: Administrator
'''
import sys

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot


class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # creates a combobox
        self.combobox = QtGui.QComboBox()

        # adds multiple items using a list comprehension
        strlist = ['Item {}'.format(i) for i in xrange(1, 11)]
        self.combobox.addItems(strlist)

        # 'currentIndexChanged()' signal
        self.combobox.currentIndexChanged['int'].connect(self.current_index_changed)

        # updates the status bar
        self.update_statusbar()

        # sets the central widget
        self.setCentralWidget(self.combobox)

    # 'current_index_changed()' slot
    @pyqtSlot(int)
    def current_index_changed(self, index):
        # updates the status bar
        self.update_statusbar()

    def update_statusbar(self):
        """
        Shows the index and text of the current item
        """
        self.statusBar().showMessage('Current index: {}, Current text: {}'.format(
            self.combobox.currentIndex(),
            self.combobox.currentText()
        ))


# creates the application
application = QtGui.QApplication(sys.argv)

# creates the window
window = Window()

# window properties
window.setWindowTitle('QComboBox - current item')  # title
window.resize(360, 50)  # size

# shows the window
window.show()

# runs the application
sys.exit(application.exec_())