import requests
import time
import json
import threading

# Ma'lumotlarni saqlash uchun baza fayli
db_file = 'baza.json'


# Funksiya ma'lumotlarni baza.json fayliga yozadi
def save_to_json(data):
    with open(db_file, 'w') as file:
        json.dump(data, file)


# Funksiya baza.json faylidagi ma'lumotlarni o'qiydi
def load_from_json():
    with open(db_file, 'r') as file:
        return json.load(file)


# POST so'rovi uchun URL manzili
login_url = 'https://my.ucell.uz/Account/Login'

# So'rovga yuboriladigan ma'lumotlar
login_data = {
    "phone_number": "998936438328",
    "password": "Shohbozbek240_2$3",
    "login_type": "3"
}


# Funksiya POST so'rovini yuboradi va session yaratadi
def login_and_get_cookie():
    with requests.Session() as session:
        login_response = session.post(login_url, json=login_data)

        # Javobdan Set-Cookie ni olish
        set_cookie = login_response.headers.get('Set-Cookie')

        # .UWCCFRONTNXAUTH qiymatini ajratib olish va vaqtinchalik saqlash
        uwccfrontnxauth = None
        if set_cookie:
            cookies = set_cookie.split(', ')
            for cookie in cookies:
                if '.UWCCFRONTNXAUTH' in cookie:
                    uwccfrontnxauth = cookie.split(';')[0]  # 'path=/' qismidan oldingi qismini ajratib olish
                    break
        else:
            print("Set-Cookie sarlavhasi topilmadi.")

        # GET so'rovi uchun URL manzili
        url = 'https://my.ucell.uz/'

        # So'rov uchun kerakli headerlar
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Cookie': f'lang=126a420370e1908ea6e01b2cb8869811716e1707%7Euz; _ga=GA1.2.2121528343.1716047651; _gid=GA1.2.1947017640.1716047651; _crp=s; _culture=uz; _gat=1; {uwccfrontnxauth}',
            'Host': 'my.ucell.uz',
            'Referer': 'https://my.ucell.uz/Account/Login',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

        response = session.get(url, headers=headers)
        set_cookie = response.headers.get('Set-Cookie')

        if set_cookie:
            cookies = set_cookie.split(';')
            for cookie in cookies:
                if 'path=/' in cookie or 'HttpOnly' in cookie or 'SameSite=Lax' in cookie:
                    continue

                # Ma'lumotlarni JSON formatiga o'tkazib, bazaga yozish
                data_to_save = {
                    'uwccfrontnxauth': uwccfrontnxauth,
                    'cookie': cookie.strip()
                }
                save_to_json(data_to_save)


# Funksiya baza.json faylidagi ma'lumotlarni olib API ga yuboradi
def send_data_to_api():
    while True:
        data = load_from_json()
        keys_url = 'http://127.0.0.1:8000/api/keys'
        response = requests.post(keys_url, json=data)
        # print(f"APIga yuborilgan javob: {response.status_code}, {response.text}")
        time.sleep(1500)  # Har 25 daqiqa


# Har 3 daqiqa (180 soniya)da funksiya chaqiriladi
def periodic_login_and_get_cookie():
    while True:
        login_and_get_cookie()
        time.sleep(1500)  # Har 25 daqiqa


# Yangi thread yaratish va funksiyalarni ishlatish
threading.Thread(target=periodic_login_and_get_cookie).start()
threading.Thread(target=send_data_to_api).start()
