from py_process_hooker import inject_python_and_monitor_dir
from wechat_pyrobot import get_on_startup
from wechat_pyrobot.msg_plugins.print_msg import PrintMsg
from wechat_pyrobot.msg_plugins.download_emotion import DownLoadEmotion


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    on_startup = get_on_startup(msg_plugins=[PrintMsg, DownLoadEmotion])
    
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console, on_startup=on_startup)








