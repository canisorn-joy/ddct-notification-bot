import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

# Token และ Secret ของคุณ
LINE_CHANNEL_ACCESS_TOKEN = "zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14bad5ee7aeaea580aa461a878fc364a"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ➡️ Group ID ของกลุ่มสตาฟที่คุณระบุ
STAFF_GROUP_ID = "Cd77115351ec001e12873a5df8fc30ed6"

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
    user_message = event.message.text
    
    # เงื่อนไข: ถ้าข้อความถูกส่งมาจากกลุ่มสตาฟที่กำหนด
    if event.source.type == 'group' and event.source.group_id == STAFF_GROUP_ID:
        if user_message.startswith("Cancel") or user_message.startswith("Announcement"):
            try:
                # ส่งข้อความตามที่คุณพิมพ์มาเป๊ะๆ ออกไปในกลุ่ม
                line_bot_api.push_message(STAFF_GROUP_ID, TextSendMessage(text=user_message))
            except Exception as e:
                print(f"Error: {str(e)}")
