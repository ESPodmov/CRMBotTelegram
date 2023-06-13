from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils.executor import set_webhook
from config import TOKEN, ACC_ID, CH_ID, SECRET, MONGODB_KEY
import dictionary
from aiohttp import web
import ssl
import requests_helper
import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
import math
from aiogram.types import ContentTypes, InputFile
from aiogram.dispatcher.filters.state import State, StatesGroup
from pymongo import MongoClient
from aiogram_broadcaster import MessageBroadcaster
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_HOST, WEBHOOK_HOST_HOST, WEBHOOK_SSL_CERT, WEBHOOK_SSL_P_KEY


WEBHOOK_PATH = f"/bot"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

API_TOKEN = TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
app = web.Application()
request_helper = requests_helper.RequestHelper(account_id=ACC_ID, channel_id=CH_ID, secret=SECRET,
                                               hook_api_version="v2")


async def handler(request):
    request_json = await request.json()
    user_id = request_json["message"]["receiver"]["client_id"]
    message_text = request_json["message"]["message"]["text"]
    message_type = request_json["message"]["message"]["type"]
    if message_type == "text":
        await bot.send_message(user_id, message_text)
    else:
        message_media = request_json["message"]["message"]["media"]
        message_file_name = request_json["message"]["message"]["file_name"]
        try:
            input_file = InputFile.from_url(message_media, message_file_name)
            if message_type == "picture":
                await bot.send_photo(user_id, photo=input_file, caption=message_text)
            elif message_type == "file":
                if message_file_name[str(message_file_name).rfind(".") + 1:] in video_file_expansions:
                    await bot.send_video(user_id, video=input_file, caption=message_text)
                else:
                    await bot.send_document(user_id, document=input_file, caption=message_text)
            elif message_type == "voice":
                await bot.send_voice(user_id, voice=input_file, caption=message_text)
        except Exception as e:
            print(e.with_traceback(e.__traceback__))
            if message_text is not None and message_text != "":
                await bot.send_message(user_id, message_text)
            await bot.send_message(user_id, msg_dictionary["crm_send_error"] + message_media, parse_mode="HTML")

    return web.Response()


app.router.add_route("post", f'/bot/amocrm/{CH_ID}_{ACC_ID}', handler)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


video_file_expansions = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"]
##########################################################
lists = dictionary.lists
additional_btns_dict = dictionary.additional_btns_dict
msg_dictionary = dictionary.msg_dictionary
services_dict = {}
keyboard_dict = {}
data_dictionary = dictionary.data_dictionary
reply_keyboards_dictionary = dictionary.reply_keyboards
client = MongoClient(MONGODB_KEY)
db = client.telegramcrm
not_available_procedures = dictionary.not_available_procedures


class States(StatesGroup):
    CONVERSATION_STATE = State()
    SEND_MESSAGES = State()


class Saver:
    def __init__(self, first_field):
        self.first_field = first_field
        self.second_field = None
        self.third_field = None


def split_items(parameters: dict, count_of_items: int):
    result = {}
    pages = 1
    key_list = list(parameters.keys())
    while pages <= math.ceil(len(parameters) / count_of_items):
        items_dict = {}
        counter = 0
        while counter < count_of_items and (counter + (pages - 1) * count_of_items) < len(parameters):
            key_num = counter + (pages - 1) * count_of_items
            items_dict[key_list[key_num]] = parameters[key_list[key_num]]
            counter = counter + 1
        result[pages] = items_dict
        pages = pages + 1
    result["current"] = 1
    return result


def create_keyboard_with_controls(keyboard_dictionary: dict, front_marker: str, row_width=1, max_items=2,
                                  dict_key: str = None):
    inline_keyboard = InlineKeyboardMarkup(row_width=row_width)
    additional_btns = additional_btns_dict
    additional_keyboard_width = 3
    items = split_items(keyboard_dictionary, max_items)
    keyboard_dict[int(dict_key)] = items
    for key in items[1]:
        callback_data = front_marker + "_" + str(key)
        curr_btn = InlineKeyboardButton(items[1][str(key)], callback_data=callback_data)
        inline_keyboard.insert(curr_btn)
    if additional_btns is not None:
        btn_array = []
        for key in additional_btns:
            callback_data = front_marker + "_" + str(key)
            curr_btn = InlineKeyboardButton(additional_btns[str(key)], callback_data=callback_data)
            btn_array.append(curr_btn)
            if len(btn_array) == additional_keyboard_width:
                inline_keyboard.inline_keyboard.append(btn_array)
                btn_array = []
    return inline_keyboard


async def edit_previous_or_next(callback: types.CallbackQuery, front_marker: str, is_next: bool = True):
    message = callback.message
    try:
        current_selecting_state = keyboard_dict[callback.from_user.id]
    except KeyError as e:
        print(e.with_traceback(e.__traceback__))
        await callback.message.delete()
        return
    current_state = int(current_selecting_state["current"])
    if is_next:
        if current_state == len(current_selecting_state) - 1:
            current_state = 1
        else:
            current_state = current_state + 1
    else:
        if current_state == 1:
            current_state = len(current_selecting_state) - 1
        else:
            current_state = current_state - 1
    keyboard_dict[callback.from_user.id]["current"] = current_state
    additional_btns = additional_btns_dict
    reply_markup = create_keyboard(keyboard_dict[callback.from_user.id][current_state],
                                   front_marker=front_marker, additional_btns=additional_btns,
                                   additional_keyboard_width=3)
    await message.edit_reply_markup(reply_markup=reply_markup)


def create_keyboard(keyboard_dictionary: dict, front_marker: str, row_width=1, additional_btns=None,
                    additional_keyboard_width=1):
    inline_keyboard = InlineKeyboardMarkup(row_width=row_width)
    for key in keyboard_dictionary:
        callback_data = front_marker + "_" + str(key)
        curr_btn = InlineKeyboardButton(keyboard_dictionary[str(key)], callback_data=callback_data)
        inline_keyboard.insert(curr_btn)
    if additional_btns is not None:
        btn_array = []
        for key in additional_btns:
            callback_data = front_marker + "_" + str(key)
            curr_btn = InlineKeyboardButton(additional_btns[str(key)], callback_data=callback_data)
            btn_array.append(curr_btn)
            if len(btn_array) == additional_keyboard_width:
                inline_keyboard.inline_keyboard.append(btn_array)
                btn_array = []
    return inline_keyboard


async def send_greetings(u_id: int):
    await bot.send_message(u_id, lists["sphere"]["message"],
                           reply_markup=create_keyboard(lists["sphere"]["items"], lists["sphere"]["name"],
                                                        row_width=1))


async def edit_callback_message(callback: types.CallbackQuery, dict_line: str, row_width: int = 1,
                                needs_back: bool = True):
    if needs_back:
        await callback.message.edit_text(lists[dict_line]["message"],
                                         reply_markup=create_keyboard(lists[dict_line]["items"],
                                                                      lists[dict_line]["name"], row_width=row_width,
                                                                      additional_btns=lists["back"]["items"]))
    else:
        await callback.message.edit_text(lists[dict_line]["message"],
                                         reply_markup=create_keyboard(lists[dict_line]["items"],
                                                                      lists[dict_line]["name"], row_width=row_width))


async def beauty_spheres_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "beauty_spheres")


async def permanent_makeup_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "permanent_types", row_width=2)


async def beauty_other_edit_to(callback: types.CallbackQuery):
    # await edit_callback_message(callback, "beauty_other")
    dict_line = "beauty_other"
    reply_markup = create_keyboard_with_controls(lists[dict_line]["items"], lists[dict_line]["name"],
                                                 dict_key=str(callback.from_user.id))
    await callback.message.edit_text(lists[dict_line]["message"], reply_markup=reply_markup)


async def basic_pm_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_basic")


async def update_pm_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_update")


async def correction_pm_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_correction")


async def confirmation_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "confirmation", row_width=2)


async def pm_zone_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_zone", row_width=2)


async def soul_section_edit_to(callback: types.CallbackQuery):
    # await edit_callback_message(callback, "soul_section")
    dict_line = "soul_section"
    reply_markup = create_keyboard_with_controls(lists[dict_line]["items"], lists[dict_line]["name"],
                                                 dict_key=str(callback.from_user.id))
    await callback.message.edit_text(lists[dict_line]["message"], reply_markup=reply_markup)


async def select_worker_edit_to(callback: types.CallbackQuery):
    try:
        dict_line = "workers"
        workers_dictionary = lists[dict_line]["items"]
        front_marker = lists[dict_line]["name"]
        message = lists[dict_line]["message"]
        current_services = services_dict[callback.from_user.id]["service"]

        for key in current_services:
            current_service_element = current_services[key]
            for key_workers in not_available_procedures:
                current_worker_cant = not_available_procedures[key_workers]
                if current_service_element in current_worker_cant:
                    workers_dictionary.pop(key_workers)
        if len(workers_dictionary) <= 1:
            await send_confirmation(u_id=callback.from_user.id)
        else:
            reply_markup = create_keyboard(workers_dictionary, front_marker, additional_btns=lists["back"]["items"])
            await callback.message.edit_text(message, reply_markup=reply_markup)
    except Exception as e:
        print(e.with_traceback(e.__traceback__))
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, msg_dictionary["error"]["confirmation_error"])
        await send_greetings(callback.from_user.id)
        return


async def education_types_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "education_section")


async def pm_education_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_education")


async def pm_basic_education_edit_to(callback: types.CallbackQuery):
    await edit_callback_message(callback, "pm_basic_education")


async def create_reply_keyboard(keyboard_elements: list, row_width: int = 1, needs_resize: bool = True):
    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=needs_resize, row_width=row_width)
    for elem in keyboard_elements:
        current_btn = KeyboardButton(reply_keyboards_dictionary["items"][elem])
        reply_keyboard.insert(current_btn)
    return reply_keyboard


async def send_template(u_id, dict_line, row_width=1, needs_back=True):
    if needs_back:
        await bot.send_message(u_id, lists[dict_line]["message"],
                               reply_markup=create_keyboard(lists[dict_line]["items"], lists[dict_line]["name"],
                                                            row_width=row_width,
                                                            additional_btns=lists["back"]["items"]))
    else:
        await bot.send_message(u_id, lists[dict_line]["message"],
                               reply_markup=create_keyboard(lists[dict_line]["items"], lists[dict_line]["name"],
                                                            row_width=row_width))


async def send_confirmation(u_id):
    await send_template(u_id, "confirmation", row_width=2)


async def turn_on_direct_messaging(u_id, state: FSMContext, needs_reply: bool = False):
    reply = None
    if needs_reply:
        reply = await create_reply_keyboard(reply_keyboards_dictionary["keyboards"]["direct_off"])
    if await state.get_state() != States.CONVERSATION_STATE.state:
        await States.CONVERSATION_STATE.set()
        await turn_on_direct_db(u_id)
        await bot.send_message(u_id, msg_dictionary["direct_on_message"], reply_markup=reply)
    else:
        await bot.send_message(u_id, msg_dictionary["already_direct_on"], reply_markup=reply_keyboards_dictionary)


async def turn_off_direct_messaging(u_id, state: FSMContext, needs_reply: bool = False):
    reply = None
    if needs_reply:
        reply = await create_reply_keyboard(reply_keyboards_dictionary["keyboards"]["direct_on"])
    if await state.get_state() == States.CONVERSATION_STATE.state:
        await state.reset_state()
        await turn_off_direct_db(u_id)
        await bot.send_message(u_id, msg_dictionary["direct_off_message"], reply_markup=reply)
    else:
        await bot.send_message(u_id, msg_dictionary["already_direct_off"], reply_markup=reply)


async def send_help_message(u_id):
    if not check_if_admin(u_id):
        await bot.send_message(u_id, msg_dictionary["help"], parse_mode="HTML")
    else:
        await bot.send_message(u_id, msg_dictionary["help"] + msg_dictionary["help_for_admin"], parse_mode="HTML")


async def delete_reply(u_id):
    await bot.send_message(u_id, msg_dictionary["delete_reply"], reply_markup=ReplyKeyboardRemove())


def check_user_exists(u_id):
    admin = False
    for elem in db.users.find({}):
        if u_id == elem["user_id"]:
            admin = True
    return admin


def check_if_admin(u_id):
    admin = False
    for elem in db.control.find({}):
        if u_id == elem["user_id"]:
            admin = True
    return admin


async def direct_is_on(u_id):
    return db.users.find({"user_id": u_id}).limit(1)[0]["direct"]


async def turn_on_direct_db(u_id):
    db.users.update_one({"user_id": u_id}, {"$set": {"direct": True}})


async def turn_off_direct_db(u_id):
    db.users.update_one({"user_id": u_id}, {"$set": {"direct": False}})


@dp.message_handler(commands=["start"], state="*")
async def start_handler(message: types.Message):
    if not check_user_exists(message.from_user.id):
        db.users.insert_one({"user_id": message.from_user.id, "direct": False})
    await bot.send_message(message.from_user.id, msg_dictionary["start_message"])
    await send_greetings(message.from_user.id)


@dp.message_handler(commands=["sign_up"], state="*")
async def sign_up_handler(message: types.Message):
    await send_greetings(message.from_user.id)


@dp.message_handler(commands=["direct_on"], state="*")
async def direct_on_handler(message: types.Message, state: FSMContext):
    await turn_on_direct_messaging(message.from_user.id, state)


@dp.message_handler(commands=["direct_off"], state="*")
async def direct_off_handler(message: types.Message, state: FSMContext):
    await turn_off_direct_messaging(message.from_user.id, state)


@dp.message_handler(commands=["help"], state="*")
async def help_handler(message: types.Message):
    await send_help_message(message.from_user.id)


@dp.message_handler(commands=["remove_keyboard"], state="*")
async def remove_reply_keyboard_handler(message: types.Message):
    await delete_reply(u_id=message.from_user.id)


@dp.message_handler(commands=["send_message_to_users"], state="*")
async def send_message_to_users_handler(message: types.Message):
    if check_if_admin(message.from_user.id):
        await message.reply(msg_dictionary["send_message_to_users"])
        await States.SEND_MESSAGES.set()
    else:
        await message.reply(msg_dictionary["unknown_command"])


@dp.message_handler(state=States.SEND_MESSAGES, content_types=ContentTypes.ANY)
async def start_sending_message_handler(message: types.Message, state: FSMContext):
    if message.text != "stop":
        await state.reset_state()
        users = db.users.find({})
        users_id = []
        for item in users:
            users_id.append(item["user_id"])
        await MessageBroadcaster(users_id, message).run()
    else:
        await state.reset_state()
        await message.reply("Операция отменена")


@dp.callback_query_handler(lambda c: c.data.startswith(lists["sphere"]["name"]), state="*")
async def service_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["sphere"]["name"], "")[1:]
    if data == "beauty_btn":
        await beauty_spheres_edit_to(callback)
    if data == "soul_btn":
        await soul_section_edit_to(callback)
    if data == "education_btn":
        await education_types_edit_to(callback)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["beauty_spheres"]["name"]), state="*")
async def beauty_spheres_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["beauty_spheres"]["name"], "")[1:]
    if data == "permanent_makeup":
        await permanent_makeup_edit_to(callback)
    if data == "other":
        await beauty_other_edit_to(callback)
    if data == "back":
        await callback.message.delete()
        await send_greetings(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["permanent_types"]["name"]), state="*")
async def permanent_types_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["permanent_types"]["name"], "")[1:]
    if data == "back":
        await beauty_spheres_edit_to(callback)
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}}
        await pm_zone_edit_to(callback)


# @dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_basic"]["name"]))
# async def pm_update_callback_handler(callback: types.CallbackQuery):
#     print(callback.data)
#     data = callback.data.replace(lists["pm_basic"]["name"], "")[1:]
#     print(data)
#     if "back" in data:
#         await permanent_makeup_edit_to(callback)
#     else:
#         service_name = dictionary["pm_basic"] + " " + dictionary[data]  # надо переделать чтобы аккуратно все было
#         services_dict[callback.from_user.id] = {"service": service_name, "worker": dictionary[data],
#                                                 "last": basic_pm_edit_to}
#         await callback.message.delete()
#         await send_confirmation(callback.from_user.id)
#
#
# @dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_update"]["name"]))
# async def pm_update_callback_handler(callback: types.CallbackQuery):
#     data = callback.data.replace(lists["pm_update"]["name"], "")[1:]
#     if "back" in data:
#         await permanent_makeup_edit_to(callback)
#     else:
#         service_name = dictionary["pm_update"] + " " + dictionary[data]
#         services_dict[callback.from_user.id] = {"line": service_name, "last": update_pm_edit_to}
#         await callback.message.delete()
#         await send_confirmation(callback.from_user.id)
#
#
# @dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_correction"]["name"]))
# async def pm_update_callback_handler(callback: types.CallbackQuery):
#     data = callback.data.replace(lists["pm_correction"]["name"], "")[1:]
#     if "back" in data:
#         await permanent_makeup_edit_to(callback)
#     else:
#         service_name = dictionary["pm_correction"] + " " + dictionary[data]
#         services_dict[callback.from_user.id] = {"line": service_name, "last": correction_pm_edit_to}
#         await callback.message.delete()
#         await send_confirmation(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_zone"]["name"]), state="*")
async def pm_zone_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["pm_zone"]["name"], "")[1:]
    if data == "back":
        await permanent_makeup_edit_to(callback)
    else:
        services_dict[callback.from_user.id]["service"]["second"] = data
        services_dict[callback.from_user.id]["last"] = pm_zone_edit_to
        await select_worker_edit_to(callback)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["confirmation"]["name"]), state="*")
async def confirmation_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.replace(lists["confirmation"]["name"], "")[1:]
    if data == "back":
        try:
            await services_dict[callback.from_user.id]["last"](callback)
        except Exception as e:
            print(e)
            await callback.message.delete()
            await send_greetings(callback.from_user.id)
            return
    elif data == "refuse":
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, msg_dictionary["refuse_answer"])
    elif data == "confirm":
        try:
            service_line = ""
            current_user_dict = services_dict[callback.from_user.id]["service"]
            for key in current_user_dict:
                service_line += data_dictionary[current_user_dict[key]] + " "
            service_line = "Новая заявка: " + service_line
        except Exception as e:
            print(e)
            await callback.message.delete()
            await bot.send_message(callback.from_user.id, msg_dictionary["error"]["confirmation_error"])
            await send_greetings(callback.from_user.id)
            return

        await send_message_to_crm(callback.from_user, callback.message.message_id, callback.message.chat.id,
                                  service_line)
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, msg_dictionary["confirmation_answer"])
        await turn_on_direct_messaging(callback.from_user.id, state=state, needs_reply=True)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["beauty_other"]["name"]), state="*")
async def beauty_other_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["beauty_other"]["name"], "")[1:]
    if data == "back":
        await beauty_spheres_edit_to(callback)
    elif data == "<<":
        await edit_previous_or_next(callback, lists["beauty_other"]["name"], is_next=False)
    elif data == ">>":
        await edit_previous_or_next(callback, lists["beauty_other"]["name"])
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}, "last": beauty_other_edit_to}
        await select_worker_edit_to(callback)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["workers"]["name"]), state="*")
async def workers_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["workers"]["name"], "")[1:]
    if data == "back":
        try:
            await services_dict[callback.from_user.id]["last"](callback)
        except Exception as e:
            print(e)
            await callback.message.delete()
            await send_greetings(callback.from_user.id)
            return
    else:
        services_dict[callback.from_user.id]["service"]["worker"] = data
        await callback.message.delete()
        await send_confirmation(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["soul_section"]["name"]), state="*")
async def soul_section_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["soul_section"]["name"], "")[1:]
    if data == "back":
        await callback.message.delete()
        await send_greetings(callback.from_user.id)
    elif data == "<<":
        await edit_previous_or_next(callback, lists["soul_section"]["name"], is_next=False)
    elif data == ">>":
        await edit_previous_or_next(callback, lists["soul_section"]["name"])
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}, "last": soul_section_edit_to}
        await callback.message.delete()
        await send_confirmation(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["education_section"]["name"]), state="*")
async def education_section_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["education_section"]["name"], "")[1:]
    if data == "back":
        await callback.message.delete()
        await send_greetings(callback.from_user.id)
    elif data == "permanent_makeup_education":
        await pm_education_edit_to(callback)
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}, "last": education_types_edit_to}
        await callback.message.delete()
        await send_confirmation(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_education"]["name"]), state="*")
async def pm_education_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["pm_education"]["name"], "")[1:]
    if data == "back":
        await education_types_edit_to(callback)
    elif data == "basic_training_from_scratch":
        await pm_basic_education_edit_to(callback)
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}, "last": pm_education_edit_to}
        await callback.message.delete()
        await send_confirmation(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(lists["pm_basic_education"]["name"]), state="*")
async def pm_basic_education_callback_handler(callback: types.CallbackQuery):
    data = callback.data.replace(lists["pm_basic_education"]["name"], "")[1:]
    if data == "back":
        await pm_education_edit_to(callback)
    else:
        services_dict[callback.from_user.id] = {"service": {"first": data}, "last": pm_basic_education_edit_to}
        await callback.message.delete()
        await send_confirmation(callback.from_user.id)


async def collect_user_data(user: types.User):
    user = user
    photos = await bot.get_user_profile_photos(user.id)
    avatar_url = ""
    if "photos" in photos:
        avatar_id = photos["photos"][0][0]["file_id"]
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile", params={"file_id": avatar_id})
        avatar_url = f"https://api.telegram.org/file/bot{TOKEN}/" + response.json()["result"]["file_path"]
    first_name = str(user.first_name)
    last_name = str(user.last_name)
    username = str(user.username)
    if first_name == "None" and last_name == "None":
        user_name = username
    else:
        user_name = ""
        if first_name != "None":
            user_name = first_name
        if last_name != "None":
            if len(user_name) != 0:
                user_name += " " + last_name
            else:
                user_name = last_name
    user_url = "https://t.me/" + username
    return avatar_url, user_name, user_url


async def send_message_to_crm(user: types.User, msg_id, chat_id, text_message="", file=None,
                              message_type="text"):
    user = user
    avatar_url, user_name, user_url = await collect_user_data(user)
    if message_type == "text":
        request_helper.send_message(msg_id=str(msg_id), conversation_id=str(chat_id),
                                    user_id=str(user.id), user_name=user_name, text=text_message,
                                    profile_link=user_url, user_avatar=avatar_url)
    else:
        file_id = file.file_id
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile", params={"file_id": file_id})
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/" + response.json()["result"]["file_path"]
        file_name = response.json()["result"]["file_path"]
        file_name = file_name[file_name.index("/") + 1:]
        file_size = int(file.file_size)
        request_helper.send_message(msg_id=str(msg_id), conversation_id=str(chat_id),
                                    user_id=str(user.id), user_name=user_name, text=text_message,
                                    profile_link=user_url, user_avatar=avatar_url, media_link=file_url,
                                    file_name=file_name, file_size=file_size, message_type=message_type)


@dp.message_handler(content_types=ContentTypes.ANY, state=States.CONVERSATION_STATE)
async def echo_handler(message: types.Message, state: FSMContext):
    # await bot.send_message(message.from_user.id, message.text)
    # print(message.photo)
    # print(message.document.file_id)
    if message.document:
        await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.caption,
                                  message.document, message_type="file")
    elif message.photo:
        await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.caption,
                                  message.photo[-1], message_type="picture")
    elif message.video:
        await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.caption,
                                  message.video, message_type="video")
    elif message.video_note:
        await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.caption,
                                  message.video_note, message_type="file")
    elif message.voice:
        await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.caption,
                                  message.voice, message_type="voice")
    elif message.text:
        text = message.text
        if text == reply_keyboards_dictionary["items"]["direct_on"]:
            await turn_on_direct_messaging(message.from_user.id, state, needs_reply=True)
        elif text == reply_keyboards_dictionary["items"]["direct_off"]:
            await turn_off_direct_messaging(message.from_user.id, state, needs_reply=True)
        else:
            if text[0] != "/":
                await send_message_to_crm(message.from_user, message.message_id, message.chat.id, message.text)
            else:
                await bot.send_message(message.from_user.id, msg_dictionary["unknown_command"])
    else:
        await bot.send_message(message.from_user.id, msg_dictionary["dunno"])


@dp.message_handler(content_types=ContentTypes.ANY)
async def simple_handler(message: types.Message, state: FSMContext):
    if await direct_is_on(message.from_user.id):
        await States.CONVERSATION_STATE.set()
        await echo_handler(message, state)
    else:
        if message.text:
            text = message.text
            if text[0] == "/":
                await bot.send_message(message.from_user.id, msg_dictionary["unknown_command"])
            else:
                await bot.send_message(message.from_user.id, msg_dictionary["to_on_direct"])
        else:
            await bot.send_message(message.from_user.id, msg_dictionary["to_on_direct"])


if __name__ == "__main__":
    executor = set_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        web_app=app
    )
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_verify_locations("./encryption/ca_bundle.pem")
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_P_KEY)
    web_app = executor.web_app
    web.run_app(web_app,
                host=WEBHOOK_LISTEN,
                port=443,
                ssl_context=context
                )
