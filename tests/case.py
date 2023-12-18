from py_process_hooker import inject_python_and_monitor_dir


if __name__ == "__main__":
    process_name = "WeChat.exe"
    open_console = True
    inject_python_and_monitor_dir(process_name, __file__, open_console=open_console)








