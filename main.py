import sys
import PySide2.QtWidgets as QtW
from widgets.mainWindow import MainWindow

# class Container:
#     def __init__(self):
#         self.app = QtW.QApplication(sys.argv)
#         self.win = MainWindow(disableConsole=False)
#         self.win.show()
#         sys.exit(self.app.exec_())
#
# container = Container()

app = QtW.QApplication(sys.argv)
win = MainWindow(disableConsole=False)
win.show()
sys.exit(app.exec_())