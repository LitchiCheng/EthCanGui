import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import Receive,Send,CanData,EthCanGui

class ReceiveThread(QtCore.QThread):
    def __init__(self, dispContent):
        super(ReceiveThread, self).__init__()
        self.dispContent = dispContent
        self.udp_read = Receive.receiveByUdp()

    def run(self):
        while True:
            self.udp_read.read(self.dispContent)

class MyWindow(QMainWindow, EthCanGui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.send_button.clicked.connect(self.sendCanData)
        self.check_send1.setChecked(True)
        self.line_id_1.setText("0x000103")
        self.line_data_1.setText("00 00 00 00 00 00 00 00")

        self.startReceiveThread()
        self.udp_send = Send.sendByUdp()

        self.usr_send_line_que = []
        self.usr_send_line_que.append((self.check_send1,self.line_id_1,self.line_data_1))
        self.usr_send_line_que.append((self.check_send2,self.line_id_2,self.line_data_2))
        self.usr_send_line_que.append((self.check_send3,self.line_id_3,self.line_data_3))
        self.usr_send_line_que.append((self.check_send4,self.line_id_4,self.line_data_4))
        self.usr_send_line_que.append((self.check_send5,self.line_id_5,self.line_data_5))
        self.usr_send_line_que.append((self.check_send6,self.line_id_6,self.line_data_6))
        
    
    def dispContent(self, argvStr):
        argvStr = str(argvStr)
        self.textEdit.append(argvStr)

    def startReceiveThread(self):
        self.serialThread = ReceiveThread(self.dispContent)
        self.serialThread.start()

    def sendCanData(self):
        for send_line in self.usr_send_line_que:  
            if send_line[0].isChecked():
                test_data = CanData.txCanData()
                test_data.setID(int(send_line[1].text(), base=16))
                test_data.setChannel(1)
                # data_array = [0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07]
                data_array = self.line_data_1.text().split(" ")
                for index in range(len(data_array)):
                    data_array[index] = int("0x" + data_array[index], base=16)
                print(data_array)
                test_data.setData(data_array)
                test_data.setDLC(len(data_array))
                self.udp_send.pushData(test_data)
                self.udp_send.send()
                self.udp_send.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())