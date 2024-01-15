import os
from abc import ABC, abstractmethod


class PluginTemplate(ABC):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    @abstractmethod
    def run(self):
        pass

    def start(self):
        self.run()

    def join(self):
        '''关闭资源'''
    
    def _name(self, file):
        return os.path.basename(file)[:-3]


class MsgPluginTemplate(ABC):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
    
    @abstractmethod
    def deal_msg(self, msg_dict:dict):
        pass

    