import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

APP_NAME = 'QSound'
ORGANIZATION = 'Pade'


def main():
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.readSettings()
    mainWindow.statusBar().showMessage(mainWindow.tr('Ready'))
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
