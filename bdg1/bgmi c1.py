import asyncio
import re
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from Config import ACC_STR_BDG1, API_ID, API_HASH

# Constants for source and target channels
source_channel = '@Bigdaddy_lottery_v_ip'  # Source channel username
target_channel = 'https://t.me/+I8Db0HLUxBtlM2E1'  # Target channel link

# URL to replace all found links with
new_url = 'https://bdggame.in/#/register?invitationCode=175185649029'

# Username to replace all found usernames with
new_username = '@ThakurMukesh99'

# Emoji replacements
emoji_replacements = {
    '💚': '✅',
    '🔥': '✅'
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
    async with TelegramClient(StringSession(ACC_STR01us), API_ID, API_HASH) as client:
        @client.on(events.NewMessage(chats=source_channel))
        async def new_message_handler(event):
            global message_id_map
            updated_text = re.sub(r'https?://\S+', new_url, event.message.text)
            updated_text = re.sub(r'@\w+', new_username, updated_text)
            for emoji, replacement in emoji_replacements.items():
                updated_text = updated_text.replace(emoji, replacement)
            updated_text = header_message + updated_text
            sent_message = await client.send_message(target_channel, updated_text, link_preview=False)
            message_id_map[event.message.id] = sent_message.id

        @client.on(events.MessageEdited(chats=source_channel))
        async def edit_message_handler(event):
            global message_id_map
            updated_text = re.sub(r'https?://\S+', new_url, event.message.text)
            updated_text = re.sub(r'@\w+', new_username, updated_text)
            for emoji, replacement in emoji_replacements.items():
                updated_text = updated_text.replace(emoji, replacement)
            updated_text = remove_header(updated_text)
            updated_text = header_message + updated_text
            if event.message.id in message_id_map:
                await client.edit_message(target_channel, message_id_map[event.message.id], updated_text)

        @client.on(events.MessageDeleted(chats=source_channel))
        async def delete_message_handler(event):
            global message_id_map
            for msg_id in event.deleted_ids:
                if msg_id in message_id_map:
                    await client.delete_messages(target_channel, [message_id_map[msg_id]])
                    del message_id_map[msg_id]

        await client.start()
        await client.run_until_disconnected()

# Running the bot
loop = asyncio.get_event_loop()
loop.run_until_complete(run_bot())
