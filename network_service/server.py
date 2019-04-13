#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'wangsy'

import sys
import json
import time
import struct

from twisted.python import log
from twisted.internet import reactor, task
from twisted.internet.protocol import Factory, Protocol

from .api import SLMS

from .config import LISTEN_PORT, HEART_CYCLE

from . import __version__


log.startLogging(sys.stdout)

# twisted clients pool
clients = {}


class Server(Protocol):

    def __init__(self):
        self.user = None
        self._data_buffer = bytes()
        self.last_heartbeat_time = int(time.time())
        self.promise = {
            1: self.register,
            2: self.single_message,
            3: self.group_message,
            4: self.broadcast_message,
            5: self.heartbeat
        }
        self.cmd_actions = (
            "load_inventory", "lighten", "get_lamp_status",
            "get_hub_status", "send_down_policyset",
            "gather_policyset", "cancel_policyset",
            "send_down_group_config", "cancel_group_config",
            "gather_group_config"
        )
        self.cmd_ack_actions = ['{}_ack'.format(i) for i in self.cmd_actions]
        self.time_actions = ("report_status", "report_alarms")

    def connectionMade(self):
        log.msg("New connection established.")
        log.msg("The host of new connection is:", self.transport.getPeer().host)

    def is_hub(self):
        if not self.user:
            return False
        if self.user.startswith('cmd'):
            # 管控指令
            return False
        return True

    def connectionLost(self, reason):
        if self.is_hub():
            log.msg("Connection break!")
            SLMS.record_offline_hub(self.user)  # 记录脱网后的集控
        if self.user in clients:
            log.msg("Remove <{}> from server!".format(self.user))
            clients.pop(self.user, None)

        log.msg("Online clients now:", clients)

    def dataReceived(self, data):
        """
        接受到数据以后的操作
        from smarlamp:
            1. cmd
        from hub:
            1. heartbeat
            2. register
            3. ack
        """
        # TODO 过滤干扰字符(无效command_id，长度不够等)
        log.msg('receive: {}, {}'.format(data, type(data)))
        self._data_buffer += data
        if len(self._data_buffer) < 12:
            return

        length, _, command_id = struct.unpack("!3I", self._data_buffer[:12])
        if length > len(self._data_buffer):
            # 长度不够， 未接收完
            return

        content = self._data_buffer[12:length]

        if command_id not in (1, 2, 3, 4, 5):
            log.msg("Invalid command_id.")
            return

        # 不同的command_id执行不同操作
        log.msg("command_id = {}, content = {}".format(command_id, content))
        self.promise[command_id](content=content)

        # 重置buffer
        self._data_buffer = self._data_buffer[length:]

        if len(self._data_buffer) < 12:
            return

    def register(self, content):
        """
        注册
        1. 管控客户端
        2. 集控客户端
        """
        content = json.loads(content)
        if self.is_hub():
            # 集控客户端
            self._register_hub(content)
        else:
            # 管控客户端
            self._register_cmd(content)

    def single_message(self, content):
        """
        单播
        """
        content = json.loads(content)
        sender = content.get("sender")
        receiver = content.get("receiver")
        body = content.get("body")
        action = body.get('action')

        if action in self.cmd_actions:
            # 管控下发指令, 往集控下发
            # sender=cmd-xxx, receiver=hub
            hub = receiver
            cmd = sender
            self._send_to_hub(content=content, hub=hub, sender=cmd)
        elif action in self.cmd_ack_actions:
            # 集控反馈指令, 往管控平台发送
            # sender=hub, receiver=cmd-xxx
            hub = sender
            cmd = receiver
            self._send_to_cmd(content=content, cmd=cmd, sender=hub)
        elif action in self.time_actions:
            # 集控定时上报指令, 内部处理完, 往集控发送ack
            # 这里需要注意: SLMS中的上报指令处理函数名必须和action同名
            ret = getattr(SLMS, action)(content=content)
            code = ret.get('code', 1)
            message = code == 0 and "上报成功" or "上报失败"
            reason = ret.get("reason")

            send_content = dict(
                action="{}_ack".format(action),
                type="ack",
                code=code,
                message=message,
                reason=reason
            )
            self.write(102, json.dumps(send_content))

    def group_message(self, content):
        """
        组播
        暂时没有用到， 不知道以后会不会有需求， 暂时不删
        """
        content = json.loads(content)
        sender = content.get("sender")
        receiver = content.get("receiver")
        message = content.get("message")
        send_content = json.dumps(dict(sender=sender, message=message))

        users = receiver
        self.send_content(send_content, 103, users, sender)

    def broadcast_message(self, content):
        """
        广播
        暂时没有用到， 不知道以后会不会有需求， 暂时不删
        """
        content = json.loads(content)
        sender = content.get("sender")
        message = content.get("message")
        send_content = json.dumps(dict(sender=sender, message=message))

        users = clients.keys()
        self.send_content(send_content, 104, users)

    def heartbeat(self, **kwargs):
        """
        处理心跳包
        """
        log.msg("receive heartbeat from {}".format(self.user))
        self.last_heartbeat_time = int(time.time())

    def _register_cmd(self, content):
        """管控客户端注册"""
        assert isinstance(content, dict)
        user = content.get("sender")
        self.user = user
        clients[user] = self
        log.msg("New client <{}> has registered!".format(user))
        log.msg("Online clients now: {}".format(clients))
        success_content = dict(
            action="register_server_ack",
            type="ack",
            code=0,
            message="向服务器注册成功"
        )
        self.write(101, json.dumps(success_content))

    def _register_hub(self, content):
        """集控客户端注册"""
        assert isinstance(content, dict)
        user = content.get("sender")
        self.user = user
        # 已存在, 断开之前连接，重新注册
        if user in clients and clients[user].is_hub():
            log.msg("Hub <{}> is already existed.".format(user))
            clients[user].abort_connection()
        body = content.get('body')
        inventory = body.get("inventory")
        default_group = body.get('default_group')
        ret_msg = SLMS.register(inventory=inventory,
                                default_group=default_group)
        code = ret_msg.get("code")
        if code != 0:
            # 注册失败
            failure_content = dict(
                action="register_server_ack",
                type="ack",
                code=code,
                message="向服务器注册失败",
                reason=ret_msg.get('reason')
            )
            self.write(101, json.dumps(failure_content))
            self.abort_connection()
            return

        clients[user] = self
        SLMS.record_connect_hub(self.user)
        log.msg("New hub <{}> has registered!".format(user))
        log.msg("Online hubs now: {}".format(clients))
        success_content = dict(
            action="register_server_ack",
            type="ack",
            code=0,
            message="向服务器注册成功"
        )
        self.write(101, json.dumps(success_content))

    def write(self, command_id, content):
        """通过transport发送(接收者为self.user)
        like self.transport.write()
        :param command_id: 指令id
        :param content: 包数据
        """
        header = self.pack_header(12 + len(content), __version__, command_id)
        log.msg("[{}] send_content to [{}]: {}".format('NS', self.user, content))
        self.transport.write(header + content.encode('utf-8'))

    def abort_connection(self):
        """中断连接"""
        self.transport.abortConnection()

    def _send_to_hub(self, content, hub, sender='NS'):
        # 给集控发送指令(cmd)
        header = self.pack_header(12 + len(content), __version__, 102)
        if hub in clients:
            # 集控在线， 正常发送
            log.msg("[{}] send_content to [{}]: {}".format(sender, hub, content))
            clients[hub].transport.write(header + content)
        else:
            # 集控脱网
            # 当前用户是cmd, 发送不在线反馈给管控(self.user)
            log.msg("Hub <{}> is offline. Can not be communicated with it.".format(hub))
            body = dict(action='ns_ack', code=101,
                        message="集控[{}]脱网, 无法通信".format(hub))
            content = dict(
                sender=sender,
                receiver=self.user,
                body=body
            )
            self.write(header + json.dumps(content))

    @staticmethod
    def pack_header(length, version, command_id):
        """generate header"""
        header = [length, version, command_id]
        header_pack = struct.pack("!3I", *header)
        return header_pack

    def _send_to_cmd(self, content, cmd, sender='NS'):
        # 给管控发送(ack)
        header = self.pack_header(12 + len(content), __version__, 102)
        if cmd not in clients:
            # 管控指令超时, 断开连接, 不在线, 和集控(self.user)断开连接
            self.abort_connection()
            return
        # 管控指令在线， 正常发送
        log.msg("[{}] send_content to [{}]: {}".format(sender, cmd, content))
        clients[cmd].transport.write(header + content)


class ServerFactory(Factory):

    def buildProtocol(self, addr):
        return Server()

    @staticmethod
    def check_users_online():
        log.msg("Check whether hubs are online.")
        for hub, server in clients.items():
            if not server.is_hub():
                continue
            now = int(time.time())
            # 大于5个心跳周期没有心跳， 则断开
            if now - server.last_heartbeat_time <= HEART_CYCLE * 5:
                continue
            log.msg("There is no heartbeat of <{}>. Break it.".format(hub))
            server.abort_connection()
            # SLMS.record_offline_hub(hub)


def start_reactor():
    sf = ServerFactory()

    task1 = task.LoopingCall(sf.check_users_online)  # 加入一个循环任务，循环检测心跳
    task1.start(61, now=False)                       # 每隔61秒检查一次心跳

    reactor.listenTCP(LISTEN_PORT, sf)
    reactor.run()
