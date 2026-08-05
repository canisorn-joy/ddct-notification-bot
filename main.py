import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = "zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14bad5ee7aeaea580aa461a878fc364a"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Group ID ของกลุ่มสตาฟ
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
    
    # ถ้าพิมพ์มาทางแชทส่วนตัว (User) หาบอท
    if event.source.type == 'user':
        try:
            # ดึงวันที่ปัจจุบันในรูปแบบภาษาอังกฤษ (เช่น August 5, 2026)
            now = datetime.now()
            current_date_str = now.strftime("%B %d, %Y")
            
            # จัดรูปแบบข้อความประกาศ
            announcement_text = f"Announcement, {current_date_str}:\n\n{user_message}"
            
            # ส่งเข้ากลุ่มสตาฟ
            if STAFF_GROUP_ID:
                line_bot_api.push_message(STAFF_GROUP_ID, TextSendMessage(text=announcement_text))
            
            # ตอบกลับคนส่งในแชทส่วนตัว
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ ส่งประกาศเข้ากลุ่มสตาฟเรียบร้อยครับ!"))
            
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ เกิดข้อผิดพลาด: {str(e)}"))
