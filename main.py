import os
import json
import asyncio
import re
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import yt_dlp

# =====================================================================
# 🛠️ PROFESSIONAL LOGGING CORE
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("MarseilleProEngine")

# =====================================================================
# 🔑 SYSTEM CONFIGURATION
# =====================================================================
BOT_TOKEN = "7538291024:AAH_Bura_BotFather_Tokeni_Gelecek"
API_ID = 12345678  
API_HASH = "b420b9b22e9a3698bc600c4e3052116c"
ADMIN_ID = 123456789  # Statistika üçün şəxsi Telegram ID-niz

app = Client("MarseilleProV5", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
DB_FILE = "marseille_v5_users.json"
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Professional Local Database Engine
def load_db() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data: dict):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: logger.error(f"DB Save Error: {e}")

def register_user(chat_id: int):
    db = load_db()
    if str(chat_id) not in db:
        db[str(chat_id)] = "az"
        save_db(db)

def get_lang(chat_id: int) -> str: 
    return load_db().get(str(chat_id), "az")

def set_lang(chat_id: int, lang: str):
    db = load_db()
    db[str(chat_id)] = lang
    save_db(db)

# =====================================================================
# 🌐 PROFESSIONAL MULTI-LANGUAGE DICTIONARY
# =====================================================================
STRINGS = {
    "az": {
        "welcome": "👋 **Marseille Media Downloader xidmətinə xoş gəlmisiniz.**\n\nSistem dilini seçin / Select language:",
        "main_menu": "🚀 **Marseille Media Engine V5 Pro**\n\nSistem aktivdir və sorğuları qəbul etməyə hazırdır.\n\n🎵 **Funksiyalar:**\n• Sürətli link analizi\n• YouTube MP3 Yükləyici (320kbps Yüksək Keyfiyyət)\n• Avtomatik keş təmizləmə sistemi",
        "btn_add": "➕ Qrupa Əlavə Et ➕",
        "btn_lang": "🌐 Dili Dəyişdir",
        "link_detected": "🔗 **Media Linki Təsdiqləndi.**\n\nYükləmə formatını seçin:",
        "btn_dl_mp3": "📥 MP3 Yüklə (320kbps HQ)",
        "dl_f_mp3": "⚡ **Audio 320kbps formatında serverə endirilir...**",
        "uploading": "📤 **Audio fayl Telegram-a ötürülür...**"
    },
    "tr": {
        "welcome": "👋 **Marseille Media Downloader servisine hoş geldiniz.**\n\nSistem dilini seçiniz / Select language:",
        "main_menu": "🚀 **Marseille Media Engine V5 Pro**\n\nSistem aktif durumdadır ve talepleri almaya hazırdır.\n\n🎵 **Özellikler:**\n• Hızlı bağlantı analizi\n• YouTube MP3 İndirici (320kbps Yüksek Kalite)\n• Otomatik önbellek temizleme sistemi",
        "btn_add": "➕ Gruba Ekle ➕",
        "btn_lang": "🌐 Dili Değiştir",
        "link_detected": "🔗 **Medya Bağlantısı Doğrulandı.**\n\nİndirme formatını seçiniz:",
        "btn_dl_mp3": "📥 MP3 Olarak İndir (320kbps)",
        "dl_f_mp3": "⚡ **Ses 320kbps formatında sunucuya indiriliyor...**",
        "uploading": "📤 **Ses dosyası Telegram'a yükleniyor...**"
    },
    "en": {
        "welcome": "👋 **Welcome to Marseille Media Downloader Service.**\n\nSelect system language:",
        "main_menu": "🚀 **Marseille Media Engine V5 Pro**\n\nThe system is active and ready to process requests.\n\n🎵 **Features:**\n• Fast link analysis\n• YouTube MP3 Downloader (320kbps High Quality)\n• Automatic cache cleaning system",
        "btn_add": "➕ Add to Group ➕",
        "btn_lang": "🌐 Change Language",
        "link_detected": "🔗 **Media Link Verified.**\n\nSelect download format:",
        "btn_dl_mp3": "📥 Download MP3 (320kbps)",
        "dl_f_mp3": "⚡ **Downloading audio in 320kbps format to server...**",
        "uploading": "📤 **Uploading audio file to Telegram...**"
    },
    "ru": {
        "welcome": "👋 **Добро пожаловать в сервис Marseille Media Downloader.**\n\nВыберите язык системы:",
        "main_menu": "🚀 **Marseille Media Engine V5 Pro**\n\nСистема активна и готова к обработке запросов.\n\n🎵 **Функции:**\n• Быстрый анализ ссылок\n• YouTube MP3 Загрузчик (320kbps Высокое Качество)\n• Автоматическая очистка кэша",
        "btn_add": "➕ Добавить в группу ➕",
        "btn_lang": "🌐 Изменить язык",
        "link_detected": "🔗 **Медиа ссылка верифицирована.**\n\nВыберите формат загрузки:",
        "btn_dl_mp3": "📥 Скачать как MP3 (320kbps)",
        "dl_f_mp3": "⚡ **Аудио скачивается на сервер в качестве 320kbps...**",
        "uploading": "📤 **Аудиофайл отправляется в Telegram...**"
    },
    "uz": {
        "welcome": "👋 **Marseille Media Downloader xizmatiga xush kelibsiz.**\n\nTizim tilini tanlang:",
        "main_menu": "🚀 **Marseille Media Engine V5 Pro**\n\nTizim faol va so'rovlarni qabul qilishga tayyor.\n\n🎵 **Xususiyatlari:**\n• Tezkor havola tahlili\n• YouTube MP3 Yuklovchi (320kbps Yuqori Sifat)\n• Avtomatik keshni tozalash tizimi",
        "btn_add": "➕ Guruhga Qo'shish ➕",
        "btn_lang": "🌐 Tilni O'zgartirish",
        "link_detected": "🔗 **Media havola tasdiqlandi.**\n\nYuklab olish formatini tanlang:",
        "btn_dl_mp3": "📥 MP3 Sifatida Yuklash (320kbps)",
        "dl_f_mp3": "⚡ **Audio 320kbps formatda serverga yuklanmoqda...**",
        "uploading": "📤 **Audio fayl Telegramga yuborilmoqda...**"
    }
}

# =====================================================================
# 🛠️ ADVANCED YT-DLP CORE ENGINE (320KBPS AUDIO CONVERTER)
# =====================================================================
def download_mp3_file(url: str, user_id: int):
    out_tmpl = f"{DOWNLOAD_DIR}/{user_id}_%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_tmpl,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.rsplit('.', 1)[0] + '.mp3', info['title']

# =====================================================================
# 📥 TELEGRAM HANDLERS & ROUTING
# =====================================================================

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    register_user(message.chat.id)
    lang = get_lang(message.chat.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇦🇿 AZ", callback_data="sl_az"), InlineKeyboardButton("🇹🇷 TR", callback_data="sl_tr"), InlineKeyboardButton("🇬🇧 EN", callback_data="sl_en")],
        [InlineKeyboardButton("🇷🇺 RU", callback_data="sl_ru"), InlineKeyboardButton("🇺🇿 UZ", callback_data="sl_uz")]
    ])
    await message.reply_text(STRINGS[lang]["welcome"], reply_markup=keyboard, quote=True)

@app.on_callback_query(filters.regex(r'^sl_'))
async def set_language_callback(client, callback_query: CallbackQuery):
    lang = callback_query.data.split("_")[1]
    set_lang(callback_query.message.chat.id, lang)
    bot_username = (await client.get_me()).username
    main_menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(STRINGS[lang]["btn_add"], url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton(STRINGS[lang]["btn_lang"], callback_data="back_to_lang")]
    ])
    await callback_query.message.edit_text(STRINGS[lang]["main_menu"], reply_markup=main_menu_keyboard)

@app.on_callback_query(filters.regex("back_to_lang"))
async def back_lang(client, callback_query: CallbackQuery):
    await start(client, callback_query.message)

youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+')

@app.on_message(filters.regex(youtube_regex))
async def handle_youtube_link(client, message: Message):
    register_user(message.chat.id)
    lang = get_lang(message.chat.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(STRINGS[lang]["btn_dl_mp3"], callback_data=f"mp3dl_{message.id}")]
    ])
    await message.reply_text(STRINGS[lang]["link_detected"], reply_markup=keyboard, quote=True)

@app.on_callback_query(filters.regex(r'^mp3dl_'))
async def process_media_choice(client, callback_query: CallbackQuery):
    msg_id = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    lang = get_lang(chat_id)
    
    target_msg = await client.get_messages(chat_id, int(msg_id))
    url = target_msg.text
    
    await callback_query.answer("Proses başladıldı...")
    status = await callback_query.message.edit_text(STRINGS[lang]["dl_f_mp3"])
    try:
        loop = asyncio.get_event_loop()
        file_path, title = await loop.run_in_executor(None, download_mp3_file, url, callback_query.from_user.id)
        await status.edit_text(STRINGS[lang]["uploading"])
        
        await target_msg.reply_audio(
            audio=file_path,
            caption=f"🎵 **Marseille Core V5 Pro**\nKeyfiyyət: `320kbps HQ Ultra Studio`",
            title=title,
            performer="Marseille Bot"
        )
        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await status.edit_text(f"❌ **Sistem Xətası:** `{str(e)}`")

# =====================================================================
# 📈 ADMIN MANAGEMENT PANEL
# =====================================================================
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def admin_stats(client, message: Message):
    db = load_db()
    total_users = len(db)
    await message.reply_text(f"📊 **Marseille Core Canlı Statistika:**\n\nSistemdəki toplam istifadəçi sayısı: `{total_users}`")

if __name__ == "__main__":
    print("🔥 MARSEILLE V5 ULTIMATE ENGINE ONLINE!")
    app.run()