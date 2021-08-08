from telebot import TeleBot
import constants
from data_warehouse_interface import DataWarehouseInterface
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


remember_places_bot = TeleBot(token=constants.TOKEN)
data_warehouse_interface = DataWarehouseInterface()
data_warehouse_interface.connect_to_database()


@remember_places_bot.message_handler(commands=['start'],
                                     func=lambda message:
                                     not data_warehouse_interface.does_user_exist(user_id=message.chat.id))
def start(message):
    data_warehouse_interface.add_user(user_id=message.chat.id)
    remember_places_bot.send_message(chat_id=message.chat.id, text='Hello')


@remember_places_bot.message_handler(commands=['add_place'],
                                     func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.NEUTRAL)
def add_place(message):
    data_warehouse_interface.add_place(user_id=message.chat.id)
    data_warehouse_interface.update_step(user_id=message.chat.id, step=constants.NAME)
    remember_places_bot.send_message(chat_id=message.chat.id, text='Specify the name')


@remember_places_bot.message_handler(func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.NAME,
                                     content_types=['text'])
def add_name(message):
    data_warehouse_interface.update_name(user_id=message.chat.id, name=message.text)
    data_warehouse_interface.update_step(user_id=message.chat.id, step=constants.LOCATION)
    remember_places_bot.send_message(chat_id=message.chat.id, text='Specify the location')


@remember_places_bot.message_handler(func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.LOCATION,
                                     content_types=['location'])
def add_location(message):
    data_warehouse_interface.update_location(user_id=message.chat.id, latitude=message.location.latitude,
                                             longitude=message.location.longitude)
    data_warehouse_interface.update_step(user_id=message.chat.id, step=constants.PHOTO)
    remember_places_bot.send_message(chat_id=message.chat.id, text='Attach a photo')


@remember_places_bot.message_handler(func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.PHOTO,
                                     content_types=['photo'])
def add_photo(message):
    photo_path = remember_places_bot.get_file(file_id=message.photo[-1].file_id).file_path
    photo_content = requests.get(url=f'http://api.telegram.org/file/bot{constants.TOKEN}/{photo_path}').content
    data_warehouse_interface.update_photo(user_id=message.chat.id, photo_content=photo_content)
    data_warehouse_interface.update_step(user_id=message.chat.id, step=constants.NEUTRAL)
    remember_places_bot.send_message(chat_id=message.chat.id, text='The place was successfully remembered')


@remember_places_bot.message_handler(commands=['show_all_places'],
                                     func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.NEUTRAL)
def show_all_places(message):
    inline_keyboard_markup = InlineKeyboardMarkup(row_width=1)
    all_places = [(place[2], place[0]) for place in data_warehouse_interface.get_all_places(user_id=message.chat.id)]
    inline_keyboard_buttons = [InlineKeyboardButton(text=name, callback_data=f'show_place {place_id}')
                               for name, place_id in all_places]
    inline_keyboard_markup.add(*inline_keyboard_buttons)
    remember_places_bot.send_message(chat_id=message.chat.id, text='All places:', reply_markup=inline_keyboard_markup)


@remember_places_bot.callback_query_handler(func=lambda callback_query:
                                            data_warehouse_interface.get_step(user_id=callback_query.message.chat.id) ==
                                            constants.NEUTRAL
                                            and
                                            callback_query.data.split()[0] ==
                                            'show_place')
def show_place(callback_query):
    place = data_warehouse_interface.get_place(place_id=int(callback_query.data.split()[1]))
    remember_places_bot.send_message(chat_id=callback_query.message.chat.id, text=place[2])
    remember_places_bot.send_location(chat_id=callback_query.message.chat.id, latitude=place[3], longitude=place[4])
    with open(file=place[5], mode='rb') as photo_file:
        remember_places_bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo_file)


@remember_places_bot.message_handler(commands=['delete_all_places'],
                                     func=lambda message:
                                     data_warehouse_interface.get_step(user_id=message.chat.id) ==
                                     constants.NEUTRAL)
def delete_all_places(message):
    inline_keyboard_markup = InlineKeyboardMarkup(row_width=2)
    inline_keyboard_buttons = [InlineKeyboardButton(text=is_confirmed, callback_data=callback_data)
                               for is_confirmed, callback_data in
                               [('Yes', 'delete_all_places Yes'), ('No', 'delete_all_places No')]]
    inline_keyboard_markup.add(*inline_keyboard_buttons)
    remember_places_bot.send_message(chat_id=message.chat.id, text='Are you sure?', reply_markup=inline_keyboard_markup)


@remember_places_bot.callback_query_handler(func=lambda callback_query:
                                            data_warehouse_interface.get_step(user_id=callback_query.message.chat.id) ==
                                            constants.NEUTRAL
                                            and
                                            callback_query.data.split()[0] ==
                                            'delete_all_places')
def delete_all_places(callback_query):
    if callback_query.data.split()[1] == 'Yes':
        data_warehouse_interface.delete_all_places(user_id=callback_query.message.chat.id)
        remember_places_bot.send_message(chat_id=callback_query.message.chat.id,
                                         text='All places were successfully deleted')
    else:
        remember_places_bot.send_message(chat_id=callback_query.message.chat.id,
                                         text='The request to delete all places has been canceled')


remember_places_bot.polling()
