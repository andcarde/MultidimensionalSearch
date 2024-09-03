import sys

from ParetoLib.GUI.GUI import MainWindow
from PyQt5.QtWidgets import QApplication

from ParetoLib.GUI.application_service import ApplicationService
from ParetoLib.GUI.controller import Controller


def main():
    # :: QApplication
    app = QApplication(sys.argv)
    # :: MainWindow
    window = MainWindow()
    window.centralwidget.adjustSize()
    window.show()
    # :: ApplicationService
    application_service = ApplicationService(window)
    Controller(application_service, window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
