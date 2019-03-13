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

from network_service.api import SLMS

from network_service import __version__


log.startLogging(sys.stdout)


class Server(Protocol):

    def __init__(self, clients):
        self.clients = clients
        self.user = None
        self._data_buffer = bytes()
        self.last_heartbeat_time = int(time.time())
        self.command_func_map = {
            1: self.handle_verify,
            2: self.handle_single_message,
            3: self.handle_group_message,
            4: self.handle_broadcast_message,
            5: self.handle_heartbeat
        }

    def connectionMade(self):
        log.msg("New connection established.")
        log.msg("The info of new connection is:", self.transport.getPeer())

    def connectionLost(self, reason):
        if self.user and not self.user.startswith('cmd'):
            log.msg("Connection break!")
        if self.user in self.clients:
            log.msg("Remove <{}> from server!".format(self.user))
            if not self.user.startswith(("cmd", "illuminance")):
                SLMS.record_offline_hub(self.user)  # 记录脱网后的集控
            del self.clients[self.user]

        log.msg("Online hubs now:", self.clients)

    def dataReceived(self, data):
        """
        接受到数据以后的操作
        """
        log.msg('receive: {}, {}'.format(data, type(data)))
        self._data_buffer += data
        if len(self._data_buffer) < 12:
            return

        while True:
            length, _, command_id = struct.unpack("!3I", self._data_buffer[:12])
            if length > len(self._data_buffer):
                break

            content = self._data_buffer[12:length]

            if command_id not in [1, 2, 3, 4, 5]:
                log.msg("Invalid command_id.")
                return

            # self.command_func_map.get(command_id)(content)
            self.handle_data(command_id, content)

            self._data_buffer = self._data_buffer[length:]

            if len(self._data_buffer) < 12:
                break

    def handle_verify(self, content):
        """
        验证函数
        """
        content = json.loads(content)
        user = content.get("sender")
        if user in self.clients:
            log.msg("Hub <%s> is already existed." % user.encode("utf-8"))
            self.clients[user].connectionLost("")

        if user.startswith(("cmd", "illuminance")):
            code = 0
        else:
            body = json.loads(content.get('body'))
            inventory = body.get("inventory")
            default_group = body.get('default_group')
            try:
            	ret_msg = SLMS.register(inventory=inventory, default_group=default_group)
            except:
                from time import sleep
                sleep(3)
                ret_msg = SLMS.register(inventory=inventory, default_group=default_group)

            # SLMS.record_test_register(content)     # 用于通信调测
            code = ret_msg.get("code")
            message = ret_msg.get("message")
            reason = ret_msg.get("reason")

        if code == 0:
            self.user = user
            self.clients[user] = self
            if not user.startswith(("cmd", "illuminance")):
                SLMS.record_reconnect_hub(self.user)     # 如果一个集控重新连接上来，自动清除之前该集控脱网的告警

            if user.startswith('cmd'):
                # 管控与ns建立的连接
                log.msg("New client <%s> has registered!" % user.encode('utf-8'))
            elif user.startswith('illuminance'):
                # TODO illuminance情况下log输出什么?
                pass
            else:
                log.msg("New hub <%s> has registered!" % user.encode('utf-8'))
            log.msg("Online hubs now:", self.clients)

            send_content = json.dumps({
                "action": "register_server_ack",
                "type": "ack",
                "code": code,
                "message": u"向服务器注册成功",
                "reason": None
            })
            self.send_content(send_content, 101, [user])
            # 注册成功后立马采集默认分组
            send_content = json.dumps(
                {"body": "{\"action\": \"gather_group_config\", \"type\": \"cmd\"}",
                 "sender": "server"}
            )
            self.send_content(send_content, 102, [user])
        else:
            send_content = json.dumps({
                "action": "register_server_ack",
                "type": "ack",
                "code": code,
                "message": u"向服务器注册失败",
                "reason": reason
            })
            self.send_content(send_content, 101, [user])

    def handle_data(self, command_id, content):
        """
        根据command_id来分配函数
        """
        self.command_func_map[command_id](content)

    def handle_single_message(self, content):
        """
        单播
        """
        content = json.loads(content)
        sender = content.get("sender")
        receiver = content.get("receiver")
        body = content.get("body")
        action = json.loads(body).get('action')
        if action == 'report_status':
            # 记录上报的全量数据
            result = SLMS.record_all_status(json.loads(body))
            # SLMS.record_test_all_status(content)       # 用于通信测试
            if result.get('code') == 0:
                send_content = json.dumps({
                    "action": "report_status_ack",
                    "type": "ack",
                    "code": 0,
                    "message": u"上报数据成功",
                    "reason": None
                })
                self.send_content(send_content, 102, users=[sender], sender='server')
            else:
                send_content = json.dumps({
                    "action": "report_status_ack",
                    "type": "ack",
                    "code": 1,
                    "message": u"上报数据失败",
                    "reason": result.get('reason')
                })
                self.send_content(send_content, 102, users=[sender], sender='server')

        elif action == 'report_alarms':
            # 记录上报的故障告警
            result = SLMS.record_alarms(body=json.loads(body), hub_sn=sender)
            # SLMS.record_test_all_status(content)       # 用于通信测试
            if result.get('code') == 0:
                send_content = json.dumps({
                    "action": "report_emergency_ack",
                    "type": "ack",
                    "code": 0,
                    "message": u"成功，已记录告警",
                    "reason": None
                })
                self.send_content(send_content, 102, users=[sender], sender='server')
            else:
                send_content = json.dumps({
                    "action": "report_emergency_ack",
                    "type": "ack",
                    "code": 1,
                    "message": u"失败，请重新上报该告警",
                    "reason": result.get('reason')
                })
                self.send_content(send_content, 102, users=[sender], sender='server')

        elif action == 'gather_group_config_ack':
            # 集控方没有主动上报默认分组的接口，只能在注册后由服务端主动采集。该分支是为了采集默认分组的特殊存在。
            # 因为有可能是云端下发采集分组的指令，也有可能是注册后采集默认分组，所以还需要进行判断。
            if receiver.startswith('cmd'):
                send_content = json.dumps(dict(sender=sender, body=body))
                self.send_content(send_content, 102, [receiver], sender)
            else:
                default_group_config = json.loads(body).get('local_group_config')
                SLMS.record_default_groupconfig(default_group_config, hub_sn=sender)

        elif action == 'measure_illuminance':
            log.msg('record_illuminance')

        elif action == 'send_down_policyset':
            """下发策略集"""
            cmd_name = content.get("sender")
            hub_sn = content.get("receiver")
            send_content = json.dumps(dict(sender=sender, body=body))
            self.send_content(send_content, 102, [hub_sn], cmd_name)

        else:
            send_content = json.dumps(dict(sender=sender, body=body))
            self.send_content(send_content, 102, [receiver], sender)

    def handle_group_message(self, content):
        """
        组播
        """
        content = json.loads(content)
        sender = content.get("sender")
        receiver = content.get("receiver")
        message = content.get("message")
        send_content = json.dumps(dict(sender=sender, message=message))

        users = receiver
        self.send_content(send_content, 103, users, sender)

    def handle_broadcast_message(self, content):
        """
        广播
        """
        content = json.loads(content)
        sender = content.get("sender")
        message = content.get("message")
        send_content = json.dumps(dict(sender=sender, message=message))

        users = self.clients.keys()
        self.send_content(send_content, 104, users)

    def handle_heartbeat(self, content):
        """
        处理心跳包
        """
        # log.msg("收到", self.user, "的心跳")
        self.last_heartbeat_time = int(time.time())

    def send_content(self, send_content, command_id, users, sender="NS"):
        """
        发送函数
        """
        length = 12 + len(send_content)
        header = [length, __version__, command_id]
        header_pack = struct.pack("!3I", *header)
        for user in users:
            if user in self.clients.keys():
                log.msg("[%s] send_content to [%s]: %s" % (sender, user, send_content))
                self.clients[user].transport.write(header_pack + send_content.encode("utf-8"))
            else:
                log.msg("Hub <%s> is offline. Can not be communicated with it." % user.encode('utf-8'))
                if not self.user in self.clients.keys():
                    continue
                send_content = json.dumps({
                    "sender": "server",
                    "receiver": self.user,
                    "body": {
                        "action": "server_ack",
                        "code": 101,
                        "message": "集控 %s 脱网, 无法通信" % user.encode('utf-8')
                    }
                })
                length = 12 + len(send_content)
                header = [length, __version__, command_id]
                header_pack = struct.pack("!3I", *header)
                self.clients[self.user].transport.write(header_pack + send_content.encode('utf-8'))


class ServerFactory(Factory):

    def __init__(self):
        self.clients = {}

    def buildProtocol(self, addr):
        return Server(self.clients)

    def check_users_online(self):
        for hub, server in self.clients.items():
            # if server.last_heartbeat_time == 0:
            #     continue
            if int(time.time()) - server.last_heartbeat_time <= 300:
                continue
            log.msg("There is no heartbeat of <%s>. Break it." % hub.encode(
                'utf-8'))
            server.transport.abortConnection()  # 如果没有心跳，丢弃连接
            offline_hub = hub
            if not offline_hub.startswith(("cmd", "illuminance")):
                SLMS.record_offline_hub(offline_hub)

def start_reactor():
    sf = ServerFactory()

    task1 = task.LoopingCall(sf.check_users_online)     # 加入一个循环任务，循环检测心跳
    task1.start(61, now=False)                          # 每隔61秒检查一次心跳

    reactor.listenTCP(9999, sf)
    reactor.run()


# start_reactor()
