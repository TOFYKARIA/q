from telethon import TelegramClient, events
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

# Запросить у пользователя ввод
api_id = input("Введите api_id: ")
api_hash = input("Введите api_hash: ")

# Создать клиент с введенными значениями
client = TelegramClient('session_name', int(api_id), api_hash)

# Команда для loliart
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]loliart'))
async def loliartcmd(event):
    """-> RandomArt"""
    
    # Проверяем, разблокирована ли команда для пользователя
    if event.sender_id not in unlocked_commands or not unlocked_commands[event.sender_id]:
        await event.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
        return
    
    await event.respond("")
    
    async with client.conversation("@AnimeLoliChan_bot") as conv:
        await conv.send_message("/loli")
        otvet = await conv.get_response()
        
        if otvet.photo:
            photo = await client.download_media(otvet.photo, "loli_hentai")
            await event.client.send_message(
                event.peer_id,
                file=photo,
                reply_to=getattr(event, "reply_to_msg_id", None),
            )
            os.remove(photo)
            await event.delete()

# Команда для loli hentai
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]loli'))
async def lolicmd(event):
    """-> random loli photo"""

    # Проверяем, разблокирована ли команда для пользователя
    if event.sender_id not in unlocked_commands or not unlocked_commands[event.sender_id]:
        await event.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
        return
    
    await event.respond("")
    
    async with client.conversation("@ferganteusbot") as conv:
        try: 
            lh = await conv.send_message("/lh")
        except Exception as e:
            return await event.respond("Failed to get photos. Please unblock @ferganteusbot")
        
        otvet = await conv.get_response()
        await lh.delete()
        
        if otvet.photo:
            await event.client.send_message(
                event.peer_id,
                message=otvet,
                reply_to=getattr(event, "reply_to_msg_id", None)
            )
            await otvet.delete()
            await event.delete()

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

# Ваши старые команды
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
        current_time = datetime.now(pytz.timezone(_time_timezone)).strftime("%H:%M")
        await client(EditProfileRequest(first_name=current_time))
        await asyncio.sleep(60)  # Обновление каждую минуту

# Основной код для запуска бота
async def main():
    await client.start()
    print("Бот успешно запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
