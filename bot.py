import json
from telethon import TelegramClient, events
import asyncio
import random
import aiohttp
import logging
import pytz
from datetime import datetime
import os
import time
from telethon.tl.functions.account import UpdateProfileRequest

# Конфигурация
prefixes = ['.', '/', '!', '-']
logger = logging.getLogger(__name__)

SECRET_CODE = "unblockcmd"
unlocked_commands = {}
config_file = "config.json"

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f)

config = load_config()

if "api_id" not in config or "api_hash" not in config:
    api_id = input("Введите api_id: ")
    api_hash = input("Введите api_hash: ")
    config["api_id"] = api_id
    config["api_hash"] = api_hash
    save_config(config)
else:
    api_id = config["api_id"]
    api_hash = config["api_hash"]

client = TelegramClient('session_name', int(api_id), api_hash)

# Команда для лоли хентая
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]loli'))
async def lolicmd(event):
    if event.sender_id not in unlocked_commands or not unlocked_commands[event.sender_id]:
        await event.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
        return
    
    await event.respond("щащащаща")
    
    async with client.conversation("@ferganteusbot") as conv:
        try: 
            lh = await conv.send_message("/lh")
        except Exception as e:
            return await event.respond("Инвалид, разблокируй @Ferganteusbot")
        
        otvet = await conv.get_response()
        await lh.delete()
        
        if otvet.photo:
            await event.client.send_message(event.peer_id, message=otvet, reply_to=getattr(event, "reply_to_msg_id", None))
            await otvet.delete()
            await event.delete()

# Разблокировка команд
@client.on(events.NewMessage(pattern='/secret'))
async def secret_handler(event):
    code = event.raw_text.split(" ")[1] if len(event.raw_text.split(" ")) > 1 else ""

    if code == SECRET_CODE:
        unlocked_commands[event.sender_id] = True
        await event.reply("Теперь ты можешь юзать .loli")
    else:
        await event.reply("Неправильный код, попробуй снова.")

# Команда помощи
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]help'))
async def help_handler(event):
    help_text = """🔮 UGCLAWS USERBOT Lite 🔮

Доступные команды:
• .help - показать это сообщение
• .anime [nsfw] - случайное аниме фото
• .im [режим] - запустить имитацию (режимы: typing/voice/video/game/mixed)
• .imstop - остановить имитацию
• .time - включить/выключить время в нике
• .time_msk - установить московское время
• .time_ekb - установить екатеринбургское время 
• .time_omsk - установить омское время
• .time_samara - установить самарское время"""

    if event.sender_id in unlocked_commands and unlocked_commands[event.sender_id]:
        help_text += "\n• .loli - случайная лоли фотография"

    await event.edit(help_text)

# Команда для отправки аниме фото
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]anime'))
async def anime_handler(event):
    args = event.raw_text.split()
    if len(args) > 1 and args[1].lower() == "nsfw":
        url = "https://api.waifu.pics/nsfw/waifu"
        caption = "🎗 Лови NSFW фото!"
    else:
        url = "https://api.waifu.pics/sfw/waifu"
        caption = "🔮 Случайное аниме фото!"

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

# Имитация активности
@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]im'))
async def im_handler(event):
    args = event.raw_text.split()[1] if len(event.raw_text.split()) > 1 else "mixed"
    mode = args.lower()
    chat_id = event.chat_id

    if chat_id in _imitation_active and _imitation_active[chat_id]:
        await event.edit("❌ Имитация уже запущена")
        return

    _imitation_active[chat_id] = True
    _imitation_tasks[chat_id] = asyncio.create_task(_imitate(event.client, chat_id, mode))

    await event.edit(f"🎭 Имитация запущена\nРежим: {mode}")

_imitation_tasks = {}
_imitation_active = {}

async def _imitate(client, chat_id, mode):
    try:
        while _imitation_active.get(chat_id, False):
            async with client.action(chat_id, mode):
                await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"Ошибка имитации: {e}")
        _imitation_active[chat_id] = False

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]imstop'))
async def imstop_handler(event):
    chat_id = event.chat_id
    _imitation_active[chat_id] = False
    if chat_id in _imitation_tasks:
        _imitation_tasks[chat_id].cancel()
        del _imitation_tasks[chat_id]

    await event.edit("🚫 Имитация остановлена")

# Время в нике
_time_running = False
_time_timezone = 'Europe/Moscow'

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time'))
async def time_handler(event):
    global _time_running
    _time_running = not _time_running
    await event.edit("Обновление времени в нике " + ("включено" if _time_running else "выключено"))
    if _time_running:
        asyncio.create_task(update_nick(event.client))

async def update_nick(client):
    global _time_running, _time_timezone
    while _time_running:
        tz = pytz.timezone(_time_timezone)
        current_time = datetime.now(tz).strftime("%H:%M")

        me = await client.get_me()
        current_nick = me.first_name.split("|")[0].strip()
        new_nick = f"{current_nick} | {current_time}"

        try:
            await client(UpdateProfileRequest(first_name=new_nick))
        except Exception as e:
            print(f"Ошибка обновления ника: {e}")

        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_msk'))
async def time_msk_handler(event):
    global _time_timezone
    _time_timezone = 'Europe/Moscow'
    await event.edit("Часовой пояс: Москва")

@client.on(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_ekb'))
async def time_ekb_handler(event):
    global _time_timezone
    _time_timezone = 'Asia/Yekaterinburg'
    await event.edit("Часовой пояс: Екатеринбург")

# Запуск бота
async def main():
    await client.start()
    print("Бот успешно запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
