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
    
    # ถ้ามีใครก็ตามพิมพ์มาทางแชทส่วนตัว (User) หาบอท
    if event.source.type == 'user':
        try:
            # ดึงวันที่ปัจจุบัน (แปลง ค.ศ. เป็น พ.ศ. โดยบวก 543)
            now = datetime.now()
            thai_months = [
                "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", 
                "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", 
                "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            day = now.day
            month = thai_months[now.month]
            year = now.year + 543
            
            current_date_str = f"{day} {month} {year}"
            
            # จัดรูปแบบข้อความตามที่ต้องการ
            announcement_text = f"ประกาศ วันที่ {current_date_str}:\n\n{user_message}"
            
            # 1. ส่งข้อความเข้าไปโผล่ในกลุ่มสตาฟอัตโนมัติ
            line_bot_api.push_message(STAFF_GROUP_ID, TextSendMessage(text=announcement_text))
            
            # 2. ตอบกลับคนส่งในแชทส่วนตัวว่าส่งสำเร็จแล้ว
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ ส่งประกาศเข้ากลุ่มสตาฟเรียบร้อยครับ!"))
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ เกิดข้อผิดพลาด: {str(e)}"))
