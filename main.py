import sys
import PySide2.QtWidgets as QtW
from widgets.mainWindow import MainWindow


app = QtW.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())