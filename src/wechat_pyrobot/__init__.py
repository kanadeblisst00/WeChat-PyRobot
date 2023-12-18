import platform


if "64" in platform.architecture()[0]:
    from .sendmsg64 import SendMsg
    from .hooklog64 import HookLog
else:
    from .sendmsg32 import SendMsg
    from .hooklog32 import HookLog




__all__ = [
    "SendMsg",
    "HookLog",
    "add_runas"
]









