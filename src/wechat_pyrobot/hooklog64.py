from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET



class HookLog:
    def __init__(self) -> None:
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        base_addr = GetModuleHandleW("WeChatWin.dll")
        self.log_addr = base_addr + call_offset_dict["LogEnterCallOffset"]
        self.c_log_addr = c_uint64(self.log_addr)
        self.lp_log_func = CFUNCTYPE(c_uint64, c_uint64, c_uint64, c_uint64,c_uint64,c_uint64,c_uint64,c_uint64,c_uint64,c_uint64,c_uint64,c_uint64,c_uint64)

    def hook_log_callback(self, *args, **kwargs):
        c_code_file = (c_char * MAX_PATH).from_address(args[1])
        code_file = c_code_file.value.decode()
        ret = self.lp_log_func(self.c_log_addr.value)(*args, **kwargs)
        c_log_info = (c_char * 1000).from_address(ret)
        log_info = c_log_info.value.decode()
        print(f"文件路径: {code_file}, 日志信息: {log_info}")
        return ret

    def hook(self, ):
        self._hook.unhook(self.log_addr)
        self._hook.hook(self.c_log_addr, self.lp_log_func, self.hook_log_callback)
    
    def unhook(self):
        self._hook.unhook(self.log_addr)

# h = HookLog()
# h.hook() 
