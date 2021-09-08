from config_paths import get_paths
from you_su_aiogram_bot import bot, dp
from classes import Person
from config import ADMIN_ID, Parser_folder_name, Buffer_folder_name

from aiogram import types
from aiogram.types import Message
import os
import logging
import re
# print(sys.path)
from _parser.parser import Parser
from _translator.translator import FileTranslator

Parser_folder_path = get_paths(["data"])[0] + "\\" + Parser_folder_name
Pars = Parser(download_path=Parser_folder_path)
Trans = FileTranslator(subs_folder_path=Parser_folder_path)

# os.chdir(sys.path[0])

logging.basicConfig(level=logging.INFO)

pers_set = set()


async def say_to_admin(dp):
    await bot.send_message(chat_id=ADMIN_ID, text='Bot has started!')


@dp.message_handler(lambda msg: msg.text[0] != '/')
async def resender(message: Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        if "youtu.be" in message.text:
            youtube_regexp = re.compile(r"youtu.be/[a-zA-Z0-9-_]{11}")
        else:
            youtube_regexp = re.compile(r'(youtube\.com\S{6}\?\S*v=[a-zA-Z0-9-_]{11})(&|$)')

        if re.search(youtube_regexp, message.text) is None:
            await bot.send_message(chat_id=message.from_user.id, text='invalid youtube link')
            print(message.text)
        else:
            print('test1')
            await work_type1_manager(message.text, message)
            print('test1_')

    else:
        await bot.send_message(chat_id=message.from_user.id, text='ghjsfg')


@dp.message_handler(commands=['start'])
async def starter(message: Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'welcome to the chat with this bot mr/mrs {message.from_user.first_name}\n\
        commands:(\'/ls_words\' - give you your last parsed words in special message; )\n\
        special message using: \nclick the buttons (1,2,...) to point word in same row as number on the button like known(than word will dissappear from this message and will add to  your own dict of known words);\n\
            click the buttons (\'<-\', \'->\') to navigate with words in message;\n\
            click the button (\'send file with recent words\') to download unknown words(words that this message contains) as .txt file;\n\
            click the button (\'cross with known words\') to remove words that you pointed as known in previous editig of special message(those words were added to your own dictionary of known words)\n\
            P.S.: the button (\'cross with known words\') is required with words from dictionary of known words, so this button will be unavaible until you fill up your dictionary with words and use command (\'/ls_words\')')


@dp.message_handler(commands=['help'])
async def helper(message: Message):
    await message.answer(text='this module has been not ready for now')


@dp.message_handler(commands=['ls_words'])
async def words_manager(message: Message, file_name: str = None):
    if os.path.exists(Parser_folder_path):
        pers_id = message.from_user.id
        print(f'pers_id:{pers_id}, command:\'/ls_words\'''')
        file_names = os.listdir(Parser_folder_path)
        print(f'file_names:{file_names}')
        '''required_file_names = list(filter(lambda x: x.strip('.txt')[x.rindex('_#id_') + 5:] ==  str(pers_id), 
        file_names))'''
        required_file_names = [i for i in file_names if str(pers_id) in i]
        print(f'required_file_names:{required_file_names}')
        if len(required_file_names) == 0:
            await bot.send_message(chat_id=pers_id,
                                   text='There are not files for you\nYou don\'t parse something or your parse/translate request in proccess')
        else:  # бред
            if len(required_file_names) >= 2:
                await clear_parser_garbage()
            # бред
            if file_name is None:
                file_name = required_file_names[0]

            with open(Parser_folder_path + '\\' + file_name, 'r', encoding='utf-8') as f:
                row_str = f.read()
                words_strs = row_str[:-1].split('\n') if row_str[-1] == '\n' else row_str.split('\n')
            #
            rows_numb = 15
            #

            if pers_id not in pers_set:
                person = Person(id=pers_id,
                                first_visible_str_idx=0,
                                visible_strs_numb=rows_numb)
                pers_set.add(person)
            else:
                person = await find_pers_by_id(pers_id, pers_set)

            person.save_words(words_strs)

            await show_words(person, 'ls_words')


async def clear_parser_garbage():
    pass


async def work_type1_manager(link: str, msg: Message):
    '''
    function gives parser and translator required arguments
    and manage results that these functions give back 
    '''
    Pars.parse(msg.from_user.id, video_link=link)

    (subs_folder_path, trans_file_name) = Trans.trans_file(
        subs_file_name=Pars.file_name_pattern + str(msg.from_user.id) + '.txt')
    assert subs_folder_path == Pars.download_path
    await words_manager(msg, trans_file_name)


@dp.callback_query_handler(lambda x: x.data.startswith('manage_vis_text_butt') and x.data)
async def visible_text_manager(callback_query: types.CallbackQuery):
    pers_id = callback_query.from_user.id
    msg_id = callback_query.message.message_id
    person = await find_pers_by_id(pers_id, pers_set)
    butt_token = callback_query.data.replace('manage_vis_text_butt', '')
    msg_strs_numb = (callback_query.message.text + '\n').count('\n')
    # print(butt_token)
    if person and butt_token in [str(i) for i in range(1, msg_strs_numb + 1)]:
        print(f'pers_id:{pers_id}, button:\'(1,2,...)\'''')
        butt_numb = int(butt_token)
        person.replace_word_to_known(person.first_visible_str_idx + butt_numb - 1)
        # print(person.first_visible_str_idx)
        # print(len(person.words_strs))
        if len(person.words_strs) != 0:

            words_strs = person.get_visible_strs()

            (output_str, main_keyboard) = await prepare_msg_type1(words_strs)
            await bot.answer_callback_query(callback_query_id=callback_query.id)
            await bot.edit_message_text(chat_id=pers_id, text=output_str,
                                        reply_markup=main_keyboard, message_id=msg_id)
        else:
            await bot.edit_message_text(chat_id=pers_id, text='You ran out of words',
                                        message_id=msg_id)

    elif person and '_move_' in butt_token:
        print(f'pers_id:{pers_id}, button:\'(<- or ->)\'')
        if len(person.words_strs) != 0:
            move_token = -1 if 'left' in butt_token else 1
            old_one = person.first_visible_str_idx
            person.change_first_visible_str_idx(person.first_visible_str_idx + person.visible_strs_numb * move_token)
            if old_one != person.first_visible_str_idx:
                words_strs = person.get_visible_strs()
                (output_str, main_keyboard) = await prepare_msg_type1(words_strs)
                await bot.answer_callback_query(callback_query_id=callback_query.id)
                await bot.edit_message_text(chat_id=pers_id, text=output_str,
                                            reply_markup=main_keyboard, message_id=msg_id)

    elif person and '_send_words' in butt_token:
        print(f'pers_id:{pers_id}, button:\'(send_words)\'')
        if not os.path.exists(Buffer_folder_name):
            os.mkdir(Buffer_folder_name)
        file_str = await prepare_output_str(person.words_strs, 'for_file')
        # /////////////////////////////////////////////////////////////////////
        old_file_name = f'buffer_file_pers_id_{pers_id}.txt'
        file_path = Buffer_folder_name + '\\' + old_file_name
        new_file_name = 'words.txt'
        new_file_path = Buffer_folder_name + '\\' + new_file_name

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_str)

        os.rename(file_path, new_file_path)
        print('rename success')

        with open(new_file_path, 'rb') as f:
            await bot.answer_callback_query(callback_query_id=callback_query.id)
            await bot.send_document(chat_id=pers_id, document=f)

        os.remove(new_file_path)
        '''
        with tempfile.NamedTemporaryFile(mode='a+') as f:
            f.name=f.name[0:f.name.rindex('\\') + 1] + 'your_secret_own_txt_file.txt'
            f.write(file_str)
            with open(f.name, 'rb') as g:

                await bot.answer_callback_query(callback_query_id=callback_query.id)
                await bot.send_document(chat_id=pers_id, document=g)
        '''

    elif person and '_cross_known' in butt_token:
        print(f'pers_id:{pers_id}, button:\'(_cross_known)\'')
        person.cut_off_with_known_words()
        words_strs = person.get_visible_strs()
        (output_str, main_keyboard) = await prepare_msg_type1(words_strs)
        await bot.answer_callback_query(callback_query_id=callback_query.id)
        await bot.edit_message_text(chat_id=pers_id, text=output_str,
                                    reply_markup=main_keyboard, message_id=msg_id)


# function is confident at fact that person exist in pers_set
async def find_pers_by_id(pers_id, pers_set):
    try:
        return list(filter(lambda x: pers_id == x, pers_set))[0]
    except Exception as e:
        print('Error in you_su_aiorgam_bot_handlers.find_pers_by_id', e)
        return None


async def show_words(person, call_token):
    words_strs = person.get_visible_strs()
    (output_str, main_keyboard) = await prepare_msg_type1(words_strs)
    if call_token == 'ls_words' and len(person.known_words_strs) > 0:
        button = types.InlineKeyboardButton(text='cross with known words',
                                            callback_data='manage_vis_text_butt_cross_known')
        main_keyboard.row(button)

    await bot.send_message(chat_id=person.id, text=output_str,
                           reply_markup=main_keyboard)


async def prepare_msg_type1(words_strs):
    output_str = await prepare_output_str(words_strs, 'for_message')
    #
    main_keyboard = types.InlineKeyboardMarkup(row_width=6)
    #
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data='manage_vis_text_butt' + str(i))
               for i in range(1, len(words_strs) + 1)]
    main_keyboard.add(*buttons)
    manage_butts = [types.InlineKeyboardButton(text='<-', callback_data='manage_vis_text_butt_move_left'),
                    types.InlineKeyboardButton(text='send file with recent words',
                                               callback_data='manage_vis_text_butt_send_words'),
                    types.InlineKeyboardButton(text='->', callback_data='manage_vis_text_butt_move_right')]
    main_keyboard.row(*manage_butts)
    return (output_str, main_keyboard)


async def prepare_output_str(words_strs, prepare_type):
    if prepare_type == 'for_message':
        return '\n'.join(
            [j[0] + j[1] for j in zip([f'{i}) ' for i in range(1, len(words_strs) + 1)], words_strs)]) + '\n'
    elif prepare_type == 'for_file':
        return '\n'.join(words_strs) + '\n'


@dp.message_handler(lambda msg: '/w' in msg.text)
async def waiter(message: Message):
    # print(f'i will sleep {int(message.text[-1])} seconds')
    # await asyncio.sleep(int(message.text[-1]))
    # text=f'i wake up from {int(message.text[-1])}\'s sleep'
    print(message.message_id)
    await bot.send_message(chat_id=message.from_user.id, text=text)
