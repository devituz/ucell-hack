import requests
import json

# Ma'lumotlarni saqlash uchun baza fayli
db_file = 'baza.json'


# Funksiya ma'lumotlarni baza.json fayliga yozadi
def save_to_json(data):
    with open(db_file, 'w') as file:
        json.dump(data, file)


# POST so'rovi uchun URL manzili
send_sms_url = 'https://my.ucell.uz/PcSms/SendSms'

# So'rov uchun kerakli headerlar
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/json; charset=utf-8',
}

# Cookie va uwccfrontnxauth ma'lumotlari
cookie_data = None
uwccfrontnxauth = None

# Baza.json faylidan cookie va uwccfrontnxauth ma'lumotlarni olish
with open(db_file) as file:
    data = json.load(file)
    cookie_data = data.get('cookie')
    uwccfrontnxauth = data.get('uwccfrontnxauth')

# So'rov uchun kerakli ma'lumotlar
sms_data = {
    "msisdn": "998948832182",
    "text": "po pitux",
    "date": None
}

# So'rov uchun headerlarga cookie va uwccfrontnxauth ni qo'shish
headers[
    'Cookie'] = f'lang=126a420370e1908ea6e01b2cb8869811716e1707%7Euz; _ga=GA1.2.2121528343.1716047651; _gid=GA1.2.1947017640.1716047651; _crp=s; _culture=uz; {uwccfrontnxauth}; {cookie_data}'

# So'rovni yuborish
response = requests.post(send_sms_url, headers=headers, json=sms_data)

# Javobni tekshirish
if response.status_code == 200:
    print("SMS yuborildi.")
else:
    print("SMS yuborishda xatolik yuz berdi:", response.status_code)
