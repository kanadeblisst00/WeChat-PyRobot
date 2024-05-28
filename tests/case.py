from py_process_hooker import inject_python_and_monitor_dir
from wechat_pyrobot import get_on_startup
from wechat_pyrobot.msg_plugins import PrintMsg, DownLoadEmotion
from wechat_pyrobot.other_plugins import HttpApi


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    on_startup = get_on_startup(msg_plugins=[PrintMsg, DownLoadEmotion], other_plugins=[HttpApi])
    
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console, on_startup=on_startup)