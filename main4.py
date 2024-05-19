import requests
import time
import json

# Ma'lumotlarni saqlash uchun baza fayli
db_file = 'baza.json'

# Funksiya ma'lumotlarni baza.json fayliga yozadi
def save_to_json(data):
    with open(db_file, 'w') as file:
        json.dump(data, file)

# POST so'rovi uchun URL manzili
login_url = 'https://my.ucell.uz/Account/Login'

# So'rovga yuboriladigan ma'lumotlar
login_data = {
    "phone_number": "998936438328",
    "password": "Shohbozbek240_2$3",
    "login_type": "3"
}

# So'rovni yuborish va session yaratish
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
                print(uwccfrontnxauth)  # ; qo'shib chiqarish
                break
    else:
        print("Set-Cookie sarlavhasi topilmadi.")

    # 3 sekund vaqt o'tkazish
    time.sleep(3)

    # GET so'rovi uchun URL manzili
    url = 'https://my.ucell.uz/'

    # So'rov uchun kerakli headerlar
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Cookie': f'lang=126a420370e1908ea6e01b2cb8869811716e1707%7Euz; _ga=GA1.2.2121528343.1716047651; _gid=GA1.2.1947017640.1716047651; _crp=s; _culture=uz; _gat=1; {uwccfrontnxauth}',
        # .UWCCFRONTNXAUTH ni Cookie ga qo'shish
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

    while True:
        response = session.get(url, headers=headers)
        set_cookie = response.headers.get('Set-Cookie')

        if set_cookie:
            cookies = set_cookie.split(';')
            for cookie in cookies:
                if 'path=/' in cookie or 'HttpOnly' in cookie or 'SameSite=Lax' in cookie:
                    continue
                print(cookie.strip())

                # Ma'lumotlarni JSON formatiga o'tkazib, bazaga yozish
                data_to_save = {
                    'uwccfrontnxauth': uwccfrontnxauth,
                    'cookie': cookie.strip()
                }
                save_to_json(data_to_save)

        # 2 daqiqada bir so'rov yuborish
        time.sleep(120)
