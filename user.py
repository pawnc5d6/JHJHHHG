###################################################
import os
import asyncio
from telethon.sync import TelegramClient, events, functions
from telethon.sessions import StringSession
from datetime import datetime
from Config import ACC_STRMAIN, API_ID, API_HASH
from telethon.tl.functions.messages import SendReactionRequest, SetTypingRequest
from telethon.tl.types import SendMessageGamePlayAction
from telethon.errors import ChatAdminRequiredError, PeerIdInvalidError, UserDeletedError
from telethon.tl.functions.account import UpdateStatusRequest
from telethon import types
from itertools import cycle
from gtts import gTTS
import psutil
import speedtest
import aiohttp
import logging
import json
import requests

##os.system('pip install asyncio')
##os.system('pip install telethon')
##os.system('pip install itertools')
###################################################
account_id = None
user_reactions = {}
auto_reaction_data = {}
typing_tasks = {}
client_global = None
is_bot_online = False
force_offline = False
muted_users = set()

###################################################
st = speedtest.Speedtest()
async def get_server_status():
    st.download()
    st.upload()
    download_speed = st.results.download / 1_000_000
    upload_speed = st.results.upload / 1_000_000
    ping_time = st.results.ping
    server_status = f"""Speed Test Result
•━••━••━••━••━•
ꑭ Ping : {ping_time} ms
ꑭ Download Speed : {download_speed:.2f} Mbps
ꑭ Upload Speed : {upload_speed:.2f} Mbps
•━••━••━••━••━•"""
    return server_status

async def clean_response(api_response):
    if not api_response or 'candidates' not in api_response:
        return "Error: Invalid response format."
    parts = api_response['candidates'][0]['content']['parts']
    response_text = parts[0]['text'] if parts else "No detailed response provided."
    filtered_text = response_text.replace("Phrase to remove", "").strip()
    return filtered_text

async def make_api_request(question):
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    params = {'key': 'AIzaSyDm06nSK4b6wgI48ClO5GtDZvuHUssqzV8'}
    data = {
        "contents": [{
            "parts": [{
                "text": question,
            }]
        }]
    }
    headers = {
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, params=params) as response:
            if response.status == 200:
                response_data = await response.json()
                cleaned_text = await clean_response(response_data)
                return cleaned_text
            else:
                return f"Failed to fetch response: {response.status}"


async def make_api_callimg(prompt):
    url = 'https://api.cloudflare.com/client/v4/accounts/4b07921748fd986e2000242245c50f21/ai/run/@cf/bytedance/stable-diffusion-xl-lightning'
    
    cloudflare_api_token = 'gBtCNoyGpbMKvUHKoZF_YIAGkQTUHsMJ3bxAk_LR'
    headers = {
        'Authorization': f'Bearer {cloudflare_api_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': prompt
    }
    response = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(url, headers=headers, json=data))
    if response.status_code == 200:
        with open('output.png', 'wb') as file:
            file.write(response.content)
        return
    else:
        error_message = f"Failed to generate image: {response.status_code} {response.text}"
        logging.error(error_message)
        return error_message



async def make_api_call(text_input):
    url = "https://api.cloudflare.com/client/v4/accounts/4b07921748fd986e2000242245c50f21/ai/run/@cf/mistral/mistral-7b-instruct-v0.1"
    headers = {
        "Authorization": "Bearer gBtCNoyGpbMKvUHKoZF_YIAGkQTUHsMJ3bxAk_LR",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "messages": [
            {"role": "system", "content": f'''Your name is UserBot Assistance, created by Vano Ganzzz and TeamRood. You are programmed to assist your owner with inquiries and deliver relevant information efficiently. In mathematical contexts, you automatically replace the "×" symbol with an asterisk (*) for accurate calculations. You aim to provide concise responses, ideally within 610 characters, but can extend this if necessary. Note: If asked about your identity, who are you then mention only "Hello! I am UserBot Assistance, created by Vano Ganzzz and TeamRood. My purpose is to assist you with inquiries and deliver relevant information efficiently." this given line nothing else '''},
            {"role": "user", "content": text_input}
        ]
    })
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('result', {}).get('response', 'No response field in result')
    else:
        logging.error(f"Failed to get response from API, status code: {response.status_code}")
        return f"Failed to get response from API, status code: {response.status_code}"

async def send_typing_message(client, peer):
    try:
        await client(SetTypingRequest(peer=peer, action=SendMessageGamePlayAction()))
    except ChatAdminRequiredError:
        print("Error: Admin privileges required - Skipping chat")
    except PeerIdInvalidError:
        print("Error: Invalid peer - Skipping chat")
    except UserDeletedError:
        print("Error: User deleted - Skipping chat")
    except Exception as e:
        print(f"Error sending typing message: {e}")

async def typing_task(client, chat_id):
    while True:
        try:
            await send_typing_message(client, chat_id)
        except (ChatAdminRequiredError, PeerIdInvalidError, UserDeletedError) as specific_error:
            print(f"Error: {specific_error} - Stopping typing in chat {chat_id}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

async def initialize_account_id(client):
    global account_id
    try:
        account_id = (await client.get_me()).id
    except Exception as e:
        print(f"Error getting account ID: {e}")
        return



###################################################

async def start_userbot():
    async with TelegramClient(StringSession(ACC_STRMAIN), API_ID, API_HASH) as client:
        print("Userbot has started.")
        await initialize_account_id(client)

###################################################
        @client.on(events.NewMessage(pattern=r"#alive"))
        async def alive_command(event):
            try:
                if event.sender_id == account_id:
                    start = datetime.now()
                    end = datetime.now()
                    ms = (end - start).microseconds / 1000
                    await event.edit(f"🤖 I Aᴍ Aʟɪᴠᴇ !!!!\nPɪɴɢ : `{ms}` 𝗺𝘀")
            except Exception as e:
                print(f"Error handling alive command: {e}")
###################################################
        @client.on(events.NewMessage(pattern=r"#gemini (.+)"))
        async def gemini_command(event):
            if event.sender_id == account_id:
                question = event.pattern_match.group(1)
                response_text = await make_api_request(question)
                await event.reply(response_text)
           
###################################################
        @client.on(events.NewMessage(pattern=r"#ai\s+(.+)"))
        async def ai_command(event):
            if event.sender_id == account_id:
                text_input = event.pattern_match.group(1)
                result = await make_api_call(text_input)
                await event.reply(result)
                
###################################################
        @client.on(events.NewMessage(pattern=r"#image\s+(.+)"))
        async def generate_image_command(event):
            if event.sender_id == account_id:
                prompt = event.pattern_match.group(1)
                result = await make_api_callimg(prompt)
                await event.reply(result, file='output.png')
                
###################################################
        @client.on(events.NewMessage())
        async def handle_new_message(event):
            global muted_users
            if event.sender_id in muted_users:
                try:
                    await event.delete()
                except Exception as e:
                    print(f"Error deleting message: {e}")

###################################################
        @client.on(events.NewMessage(pattern=r"#mute(?:\s+([@\w]+))?"))
        async def mute_command(event):
            global account_id, muted_users
            if event.sender_id != account_id:
                return
            user_to_mute = None
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                user_to_mute = reply_msg.sender_id
            else:
                cmd_args = event.pattern_match.group(1)
                if cmd_args:
                    if cmd_args.startswith("@"):
                        user_to_mute_entity = await client.get_input_entity(cmd_args)
                        user_to_mute = user_to_mute_entity.user_id
                    else:
                        user_to_mute = int(cmd_args)
            if user_to_mute:
                muted_users.add(user_to_mute)
                await event.reply(f"User {user_to_mute} has been muted.")
            else:
                await event.reply("The #mute command usage is incorrect.")

###################################################
        @client.on(events.NewMessage(pattern=r"#unmute\s+([@\w]+)"))
        async def unmute_command(event):
            global account_id, muted_users
            if event.sender_id != account_id:
                return
            cmd_args = event.pattern_match.group(1)
            user_to_unmute = None
            if cmd_args.startswith("@"):
                user_to_unmute_entity = await client.get_input_entity(cmd_args)
                user_to_unmute = user_to_unmute_entity.user_id
            else:
                user_to_unmute = int(cmd_args)

            if user_to_unmute in muted_users:
                muted_users.remove(user_to_unmute)
                await event.reply(f"User {user_to_unmute} has been unmuted.")
            else:
                await event.reply("This user was not muted or the #unmute command usage is incorrect.")
                            
###################################################                
        @client.on(events.NewMessage(pattern=r"#online"))
        async def online_command(event):
            global is_bot_online
            if event.sender_id == account_id:
                is_bot_online = True
                await event.edit("Online Status Pushed")
                async def set_online_status():
                    global is_bot_online
                    while is_bot_online:
                        try:
                            await client(UpdateStatusRequest(offline=False))
                            await asyncio.sleep(10)
                        except Exception as e:
                            print(f"Error updating online status: {e}")
                            break
                asyncio.create_task(set_online_status())
                
###################################################
        @client.on(events.NewMessage(pattern=r"#offline"))
        async def offline_command(event):
            global is_bot_online
            if event.sender_id == account_id:
                is_bot_online = False
                await event.edit("Offline Status Pushed")
                await client(UpdateStatusRequest(offline=True))
                
###################################################                
        @client.on(events.NewMessage())
        async def handle_new_message(event):
            chat_id = event.chat_id
            sender_id = event.sender_id
            if chat_id in muted_users and sender_id in muted_users[chat_id]:
                await event.delete()
                  
###################################################                
        @client.on(events.NewMessage(pattern=r'#ulist (@\w+)'))
        async def ulist_command(event):
            if event.sender_id == account_id:
                group_username = event.pattern_match.group(1)
                try:
                    group_entity = await client.get_entity(group_username)
                    participants = await client.get_participants(group_entity)
                    with open('userlist@TeamRood.txt', 'w') as file:
                        for user in participants:
                            if user.username:
                                file.write(f"@{user.username}\n")
                    await client.send_file(event.chat_id, 'userlist@TeamRood.txt', caption='dn')
                    os.remove('userlist@TeamRood.txt')
                    await event.delete()
                except Exception as e:
                    await event.reply(f"An error occurred: {str(e)}")
###################################################                
        @client.on(events.NewMessage(pattern=r'#chk (\d+)'))
        async def gen_command(event):
            if event.sender_id == account_id:
                number_input = event.pattern_match.group(1)
                chat = '@SDBB_Bot'
                processing_message = await event.edit("Processing your request...")
                try:
                    async with event.client.conversation(chat) as conv:
                        await conv.send_message(f'.chk {number_input}')
                        await asyncio.sleep(3)
                        response = await conv.get_response()
                        await processing_message.edit(f"{response.text}")
                except Exception as e:
                    await processing_message.edit(f"An error occurred: {str(e)}")
                    
###################################################                
        @client.on(events.NewMessage(pattern=r'#gen (\d+)'))
        async def gen_command(event):
            if event.sender_id == account_id:
                number_input = event.pattern_match.group(1)
                chat = '@SDBB_Bot'
                processing_message = await event.edit("Processing your request...")
                try:
                    async with event.client.conversation(chat) as conv:
                        await conv.send_message(f'.gen {number_input}')
                        await asyncio.sleep(3)
                        response = await conv.get_response()
                        await processing_message.edit(f"{response.text}")
                except Exception as e:
                    await processing_message.edit(f"An error occurred: {str(e)}")

################################################### 
        @client.on(events.NewMessage(pattern=r"#cp"))
        async def copy_message(event):
            try:
                if event.sender_id == account_id and event.is_reply:
                    original_message = await event.get_reply_message()
                    if original_message:
                        await event.edit(f"```{original_message.text}```")
            except Exception as e:
                print(f"Error handling #cp command: {e}")
                
###################################################
        @client.on(events.NewMessage(pattern=r"#voice"))
        async def voice_command_handler(event):
            try:
                if event.sender_id == account_id:
                    text = ""
                    if event.is_reply:
                        replied_message = await event.get_reply_message()
                        text = replied_message.text
                    if not text and len(event.text.split()) > 1:
                        text = event.text.split("#voice", 1)[1].strip()
                    if text:
                        chat_entity = await event.get_chat()
                        user_entity = await client.get_entity(chat_entity.id)
                        spachen = gTTS(text=text, lang="en", slow=False)
                        spachen.save('@TeamRood.mp3')
                        await event.reply(file='@TeamRood.mp3', parse_mode="html")
            except Exception as e:
                print(f"Error handling voice command: {e}")

###################################################                
        @client.on(events.NewMessage(pattern=r"#setpic"))
        async def set_profile_picture(event):
            if event.sender_id == account_id:
                try:
                    replied_message = await event.get_reply_message()
                    if replied_message and replied_message.media:
                        media = await replied_message.download_media(os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloads/"))
                        await client(UploadProfilePhotoRequest(
                            file=await client.upload_file(media)
                        ))
                        await event.reply("**Changed profile picture successfully!!**")
                        try:
                            os.remove(media)
                        except Exception as e:
                            print(str(e))
                    else:
                        await event.reply("Please reply to a media file (photo) to set it as the profile picture.")
                except Exception as e:
                    print(f"Error changing profile picture: {e}")
                
###################################################
        @client.on(events.NewMessage(pattern=r"#react (.+)"))
        async def react_message(event):
            try:
                if event.sender_id == account_id and event.is_reply:
                    original_message = await event.get_reply_message()
                    if original_message:
                        emoji = event.pattern_match.group(1)
                        await client(SendReactionRequest(
                            peer=await event.get_input_chat(),
                            msg_id=original_message.id,
                            reaction=[types.ReactionEmoji(emoticon=emoji)]
                        ))
                    else:
                        await event.reply("Rᴇᴘʟʏ Tᴏ Mᴇꜱꜱᴀɢᴇ")
            except Exception as exc:
                print(f"Error: {exc}")
                
###################################################
        @client.on(events.NewMessage(pattern=r"#areact (.+)"))
        async def enable_auto_reaction(event):
            global auto_reaction_data
            if event.sender_id == account_id and event.is_reply:
                replied_to_message = await event.get_reply_message()
                user_entity = await event.client.get_entity(replied_to_message.sender_id)
                user_name = f"{user_entity.first_name} {user_entity.last_name}" if user_entity.last_name else user_entity.first_name
                user_to_enable = replied_to_message.sender_id
                emoji = event.pattern_match.group(1)
                auto_reaction_data[user_to_enable] = emoji
                await event.edit(f"Aᴜᴛᴏ-Rᴇᴀᴄᴛɪᴏɴ Eɴᴀʙʟᴇᴅ Fᴏʀ {user_name}")

###################################################
        @client.on(events.NewMessage(pattern=r"#sreact"))
        async def disable_auto_reaction(event):
            global auto_reaction_data
            if event.sender_id == account_id and event.is_reply:
                replied_to_message = await event.get_reply_message()
                user_to_disable = replied_to_message.sender_id
                user_entity = await event.client.get_entity(replied_to_message.sender_id)
                user_name = f"{user_entity.first_name} {user_entity.last_name}" if user_entity.last_name else user_entity.first_name
                if user_to_disable in auto_reaction_data:
                    del auto_reaction_data[user_to_disable]
                    await event.edit(f"Aᴜᴛᴏ-Rᴇᴀᴄᴛɪᴏɴ Dɪꜱᴀʙʟᴇᴅ Fᴏʀ {user_name}")

        @client.on(events.NewMessage(incoming=True))
        async def auto_react_to_messages(event):
            global auto_reaction_data
            user_id = event.sender_id
            if user_id in auto_reaction_data:
                emoji = auto_reaction_data[user_id]
                try:
                    await client(SendReactionRequest(
                        peer=await event.get_input_chat(),
                        msg_id=event.id,
                        reaction=[types.ReactionEmoji(emoticon=emoji)]
                    ))
                except Exception as exc:
                    await event.reply(f"Error: {exc}")

###################################################
        @client.on(events.NewMessage(pattern=r"#creact"))
        async def continuous_reaction(event):
            try:
                if event.sender_id == account_id and event.is_reply:
                    original_message = await event.get_reply_message()
                    if original_message:
                        reactions = cycle(["👍", "🔥", "❤️️","🥰","💯"])
                        for reaction in reactions:
                            try:
                                await client(SendReactionRequest(
                                    peer=await event.get_input_chat(),
                                    msg_id=original_message.id,
                                    reaction=[types.ReactionEmoji(emoticon=reaction)]
                                ))
                            except Exception as e:
                                print(f"Error giving reaction {reaction}: {e}")
                                continue
                            await asyncio.sleep(8)
            except Exception as e:
                print(f"Error handling #creact command: {e}")

        @client.on(events.NewMessage(pattern=r"#stopcreact"))
        async def stop_continuous_reaction(event):
            if event.sender_id == account_id and event.is_reply:
                replied_to_message = await event.get_reply_message()
                if replied_to_message:
                    original_user_id = replied_to_message.from_id.user_id if replied_to_message.from_id else None
                    if original_user_id in auto_reaction_data:
                        del auto_reaction_data[original_user_id]
                        await event.edit(f"Cᴏɴᴛɪɴᴜᴏᴜꜱ Rᴇᴀᴄᴛɪᴏɴ Dɪꜱᴀʙʟᴇᴅ Fᴏʀ {original_user_id}")
                    else:
                        await event.edit("Cᴏɴᴛɪɴᴜᴏᴜꜱ Rᴇᴀᴄᴛɪᴏɴ ɴᴏᴛ ꜰᴏᴜɴᴅ")
                else:
                    await event.edit("Rᴇᴘʟʏ Tᴏ Mᴇꜱꜱᴀɢᴇ")

###################################################
        @client.on(events.NewMessage(pattern=r"#playing"))
        async def start_typing(event):
            bot_id = (await client.get_me()).id
            if event.sender_id == bot_id:
                chat_id = event.chat_id
                if chat_id not in typing_tasks:
                    typing_tasks[chat_id] = asyncio.ensure_future(typing_task(client, chat_id))
                    await event.edit("Pʟᴀʏɪɴɢ Sᴛᴀᴛᴜꜱ Aᴄᴛɪᴠᴀᴛᴇᴅ")
                    
###################################################
        @client.on(events.NewMessage(pattern=r"#splaying"))
        async def stop_typing(event):
            bot_id = (await client.get_me()).id
            if event.sender_id == bot_id:
                chat_id = event.chat_id
                if chat_id in typing_tasks:
                    typing_tasks[chat_id].cancel()
                    del typing_tasks[chat_id]
                    await event.edit("Pʟᴀʏɪɴɢ Sᴛᴀᴛᴜꜱ Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")

###################################################
        @client.on(events.NewMessage(pattern=r"#count"))
        async def count_command(event):
            try:
                if event.sender_id == account_id:
                    start = datetime.now()
                    u = 0  # number of users
                    g = 0  # number of basic groups
                    c = 0  # number of super groups
                    bc = 0  # number of channels
                    b = 0   # number of bots
                    await event.edit("Retrieving Telegram Count(s)")
                    async for d in client.iter_dialogs(limit=None):
                        if d.is_user:
                            if d.entity.bot:
                                b += 1
                            else:
                                u += 1
                        elif d.is_channel:
                            if d.entity.broadcast:
                                bc += 1
                            else:
                                c += 1
                        elif d.is_group:
                            g += 1
                        else:
                            print(d.stringify())
                    end = datetime.now()
                    ms = (end - start).seconds
                    await event.edit("""•━••━••━••━••━•
ꑭ **Tᴏᴏᴋ "{}"" Sᴇᴄᴏɴᴅs.**
ꑭ **Uꜱᴇʀꜱ** : \t{}
ꑭ **Gʀᴏᴜᴘꜱ** : \t{}
ꑭ **Sᴜᴘᴇʀ Gʀᴏᴜᴘꜱ** : \t{}
ꑭ **Cʜᴀɴɴᴇʟs** : \t{}
ꑭ **Bᴏᴛꜱ** : \t{}
•━••━••━••━•••━•""".format(ms, u, g, c, bc, b))
            except Exception as e:
                print(f"Error handling count command: {e}")

###################################################
        @client.on(events.NewMessage(pattern=r"#usernames", outgoing=True))
        async def list_usernames(event):
            try:
                if event.sender_id == account_id:
                    result = await client(functions.channels.GetAdminedPublicChannelsRequest())
                    output_str = ""
                    for channel_obj in result.chats:
                        output_str += f"- {channel_obj.title} @{channel_obj.username} \n"
                    await event.edit(output_str)
            except Exception as e:
                print(f"Error handling listmyusernames command: {e}")

###################################################
        @client.on(events.NewMessage(pattern=r"#tagall"))
        async def tag_all(event):
            if event.fwd_from:
                return
            mentions = "@tagall"
            chat = await event.get_input_chat()
            async for participant in client.iter_participants(chat, 1000):
                mentions += f"[\u2063](tg://user?id={participant.id})"
            await event.reply(mentions)
            await event.delete()

###################################################
        @client.on(events.NewMessage(pattern=r"#cmd"))
        async def execute_command(event):
            user_id = event.sender_id
            if user_id == (await client.get_me()).id:
                command = event.raw_text.split(" ", 1)[1].strip()
                try:
                    result = os.popen(command).read()
                    message = f"Command executed successfully:\n{result}"
                except Exception as e:
                    message = f"Error executing the command: {str(e)}"
                await event.reply(message)
                
###################################################
        @client.on(events.NewMessage(pattern=r"#bin"))
        async def bin_command(event):
            try:
                if event.sender_id == account_id:
                    with open('combos.txt', 'r') as file:
                        for line in file:
                            line = line.strip()
                            await client.send_message('@SDBB_Bot', f'/chk {line}')
                            await asyncio.sleep(50)
            except Exception as e:
                print(f"Error handling bin command: {e}")

###################################################
        @client.on(events.NewMessage(pattern=r"#speed"))
        async def server_status_command(event):
            if event.sender_id == account_id:
                status_message = await get_server_status()
                await event.edit(status_message)
                
###################################################
        await client.run_until_disconnected()
loop = asyncio.get_event_loop()
loop.run_until_complete(start_userbot())
###################################################