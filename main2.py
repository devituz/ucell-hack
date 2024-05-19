import requests

# POST so'rovi uchun URL manzili
url = 'https://my.ucell.uz/Account/Login'

# So'rovga yuboriladigan ma'lumotlar
data = {
    "phone_number": "998936438328",
    "password": "Shohbozbek240_2$3",
    "login_type": "3"
}

# So'rovni yuborish
response = requests.post(url, json=data)

# Javobdan Set-Cookie ni olish
set_cookie = response.headers.get('Set-Cookie')

# .UWCCFRONTNXAUTH qiymatini ajratib olish va chop etish
if set_cookie:
    cookies = set_cookie.split(', ')
    for cookie in cookies:
        if '.UWCCFRONTNXAUTH' in cookie:
            uwccfrontnxauth = cookie.split(';')[0]  # 'path=/' qismidan oldingi qismini ajratib olish
            print(uwccfrontnxauth)  # ; qo'shib chiqarish
            break
else:
    print("Set-Cookie sarlavhasi topilmadi.")
