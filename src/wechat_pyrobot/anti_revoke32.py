import re
from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET


class GeneralStructW32(Structure):
    _fields_ = [
        ('value', c_wchar_p),
        ('len1', c_uint32),
        ('len2', c_uint32),
        ('_unkown_value0', c_uint32),
        ('_unkown_value1', c_uint32)
    ]


class AntiRevoke:
    def __init__(self) -> None:
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        base = GetModuleHandleW("WeChatWin.dll")
        self.addr = base + call_offset_dict["RevokeMsgCallOffset"]

    def hook_callback(self, pcontext):
        context = pcontext.contents
        
        if context.EAX == 4:
            # 防撤回就是这么简单, 核心就这一行代码
            context.EAX = 0
            # 打印撤回消息
            msg = GeneralStructW32.from_address(context.ESI + 0x70)
            xml = msg.value
            msgid = re.search(r'<newmsgid>(\d+)</newmsgid>', xml).group(1)
            replacemsg = re.search(r'<replacemsg><!\[CDATA\[(.*?)\]\]></replacemsg>', xml).group(1)
            print(f"{replacemsg}, msgid: {msgid}")


    def hook(self):
        self._hook.unhook(self.addr)
        self._hook.hook(self.addr, self.hook_callback)
    
    def unhook(self):
        self._hook.unhook(self.addr)


