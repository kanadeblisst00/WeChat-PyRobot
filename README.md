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

![](http://cdn.ikanade.cn/room_qrcode_20240122.jpg)

如果二维码失效了，可以加我好友`kanadeblisst`，备注`进群`

## 使用教程

#### 当前支持功能

- 发送文本消息
- 发送图片消息
- hook微信日志输出
- hook接收消息
- 消息防撤回
- 下载聊天表情包

#### 准备环境

1. 安装支持的版本微信
2. 安装32位或64位Python(取决于你安装的微信是32位还是64位)，版本大于等于3.8
3. `pip install wechat_pyrobot==1.1.1`

如果国内源还没有同步最新版本，可以指定`-i https://pypi.org/simple/`选项使用pip官方库

#### 使用

首先创建一个目录，例如`robot_code`，再创建一个`main.py`(名称随意)写入以下代码:
```python
from py_process_hooker import inject_python_and_monitor_dir
from wechat_pyrobot import get_on_startup
from wechat_pyrobot.msg_plugins.print_msg import PrintMsg
from wechat_pyrobot.msg_plugins.download_emotion import DownLoadEmotion


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    on_startup = get_on_startup(msg_plugins=[PrintMsg, DownLoadEmotion])
    
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console, on_startup=on_startup)
```

启动并登录微信，执行这个`main.py`就会把Python注入到微信并且打开控制台

![](http://cdn.ikanade.cn/20231217113557.png)

现在默认是注入就监听消息和打开消息防撤回

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

例如 创建一个`sendmsg.py`，写入以下代码后保存：
```python
import time
from module import SendMsg


st = SendMsg()
st.send_text("filehelper", "测试消息!")
# 注意发送消息之间要间隔时间
time.sleep(1)
st.send_image("filehelper", r"D:\a.png")
```

第一个参数是wxid，获取方式后面再讲，或者下篇接收消息也能获取到好友的wxid，第二个参数是消息内容

发送消息时不要使用死循环，会阻塞Python进程，如果想定时发送消息，可以使用Python的定时器`threading.Timer`或者多线程`threading.Thread`

#### threading.Timer
```python
import time
from threading import Timer
from module import SendMsg


st = SendMsg()

def send_timer(n: int):
    global msg_timer
    t = time.strftime("%Y-%m-%d")
    msg_text = f"{t}: {n}"
    st.send_text("filehelper", msg_text)
    # 10秒后再执行一次
    msg_timer = Timer(10, send_timer, (n+1, ))
    msg_timer.start()
 

# 2秒后执行send_timer
msg_timer = Timer(2, send_timer, (1, ))
msg_timer.start()
# timer.cancel()#取消执行
```
取消定时器(解释见下面的骚操作)：
```python
import sys

sendmsg_timer = sys.modules["sendmsg_timer"]
msg_timer = sendmsg_timer.msg_timer
msg_timer.cancel()
```

#### hook日志

例如创建一个`hooklog.py`，写入一下代码后保存:
```python
from module import HookLog

hooker = HookLog()
hooker.hook() 
```

日志会被打印在控制台，如果想输出到文件，可以改下代码写入到文件

hook不会阻塞进程，因为回调函数是在微信内部被调用，所以不需要使用多线程

#### 骚操作

之前说了加载模块都会被保存在`sys.modules`这个字典里，而这个热加载就是以模块形式加载代码

所以你可以在新文件里引用之前文件的变量和方法，例如我新建一个`unhooklog.py`, 写入如下代码:
```python
import sys

# 获取robot.py模块
robot = sys.modules["robot"]
# 获取robot模块中的hooker变量
hooker = robot.hooker
# 取消hook
hooker.unhook()
```
不过，因为hook类已经被定义成了单例模式，所以即使你新建一个文件在实例化一个也是一样的效果
```python
from module import HookLog

hooker = HookLog()
hooker.unhook() 
```

#### 接收消息

创建一个`hookmsg.py`(名称随意，别数字开头就行)，写入以下代码后保存:
```python
from module import HookMsg

def msg_callback(json_msg_str:str):
    print(json_msg_str)

hooker = HookMsg(msg_callback)
hooker.hook() 
```

后续再优化使用方式，注入后会自动加载hook消息的脚本，并引入消息插件的模式。可以自己编写py插件脚本来处理消息

#### 撤回消息

创建一个`revoke.py`，写入以下代码后保存:
```python
from module import AntiRevoke

ar = AntiRevoke()
ar.hook()
```

界面上的消息不会被撤回，但也不会有撤回提示。控制台会打印谁谁谁撤回了一条消息，但是没有消息内容，只有消息的msgid。你可以先将消息保存下来，然后通过这个msgid来查询撤回的哪个消息

