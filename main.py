import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = "zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14bad5ee7aeaea580aa461a878fc364a"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ปริ้นท์ข้อมูลทุกอย่างลงไปในหน้า Logs ของ Render เพื่อให้คุณเห็นรหัสลับ
    print("========== ตรวจพบข้อความ ==========")
    print(f"Source Type: {event.source.type}")
    if hasattr(event.source, 'group_id'):
        print(f"🎯 Group ID ของห้องนี้คือ: {event.source.group_id}")
    if hasattr(event.source, 'room_id'):
        print(f"🎯 Room ID ของห้องนี้คือ: {event.source.room_id}")
    print("==================================")
