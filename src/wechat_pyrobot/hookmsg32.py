import json
from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .ctypes_json import CDataJSONEncoder
from .offset import CALL_OFFSET



struct_size = 0x2E0

class GeneralStructW32(Structure):
    _fields_ = [
        ('value', c_wchar_p),
        ('len1', c_uint32),
        ('len2', c_uint32),
        ('_unkown_value0', c_uint32),
        ('_unkown_value1', c_uint32)
    ]

class WeChatMsgStruct32(Structure):
    _fields_ = [
        ('_unkown_value0', c_uint32 * 8),
        ('localid', c_uint32),
        ('_unkown_value2', c_uint32 * 3),
        ('msgid', c_ulonglong),
        ('msg_type', c_uint32),
        ('is_self_msg', c_uint32),
        ('_unkown_value3', c_uint32),
        ('timestamp', c_uint32),
        ('sender', GeneralStructW32),
        ('_unkown_value4', c_uint32 * 5),
        ('content', GeneralStructW32),
        ('_unkown_value5', c_uint32 * 66),
        ('room_sender', GeneralStructW32),
        ('sign', GeneralStructW32),
        ('thumb_path', GeneralStructW32),
        ('file_path', GeneralStructW32),
    ]

class MyCDataJSONEncoder(CDataJSONEncoder):
    def default(self, obj):
        if isinstance(obj, GeneralStructW32):
            return super().default(obj.value)
        return super().default(obj)


class HookMsg:
    def __init__(self, callback=None) -> None:
        self.callback = callback or self.default_callback
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        base = GetModuleHandleW("WeChatWin.dll")
        self.addr = base + call_offset_dict["HookMsgCallOffset"]

    def default_callback(self, json_msg:str):
        print("收到消息, 消息内容: ", json_msg)
    
    def hook_callback(self, pcontext):
        context = pcontext.contents
        eax = context.EAX
        start_addr = DWORD.from_address(eax + 0x10).value
        end_addr = DWORD.from_address(eax + 0x14).value
        for addr in range(start_addr, end_addr, struct_size):
            msg = WeChatMsgStruct32.from_address(addr)
            json_msg = json.dumps(msg, cls=MyCDataJSONEncoder, ensure_ascii=False)
            self.callback(json_msg)

    def hook(self):
        self._hook.unhook(self.addr)
        self._hook.hook(self.addr, self.hook_callback)
    
    def unhook(self):
        self._hook.unhook(self.addr)


