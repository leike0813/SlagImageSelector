import sys
import PySide2.QtWidgets as QtW
from widgets.mainWindow import MainWindow


app = QtW.QApplication(sys.argv)
win = MainWindow(disableConsole=False)
win.show()
sys.exit(app.exec_())