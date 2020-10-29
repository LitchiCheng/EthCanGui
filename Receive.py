import CanFrame_pb2
import socket, struct, time, os, sys
import CanData as can
from datetime import datetime

class receiveBase(object):
    def __init__(self):
        self.data_que = []
    def pushData(self, rx_data):
        if isinstance(rx_data, can.rxCanData):
            self.data_que.append(rx_data)
        else:
            print("push data type error %s %s" % (type(rx_data),type(can.txCanData)))
    def read(self):
        pass

class receiveByUdp(receiveBase):
    def __init__(self):
        super(receiveByUdp, self).__init__()
        self.so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.so.settimeout(2)
        self.launchEthCanTool()
        self.msgdict = {}
        self.framerate = (0, 0)
        self.remoteaddr = ""
        self.data = ""
        self.launchEthCanTool()
        self.queryForFrame(50)
        self.count = 0
        self.use_usrstamp = False

    def setUserTimestamp(self, status):
        self.use_usrstamp = status

    def launchEthCanTool(self):
        self.so.sendto(struct.pack('<2I', 0x1016, 0xffffffff), ('192.168.192.4', 15003))
        try:
            (self.data, self.remoteaddr) = self.so.recvfrom(1024)
        except socket.timeout:
            pass
        self.so.sendto(struct.pack('<2I', 0x1018, 0xffffffff), ('192.168.192.4', 15003))
        try:
            (self.data, self.remoteaddr) = self.so.recvfrom(1024)
        except socket.timeout:
            pass
    
    def queryForFrame(self, num):
        fullMsg = struct.pack('<2I', 0x1019, num)
        self.so.sendto(fullMsg, ('192.168.192.4', 15003))

    def read(self, print_callback):
        try:
            (self.data, self.remoteaddr) = self.so.recvfrom(1024)
        except socket.timeout:
            print('timeout')
            self.launchEthCanTool()
        (msgId, pbdata) = struct.unpack('<I' + str(len(self.data) - 4) + 's', self.data)
        frame = CanFrame_pb2.CanFrame()
        update = False
        if(0x00001019 == msgId):
            try:
                frame.ParseFromString(pbdata)
            except:
                print('pbdata parse error')
                print(self.data)
                os.system('pause')
            self.msgdict[frame.ID] = frame
            update = True
            self.count = self.count + 1
            
                
        elif 0x00001041 == msgId:
            self.framerate = struct.unpack('<2I', pbdata)
        if(update):
            dirc = ''
            if(self.msgdict[frame.ID].Direction == 1):
                dirc = 'TX'
            else:
                dirc = 'RX'
            if not self.use_usrstamp:
                tmps = '%d\t0x%04X\t%d\t%d\t%s\t%d\t ' % (
                    self.count, self.msgdict[frame.ID].ID, self.msgdict[frame.ID].Channel, self.msgdict[frame.ID].DLC, dirc, self.msgdict[frame.ID].Timestamp)
            else:
                tmps = '%d\t0x%04X\t%d\t%d\t%s\t%s\t ' % (
                    self.count, self.msgdict[frame.ID].ID, self.msgdict[frame.ID].Channel, self.msgdict[frame.ID].DLC, dirc, datetime.strftime(datetime.now(), '%H:%M:%S.%f')[0:-3])
            for i in range(0, self.msgdict[frame.ID].DLC):
                tmps += ('0x%02X ' % self.msgdict[frame.ID].Data[i])
            tmps += '\n'
            # sys.stdout.write(tmps)
            print_callback(tmps)

if __name__ == "__main__":
    test = receiveByUdp()
    while True:
        test.read()