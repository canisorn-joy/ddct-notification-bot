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
    source_type = event.source.type
    
    # ถ้าข้อความถูกส่งมาจากกลุ่มหรือ OpenChat
    if source_type in ['group', 'room']:
        target_id = event.source.group_id if source_type == 'group' else event.source.room_id
        user_id = event.source.user_id
        
        try:
            # 1. ส่ง Group ID ไปบอกคุณทาง "แชทส่วนตัว" ทันที
            line_bot_api.push_message(
                user_id, 
                TextSendMessage(text=f"🎯 Group ID ของกลุ่มนี้คือ:\n{target_id}")
            )
            
            # 2. สั่งให้บอทออกจากกลุ่มทันทีแบบไร้ร่องรอย
            if source_type == 'group':
                line_bot_api.leave_group(target_id)
            else:
                line_bot_api.leave_room(target_id)
                
        except Exception as e:
            print(f"Error: {str(e)}")
