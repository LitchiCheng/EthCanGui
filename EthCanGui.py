import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
import Receive,Send,CanData,EthCanGuiUi,time
from datetime import datetime

class ReceiveThread(QtCore.QThread):
    updated = QtCore.pyqtSignal(str)
    def __init__(self, dispContent):
        super(ReceiveThread, self).__init__()
        self.dispContent = dispContent
        self.udp_read = Receive.receiveByUdp()

    def run(self):
        while True:
            time.sleep(0.0001)
            rec_str = self.udp_read.read(self.dispContent)
            if rec_str != "":
                self.updated.emit(str(rec_str))
            elif rec_str == "receive no data...........":
                self.udp_read.launchEthCanTool()
    
    def setUserTimestamp(self, status):
        self.udp_read.setUserTimestamp(status)

class MyWindow(QMainWindow, EthCanGuiUi.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.usr_send_line_que = []
        self.usr_send_line_que.append((self.check_send1,self.line_id_1,self.line_data_1))
        self.usr_send_line_que.append((self.check_send2,self.line_id_2,self.line_data_2))
        self.usr_send_line_que.append((self.check_send3,self.line_id_3,self.line_data_3))
        self.usr_send_line_que.append((self.check_send4,self.line_id_4,self.line_data_4))
        self.usr_send_line_que.append((self.check_send5,self.line_id_5,self.line_data_5))
        self.usr_send_line_que.append((self.check_send6,self.line_id_6,self.line_data_6))

        self.send_button.clicked.connect(self.sendCanData)
        self.save_button.clicked.connect(self.saveCanData)
        self.stop_button.clicked.connect(self.stopPrint)
        self.comboBox.currentIndexChanged.connect(self.selectTimeType)

        self.save_flag = False
        self.print_flag = True
        self.save_dirpath = ("","")

        self.serialThread = ReceiveThread(self.dispContent)
        self.serialThread.start()
        self.serialThread.updated.connect(self.updateText)

        self.udp_send = Send.sendByUdp()

        self.textEdit.document().setMaximumBlockCount(3000)

    def updateText(self, text):
        if self.print_flag:
            self.textEdit.append(str(text))
        # save to file
        if self.save_flag:
            if self.save_dirpath[0] != "":
                self.file.write(text)

    def selectTimeType(self):
        if self.comboBox.currentText() == "Original Stamp":
            self.serialThread.setUserTimestamp(False)
        elif self.comboBox.currentText() == "User Date":
            self.serialThread.setUserTimestamp(True)

    def stopPrint(self):
        self.print_flag = not self.print_flag
        if self.print_flag:
            self.stop_button.setText("Stop Print")
            self.textEdit.moveCursor(self.textEdit.textCursor().End)
        else:
            self.stop_button.setText("Continue Print")

    def saveCanData(self):
        self.save_flag = not self.save_flag
        if self.save_flag:
            self.save_button.setText("Stop Save")
            # can_2020-24-15-24-53.740404.log %Y-%m-%d %H:%M:%S
            file_str = datetime.strftime(datetime.now(), 'can_%Y-%m-%d-%H:%M:%S.%f').replace(" ","")
            print(datetime.now())
            self.save_dirpath = QFileDialog.getSaveFileName(self, '选择保存路径', 'C:\\' +file_str+'.log', 'log(*.log)')
            print(self.save_dirpath)
            if self.save_dirpath[0] is "":
                self.save_flag = False
                self.save_button.setText("Start Save")
            else:
                self.save_flag = True
                self.file = open(self.save_dirpath[0],'a')
        else:
            self.save_button.setText("Start Save")
            self.file.close()
        
    def dispContent(self, argvStr):
        # # print(argvStr)
        # if self.print_flag:
        #     self.textEdit.append(str(argvStr))
        #     self.textEdit.moveCursor(self.textEdit.textCursor().End)
        # # save to file
        # if self.save_flag:
        #     if self.save_dirpath[0] != "":
        #         with open(self.save_dirpath[0],'a') as f:
        #             f.write(argvStr)
        pass

    def sendCanData(self):
        for send_line in self.usr_send_line_que:  
            if send_line[0].isChecked():
                test_data = CanData.txCanData()
                test_data.setID(int(send_line[1].text(), base=16))
                test_data.setChannel(1)
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
    with open('qss/DarkOrangeQss.txt') as file:
        qss_str = file.readlines()
        qss_str = ''.join(qss_str).strip('\n')
        app.setStyleSheet(qss_str)
    myWin.show()
    sys.exit(app.exec_())
    myWin.file.close()