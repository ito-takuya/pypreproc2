# Taku Ito
# 09/24/14
# PyPreproc2
#
# Script is to generate a GUI form from the default YAML configuration file

import sys, yaml
from PyQt4 import QtGui, QtCore
from formlayout import fedit

class Config(QtGui.QWidget):

    def __init__(self):
        super(Config, self).__init__()
        self.verticalLayout = QtGui.QVBoxLayout()
        self.plainTextEdit = QtGui.QPlainTextEdit()
        self.verticalLayout.addWidget(self.plainTextEdit)
        self.pushButton = QtGui.QPushButton("Load Yaml")
        self.verticalLayout.addWidget(self.pushButton)
        self.setLayout(self.verticalLayout)
        self.pushButton.clicked.connect(self.loadYaml)

    def loadYaml(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, "Open File", ".", "Yaml(*.yaml);;AllFiles(*.*)"))
        f = open(fileName)
        getData = yaml.safe_load(f)
        prettyData = yaml.dump(getData, default_flow_style=False)
        self.plainTextEdit.appendPlainText(str(prettyData))

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Config()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


