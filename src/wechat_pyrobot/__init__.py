import platform


if "64" in platform.architecture()[0]:
    from .sendmsg64 import SendMsg
    from .hooklog64 import HookLog
    from .anti_revoke64 import AntiRevoke
    from .hookmsg64 import HookMsg
else:
    from .sendmsg32 import SendMsg
    from .hooklog32 import HookLog
    from .anti_revoke32 import AntiRevoke
    from .hookmsg32 import HookMsg


__version__ = "0.1.1"

__all__ = [
    "SendMsg",
    "HookLog",
    "HookMsg",
    "AntiRevoke"
]









