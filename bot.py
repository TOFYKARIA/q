from telethon import TelegramClient, events, functions, types
import asyncio
import random
import aiohttp
import logging
import pytz
from datetime import datetime
import os
import time

# Конфигурация
prefixes = ['.', '/', '!', '-']
logger = logging.getLogger(__name__)

# Секретный код для разблокировки команд
SECRET_CODE = "unblockcmd"  # Код для разблокировки команд

# Словарь для хранения информации о пользователях, которые разблокировали команды
unlocked_commands = {}

# Создание клиента
client = TelegramClient('session_name', api_id, api_hash)

# Команда для loliart
class LoliArt:
    """RandomArt/Photo BY:@neetchan"""

    strings = {
        "name": "LoliArt",
        "loading_photo": "<emoji document_id=5215327832040811010>🔮</emoji> <b>Process your Loli Art...</b>",
        "error_loading": "<b>Failed to get photos. Please unblock @AnimeLoliChan_bot</b>",
    }
    
    async def loliartcmd(self, message):
        """-> RandomArt"""
        
        # Проверяем, разблокирована ли команда для пользователя
        if message.sender_id not in unlocked_commands or not unlocked_commands[message.sender_id]:
            await message.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
            return
        
        await message.reply(self.strings["loading_photo"])
        
        async with client.conversation("@AnimeLoliChan_bot") as conv:
            await conv.send_message("/lol")
        
            otvet = await conv.get_response()
          
            if otvet.photo:
                phota = await client.download_media(otvet.photo, "loli_hentai")
                await client.send_message(
                    message.peer_id,
                    file=phota,
                    reply_to=message.reply_to_msg_id if message.reply_to_msg_id else None,
                )

                os.remove(phota)
                
                await message.delete()

# Команда для loli hentai
class LoliHentai:
    """Your the best friend in loli hentai"""

    strings = {
        "name": "LoliHentai",
        "loading_photo": "<emoji document_id=5215327832040811010>⏳</emoji> <b>loading your loli photo...</b>",
        "error_loading": "<b>Failed to get photos. Please unblock @ferganteusbot</b>",
        "search": "<emoji document_id=5328311576736833844>🔴</emoji> loading your photo..."
    }
    
    async def lolicmd(self, message):
        """-> random loli photo"""

        # Проверяем, разблокирована ли команда для пользователя
        if message.sender_id not in unlocked_commands or not unlocked_commands[message.sender_id]:
            await message.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
            return
        
        await message.reply(self.strings["loading_photo"])
        
        async with client.conversation("@ferganteusbot") as conv:
            try: 
                lh = await conv.send_message("/lh")
            except Exception as e:
                return await message.reply(self.strings["error_loading"])
        
            otvet = await conv.get_response()
            await lh.delete()
            if otvet.photo:
                await client.send_message(
                    message.peer_id,
                    message=otvet,
                    reply_to=message.reply_to_msg_id if message.reply_to_msg_id else None
                )
                await otvet.delete()
                await message.delete()

# Команда для ввода пароля и разблокировки команд
@client.on(events.NewMessage(pattern='/secret'))
async def secret_handler(event):
    """Разблокировать команды loli и loliart по паролю"""
    code = event.raw_text.split(" ")[1] if len(event.raw_text.split(" ")) > 1 else ""

    # Проверяем правильность пароля
    if code == SECRET_CODE:
        unlocked_commands[event.sender_id] = True
        await event.reply("Секретный код принят! Теперь вы можете использовать команды .loli и .loliart.")
    else:
        await event.reply("Неверный код! Попробуйте снова.")

# Обновленная команда help
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]help'))
async def help_handler(event):
    """Показывает список всех команд"""
    
    help_text = """🔱 UGCLAWS USERBOT 🔱

Доступные команды:
• 💧.help - показать это сообщение
• 💧.anime [nsfw] - отправить случайное аниме фото
• 💧.im [режим] - запустить имитацию (режимы: typing/voice/video/game/mixed)
• 💧.imstop - остановить имитацию
• 💧.time - включить/выключить время в нике
• 💧.time_msk - установить московское время
• 💧.time_ekb - установить екатеринбургское время 
• 💧.time_omsk - установить омское время
• 💧.time_samara - установить самарское время"""

    # Проверяем, доступна ли команда .loli и .loliart
    if event.sender_id in unlocked_commands and unlocked_commands[event.sender_id]:
        help_text += "\n• 💧.loli - случайная лоли фотография"
        help_text += "\n• 💧.loliart - случайное лоли искусство"

    await event.edit(help_text)

# Команда .anime
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]anime'))
async def anime_handler(event):
    """Отправляет случайное аниме фото"""
    args = event.raw_text.split()
    if len(args) > 1 and args[1].lower() == "nsfw":
        url = "https://api.waifu.pics/nsfw/waifu"
        caption = "🎗Лови NSFW фото!"
    else:
        url = "https://api.waifu.pics/sfw/waifu"
        caption = "🔮Случайное аниме фото!"

    message = await event.respond("ван сек..")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "url" in data:
                        await event.client.send_file(event.chat_id, data["url"], caption=caption)
                        await message.delete()
                    else:
                        await message.edit("Ошибка: не удалось найти URL в ответе.")
                else:
                    await message.edit(f"Ошибка: {response.status}")
    except Exception as e:
        await message.edit(f"Ошибка: {e}")

# Команда для имитации действий
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]im'))
async def im_handler(event):
    """Запустить имитацию: .im <режим>
    Режимы: typing/voice/video/game/mixed"""

    args = event.raw_text.split()[1] if len(event.raw_text.split()) > 1 else "mixed"
    mode = args.lower()
    chat_id = event.chat_id

    if chat_id in _imitation_active and _imitation_active[chat_id]:
        await event.edit("❌ Имитация уже запущена")
        return

    _imitation_active[chat_id] = True

    _imitation_tasks[chat_id] = asyncio.create_task(
        _imitate(event.client, chat_id, mode)
    )

    await event.edit(f"🎭 Имитация запущена\nРежим: {mode}")

_imitation_tasks = {}
_imitation_active = {}

async def _imitate(client, chat_id, mode):
    """Бесконечная имитация действия"""
    try:
        while _imitation_active.get(chat_id, False):
            if mode == "typing":
                async with client.action(chat_id, 'typing'):
                    await asyncio.sleep(5)
            elif mode == "voice":
                async with client.action(chat_id, 'record-audio'):
                    await asyncio.sleep(5)
            elif mode == "video":
                async with client.action(chat_id, 'record-video'):
                    await asyncio.sleep(5)
            elif mode == "game":
                async with client.action(chat_id, 'game'):
                    await asyncio.sleep(5)
            elif mode == "mixed":
                actions = ['typing', 'record-audio', 'record-video', 'game']
                async with client.action(chat_id, random.choice(actions)):
                    await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"Imitation error: {e}")
        _imitation_active[chat_id] = False

# Команда для остановки имитации
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]imstop'))
async def imstop_handler(event):
    """Остановить имитацию"""
    chat_id = event.chat_id

    if chat_id in _imitation_active:
        _imitation_active[chat_id] = False
        if chat_id in _imitation_tasks:
            _imitation_tasks[chat_id].cancel()
            del _imitation_tasks[chat_id]

    await event.edit("🚫 Имитация остановлена")

# Для времени в нике
_time_running = False
_time_timezone = 'Europe/Moscow'

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time'))
async def time_handler(event):
    """Включить/выключить время в нике"""
    global _time_running
    if _time_running:
        _time_running = False
        await event.edit("Обновление времени в нике остановлено")
    else:
        _time_running = True
        await event.edit("Обновление времени в нике запущено")
        asyncio.create_task(update_nick(event.client))

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_msk'))
async def time_msk_handler(event):
    """Переключить время на МСК"""
    global _time_timezone
    _time_timezone = 'Europe/Moscow'
    await event.edit("Время в нике будет отображаться по МСК")

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_ekb'))
async def time_ekb_handler(event):
    """Переключить время на ЕКБ"""
    global _time_timezone
    _time_timezone = 'Asia/Yekaterinburg'
    await event.edit("Время в нике будет отображаться по ЕКБ")

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_omsk'))
async def time_omsk_handler(event):
    """Переключить время на Омск"""
    global _time_timezone
    _time_timezone = 'Asia/Omsk'
    await event.edit("Время в нике будет отображаться по Омску")

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_samara'))
async def time_samara_handler(event):
    """Переключить время на Самару"""
    global _time_timezone
    _time_timezone = 'Europe/Samara'
    await event.edit("Время в нике будет отображаться по Самаре")

async def update_nick(client):
    """Обновление времени в нике"""
    while _time_running:
        now = datetime.now(pytz.timezone(_time_timezone))
        await client(UpdateProfileRequest(first_name=f"Time: {now.strftime('%H:%M:%S')}"))
        await asyncio.sleep(60)

# Основной код для запуска бота
async def main():
    # Создаем экземпляры классов команд
    loli_art = LoliArt()
    loli_hentai = LoliHentai()

    # Регистрируем обработчики команд
    client.add_event_handler(loli_art.loliartcmd, events.NewMessage(pattern=f'[{"".join(prefixes)}]loliart'))
    client.add_event_handler(loli_hentai.lolicmd, events.NewMessage(pattern=f'[{"".join(prefixes)}]loli'))
    client.add_event_handler(secret_handler)
    client.add_event_handler(help_handler)
    client.add_event_handler(anime_handler)
    client.add_event_handler(im_handler)
    client.add_event_handler(imstop_handler)
    client.add_event_handler(time_handler)
    client.add_event_handler(time_msk_handler)
    client.add_event_handler(time_ekb_handler)
    client.add_event_handler(time_omsk_handler)
    client.add_event_handler(time_samara_handler)

    print("Бот запускается...")
    await client.start()
    print("Бот успешно запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
