#### 教程目录

1. [在windows11上编译python](https://mp.weixin.qq.com/s/nJq8XX203Wc_gwT5hSWYZA)
2. [将python注入到其他进程并运行](https://mp.weixin.qq.com/s/gvV9GRQZbvxHQSjfDieiqw)
3. [注入Python并使用ctypes主动调用进程内的函数和读取内存结构体](https://mp.weixin.qq.com/s/Dy8-nJPoXJp9_ZrrwOrC0w)
4. [调用汇编引擎实战发送文本和图片消息(支持32位和64位微信)](https://mp.weixin.qq.com/s/PJZDf5937SsncGU-RhZ3tA)
5. [允许Python加载运行py脚本且支持热加载](https://mp.weixin.qq.com/s/FWW1FecRo_yAhh9eLScAoA)
6. 利用汇编和反汇编引擎写一个x86任意地址hook，实战Hook微信日志
7. 封装Detour为dll，用于Python中x64函数 hook，实战Hook微信日志
8. 实战32位和64位接收消息和消息防撤回
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

![](http://cdn.ikanade.cn/%E7%BE%A4.jpg)

如果二维码失效了，可以加我好友`kanadeblisst`，备注`进群`，或者加完好友发送`进群`

## 使用教程

#### 当前支持功能

- 发送文本消息
- 发送图片消息
- hook微信日志输出
- hook接收消息(下篇更新)
- 防撤回(下篇更新)

#### 准备环境

1. 安装支持的版本微信
2. 安装32位或64位Python(取决于你安装的微信是32位还是64位)，版本大于等于3.7
3. `pip install --upgrade wechat_pyrobot`

后续如果更新功能都需要执行一遍`pip install --upgrade wechat_pyrobot`

#### 使用

首先创建一个目录，例如`robot_code`，再创建一个`main.py`(名称随意)写入一下代码:
```python
from py_process_hooker import inject_python_and_monitor_dir


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console)
```

启动并登录微信，执行这个`main.py`就会把Python注入到微信并且打开控制台

![](http://cdn.ikanade.cn/%E7%BE%A4%E5%B0%8F%E5%9B%BE.jpg)

接着你在当前目录创建的任何代码保存后，都会被自动加载到微信并执行(注意创建的带代码文件名不能以数字开头)

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

待更新

#### 撤回消息

待更新


