#### 教程目录

1. [在windows11上编译python](https://mp.weixin.qq.com/s/nJq8XX203Wc_gwT5hSWYZA)
2. [将python注入到其他进程并运行](https://mp.weixin.qq.com/s/gvV9GRQZbvxHQSjfDieiqw)
3. [注入Python并使用ctypes主动调用进程内的函数和读取内存结构体](https://mp.weixin.qq.com/s/Dy8-nJPoXJp9_ZrrwOrC0w)
4. [调用汇编引擎实战发送文本和图片消息(支持32位和64位微信)](https://mp.weixin.qq.com/s/PJZDf5937SsncGU-RhZ3tA)
5. [允许Python加载运行py脚本且支持热加载](https://mp.weixin.qq.com/s/FWW1FecRo_yAhh9eLScAoA)
6. [利用汇编和反汇编引擎写一个x86任意地址hook，实战Hook微信日志](https://mp.weixin.qq.com/s/gAVt731tfOiS5o7U1b3haQ)
7. [封装Detours为dll，用于Python中x64函数 hook，实战Hook微信日志](https://mp.weixin.qq.com/s/wbsjxv7Zt67pMi5ZYD0cfQ)
8. [实战32位和64位接收消息和消息防撤回](https://mp.weixin.qq.com/s/UUO27gRLdIKzTlaSuwiV0w)
9. 实战读取内存链表结构体(好友列表)
10. 做一个僵尸粉检测工具
11. 根据bug反馈和建议进行细节上的优化
12. 其他功能看心情加

#### 当前支持版本

32位:
- `3.9.8.12`

64位:
- `3.9.8.15`

等这个系列教程结束再更新新版本，hook库和主动调用都已经说完了，也可以等群友提pr来更新。

#### 群二维码

![](http://cdn.ikanade.cn/Python_room_qrcode_20240407.jpg)

如果二维码失效了，可以加我好友`kanadeblisst`，备注`机器人群`

## 使用教程

#### 当前支持功能

- 发送文本消息
- 发送AT消息
- 发送图片消息
- hook微信日志输出
- hook接收消息
- 消息防撤回
- 下载聊天表情包
- 获取好友列表
- 获取群列表
- 获取公众号列表

#### 准备环境

1. 安装支持的版本(`3.9.8.15`)微信
2. 安装Python，版本大于等于3.8 (最好就用3.8)，测试3.10+容易出bug
3. `pip install wechat_pyrobot==1.3.0`

如果国内源还没有同步最新版本，可以指定`-i https://pypi.org/simple/` 选项使用pip官方库

#### 使用

首先创建一个目录，例如`robot_code`，再创建一个`main.py`(名称随意)写入以下代码:
```python
from py_process_hooker import inject_python_and_monitor_dir
from wechat_pyrobot import get_on_startup
from wechat_pyrobot.msg_plugins import PrintMsg, DownLoadEmotion
from wechat_pyrobot.other_plugins import HttpApi


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    on_startup = get_on_startup(msg_plugins=[PrintMsg, DownLoadEmotion], other_plugins=[HttpApi])
    
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console, on_startup=on_startup)
```

启动并登录微信，执行这个`main.py`就会把Python注入到微信并且打开控制台

![](http://cdn.ikanade.cn/20231217113557.png)

现在默认是注入就会加载插件并监听消息和打开消息防撤回，插件HttpApi会加载一个http服务来用于发送文字和图片消息

#### 待实现插件列表

- 监听群聊中的群二维码
- 监听并实时采集关注的公众号文章
- 自动下载并解密聊天中的图片
- chatgpt自动回复
- 群消息关键词提醒
- 消息保存到数据库，如sqlite、postgresql等
- 自动接收转账
- 监听收款信息对接发卡平台，目前可以用v免签+独角数卡

有兴趣的可以进群等待更新

#### 发送消息

```python
import requests

url = "http://127.0.0.1:26666/sendmsg"
params = {
    "touser": "filehelper",
    "msg": "测试消息"
}

requests.get(url, params=params)
```
AT消息
```python
import requests
import json
url = "http://127.0.0.1:26666/sendatmsg"
data = {
    "touser": "11111111111@chatroom",
    "msg": "@昵称 222222",
    "atwxid": "被@人的wxid"
}
headers = {
    "content-type": "application/json"
}
print(requests.get(url, params=data).json())
```

图片消息

```python
import requests

url = "http://127.0.0.1:26666/sendimage"
params = {
    "touser": "filehelper",
    "path": r"C:\Users\Administrator\Pictures\图片1.jpg"
}

requests.get(url, params=params)
```

还有一个post的版本，图片类似
```python
import requests

url = "http://127.0.0.1:26666/post_sendmsg"
data = {
    "touser": "filehelper",
    "msg": "测试消息2"
}

requests.post(url, json=data)
```
#### 联系人列表

目前没有区分公众号、群和好友，有需求的可以自己加判断区分

```python
import requests

url = "http://127.0.0.1:26666/contacts"
print(requests.get(url).json())
```

#### 接收消息

接收消息现在由插件控制，你可以编写自己的插件然后在`get_on_startup`的参数msg_plugins添加它。插件执行目前是同步单线程，如果需要多线程的话，可以自己根据需要修改get_on_startup里的msg_thread_func函数。

例如我想写一个将消息保存到文件的插件, `robot_code`下新建一个目录my_msg_plugin，下面新建一个文件`save_to_file.py`：

```python
import os
import json
from wechat_pyrobot.plugin_class import MsgPluginTemplate


class SaveToFile(MsgPluginTemplate):
    def __init__(self, **kwargs) -> None:
        self.name = os.path.basename(__file__)[:-3]
        super().__init__(**kwargs)
        # kwargs["pwd"]是main.py所在路径
        self.msg_save_path = os.path.join(kwargs["pwd"], "msg_save_path")
        os.makedirs(self.msg_save_path, exist_ok=True)
    
    def deal_msg(self, msg_dict):
        path = os.path.join(self.msg_save_path, f'{msg_dict["msgid"]}.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(msg_dict)) 
```

接着，你需要关闭微信。修改main.py代码，导入你自己的插件，然后注入Python到微信，代码如下:

```python
from py_process_hooker import inject_python_and_monitor_dir
from wechat_pyrobot import get_on_startup
from wechat_pyrobot.msg_plugins import PrintMsg, DownLoadEmotion
from wechat_pyrobot.other_plugins import HttpApi
from my_msg_plugin.save_to_file import SaveToFile


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    on_startup = get_on_startup(msg_plugins=[PrintMsg, DownLoadEmotion, SaveToFile], other_plugins=[HttpApi])
    
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console, on_startup=on_startup)
```


#### 防撤回消息

防撤回在注入时默认就会加载，无法再调用
