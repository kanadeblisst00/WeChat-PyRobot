import os
from ..plugin_class import MsgPluginTemplate


class PrintMsg(MsgPluginTemplate):
    def __init__(self, **kwargs) -> None:
        self.name = os.path.basename(__file__)[:-3]
        super().__init__(**kwargs)

    def deal_msg(self, msg_dict):
        print(f"插件[{self.name}]: {msg_dict}")
    
