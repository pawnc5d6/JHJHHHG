import requests
import time
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

# --- Configuration ---
allowed_users = ['thakurmukesh99', 'itsmerood']

api_id = "22157690"
api_hash = "819a20b5347be3a190163fff29d59d81"
string_session = "1BVtsOKcBu3eAzs33mTnTaQ01gqZYoU8wVHyBZSVF_Aa5iBq14yrE_5ssRZOqHODafKRE5OgRBxEeOZI1KQD0ZgC0GVwxROlO2lb4T0FAxUjahwAR0XUx03z_WBb4ftgaJ4YYfB5Mb74DyvAZjPC_XSddemUaHeWvieU0sKkegfvrhJ5UnqsSOPvbCT2pBuc8IzgG0NGwWeo73fHYkI0Q-WWLAE_yAN6XJ9JS2CILG9AU2j53JFAHn3MrDY_7zemxJXGp_Kf4xyn7s8VntgLeBqf5iJHKDdZx_9Bmlall2EEwpfvvPzOrCdxgbjA2-LZjV1kN2sxEa4DQWKWKtenqUerZeR3dYWk="
username = '916260844761'
password = 'Indore123'
check_interval = 0.1

# --- Telegram Bot Initialization ---
bot = TelegramClient(StringSession(string_session), api_id, api_hash)


headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'ar-real-ip': '49.43.3.93',
    'authorization': '',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://9987up.club',
    'priority': 'u=1, i',
    'referer': 'https://9987up.club/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

json_data1 = {
    'username': username,
    'pwd': password,
    'phonetype': -1,
    'logintype': 'mobile',
    'language': 0,
    'random': '99925604285642f1a86e0f0c5a82c262',
    'signature': '59F151D9F36658E2111B42494D7B59FF',
    'timestamp': 1717496899,
}



async def main():
    try:
        await bot.connect()
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")
        return

    try:
        # --- Login Request (only done once) ---
        login_response = requests.post('https://api.v8gamerecord.com/api/webapi/Login', headers=headers, json=json_data1)
        login_data = login_response.json()

        if login_data['code'] != 0:
            print(f"Login failed. Error: {login_data.get('message', 'Unknown')}")
            return

        access_token = login_data['data']['token']
        headers['authorization'] = f'Bearer {access_token}'
        print("Login successful.")
        for user in allowed_users:
            await bot.send_message(user, "Welcome to the trade alert bot!")
        
        # --- Trade Data Request (repeated in a loop) ---
        last_issue_number = None 
        while True:
            json_data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 13,
            'language': 0,
            'random': '784fff42f78a4be8b9dc14aca7c21635',
            'signature': 'C088EA2ED006D3DCE90C805DB748F0D6',
            'timestamp': 1717498501,
            }
            api_response = requests.post(
                'https://api.v8gamerecord.com/api/webapi/GetTRXNoaverageEmerdList',
                headers=headers,
                json=json_data,
            )
            api_data = api_response.json()

            # --- Trade Analysis ---
            if api_data.get('data', {}).get('data', {}).get('gameslist'):
                trades = api_data['data']['data']['gameslist'][:2]
                current_issue_number = trades[0]['issueNumber']

                if current_issue_number != last_issue_number:
                    last_issue_number = current_issue_number

                    print("\nLatest trades updated:")
                    print("Issue Number         Number     Colour     Premium")
                    for trade in trades:
                        print(f"{trade['issueNumber']}       {trade['number']}          {trade['colour']}      {trade['premium']}")
                    numbers = [int(trade['number']) for trade in trades]
                    if (numbers[0] == 0 and numbers[1] == 2) or (numbers[0] == 0 and numbers[1] == 4):
                        message = "Trx Wingo 1min alert"
                        print("Take trade ---> Trx Wingo 1min")
                        for user in allowed_users:
                            await bot.send_message(user, message)

            await asyncio.sleep(check_interval)
    finally:
        await bot.disconnect()

# --- Run the Main Function ---
if __name__ == "__main__":
    bot.loop.run_until_complete(main()) 
