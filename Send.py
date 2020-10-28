import CanFrame_pb2
import socket
import struct
import time
import os
import sys
import CanData as can
import copy

class sendBase(object):
    def __init__(self):
        self.data_que = []
    def pushData(self, tx_data):
        if isinstance(tx_data, can.txCanData):
            self.data_que.append(tx_data)
        else:
            print("push data type error %s %s" % (type(tx_data),type(can.txCanData)))
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
    test_data = can.txCanData()
    test_data.setID(0x103)
    test_data.setChannel(1)
    data_array = [0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07]
    test_data.setData(data_array)
    test_data.setDLC(len(data_array))

    udp_send = sendByUdp()
    while True:
        test_data.setID(0x103)
        udp_send.pushData(test_data)
        # test_data2 = can.txCanData()
        test_data2 = copy.deepcopy(test_data)
        test_data2.setID(0x105)
        udp_send.pushData(test_data2)
        udp_send.send()
        udp_send.clear()
        time.sleep(0.1)