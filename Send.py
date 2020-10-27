import CanFrame_pb2
import socket
import struct
import time
import os
import sys

class direction:
    rx = 0
    tx = 1

class txCanData(object):
    def __init__(self):
        self.id = 0x000
        self.is_extend = False
        self.is_remote = False
        self.DLC = 8
        self.Data = [0x00,00,0x00,0x00,0x00,0x00,0x00,0x00]
        self.channel = 1
        self.timestamp = 0
        self.direction = direction.tx
    def copy(self, orig):
        self.id = orig.getID()
        self.is_extend = orig.getExtend()
        self.is_remote = orig.getRemote()
        self.DLC = orig.getDLC()
        self.copyData(orig)
        self.channel = orig.getChannel()
        self.timestamp = 0
        self.direction = direction.tx
    def setExtend(self):
        self.is_extend = True
    def getExtend(self):
        return self.is_extend
    def setRemote(self):
        self.is_remote = True
    def getRemote(self):
        return self.is_remote
    def setID(self,id):
        self.id = id
    def getID(self):
        return self.id
    def setDLC(self,num):
        if num > 8:
            self.DLC = 8
        else:
            self.DLC = num
    def getDLC(self):
        return self.DLC
    def copyData(self,org_data):
        if len(org_data.Data) == 8:
            self.Data = org_data.Data.copy()
    def setData(self,array_data):
        if len(array_data) == 8:
            self.Data = array_data.copy()
    def getData(self):
        return self.Data
    def setChannel(self,channel):
        self.channel = channel
    def getChannel(self):
        return self.channel

class sendBase(object):
    def __init__(self):
        self.data_que = []
    def pushData(self, tx_data):
        if isinstance(tx_data, txCanData):
            self.data_que.append(tx_data)
        else:
            print("push data type error %s %s" % (type(tx_data),type(txCanData)))
        self.data_que.append(tx_data)
    def send(self):
        pass
    
class sendByUdp(sendBase):
    def send(self):
        cmd_hear = 0x00001017
        remote_addr = ('192.168.192.4', 15003)
        so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        so.settimeout(2)
        for tx_data in self.data_que:
            # 转换数据到protobuff
            frame = CanFrame_pb2.CanFrame()
            frame.ID = tx_data.getID()
            frame.Extended = tx_data.getExtend()
            frame.Remote = tx_data.getRemote()
            frame.DLC = tx_data.getDLC()
            databytes = bytearray(tx_data.getDLC())
            for i in range(0 , tx_data.getDLC()):
                databytes[i] = tx_data.Data[i]
            frame.Data = bytes(databytes)
            frame.Channel = tx_data.getChannel()
            # udp发送字节流
            serialized_pb_CAN_msg = frame.SerializeToString()
            msg = struct.pack('<I' + str(len(serialized_pb_CAN_msg)) + 's', cmd_hear, serialized_pb_CAN_msg)
            so.sendto(msg, remote_addr)
    def clear(self):
        self.data_que.clear()

if __name__ == "__main__":
    test_data = txCanData()
    test_data.setID(0x103)
    test_data.setChannel(1)
    data_array = [0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07]
    test_data.setData(data_array)
    test_data.setDLC(len(data_array))

    udp_send = sendByUdp()
    while True:
        test_data.setID(0x103)
        udp_send.pushData(test_data)
        test_data2 = txCanData()
        test_data2.copy(test_data)
        test_data2.setID(0x105)
        udp_send.pushData(test_data2)
        udp_send.send()
        udp_send.clear()
        time.sleep(0.1)