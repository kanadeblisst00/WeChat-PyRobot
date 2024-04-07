'''
给发送消息提供http接口服务
'''
from threading import Thread
from .. import SendMsg, GetContacts
from typing import List
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MsgItem(BaseModel):
    touser: str
    msg: str 

class ImageItem(BaseModel):
    touser: str
    path: str  

class AtMsgItem(BaseModel):
    touser: str
    msg: str 
    atwxid: List[str]

class HttpApi(Thread):
    def __init__(self) -> None:
        super().__init__()
        sg = SendMsg()
        
        @app.post("/post_sendmsg")
        def post_sendmsg(item:MsgItem):
            touser = item.touser
            msg = item.msg
            r = sg.send_text(touser, msg)
            return {"result": r}

        @app.post("/post_sendimage")
        def post_sendimage(item:ImageItem):
            touser = item.touser
            path = item.path
            r = sg.send_image(touser, path)
            return {"result": r}
        
        @app.post("/post_sendatmsg")
        def post_sendatmsg(item:AtMsgItem):
            touser = item.touser
            msg = item.msg
            atwxid = item.atwxid
            if isinstance(atwxid, str):
                atwxid = [atwxid]
            r = sg.send_at_text(touser, msg, atwxid)
            return {"result": r}
        
        @app.get("/sendmsg")
        def sendmsg(touser: str, msg: str):
            r = sg.send_text(touser, msg)
            return {"result": r}
        
        @app.get("/sendatmsg")
        def sendatmsg(touser: str, msg: str, atwxid:str):
            r = sg.send_at_text(touser, msg, [atwxid])
            return {"result": r}
        
        @app.get("/sendimage")
        def sendimage(touser: str, path: str):
            r = sg.send_image(touser, path)
            return {"result": r}
        
        @app.get("/contacts")
        def getcontacts():
            return GetContacts().value
    
    def run(self):
        uvicorn.run(app="wechat_pyrobot.other_plugins.http_api:app", host="127.0.0.1", port=26666, reload=False)


if __name__ == "__main__":
    HttpApi().start()