import re
from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET


class AntiRevoke:
    def __init__(self) -> None:
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        base_addr = GetModuleHandleW("WeChatWin.dll")
        self.addr = base_addr + call_offset_dict["RevokeMsgCallOffset"]
        self.c_addr = c_uint64(self.addr)
        self.lp_func = CFUNCTYPE(c_uint64, c_uint64)

    def hook_callback(self, *args):
        xml = c_wchar_p.from_address(args[0]).value
        ret = self.lp_func(self.c_addr.value)(*args)
        if ret == 4:
            msgid = re.search(r'<newmsgid>(\d+)</newmsgid>', xml).group(1)
            replacemsg = re.search(r'<replacemsg><!\[CDATA\[(.*?)\]\]></replacemsg>', xml).group(1)
            print(f"{replacemsg}, msgid: {msgid}")
            return 0
        return ret

    def hook(self, ):
        self._hook.unhook(self.addr)
        self._hook.hook(self.c_addr, self.lp_func, self.hook_callback)
    
    def unhook(self):
        self._hook.unhook(self.addr)

# h = HookLog()
# h.hook() 
