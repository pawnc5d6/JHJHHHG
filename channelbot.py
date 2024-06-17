import requests
import time
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'ar-real-ip': '49.43.3.84',
    'authorization': '', 
    'cache-control': 'no-cache',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://bdggame.club',
    'pragma': 'no-cache',
    'referer': 'https://bdggame.club/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

login_data = {
    'username': '918827902554',
    'pwd': 'Indore123',
    'phonetype': -1,
    'logintype': 'mobile',
    'language': 0,
    'random': 'ca3fdc8125ac4a6991f90d2109224481',
    'signature': 'FFF82923695DF2087D5752C7A640732D',
    'timestamp': 1715316103,
}

post_data2 = {
    'pageSize': 10,
    'pageNo': 1,
    'typeId': 1,
    'language': 0,
    'random': 'ed88c80f22484aa28726a40ecdd2d16c',
    'signature': '4B64182D83BABE0A0A5A9F82E308EA08',
    'timestamp': 1715321661,
}

allowed_users = ['thakurmukesh99', 'itsmerood']

last_issue_number = None

api_id = "22157690" 
api_hash = "819a20b5347be3a190163fff29d59d81"  
string_session = "1BVtsOKcBu3eAzs33mTnTaQ01gqZYoU8wVHyBZSVF_Aa5iBq14yrE_5ssRZOqHODafKRE5OgRBxEeOZI1KQD0ZgC0GVwxROlO2lb4T0FAxUjahwAR0XUx03z_WBb4ftgaJ4YYfB5Mb74DyvAZjPC_XSddemUaHeWvieU0sKkegfvrhJ5UnqsSOPvbCT2pBuc8IzgG0NGwWeo73fHYkI0Q-WWLAE_yAN6XJ9JS2CILG9AU2j53JFAHn3MrDY_7zemxJXGp_Kf4xyn7s8VntgLeBqf5iJHKDdZx_9Bmlall2EEwpfvvPzOrCdxgbjA2-LZjV1kN2sxEa4DQWKWKtenqUerZeR3dYWk="
bot = TelegramClient(StringSession(string_session), api_id, api_hash)

with requests.Session() as s, bot:
    login_url = 'https://api.bigdaddygame.cc/api/webapi/Login'
    response = s.post(login_url, headers=headers, json=login_data)

    if response.json().get('code') == 0:
        print("Login successful.")
        for user in allowed_users:
            bot.send_message(user, "Welcome to the trade alert bot !")
        
        while True:
            add_post2_url = 'https://api.bigdaddygame.cc/api/webapi/GetNoaverageEmerdList'
            response2 = s.post(add_post2_url, headers=headers, json=post_data2)
            data2 = response2.json()

            if response2.status_code == 200 and data2['code'] == 0:
                current_issue_number = data2['data']['list'][0]['issueNumber']
                if last_issue_number is None or current_issue_number != last_issue_number:
                    last_issue_number = current_issue_number
                    latest_trades = data2['data']['list'][:2]
                    print("Latest trades updated:")
                    print(f"{'Issue Number':<20} {'Number':<10} {'Colour':<10} {'Premium':<10}")
                    for entry in latest_trades:
                        print(f"{entry['issueNumber']:<20} {entry['number']:<10} {entry['colour']:<10} {entry['premium']:<10}")
                    
                    numbers = [int(trade['number']) for trade in latest_trades]
                    if (numbers[0] == 0 and numbers[1] == 2) or (numbers[0] == 0 and numbers[1] == 4):
                        print("Take trade")
                        message = f"Trade Alert: {int(last_issue_number) + 1} "
                        for user in allowed_users:
                            bot.send_message(user, message)
            else:
                print("Failed to retrieve data or no new data.")

            time.sleep(0.1)
    else:
        print("Login failed. Error:", response.json().get('msg'))
        
