import sys
import os
import logging

from PySide6.QtWidgets import QApplication

from ui.mainwindow import MainWindow

logger = logging.getLogger(__name__)


def main():
    if os.getenv('DEBUG') == 'true' or os.getenv('DEBUG') == 'True':
        logging.basicConfig(level=logging.DEBUG)
        logger.debug('Logging level set to DEBUG')
    else:
        logging.basicConfig(level=logging.ERROR)
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.readSettings()
    mainWindow.statusBar().showMessage(mainWindow.tr('Ready'))
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
