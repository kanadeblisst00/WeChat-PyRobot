import traceback
import json
from py_process_hooker.winapi import *
from .offset import CALL_OFFSET
from .hookmsg64 import GeneralStructW64, MyCDataJSONEncoder


class ContactInfoStruct64(Structure):
    _fields_ = [
        ('_unkown_value0', c_uint64 * 8),
        ('wxid', GeneralStructW64),
        ('wxh', GeneralStructW64),
        ('_v3', GeneralStructW64),
        ('_unkown_value2', c_uint32),
        ('type', c_uint32),
        ("verify_flag", c_uint32),
        ('_unkown_value3', c_uint32),
        ('_unkown_value1', c_uint64 * 4),
        ('nickname', GeneralStructW64)
    ]


class GetContacts:
    def __init__(self) -> None:
        pass

    @property
    def value(self):
        head = self.get_head_pointer()
        contacts = self.traverse_tree(head)
        return contacts

    def get_head_pointer(self):
        version = GetWeChatVersion()
        offsets_list = CALL_OFFSET[version]["GetContactListOffset"]
        base = GetModuleHandleW("WeChatWin.dll")
        for offsets in offsets_list:
            try:
                head_addr = c_uint64.from_address(base + offsets[0]).value
                for offset in offsets[1:]:
                    head_addr = c_uint64.from_address(head_addr + offset).value
            except:
                traceback.print_exc()
                continue
            else:
                if not head_addr or not c_uint64.from_address(head_addr).value:
                    continue
                return head_addr
            
    def traverse_tree(self, head):
        contacts = []
        next_left_node = c_uint64.from_address(head).value
        while next_left_node != head:
            c = ContactInfoStruct64.from_address(next_left_node)
            json_contact = json.dumps(c, cls=MyCDataJSONEncoder, ensure_ascii=False)
            contact = json.loads(json_contact)
            contacts.append(contact)
            next_left_node = c_uint64.from_address(next_left_node).value
        return contacts
