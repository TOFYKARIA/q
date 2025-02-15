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

# Команда для loliart
@loader.tds
class loliArt(loader.Module):
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
        
        await utils.answer(message, self.strings("loading_photo"))
        
        async with self._client.conversation("@AnimeLoliChan_bot") as conv:
            await conv.send_message("/lol")
        
            otvet = await conv.get_response()
          
            if otvet.photo:
                phota = await self._client.download_media(otvet.photo, "loli_hentai")
                await message.client.send_message(
                    message.peer_id,
                    file=phota,
                    reply_to=getattr(message, "reply_to_msg_id", None),
                    )

                os.remove(phota)
                
                await message.delete()

# Команда для loli hentai
@loader.tds
class lolihentai(loader.Module):
    """Your the best friend in loli hentai"""

    strings = {
        "name": "LoliHentai",
        "loading_photo": "<emoji document_id=5215327832040811010>⏳</emoji> <b>loading your loli photo...</b>",
        "error_loading": "<b>Failed to get photos. Please unblock @ferganteusbot</b>",
        "search": "<emoji document_id=5328311576736833844>🔴</emoji> loading your photo..."
    }

    strings_ru = {
        "name": "LoliHentai",
        "loading_photo": "<emoji document_id=5215327832040811010>⏳</emoji> <b>загрузка вашей лоли фотографии...</b>",
        "error_loading": "<b>Не удалось получить фотографии. Пожалуйста, разблокируйте @ferganteusbot</b>",
        "search": "<emoji document_id=5328311576736833844>🔴</emoji> загрузка вашей фотографии..."
    }
    
    async def lolicmd(self, message):
        """-> random loli photo"""

        # Проверяем, разблокирована ли команда для пользователя
        if message.sender_id not in unlocked_commands or not unlocked_commands[message.sender_id]:
            await message.reply("Команда не разблокирована! Введите /secret [пароль] для доступа.")
            return
        
        await utils.answer(message, self.strings("loading_photo"))
        
        async with self._client.conversation("@ferganteusbot") as conv:
            try: 
                lh = await conv.send_message("/lh")
            except Exception as e:
                return await utils.answer(message, self.strings("error_loading"))
        
            otvet = await conv.get_response()
            await lh.delete()
            if otvet.photo:
                await message.client.send_message(
                    message.peer_id,
                    message=otvet,
                    reply_to=getattr(message, "reply_to_msg_id", None))
                await otvet.delete()
                await message.delete()

# Команда для ввода пароля и разблокировки команд
@events.register(events.NewMessage(pattern='/secret'))
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
@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]help'))
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

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]anime'))
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

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]im'))
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

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]imstop'))
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

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]time'))
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

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_msk'))
async def time_msk_handler(event):
    """Переключить время на МСК"""
    global _time_timezone
    _time_timezone = 'Europe/Moscow'
    await event.edit("Время в нике будет отображаться по МСК")

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_ekb'))
async def time_ekb_handler(event):
    """Переключить время на ЕКБ"""
    global _time_timezone
    _time_timezone = 'Asia/Yekaterinburg'
    await event.edit("Время в нике будет отображаться по ЕКБ")

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_omsk'))
async def time_omsk_handler(event):
    """Переключить время на Омск"""
    global _time_timezone
    _time_timezone = 'Asia/Omsk'
    await event.edit("Время в нике будет отображаться по Омску")

@events.register(events.NewMessage(pattern=f'[{"".join(prefixes)}]time_samara'))
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
    client = await setup_client()

    handlers = [
        secret_handler,  # Обработчик команды /secret
        loliArt.loliartcmd,  # Обработчик команды .loliart
        lolihentai.lolicmd,  # Обработчик команды .loli
        help_handler,
        anime_handler,
        im_handler,
        imstop_handler,
        time_handler,
        time_msk_handler,
        time_ekb_handler,
        time_omsk_handler,
        time_samara_handler
    ]

    for handler in handlers:
        client.add_event_handler(handler)

    print("Бот запускается...")
    await client.start()

    print("Бот успешно запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
