# -*- coding: utf-8 -*-
"""
Long Chang, UH, August 2013
"""

import sys
from PyQt4 import QtCore, QtGui
from GDS2v3 import GDS2v3

class mainGUI(QtGui.QMainWindow):
    def __init__(self):
        super(mainGUI, self).__init__()
        self.setGeometry(100,100,300,400)
        self.setAcceptDrops(True)
        self.initGUI()
        self.initLayout()
        self.initConnection()
        self.filepath = ''
        self.GDS2v3 = GDS2v3()
        self.GDS2v3.setMode(2)
        
    def initGUI(self):
        self.centralWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.rbSetMode2 = QtGui.QRadioButton(self.centralWidget)
        self.rbSetMode2.setChecked(True)
        self.rbSetMode2.setToolTip('Mode 2\nField size: 1000 um x 1000um\nStep resolution: 5nm\n\nMode 2 is used for general purpose ebeam writing due to its large field size. The resolution in is easily 20 nm.')
        self.rbSetMode2.setText('Mode 2')
        self.rbSetMode4 = QtGui.QRadioButton(self.centralWidget)
        self.rbSetMode4.setToolTip('Mode 4\nField size: 100 um x 100 um\nStep resolution: 0.5 nm\n\nMode 4 is used for high resolution and high precision ebeam writing.')
        self.rbSetMode4.setText('Mode 4')
        self.lwCellName = QtGui.QListWidget(self.centralWidget)
        self.lwCellName.addItem('Drag and Drop a GDS File into window')
        self.lwCellName.addItem('Select a cell name for conversion')
        self.lwCellName.addItem('Press convert')
        self.bConvert = QtGui.QPushButton(self.centralWidget)
        self.bConvert.setText('Convert')
        self.bConvert.setToolTip('Converts a #.GDS layout to *.v30')
        
    def initLayout(self):
        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.addWidget(self.rbSetMode2)
        self.horizontalLayout.addWidget(self.rbSetMode4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.lwCellName)
        self.verticalLayout.addWidget(self.bConvert)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
    
    def initConnection(self):
        self.bConvert.clicked.connect(self.convert)
        QtCore.QObject.connect(self.rbSetMode2, QtCore.SIGNAL("clicked()"), self.setMode2)
        QtCore.QObject.connect(self.rbSetMode4, QtCore.SIGNAL("clicked()"), self.setMode4)
        
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(mainGUI, self).dragEnterEvent(event)
 
    def dragMoveEvent(self, event):
        super(mainGUI, self).dragMoveEvent(event)
 
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.filepath = str(url.path())
                if not self.filepath[-4:].lower() == '.gds':
                    raise TypeError('ConverterGUI: Please drop a GDS file into the window')
                self.loadGDS()
                event.acceptProposedAction()
        else:
            super(mainGUI,self).dropEvent(event)
    
    def setMode2(self):
        self.GDS2v3.setMode(2)
            
    def setMode4(self):
        self.GDS2v3.setMode(4)
    
    def loadGDS(self):
        self.GDS2v3.g.__init__()
        self.GDS2v3.readGDS(self.filepath)
        sname = sorted(self.GDS2v3.g.structureName)
        self.lwCellName.clear()
        self.lwCellName.addItems(sname)
        try:
            self.lwCellName.setItemSelected(self.lwCellName.item(sname.index('main')),True)
        except:
            self.lwCellName.setItemSelected(self.lwCellName.item(0),True)
        
    def convert(self):
        self.GDS2v3.v.__init__()
        self.GDS2v3.c.__init__()
        #Set the mode
        if self.rbSetMode2.isChecked():
            self.setMode2()
        elif self.rbSetMode4.isChecked():
            self.setMode4()
        else:
            raise ValueError('ConverterGUI: No mode is selected')
        
        #Determine selected cell
        item = self.lwCellName.selectedItems()
        cellName = str(item[0].text())
        self.GDS2v3.selectCell(cellName)
        
        #Convert from GDS 2 ELD
        self.GDS2v3.convGDS2ELD()
        
        #Convert from ELD to v30
        self.GDS2v3.convELD2v3()
            
        #Write v30 file
        self.GDS2v3.writev3()
        msg = 'Conversion was successful.\n\nThe converted file is called:\n\n' + self.filepath[:-4] + '.v30'
        self.report(msg)
    
    def report(self, msg):
        self.reportDialog = reportDialog(self)
        self.reportDialog.setMessage(msg)
        self.reportDialog.show()
    
class reportDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(reportDialog, self).__init__(parent)
        self.initGUI()
        self.initLayout()
        self.initConnection()

    def initGUI(self):
        self.bOK = QtGui.QPushButton(self)
        self.bOK.setText('OK')
        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.setText("This is a QTextBrowser!")

    def initLayout(self):
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.addWidget(self.bOK)
    
    def initConnection(self):
        self.bOK.clicked.connect(self.close)
    
    def setMessage(self, msg):
        self.textBrowser.setText(msg)
        
if __name__ == '__main__':
 
    app = QtGui.QApplication(sys.argv)
    window = mainGUI()
    window.show()
    sys.exit(app.exec_())