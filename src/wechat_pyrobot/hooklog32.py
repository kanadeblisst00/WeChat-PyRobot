from py_process_hooker import Hook
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET


base = GetModuleHandleW("WeChatWin.dll")

def hook_log_callback_enter(pcontext):
    context = pcontext.contents
    esp = context.ESP
    # 计算调用日志函数的地址偏移
    esp_call_offset = c_ulong.from_address(esp).value - base
    #获取日志中的代码文件路径
    edx = context.EDX
    c_code_file = (c_char * MAX_PATH).from_address(edx)
    code_file = c_code_file.value.decode()
    print(f"调用地址: WeChatWin.dll+{hex(esp_call_offset)}， 代码路径: {code_file}, ", end=" ")

def hook_log_callback_leave(pcontext):
    context = pcontext.contents  
    eax = context.EAX
    c_log_info = (c_char * 1000).from_address(eax)
    log_info = c_log_info.value.decode()
    print("日志信息: ", log_info)
        

class HookLog:
    def __init__(self) -> None:
        self._hook = Hook()
        wx_version = GetWeChatVersion()
        call_offset_dict = CALL_OFFSET[wx_version]
        self.enter_addr = base + call_offset_dict["LogEnterCallOffset"]
        self.leave_addr = base + call_offset_dict["LogLeaveCallOffset"]

    def hook(self):
        self._hook.unhook(self.enter_addr)
        self._hook.hook(self.enter_addr, hook_log_callback_enter)
        self._hook.unhook(self.leave_addr)
        self._hook.hook(self.leave_addr, hook_log_callback_leave)
    
    def unhook(self):
        self._hook.unhook(self.enter_addr)
        self._hook.unhook(self.leave_addr)


# h = HookLog()
# h.run()