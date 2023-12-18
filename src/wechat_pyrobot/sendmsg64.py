# -*- coding: utf-8 -*-
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET


class GeneralStructW(Structure):
    _fields_ = [
        ('content', c_wchar_p),
        ('content_len1', c_uint64),
        ('content_len2', c_uint64),
        ('null_word1', c_int64),
        ('null_word2', c_int64)
    ]

class SendMsg:
    buffer_len = 0x500
    
    def __init__(self) -> None:
        wx_version = GetWeChatVersion()
        self.call_offset_dict = CALL_OFFSET[wx_version]
        self.wxwin_base = GetModuleHandleW("WeChatWin.dll")
        self.buffer_struct = c_int64 * self.buffer_len
        self.text_calls = self.build_text_call()
        self.image_calls = self.build_image_call()
    
    def build_text_call(self):
        args_type = (
            self.buffer_struct,
            POINTER(GeneralStructW),
            POINTER(GeneralStructW),
            self.buffer_struct,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
        )
        sendmsg_call_addr = self.wxwin_base + self.call_offset_dict["SendTextCallOffset"]
        sendmsg_call = CFUNCTYPE(void, *args_type)(sendmsg_call_addr)
        free_call_addr = self.wxwin_base + self.call_offset_dict["SendMsgFreeCallOffset"]
        free_call = CFUNCTYPE(void, self.buffer_struct)(free_call_addr)
        return sendmsg_call, free_call
    
    def send_text(self, wxid:str, text:str):
        wxid_struct = GeneralStructW()
        c_wxid = c_wchar_p(wxid)
        wxid_struct.content = c_wxid
        wxid_struct.content_len1 = len(wxid)
        wxid_struct.content_len2 = len(wxid)

        text_struct = GeneralStructW()
        c_text = c_wchar_p(text)
        text_struct.content = c_text
        text_struct.content_len1 = len(text)
        text_struct.content_len2 = len(text)

        buffer1 = self.buffer_struct(*[0]*self.buffer_len)
        buffer2 = self.buffer_struct(*[0]*self.buffer_len)
        self.text_calls[0](buffer1, byref(wxid_struct), byref(text_struct), buffer2, 1, 1, 0, 0)
        self.text_calls[1](buffer1)
    
    def build_image_call(self):
        call0_addr = self.wxwin_base + self.call_offset_dict["SendImageCall0Offset"]
        call0 = CFUNCTYPE(c_int64)(call0_addr)
        args_type = (
            c_int64,
            self.buffer_struct,
            POINTER(GeneralStructW),
            POINTER(GeneralStructW),
            self.buffer_struct
        )
        call1_addr = self.wxwin_base + self.call_offset_dict["SendImageCall1Offset"]
        call1 = CFUNCTYPE(void, *args_type)(call1_addr)
        free_call_addr = self.wxwin_base + self.call_offset_dict["SendMsgFreeCallOffset"]
        free_call = CFUNCTYPE(void, self.buffer_struct)(free_call_addr)
        return call0, call1, free_call

    def send_image(self, wxid:str, img_path:str):
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
        buffer2_0x40 = c_int(0)
        buffer2[8] = addressof(buffer2_0x40)
        buffer2_0x48 = c_int(0)
        buffer2[9] = addressof(buffer2_0x48)
        chat_mgr = self.image_calls[0]()
        self.image_calls[1](chat_mgr, buffer1, byref(wxid_struct), byref(img_path_struct), buffer2)
        self.image_calls[2](buffer1)


if __name__ == "__main__":
    st = SendMsg()
    st.send_text("filehelper", "测试消息!")
    st.send_image("filehelper", r"C:\Users\Administrator\Pictures\1111.jpg")