#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/13
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")

import django

django.setup()

import json
import socket
import struct

from utils.exceptions import ConnectNSError, AuthenticateNSError, ConnectHubTimeOut


SENDER = 'NS'


class MessageSocket(object):
    """
    用于发送和接收消息，默认发送方是自己(smartlamp平台)
    """

    BUFFER_SIZE = 4096000

    def __init__(self, ip, port, sender=None, timeout=60):
        self.version = 0
        self.addr = (ip, port)
        self.sender = sender  # 用于__enter__中
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        try:
            self.socket.connect(self.addr)
        except ConnectionRefusedError:
            raise ConnectNSError

    def _pack_header(self, command_id, message):
        """
        打包数据头
        """
        length = 12 + len(message)
        version = self.version
        command_id = command_id
        header = [length, version, command_id]
        packed_header = struct.pack('!3I', *header)
        return packed_header

    def verify(self, sender=SENDER):
        """
        向服务器发送验证，并接收返回的验证消息
        成功返回 True
        """
        verify_message_dict = {
            "sender": sender,
            "action": "register"
        }
        message = json.dumps(verify_message_dict)
        packed_header = self._pack_header(command_id=1, message=message)
        self.socket.sendall(packed_header + message.encode('utf-8'))   # 发送验证消息

        # 接收验证消息，如果验证通过返回True
        data = self.socket.recv(1024)
        length, version, command_id = struct.unpack('!3I', data[:12])
        content = data[12:length]
        content = json.loads(content)
        body = content.get('body', {})
        code = body.get('code')
        return True if code == 0 else False

    def send_single_message(self, receiver, body, sender=SENDER):
        """
        发送一对一消息
        """
        body_dict = {
            "sender": sender,
            "receiver": receiver,
            "body": body
        }

        body = json.dumps(body_dict)
        packed_header = self._pack_header(command_id=2, message=body)
        self.socket.sendall(packed_header + body.encode('utf-8'))

    def send_group_message(self, receiver, message, sender=SENDER):
        """
        发送组聊内容，给指定的若干个hub发送指令
        """
        message_dict = {
            "sender": sender,
            "receiver": receiver,
            "message": message
        }

        message = json.dumps(message_dict)
        packed_header = self._pack_header(command_id=3, message=message)
        self.socket.sendall(packed_header + message.encode('utf-8'))

    def send_broadcast_message(self, message, sender=SENDER):
        """
        发送群聊内容，给所有已连接服务器的hub发送指令
        """
        message_dict = {
            "sender": sender,
            "message": message
        }

        message = json.dumps(message_dict)
        packed_header = self._pack_header(command_id=4, message=message)
        self.socket.sendall(packed_header + message.encode('utf-8'))

    def receive_data(self, buffer_size=BUFFER_SIZE):
        """
        用来接收、处理消息，返回处理好的消息
        """
        # 数据可能不能一次性接收完整
        import time
        start = time.time()
        pack_data = bytes()
        recv_len = 0
        buf_data = self.socket.recv(buffer_size)
        recv_len += len(buf_data)
        length, _, _ = struct.unpack('!3I', buf_data[:12])
        pack_data += buf_data
        while recv_len < length:
            buf_data = self.socket.recv(buffer_size)
            recv_len += len(buf_data)
            pack_data += buf_data
        # pack_data = ''.join(pack_data)

        length, version, command_id = struct.unpack('!3I', pack_data[:12])
        content = pack_data[12:length]
        content_dict = json.loads(content)
        body = content_dict.get('body')
        end = time.time()
        print(11111111111111111111111, end - start)
        if isinstance(body, str):
            return json.loads(body)
        elif isinstance(body, dict):
            return body
        else:
            print('其他数据类型')

    def __enter__(self):
        verify = self.verify(sender=self.sender)
        if not verify:
            raise AuthenticateNSError
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
        if exc_type == socket.timeout:
            raise ConnectHubTimeOut
        # return True


if __name__ == '__main__':
    body = {
        "action": "get_lamp_status",
        "type": "cmd",
        "lamp_sn": "lamp-100001"
    }
    body = json.dumps(body)
    with MessageSocket('127.0.0.1', 9995, sender='cmd-wangsy') as msg_socket:
        msg_socket.send_single_message(receiver='cabbyw-000001', body=body, sender=msg_socket.sender)
        recv = msg_socket.receive_data()
        print(recv)
