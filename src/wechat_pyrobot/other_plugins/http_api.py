'''
给发送消息提供http接口服务
'''
from threading import Thread
from .. import SendMsg
import uvicorn
from fastapi import FastAPI


app = FastAPI()

class HttpApi(Thread):
    def __init__(self) -> None:
        super().__init__()
        sg = SendMsg()

        @app.post("/post_sendmsg")
        def post_sendmsg(touser:str, msg:str):
            r = sg.send_text(touser, msg)
            return {"result": r}

        @app.post("/post_sendimage")
        def post_sendimage(touser: str, path: str):
            r = sg.send_image(touser, path)
            return {"result": r}
        
        @app.get("/sendmsg")
        def sendmsg(touser: str, msg: str):
            r = sg.send_text(touser, msg)
            return {"result": r}
        
        @app.get("/sendimage")
        def sendimage(touser: str, path: str):
            r = sg.send_image(touser, path)
            return {"result": r}
    
    def run(self):
        uvicorn.run(app="wechat_pyrobot.other_plugins.http_api:app", host="127.0.0.1", port=26666, reload=False)


if __name__ == "__main__":
    HttpApi().start()