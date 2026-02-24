import sys
from PyQt5.QtWidgets import QApplication
from pet_window import PetWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PetWindow()
    sys.exit(app.exec_())
