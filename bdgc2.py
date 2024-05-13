import asyncio
import re
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from Config import ACC_ROODIND, API_ID, API_HASH

Kang_from = 'https://t.me/BDGGAMEVIPOFFICIAL'
Kang_To = 'https://t.me/+6d-tcmIo1AZhMGNl'

new_url = 'https://bdggame.in/#/register?invitationCode=175185649029'

new_username = '@ThakurMukesh99'

emoji_replacements = {
    '💰': '✅',
    '💲': '✅',
    '🦋': '✅'
}

header_message = """━━━━━━━∙⋆⋅⋆∙━━━━━━━
  **💫💫🥰 BIG DADDY 🥰💫💫**

𝙁𝙤𝙡𝙡𝙤𝙬 𝙖𝙩 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙧𝙞𝙨𝙠⬅️
𝙈𝘼𝙄𝙉𝙏𝘼𝙄𝙉 𝙁𝙐𝙉𝘿 𝙇𝙀𝙑𝙀𝙇 **7-11**💰
━━━━━━━∙⋆⋅⋆∙━━━━━━━
"""

message_id_map = {}

def remove_header(text):
    if text.startswith(header_message):
        return text[len(header_message):]
    return text

async def run_bot():
    async with TelegramClient(StringSession(ACC_ROODIND), API_ID, API_HASH) as client:
        print("c2 bot started")
        @client.on(events.NewMessage(chats=Kang_from))
        async def new_message_handler(event):
            global message_id_map
            updated_text = re.sub(r'https?://\S+', new_url, event.message.text)
            updated_text = re.sub(r'@\w+', new_username, updated_text)
            for emoji, replacement in emoji_replacements.items():
                updated_text = updated_text.replace(emoji, replacement)
            updated_text = header_message + updated_text
            # Adjusted regex pattern to match the exact format of the text to be removed
            updated_text = re.sub(r'🦢🚻🔤🔣 🎦⚧🎦🎦⏹🦢\n1️⃣  🔠🔠🔠🔠🔠🔠    🔠🔠🔠 🔠 🔠\n  ➡️𝙁𝙤𝙡𝙡𝙤𝙬 𝙖𝙩 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙧𝙞𝙨𝙠⬅️\n✅𝙈𝘼𝙄𝙉𝙏𝘼𝙄𝙉 𝙁𝙐𝙉𝘿 𝙇𝙀𝙑𝙀𝙇 𝟔-𝟖✅', '', updated_text)
            sent_message = await client.send_message(Kang_To, updated_text, link_preview=False)
            message_id_map[event.message.id] = sent_message.id


        @client.on(events.MessageEdited(chats=Kang_from))
        async def edit_message_handler(event):
            global message_id_map
            updated_text = re.sub(r'https?://\S+', new_url, event.message.text)
            updated_text = re.sub(r'@\w+', new_username, updated_text)
            for emoji, replacement in emoji_replacements.items():
                updated_text = updated_text.replace(emoji, replacement)
            updated_text = remove_header(updated_text)
            updated_text = header_message + updated_text
            updated_text = re.sub(r'🦢🚻🔤🔣 🎦⚧🎦🎦⏹🦢\n1️⃣  🔠🔠🔠🔠🔠🔠    🔠🔠🔠 🔠 🔠\n  ➡️𝙁𝙤𝙡𝙡𝙤𝙬 𝙖𝙩 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙧𝙞𝙨𝙠⬅️\n💰𝙈𝘼𝙄𝙉𝙏𝘼𝙄𝙉 𝙁𝙐𝙉𝘿 𝙇𝙀𝙑𝙀𝙇 𝟔-𝟖💰', '', updated_text)
            if event.message.id in message_id_map:
                await client.edit_message(Kang_To, message_id_map[event.message.id], updated_text)

        @client.on(events.MessageDeleted(chats=Kang_from))
        async def delete_message_handler(event):
            global message_id_map
            for msg_id in event.deleted_ids:
                if msg_id in message_id_map:
                    await client.delete_messages(Kang_To, [message_id_map[msg_id]])
                    del message_id_map[msg_id]

        await client.start()
        await client.run_until_disconnected()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_bot())
