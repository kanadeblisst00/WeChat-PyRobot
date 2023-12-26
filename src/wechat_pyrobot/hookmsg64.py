import json
from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .ctypes_json import CDataJSONEncoder
from .offset import CALL_OFFSET


struct_size = 0x450

class GeneralStructW64(Structure):
    _fields_ = [
        ('value', c_wchar_p),
        ('len1', c_uint32),
        ('len2', c_uint32),
        ('_unkown_value0', c_uint64),
        ('_unkown_value1', c_uint64)
    ]

class WeChatMsgStruct64(Structure):
    _fields_ = [
        ('_unkown_value0', c_uint64 * 4),
        ('localid', c_uint64),
        ('_unkown_value2', c_uint64),
        ('msgid', c_uint64),
        ('msg_type', c_uint32),
        ('is_self_msg', c_uint32),
        ('_unkown_value3', c_uint32),
        ('timestamp', c_uint32),
        ('sender', GeneralStructW64),
        ('_unkown_value4', c_uint64 * 4),
        ('content', GeneralStructW64),
        ('_unkown_value5', c_uint64 * 51),
        ('room_sender', GeneralStructW64),
        ('sign', GeneralStructW64),
        ('thumb_path', GeneralStructW64),
        ('file_path', GeneralStructW64),
    ]

class MyCDataJSONEncoder(CDataJSONEncoder):
    def default(self, obj):
        if isinstance(obj, GeneralStructW64):
            return super().default(obj.value)
        return super().default(obj)

class HookMsg:
    def __init__(self, callback=None) -> None:
        self.callback = callback or self.default_callback
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        base_addr = GetModuleHandleW("WeChatWin.dll")
        self.addr = base_addr + call_offset_dict["HookMsgCallOffset"]
        self.c_addr = c_uint64(self.addr)
        self.lp_func = CFUNCTYPE(c_uint64, c_uint64, c_uint64)
    
    def default_callback(self, json_msg:str):
        print("收到消息, 消息内容: ", json_msg)

    def hook_callback(self, *args):
        arg1 = args[1]
        start_addr = c_uint64.from_address(arg1 + 0x8).value
        end_addr = c_uint64.from_address(arg1 + 0x10).value
        for addr in range(start_addr, end_addr, struct_size):
            msg = WeChatMsgStruct64.from_address(addr)
            json_msg = json.dumps(msg, cls=MyCDataJSONEncoder, ensure_ascii=False)
            self.callback(json_msg)
        ret = self.lp_func(self.c_addr.value)(*args)
        return ret

    def hook(self):
        self._hook.unhook(self.addr)
        self._hook.hook(self.c_addr, self.lp_func, self.hook_callback)
    
    def unhook(self):
        self._hook.unhook(self.addr)


