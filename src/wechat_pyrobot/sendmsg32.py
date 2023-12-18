# -*- coding: utf-8 -*-
import keystone
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET


def asm32_to_code(asm_code):
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    bytes_code, _ = ks.asm(asm_code, as_bytes=True)
    return bytes_code

class GeneralStructW(Structure):
    _fields_ = [
        ('content', c_wchar_p),
        ('content_len1', c_uint32),
        ('content_len2', c_uint32),
        ('null_word1', c_uint32),
        ('null_word2', c_uint32)
    ]


class SendMsg:
    buffer_len = 0x500

    def __init__(self) -> None:
        wx_version = GetWeChatVersion()
        self.call_offset_dict = CALL_OFFSET[wx_version]
        self.wxwin_base = GetModuleHandleW("WeChatWin.dll")
        self.buffer_struct = c_uint32 * self.buffer_len
        # 这个内存函数只要我不主动释放它，它就一直能被调用，所以将它设置成self的属性
        self.text_call, self.text_buf = self.build_text_call()
        self.image_call, self.image_buf = self.build_image_call()

    def __del__(self):
        VirtualFree(self.text_buf, 0, MEM_RELEASE)
        VirtualFree(self.image_buf, 0, MEM_RELEASE)

    def build_text_call(self):
        '''构建发送文本消息函数'''
        # 这个需要设置成self的属性，防止被回收
        self.text_call1 = c_int(self.wxwin_base + self.call_offset_dict["SendTextCallOffset"])
        self.text_call2 = c_int(self.wxwin_base + self.call_offset_dict["SendMsgFreeCallOffset"])
        # 取内存地址
        call1_addr = addressof(self.text_call1)
        call2_addr = addressof(self.text_call2)
        # 开始写汇编
        asm_code = f'''
        push ebp;
        mov ebp, esp;
        push 0x0;
        push 0x0;
        push 0x1;
        push 0x1;
        mov eax, dword ptr [ebp+0x8]; // ebp+0x8是第一个参数
        push eax;
        mov eax, dword ptr [ebp+0xC]; // 第二个参数
        push eax;
        mov edx, dword ptr [ebp+0x10]; // 第三个参数
        mov ecx, dword ptr [ebp+0x14]; // 第四个参数
        call dword ptr ds:[{call1_addr:#02x}];
        add esp, 0x18;
        mov ecx, dword ptr [ebp+0x14];
        call dword ptr ds:[{call2_addr:#02x}];
        pop ebp;
        ret;
        '''
        # 汇编转机器码
        shellcode = asm32_to_code(asm_code.encode())
        # 分配一个可读可写可执行的内存区域
        mem_buf = VirtualAlloc(0, 4096, MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        # 将机器码写到内存地址里
        memmove(mem_buf, shellcode, len(shellcode))
        args_type = (
            self.buffer_struct,
            POINTER(GeneralStructW),
            POINTER(GeneralStructW),
            self.buffer_struct
        )
        mem_call = CFUNCTYPE(void, *args_type)(mem_buf)
        return mem_call, mem_buf

    def send_text(self, wxid:str, text:str):
        '''发送文本消息'''
        # 构建微信id结构体
        wxid_struct = GeneralStructW()
        c_wxid = c_wchar_p(wxid)
        wxid_struct.content = c_wxid
        wxid_struct.content_len1 = len(wxid)
        wxid_struct.content_len2 = len(wxid)
        # 构建文本结构体
        text_struct = GeneralStructW()
        c_text = c_wchar_p(text)
        text_struct.content = c_text
        text_struct.content_len1 = len(text)
        text_struct.content_len2 = len(text)
        # 创建DWROD数组，并赋值为0。相对于c语言中的 c_uint32 buffer1[buffer_len] = {0};
        buffer1 = self.buffer_struct(*[0]*self.buffer_len)
        buffer2 = self.buffer_struct(*[0]*self.buffer_len)
        # 发送文本消息
        self.text_call(buffer1, byref(text_struct), 
                                byref(wxid_struct), buffer2)
    
    def build_image_call(self):
        '''构建发送图片的函数'''
        self.image_call1 = c_int(self.wxwin_base + self.call_offset_dict["SendImageCall0Offset"])
        self.image_call2 = c_int(self.wxwin_base + self.call_offset_dict["SendImageCall1Offset"])
        self.image_call3 = c_int(self.wxwin_base + self.call_offset_dict["SendImageCall2Offset"])
        self.image_call4 = c_int(self.wxwin_base + self.call_offset_dict["SendMsgFreeCallOffset"])
        call1_addr = addressof(self.image_call1)
        call2_addr = addressof(self.image_call2)
        call3_addr = addressof(self.image_call3)
        call4_addr = addressof(self.image_call4)
        asm_code = f'''
        push ebp;
        mov ebp, esp;
        call dword ptr ds:[{call1_addr:#02x}];
        mov ecx, eax;
        mov edx, dword ptr [ebp+0x8]; // buffer1
        push edx;
        mov eax, dword ptr [ebp+0xC]; // img_path
        push eax;
        mov eax, dword ptr [ebp+0x10]; // wxid
        push eax;
        mov eax, dword ptr [ebp+0x14]; // buffer2
        push eax;
        call dword ptr ds:[{call2_addr:#02x}];
        mov ecx, dword ptr [ebp+0x14];
        call dword ptr ds:[{call3_addr:#02x}];
        mov ecx, dword ptr [ebp+0x14];
        call dword ptr ds:[{call4_addr:#02x}];
        pop ebp;
        ret;
        '''
        shellcode = asm32_to_code(asm_code.encode())
        mem_buf = VirtualAlloc(0, 4096, MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        # 将机器码写到内存地址里
        memmove(mem_buf, shellcode, len(shellcode))
        args_type = (
            self.buffer_struct,
            POINTER(GeneralStructW),
            POINTER(GeneralStructW),
            self.buffer_struct
        )
        mem_call = CFUNCTYPE(void, *args_type)(mem_buf)
        return mem_call, mem_buf

    def send_image(self, wxid:str, img_path:str):
        '''发送图片消息'''
        wxid_struct = GeneralStructW()
        c_wxid = c_wchar_p(wxid)
        wxid_struct.content = c_wxid
        wxid_struct.content_len1 = len(wxid)
        wxid_struct.content_len2 = len(wxid)

        img_path_struct = GeneralStructW()
        c_img_path = c_wchar_p(img_path)
        img_path_struct.content = c_img_path
        img_path_struct.content_len1 = len(img_path)
        img_path_struct.content_len2 = len(img_path)
        
        buffer1 = self.buffer_struct(*[0]*self.buffer_len)
        buffer2 = self.buffer_struct(*[0]*self.buffer_len)
        # 这个值不知道是做什么用的，不设置就会崩溃
        buffer1_0x2C = c_int(0)
        buffer1[0xB] = addressof(buffer1_0x2C)

        self.image_call(buffer1, byref(img_path_struct), 
                                byref(wxid_struct), buffer2)

if __name__ == "__main__":
    st = SendMsg()
    st.send_text("filehelper", "测试消息!")
    st.send_image("filehelper", r"C:\Users\Administrator\Pictures\1111.jpg")