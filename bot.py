import telebot
import requests
import json
import re
from urllib.parse import quote

bot = telebot.TeleBot("7041023451:AAGRSvmj0qPZha0kDOwY2RsI7wkEDI-O_4U")

cookies = {
    'source': 'mb',
    '_gid': 'GA1.2.1236421304.1706295770',
    '_gat_gtag_UA_137597827_4': '1',
    'session_key': 'hnl4y8xtfe918iiz2go67z85nsrvwqdn',
    '_ga': 'GA1.2.1006342705.1706295770',
    'datadome': '3AmY3lp~TL1WEuDKCnlwro_WZ1C6J66V1Y0TJ4ITf1Hvo4833Fh4LF3gHrPCKFJDPUPoXh2dXQHJ_uw0ifD8jmCaDltzE5T3zzRDbXOKH9rPNrTFs29DykfP3cfo7QGy',
    '_ga_R04L19G92K': 'GS1.1.1706295769.1.1.1706295794.0.0.0',
}

headers = {
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://shop.garena.sg',
    'Referer': 'https://shop.garena.sg/app/100067/idlogin',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'accept': 'application/json',
    'content-type': 'application/json',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'x-datadome-clientid': 'DLm2W1ajJwdv~F~a_1d_1PyWnW6ns7GY5ChVcZY3HJ9r6D29661473aQaL2~3Nfh~Vf3m7rie7ObIb1_3eRN7J0G6uFZhMq5pM2jA828fE1dS7rZ7H3MWGQ5vGraAQWd',
}

def get_map_data(map_code):
    url = f"https://mapshare.freefiremobile.com/?&action=ugc_mapdetail®ion=VN&lang=vn&map_code=%23{map_code}&version=OB46&fbclid=IwY2xjawKJmA5leHRuA2FlbQIxMA..."
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text.encode(response.encoding).decode('utf-8', errors='ignore')

        title_match = re.search(r'<title>(.*?)</title>', html_content)
        map_name = title_match.group(1).replace('ㅤ', '').strip() if title_match else "Không tìm thấy tên bản đồ"

        if map_name.startswith("[FF] "):
            map_name = map_name[len("[FF] "):]

        map_name = re.sub(r'[^\w\s]', '', map_name)

        creator_match = re.search(r'<span data-v-8c8a6f11="">(.*?)</span>', html_content)
        creator = creator_match.group(1).strip() if creator_match else "Không tìm thấy người tạo"

        banner_match = re.search(r'<img data-v-fb1e2bab="" src="(data:image/png;base64,[^"]+)"', html_content)
        banner = banner_match.group(1).strip() if banner_match else None

        likes = "Không tìm thấy"
        stars = "Không tìm thấy"

        return {
            "map_name": map_name,
            "creator": creator,
            "banner": banner,
            "likes": likes,
            "stars": stars
        }
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gửi yêu cầu (get_map_data): {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định (get_map_data): {e}")
        return None

def get_data(UID):
    json_data = {
        'app_id': 100067,
        'login_id': UID,
        'app_server_id': 0,
    }
    try:
        response = requests.post(
            'https://shop.garena.sg/api/auth/player_id_login',
            cookies=cookies, headers=headers, json=json_data
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gửi yêu cầu (get_data): {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định (get_data): {e}")
        return None

@bot.message_handler(commands=['map'])
def send_map_info(message):
    chat_id = message.chat.id
    try:
        map_code = message.text.split()[1].replace('#', '')
        map_data = get_map_data(map_code)

        if map_data:
            response_text = (
                f"Tên bản đồ: {map_data['map_name']}\n"
                f"Người tạo: {map_data['creator']}\n"
                f"Lượt thích: {map_data['likes']}\n"
                f"Đánh giá: {map_data['stars']}"
            )
            bot.reply_to(message, response_text)

            if map_data['banner']:
                if map_data['banner'].startswith("data:image"):
                    bot.send_message(chat_id, "Không thể hiển thị ảnh trực tiếp từ Base64 trong tin nhắn văn bản.")
                elif map_data['banner'].startswith("http"):
                    try:
                        bot.send_photo(chat_id, map_data['banner'])
                    except Exception as e:
                        bot.send_message(chat_id, f"Lỗi khi gửi ảnh banner: {str(e)}")
                else:
                    bot.send_message(chat_id, "Không tìm thấy hoặc không hỗ trợ định dạng banner.")
        else:
            bot.reply_to(message, "Không thể lấy thông tin bản đồ.")

    except IndexError:
        bot.reply_to(message, "Vui lòng cung cấp mã bản đồ! Ví dụ: /map #ABC123")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi (send_map_info): {str(e)}")

@bot.message_handler(commands=['idplayer', 'id'])
def handle_id_command(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Vui lòng nhập đúng cú pháp: /id <UID>")
            return

        UID = args[1]
        data = get_data(UID)
        if data:
            try:
                decoded_text = data.encode('utf-8').decode('unicode-escape')
                player_info = json.loads(decoded_text)

                if 'nickname' not in player_info or player_info['nickname'] == "":
                    bot.reply_to(message, "Bạn đã nhập ID không tồn tại. Vui lòng nhập lại.")
                    return

                nickname = player_info['nickname']
                region = player_info.get("region", "Không rõ")

                reply_message = (
                    f"Tên Người Chơi : {nickname}\n"
                    f"Quốc Gia       : {region}\n"
                    f"ID đã nhập     : {UID}"
                )
                bot.reply_to(message, reply_message)
            except json.JSONDecodeError:
                bot.reply_to(message, f"Lỗi khi giải mã dữ liệu JSON: {data}")
            except Exception as e:
                bot.reply_to(message, f"Đã xảy ra lỗi khi xử lý thông tin người chơi: {e}")
        else:
            bot.reply_to(message, "Không thể lấy thông tin người chơi.")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi (handle_id_command): {str(e)}")

bot.polling()
