'''
给发送消息提供http接口服务
'''
from threading import Thread
from .. import SendMsg


class HttpApi(Thread):
    def __init__(self) -> None:
        super().__init__()
    
    def run(self):
        pass
