import os
import json
import asyncio
import re
import logging
from typing import Dict, List, Any
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

# =====================================================================
# 🛠️ PROFESSIONAL LOGGING & SECURITY ENGINE 
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[logging.FileHandler("marseille_core.log"), logging.StreamHandler()]
)
logger = logging.getLogger("MarseilleCore")

# =====================================================================
# 🔑 SYSTEM CONFIGURATION
# =====================================================================
BOT_TOKEN = "8918931473:AAGldV4Bg-PsU4jQSsFJvlrBAr0PkuL9zug"
API_ID = 39652160
API_HASH = "b420b9b22e9a3698bc600c4e3052116c"

app = Client("MarseilleUltimateV5", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

DB_FILE = "marseille_v5_db.json"
DOWNLOAD_DIR = "downloads"
QUEUE: Dict[int, List[Dict[str, Any]]] = {} # Hər qrup üçün özəl professional növbə yaddaşı

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Professional Local JSON Database Mühərriki
def load_db() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception as e:
            logger.error(f"Database oxunma xətası: {e}")
            return {}
    return {}

def save_db(data: dict):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: logger.error(f"Database save xətası: {e}")

def get_lang(chat_id: int) -> str: return load_db().get(str(chat_id), "az")
def set_lang(chat_id: int, lang: str):
    db = load_db(); db[str(chat_id)] = lang; save_db(db)

# =====================================================================
# 🌐 MULTI-LANGUAGE DICTIONARY (5 DİLDƏ TAM DETALLI MESAJLAR)
# =====================================================================
STRINGS = {
    "az": {
        "welcome": "👋 **Salam rəis! Mən Marseille Ultimate V5 - Ən Güclü Media Mühərriyəm!**\n\nSistem dilini seçin / Select language:",
        "main_menu": "🚀 **Marseille Mühəndislik Paneli V5**\n\n🎵 **Özəlliklər:**\n• Qruplarda Canlı Səsli Çat Musiqisi\n• Ard-arda Mahnı Növbəsi Siyahısı\n• YouTube MP3 Yükləyici (320kbps)\n• İkiqat Keşləmə və Anti-Lag Sistemi!",
        "btn_add": "➕ Boti Qrupa Admin Et ➕",
        "btn_lang": "🌐 Dili Dəyişdir",
        "link_detected": "🔗 **Muzika Analiz Olundu!**\n\nNə etmək istəyirsiniz qardaşım? Aşağıdan seçin:",
        "btn_play_vc": "🔊 Səsli Çatda Canlı Oxut",
        "btn_dl_mp3": "📥 Ultra-MP3 Kimi Yüklə",
        "searching": "🔍 **Kiber-Mühərrik YouTube-da axtarış edir...**",
        "downloading": "📥 **Audio yoxlanılır və səsli çata axın (stream) başladılır...**",
        "dl_f_mp3": "⚡ **Audio 320kbps HQ keyfiyyətdə serverə endirilir...**",
        "uploading": "📤 **Tərtemiz MP3 faylı Teleqrama ötürülür...**",
        "playing": "🎶 **İndi Canlı Oxunur:**\n📝 **Mahnı:** `{title}`\n👤 **İstəyən:** {user}",
        "added_queue": "⏳ **Mahnı Növbəyə Əlavə Edildi!**\n📝 `{title}`\n📌 Növbədəki yeri: **#{pos}**",
        "stop": "⏸️ **Muzika müvəqqəti dayandırıldı!**",
        "resume": "▶️ **Muzika qaldığı yerdən davam edir!**",
        "not_in_vc": "❌ **Xəta:** Qrupda aktiv səsli çat tapılmadı və ya admin icazəm yoxdur!",
        "queue_empty": "📋 **Növbə boşdur! Oxunacaq mahnı qalmadı.**"
    },
    "tr": {
        "welcome": "👋 **Merhaba! Ben Marseille Ultimate V5 - En Gelişmiş Medya Motoru!**\n\nDil seçimi yapınız:",
        "main_menu": "🚀 **Marseille Mühendislik Paneli V5**\n\n🎵 **Özellikler:**\n• Sesli Sohbette Canlı Müzik\n• Gelişmiş Şarkı Sıralama (Queue)\n• YouTube MP3 İndirici (320kbps)\n• Anti-Lag ve Çökme Koruması!",
        "link_detected": "🔗 **Müzik Analiz Edildi!**\n\nNe yapmak istersiniz reis? Seçim yapın:",
        "btn_play_vc": "🔊 Sesli Sohbette Çal",
        "btn_dl_mp3": "📥 MP3 Olarak İndir",
        "searching": "🔍 **Siber Motor YouTube'da arama yapıyor...**",
        "downloading": "📥 **Ses akışı başlatılıyor...**",
        "dl_f_mp3": "⚡ **Ses 320kbps kalitesinde sunucuya indiriliyor...**",
        "uploading": "📤 **MP3 dosyası Telegram'a yükleniyor...**",
        "playing": "🎶 **Şimdi Canlı Çalınıyor:**\n📝 **Şarkı:** `{title}`\n👤 **İstek:** {user}",
        "added_queue": "⏳ **Şarkı Sıraya Eklendi!**\n📝 `{title}`\n📌 Sıradaki Yeri: **#{pos}**",
        "stop": "⏸️ **Müzik duraklatıldı!**",
        "resume": "▶️ **Müzik devam ediyor!**",
        "not_in_vc": "❌ **Hata:** Aktif bir sesli sohbet bulunamadı!"
    },
    "en": {
        "welcome": "👋 **Hello! I am Marseille Ultimate V5 - The Most Powerful Media Engine!**\n\nSelect system language:",
        "main_menu": "🚀 **Marseille Engineering Panel V5**\n\n🎵 **Features:**\n• Voice Chat Live Streaming\n• Advanced Song Queue System\n• YouTube MP3 Downloader (320kbps)\n• Anti-Lag & Crash Protection Engine!",
        "link_detected": "🔗 **Media Analyzed Successfully!**\n\nWhat would you like to do? Select below:",
        "btn_play_vc": "🔊 Stream in Voice Chat",
        "btn_dl_mp3": "📥 Download High-Quality MP3",
        "searching": "🔍 **Cyber-Engine searching on YouTube...**",
        "downloading": "📥 **Downloading and initializing stream...**",
        "dl_f_mp3": "⚡ **Downloading audio in 320kbps HQ format...**",
        "uploading": "📤 **Uploading MP3 file to Telegram...**",
        "playing": "🎶 **Now Playing Live:**\n📝 **Title:** `{title}`\n👤 **Requested by:** {user}",
        "added_queue": "⏳ **Added to Queue!**\n📝 `{title}`\n📌 Position: **#{pos}**",
        "stop": "⏸️ **Music paused!**",
        "resume": "▶️ **Music resumed!**",
        "not_in_vc": "❌ **Error:** No active voice chat found!"
    },
    "ru": {
        "welcome": "👋 **Привет! Я Marseille Ultimate V5 - Мощный Медиа Движок!**\n\nВыберите язык системы:",
        "main_menu": "🚀 **Инженерная Панель Марсель V5**\n\n🎵 **Функции:**\n• Трансляция в Голосовой Чат\n• Продвинутая Очередь Треков\n• YouTube MP3 Скачивание (320kbps)\n• Защита от зависаний и задержек!",
        "link_detected": "🔗 **Медиа успешно проанализировано!**\n\nЧто вы хотите сделать? Выберите ниже:",
        "btn_play_vc": "🔊 Включить в Голосовом Чате",
        "btn_dl_mp3": "📥 Скачать как HQ MP3",
        "searching": "🔍 **Кибер-движок ищет на YouTube...**",
        "downloading": "📥 **Запуск аудиопотока...**",
        "dl_f_mp3": "⚡ **Скачивание аудио в качестве 320kbps...**",
        "uploading": "📤 **Отправка MP3 файла в Telegram...**",
        "playing": "🎶 **Сейчас играет:**\n📝 **Название:** `{title}`\n👤 **Заказчик:** {user}",
        "added_queue": "⏳ **Добавлено в очередь!**\n📝 `{title}`\n📌 Позиция: **#{pos}**",
        "stop": "⏸️ **Музыка приостановлена!**",
        "resume": "▶️ **Музыка продолжается!**",
        "not_in_vc": "❌ **Ошибка:** Активный голосовой чат не найден!"
    },
    "uz": {
        "welcome": "👋 **Salom! Men Marseille Ultimate V5 - Eng Kuchli Media Dvigateli!**\n\nTizim tilini tanlang:",
        "main_menu": "🚀 **Marseille Muhandislik Paneli V5**\n\n🎵 **Xususiyatlari:**\n• Ovozli Chatda Jonli Translyatsiya\n• Kengaytirilgan Qo'shiqlar Navbati (Queue)\n• YouTube MP3 Yuklovchi (320kbps)\n• Anti-Lag va nosozlikdan himoya tizimi!",
        "link_detected": "🔗 **Media muvaffaqiyatli tahlil qilindi!**\n\nNima qilmoqchisiz? Quyidan tanlang:",
        "btn_play_vc": "🔊 Ovozli Chatda Ijro Etish",
        "btn_dl_mp3": "📥 HQ MP3 Sifatida Yuklash",
        "searching": "🔍 **Kiber-dvigateli YouTube-da qidirmoqda...**",
        "downloading": "📥 **Ovozli oqim boshlanmoqda...**",
        "dl_f_mp3": "⚡ **Audio 320kbps formatda yuklanmoqda...**",
        "uploading": "📤 **MP3 fayli Telegramga yuborilmoqda...**",
        "playing": "🎶 **Hozir Ijro Etilmoqda:**\n📝 **Nomi:** `{title}`\n👤 **Buyurtmachi:** {user}",
        "added_queue": "⏳ **Navbatga qo'shildi!**\n📝 `{title}`\n📌 Navbatdagi joyi: **#{pos}**",
        "stop": "⏸️ **Musiqa vaqtincha to'xtatildi!**",
        "resume": "▶️ **Musiqa davom ettirilmoqda!**",
        "not_in_vc": "❌ **Xatolik:** Faol ovozli chat topilmadi!"
    }
}

# =====================================================================
# 🛠️ ADVANCED YT-DLP CORE ENGINE
# =====================================================================
def get_youtube_stream(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch',
        'noplaylist': True,
        'quiet': True,
        'source_address': '0.0.0.0' # Şəbəkə sıxılmasının qarşısını almaq üçün IPv4 məجبuriyyəti
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info: info = info['entries'][0]
        return info['url'], info['title']

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
# 📋 ADVANCED AUDIO QUEUE SYSTEM (NÖVBƏ MENECERİ)
# =====================================================================
async def start_queue_engine(chat_id: int, client: Client):
    """Mahnı bitəndə növbəti mahnını avtomatik başladan ağıllı mühərrik"""
    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return
    
    lang = get_lang(chat_id)
    # Cari mahnı bitibsə, növbətidən davam edirik
    next_track = QUEUE[chat_id].pop(0)
    
    try:
        await call_py.join_group_call(chat_id, AudioPiped(next_track['url']))
        await client.send_message(
            chat_id, 
            STRINGS[lang]["playing"].format(title=next_track['title'], user=next_track['user'])
        )
    except Exception as e:
        logger.error(f"Queue Engine Xətası: {e}")
        # Əgər xəta olarsa növbəti mahnıya keçməyə çalış
        await start_queue_engine(chat_id, client)

@call_py.on_stream_end()
async def handler(client: Client, update):
    """Səsli çatda canlı yayım bitəndə avtomatik işə düşən GitCalls Event Handler"""
    chat_id = update.chat_id
    if chat_id in QUEUE and QUEUE[chat_id]:
        await start_queue_engine(chat_id, client)
    else:
        try: await call_py.leave_group_call(chat_id)
        except: pass

# =====================================================================
# 📥 TELEGRAM HANDLERS & ROUTING
# =====================================================================

@app.on_message(filters.command("start"))
async def start(client, message: Message):
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

# YouTube Link Detektoru
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+')

@app.on_message(filters.regex(youtube_regex))
async def handle_youtube_link(client, message: Message):
    lang = get_lang(message.chat.id)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(STRINGS[lang]["btn_play_vc"], callback_data=f"vcplay_{message.id}"),
            InlineKeyboardButton(STRINGS[lang]["btn_dl_mp3"], callback_data=f"mp3dl_{message.id}")
        ]
    ])
    await message.reply_text(STRINGS[lang]["link_detected"], reply_markup=keyboard, quote=True)

# İdarəetmə Düymələrinin Logikası
@app.on_callback_query(filters.regex(r'^(vcplay|mp3dl)_'))
async def process_media_choice(client, callback_query: CallbackQuery):
    action, msg_id = callback_query.data.split("_")
    chat_id = callback_query.message.chat.id
    lang = get_lang(chat_id)
    
    target_msg = await client.get_messages(chat_id, int(msg_id))
    url = target_msg.text
    user_mention = callback_query.from_user.mention
    
    if action == "vcplay":
        await callback_query.answer("🔊 Növbə və səs sistemi yoxlanılır...")
        status = await callback_query.message.edit_text(STRINGS[lang]["searching"])
        try:
            loop = asyncio.get_event_loop()
            stream_url, title = await loop.run_in_executor(None, get_youtube_stream, url)
            
            # NÖVBƏ SİSTEMİNİN İDARƏSİ (Mühəndislik Blok)
            if chat_id in QUEUE and len(QUEUE[chat_id]) > 0 or call_py.is_connected(chat_id):
                if chat_id not in QUEUE: QUEUE[chat_id] = []
                QUEUE[chat_id].append({'url': stream_url, 'title': title, 'user': user_mention})
                pos = len(QUEUE[chat_id])
                await status.edit_text(STRINGS[lang]["added_queue"].format(title=title, pos=pos))
            else:
                await status.edit_text(STRINGS[lang]["downloading"])
                await call_py.join_group_call(chat_id, AudioPiped(stream_url))
                await status.edit_text(STRINGS[lang]["playing"].format(title=title, user=user_mention))
        except Exception as e:
            await status.edit_text(f"❌ **Kiber-Səs Xətası:** `{str(e)}`")
            
    elif action == "mp3dl":
        await callback_query.answer("📥 MP3 arxitekturası işə düşdü...")
        status = await callback_query.message.edit_text(STRINGS[lang]["dl_f_mp3"])
        try:
            loop = asyncio.get_event_loop()
            file_path, title = await loop.run_in_executor(None, download_mp3_file, url, callback_query.from_user.id)
            await status.edit_text(STRINGS[lang]["uploading"])
            
            await target_msg.reply_audio(
                audio=file_path,
                caption=f"🎵 **Marseille Core V5 Pro**\n🔥 **Auditoriya:** `320kbps HQ Ultra`",
                title=title,
                performer="Marseille Bot"
            )
            await status.delete()
            if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            await status.edit_text(f"❌ **Yükləmə xətası:** `{str(e)}`")

# =====================================================================
# 🎛️ PROFESSIONAL ADMİN KOMANDALARI
# =====================================================================
@app.on_message(filters.command(["oynat", "play"]) & filters.group)
async def play_by_command(client, message: Message):
    lang = get_lang(message.chat.id)
    if len(message.command) < 2: return await message.reply_text("❌ `/oynat Mahnı adı` yaz rəis.")
    query = " ".join(message.command[1:])
    status = await message.reply_text(STRINGS[lang]["searching"])
    try:
        loop = asyncio.get_event_loop()
        stream_url, title = await loop.run_in_executor(None, get_youtube_stream, query)
        user_mention = message.from_user.mention if message.from_user else "Anonim"
        
        if message.chat.id in QUEUE and len(QUEUE[message.chat.id]) > 0 or call_py.is_connected(message.chat.id):
            if message.chat.id not in QUEUE: QUEUE[message.chat.id] = []
            QUEUE[message.chat.id].append({'url': stream_url, 'title': title, 'user': user_mention})
            await status.edit_text(STRINGS[lang]["added_queue"].format(title=title, pos=len(QUEUE[message.chat.id])))
        else:
            await call_py.join_group_call(message.chat.id, AudioPiped(stream_url))
            await status.edit_text(STRINGS[lang]["playing"].format(title=title, user=user_mention))
    except Exception as e: await status.edit_text(f"❌ Xəta: `{str(e)}`")

@app.on_message(filters.command(["dur", "pause"]) & filters.group)
async def pause(client, message: Message):
    try: await call_py.pause_group_call(message.chat.id); await message.reply_text(STRINGS[get_lang(message.chat.id)]["stop"])
    except: await message.reply_text(STRINGS[get_lang(message.chat.id)]["not_in_vc"])

@app.on_message(filters.command(["davam", "resume"]) & filters.group)
async def resume(client, message: Message):
    try: await call_py.resume_group_call(message.chat.id); await message.reply_text(STRINGS[get_lang(message.chat.id)]["resume"])
    except: await message.reply_text(STRINGS[get_lang(message.chat.id)]["not_in_vc"])

@app.on_message(filters.command(["kec", "skip", "next"]) & filters.group)
async def skip_track(client, message: Message):
    chat_id = message.chat.id
    lang = get_lang(chat_id)
    if chat_id in QUEUE and QUEUE[chat_id]:
        await message.reply_text("⏭️ **Cari mahnı keçildi, növbəti mahnı başladılır...**")
        await start_queue_engine(chat_id, client)
    else:
        await message.reply_text(STRINGS[lang]["queue_empty"])

@app.on_message(filters.command(["kec", "leave", "stop"]) & filters.group)
async def leave(client, message: Message):
    try: 
        if message.chat.id in QUEUE: QUEUE[message.chat.id].clear()
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("👋 **Səsli çatdan çıxdım və növbə siyahısını sıfırladım!**")
    except: pass

if __name__ == "__main__":
    logger.info("🔥 MARSEILLE V5 ULTIMATE ENGINE STARTING...")
    call_py.start()
    app.run()