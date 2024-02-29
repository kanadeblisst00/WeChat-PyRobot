import os
import time
import traceback
import xml.etree.ElementTree as ET 
from ..plugin_class import MsgPluginTemplate


class MonitorBiz(MsgPluginTemplate):
    def __init__(self, **kwargs) -> None:
        self.name = os.path.basename(__file__)[:-3]
        super().__init__(**kwargs)

    def deal_msg(self, msg_dict):
        if msg_dict["msg_type"] != 0x31:
            return
        xml = msg_dict["content"]
        try:
            items = self.parse_xml(xml)
        except:
            traceback.print_exc()
        else:
            if items:
                nickname = items[0]["nickname"]
                print(f"监听到公众号({nickname}){len(items)}条文章推送！")
                self.save_items(items)
    
    def save_items(self, items):
        for item in items:
            print(item["title"], item["url"])
    
    def find_ele(self, ele, tag):
        a = ele.find(tag)
        text = a.text if a is not None else ""
        return text

    def parse_sub_ele(self, ele):
        title = self.find_ele(ele, 'title')
        pub_time = self.find_ele(ele, 'pub_time')
        pub_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(pub_time)))
        url = self.find_ele(ele, "url")
        return {"title":title,"pub_time":pub_time,"url":url}

    def parse_xml(self, xml):
        root = ET.fromstring(xml) 
        category = root.find(".//category[@type]")
        if not category or not category.get('count', default=None):
            return []
        count = int(category.get('count'))
        nickname = root.find(".//publisher/nickname").text
        username = root.find(".//publisher/username").text
        items = []
        for item in root.iter('item'): 
            d = self.parse_sub_ele(item)
            if "mp.weixin.qq.com" not in d["url"]:
                continue
            d["nickname"] = nickname
            items.append(d)
        if len(items) != count:
            return []
        return items
    
