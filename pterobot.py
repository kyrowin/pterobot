import aiohttp
import os  
from dotenv import load_dotenv  
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.exceptions import Unauthorized
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
env_errors = ""
BOT_TOKEN = os.getenv('BOT_TOKEN')
PTERODACTYL_URL = os.getenv('PTERODACTYL_URL')
PTERODACTYL_API_KEY = os.getenv('PTERODACTYL_API_KEY')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
headers = {
    'Authorization': f'Bearer {PTERODACTYL_API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'Application/vnd.pterodactyl.v1+json'
}
if PTERODACTYL_URL == 'https://pterodactyl.example.com':
    env_errors +="\nПроблема: стандартный PTERODACTYL_URL в .env"
if PTERODACTYL_API_KEY == 'ptlc_AAAAAAAAAAAAAAAAAAAAAAAAAAAA':
    env_errors +="\nПроблема: стандартный PTERODACTYL_API_KEY в .env"
if env_errors == "":
    pass
else:
    env_errors +="\n(Решите проблемы, иначе вы не сможете продолжить)"

async def api_request(method, endpoint, json=None):
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method,
            f'{PTERODACTYL_URL}/api/client/{endpoint}',
            headers=headers,
            json=json
        ) as response:
            if response.status == 204:
                return True
            return await response.json()
async def get_servers():
    return await api_request('GET', '')
async def get_server_status(server_id):
    return await api_request('GET', f'servers/{server_id}/resources')
async def get_server_details(server_id):
    return await api_request('GET', f'servers/{server_id}')
async def power_action(server_id, action):
    return await api_request('POST', f'servers/{server_id}/power', {'signal': action})

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🖥 Мои серверы", callback_data="list_servers"))
    await message.answer(f"👋 Добро пожаловать в панель управления серверами pterodactyl!\n{env_errors}", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "list_servers")
async def list_servers(callback_query: types.CallbackQuery):
    servers_data = await get_servers()
    servers_list = "📋 Список серверов:\n\n"
    keyboard = InlineKeyboardMarkup(row_width=1)
    for server in servers_data['data']:
        attrs = server['attributes']
        server_id = attrs['identifier']
        status_data = await get_server_status(server_id)
        current_state = status_data['attributes']['current_state']
        state_emoji = {
            'running': '🟢',
            'starting': '🟡',
            'stopping': '🟡',
            'offline': '⚫'
        }.get(current_state, '⚪')
        servers_list += f"{state_emoji} {attrs['name']} | {current_state.upper()}\n\n"

        keyboard.add(InlineKeyboardButton(
            f"⚙️ Управление {attrs['name']}", 
            callback_data=f"server_{server_id}"
        ))
    
    keyboard.add(InlineKeyboardButton("🔄 Обновить", callback_data="list_servers"))
    try:
        await callback_query.message.edit_text(servers_list, reply_markup=keyboard)
        await callback_query.answer()
    except:
        await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('server_'))
async def server_menu(callback_query: types.CallbackQuery):
    server_id = callback_query.data.split('_')[1]
    server_data = await get_server_details(server_id)
    status_data = await get_server_status(server_id)
    
    if 'attributes' in server_data and 'attributes' in status_data:
        attrs = server_data['attributes']
        status_attrs = status_data['attributes']
        current_ram = status_attrs['resources']['memory_bytes'] / 1024 / 1024
        max_ram = attrs['limits']['memory']
        current_disk = status_attrs['resources']['disk_bytes'] / 1024 / 1024
        max_disk = attrs['limits']['disk']
        ip = attrs['relationships']['allocations']['data'][0]['attributes']['ip_alias']
        port = attrs['relationships']['allocations']['data'][0]['attributes']['port']
        current_cpu = status_attrs['resources']['cpu_absolute']
        max_cpu = attrs['limits']['cpu']
        current_state = status_attrs['current_state']
        state_emoji = {
            'running': '🟢',
            'starting': '🟡',
            'stopping': '🟡',
            'offline': '⚫'
        }.get(current_state, '⚪')
        iof max_disk == 0:
            max_disk = "неограничено "
        if ip == None:
            ip = attrs['relationships']['allocations']['data'][0]['attributes']['ip']
        server_info = f"""
⚙️ Сервер: {attrs['name']}
Статус: {state_emoji} {current_state.upper()}

📊 Статистика:
CPU: {current_cpu:.1f}%/{max_cpu}%
RAM: {current_ram:.1f}MB/{max_ram}MB
Диск: {current_disk:.1f}MB/{max_disk}MB

🌐 IP: {ip}:{port}
"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("▶️ Запуск", callback_data=f"power_{server_id}_start"),
            InlineKeyboardButton("⏹ Стоп", callback_data=f"power_{server_id}_stop"),
            InlineKeyboardButton("🔄 Рестарт", callback_data=f"power_{server_id}_restart"),
            InlineKeyboardButton("🔄 Обновить", callback_data=f"server_{server_id}"),
            InlineKeyboardButton("⬅️ Назад", callback_data="list_servers")
        )
        try:
            await callback_query.message.edit_text(server_info, reply_markup=keyboard)
        except:
            pass
    else:
        await callback_query.answer("Ошибка получения данных сервера", show_alert=True)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('power_'))
async def handle_power_action(callback_query: types.CallbackQuery):
    _, server_id, action = callback_query.data.split('_')
    action_text = {
        'start': 'запуск',
        'stop': 'остановка',
        'restart': 'перезапуск'
    }
    await callback_query.answer(f"Выполняется {action_text[action]}...")
    success = await power_action(server_id, action)
    if success:
        await server_menu(callback_query)
    else:
        await callback_query.answer("Ошибка выполнения команды", show_alert=True)

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Unauthorized:
        print("Произошла ошибка запуска бота. Проверьте что вы правильно выставили BOT_TOKEN в .env (предварительно переименовав .env.example в .env)")