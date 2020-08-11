from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
import calendar
import config
import aiosqlite3
import re
import os
import keyboards as kb


bot = Bot(token=os.environ.get('TOKEN'))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def process_check_auth(message: types.Message):
    await bot.send_message(message.from_user.id, config.auth_pwd)

@dp.message_handler(lambda message: message.text in [os.environ.get('PASSWORD')])
async def process_start(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            try: 
                await cursor.execute("SELECT * FROM command WHERE user_id={}".format(message.from_user.id))
                if await cursor.fetchone() is None:
                    await cursor.execute("INSERT INTO command VALUES ({},'{}','{}','{}','{}',{},{},{},'{}',{},{},{})".format(message.from_user.id, 'location_one', 'location_two', '', '', 30, 0, 0, '', 0, 0, 0))
                else:
                    await cursor.execute("UPDATE command SET current_location='{}', next_location='{}', coins={}, artifact={}, last_hint_id={}, end_date={}, hidden_location='{}', end_game={} WHERE user_id={}".format('location_one', 'location_two', 30, 0, 0, 0, '', 0, message.from_user.id))
                await conn.commit()
            except Exception:
                await cursor.execute("CREATE TABLE command (user_id INTEGER, current_location TEXT, next_location TEXT, status TEXT, color TEXT, coins INTEGER, artifact INTEGER, last_hint_id INTEGER, hidden_location TEXT, start_time INTEGER, end_date INTEGER, end_game INTEGER)")
                await cursor.execute("INSERT INTO command VALUES ({},'{}','{}','{}','{}',{},{},{},'{}',{},{},{})".format(message.from_user.id, 'location_one', 'location_two', '', '', 30, 0, 0, '', 0, 0, 0))
                await conn.commit()

    await bot.send_message(message.from_user.id, config.select_color_button, reply_markup=kb.kb_ColorCommand)

@dp.message_handler(lambda message: message.text in [config.color_white, config.color_gray, config.color_red, config.color_orange, config.color_yellow, config.color_green, config.color_blue, config.color_havyblue, config.color_purple, config.color_pink])
async def process_check_command(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            await cursor.execute("UPDATE command SET color='{}' WHERE user_id={}".format(message.text, message.from_user.id))
            await conn.commit()

    await bot.send_message(message.from_user.id, 'Вы выбрали ' + message.text + ' цвет команды, вы уверены?', reply_markup=kb.kb_check)

@dp.message_handler(lambda message: message.text in [config.say_change])
async def process_send_color_command(message: types.Message):
    await bot.send_message(message.from_user.id, config.select_color_button, reply_markup=kb.kb_ColorCommand)

@dp.message_handler(lambda message: message.text in [config.say_continue])
async def process_send_choise_status(message: types.Message):
    await bot.send_message(message.from_user.id, config.choise_status, reply_markup=kb.kb_ChoiseStatus)

@dp.message_handler(lambda message: message.text in [config.say_member, config.say_continue_member])
async def process_send_chat_link(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            await cursor.execute("UPDATE command SET status='{}' WHERE user_id={}".format(message.text, message.from_user.id))
            await conn.commit()
            await cursor.execute("SELECT color FROM command WHERE user_id={}".format(message.from_user.id))
            color = re.sub(r'[,\'\)\(]', '', str(await cursor.fetchone()))

            await bot.send_message(message.from_user.id, config.say_you_member + color, reply_markup=kb.kb_remove)
            if color == config.color_white:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatWhite)
            if color == config.color_gray:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatGray)
            if color == config.color_red:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatRed)
            if color == config.color_orange:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatOrange)
            if color == config.color_yellow:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatYellow)
            if color == config.color_green:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatGreen)
            if color == config.color_blue:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatBlue)
            if color == config.color_havyblue:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatHavyBlue)
            if color == config.color_purple:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatPurple)
            if color == config.color_pink:
                await bot.send_message(message.from_user.id, config.chat_command, reply_markup=kb.kb_ChatPink)

@dp.message_handler(lambda message: message.text in [config.say_captain])
async def process_check_captain_status(message: types.Message):
    await bot.send_message(message.from_user.id, config.check_captain_status, reply_markup=kb.kb_ChoiseContinueStatus)

@dp.message_handler(lambda message: message.text in [config.say_continue_captain])
async def process_send_preview_message(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            await cursor.execute("UPDATE command SET status='{}' WHERE user_id={}".format(message.text, message.from_user.id))
            await conn.commit()

            sql_get_chat_id = "SELECT chat_id \
                                FROM locations v_loc \
                                JOIN command v_com on (v_com.color = v_loc.location_color) \
                                WHERE user_id={}".format(message.from_user.id)
            locations = [(os.environ.get('CHAT_ID1'), config.color_white, 'team_map_white', config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_eleven),
                        (os.environ.get('CHAT_ID2'), config.color_gray, 'team_map_gray', config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_eleven),
                        (os.environ.get('CHAT_ID3'), config.color_red, 'team_map_red', config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_eleven),
                        (os.environ.get('CHAT_ID4'), config.color_orange, 'team_map_orange', config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_eleven),
                        (os.environ.get('CHAT_ID5'), config.color_yellow, 'team_map_yellow', config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_eleven),
                        (os.environ.get('CHAT_ID6'), config.color_green, 'team_map_green', config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_eleven),
                        (os.environ.get('CHAT_ID7'), config.color_blue, 'team_map_blue', config.location_seven, config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_eleven),
                        (os.environ.get('CHAT_ID8'), config.color_havyblue, 'team_map_havyblue', config.location_eight, config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eleven),
                        (os.environ.get('CHAT_ID9'), config.color_purple, 'team_map_purple', config.location_nine, config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_eleven),
                        (os.environ.get('CHAT_ID10'), config.color_pink, 'team_map_pink', config.location_ten, config.location_one, config.location_two, config.location_three, config.location_four, config.location_five, config.location_six, config.location_seven, config.location_eight, config.location_nine, config.location_eleven)]
            try:
                await cursor.execute(sql_get_chat_id)
                location_data = await cursor.fetchone()
            except Exception:
                await cursor.execute("CREATE TABLE locations (chat_id INTEGER, location_color TEXT, team_map TEXT, location_one TEXT, location_two TEXT, location_three TEXT, location_four TEXT, location_five TEXT, location_six TEXT, location_seven TEXT, location_eight TEXT, location_nine TEXT, location_ten TEXT, location_eleven TEXT)")
                await cursor.executemany("INSERT INTO locations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", locations)
                await conn.commit()
                await cursor.execute(sql_get_chat_id)
                location_data = await cursor.fetchone()

            chat_id = re.sub(r'[,\)\(]', '', str(location_data))
            await cursor.execute("UPDATE command SET start_time={} WHERE user_id={}".format(calendar.timegm(datetime.utcnow().timetuple()), message.from_user.id))
            await conn.commit()
    await bot.send_photo(message.from_user.id, open('preview_msg.png', 'rb'), reply_markup=kb.kb_TeamMap)
    await bot.send_photo(chat_id, open('preview_msg.png', 'rb'))

@dp.message_handler(lambda message: message.text in [config.say_get_team_map])
async def process_send_start_location_data(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            sql_get_location_data = "SELECT chat_id, team_map, location_one \
                                    FROM locations v_loc \
                                    JOIN command v_com on (v_com.color = v_loc.location_color) \
                                    WHERE user_id={}".format(message.from_user.id)
            await cursor.execute(sql_get_location_data)
            data = re.split(r',', re.sub(r'[\)\(]', '', str(await cursor.fetchone())), 2)
            chat_id = data[0]
            team_map = re.sub(r'[ \']', '', data[1])
            btnStartLocation = KeyboardButton(config.start_location + re.sub(r'\'', '', data[2][:-1]))
            kb_startLocation = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btnStartLocation)

            await bot.send_photo(message.from_user.id, open('team_map/' + team_map + '.png', 'rb'), reply_markup=kb_startLocation)
            await bot.send_photo(chat_id, open('team_map/' + team_map + '.png', 'rb'))

@dp.message_handler(regexp = '^' + config.start_location + r'\w*')
async def process_check_start_location(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT end_game FROM command WHERE user_id={}".format(message.from_user.id))
            end_game = int(re.sub(r'[\,\)\(\']', '', str(await cursor.fetchone())))
            if end_game == 0:
                message_id = await bot.send_message(message.from_user.id, config.check_start_location, reply_markup=kb.kb_ChoiseActionLocation)
                await cursor.execute("UPDATE command SET last_hint_id={} WHERE user_id={}".format(message_id.message_id, message.from_user.id))
                await conn.commit()
            else:
                await bot.send_message(message.from_user.id, config.say_you_end_game)

@dp.message_handler(lambda message: message.text in [config.say_start_later_location])
async def process_send_start_later_location(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            await cursor.execute("SELECT current_location FROM command WHERE user_id={}".format(message.from_user.id))
            current_location = re.sub(r'[,\)\(\']', '', str(await cursor.fetchone()))
            sql_get_location_number = "SELECT " + current_location + " \
                                        FROM locations v_loc \
                                        JOIN command v_com on (v_com.color = v_loc.location_color) \
                                        WHERE user_id={}".format(message.from_user.id)
            await cursor.execute(sql_get_location_number)
            btnStartLocation = KeyboardButton(config.start_location + re.sub(r'[\)\(\']', '', str(await cursor.fetchone()))[:-1])
            kb_startLocation = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btnStartLocation)
            await bot.send_message(message.from_user.id, config.check_start_location, reply_markup=kb_startLocation)

@dp.message_handler(lambda message: message.text in [config.blitz, config.scientist, config.say_continue_location, config.say_restart])
async def process_send_legend(message: types.Message):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            sql_get_chat_id = "SELECT v_loc.chat_id, v_com.current_location, v_com.hidden_location, v_com.last_hint_id, v_com.end_game \
                                FROM locations v_loc \
                                JOIN command v_com on (v_com.color = v_loc.location_color) \
                                WHERE user_id={}".format(message.from_user.id)
            await cursor.execute(sql_get_chat_id)
            data = re.split(r',', re.sub(r'[\)\(]', '', str(await cursor.fetchone())))
            chat_id = re.sub(r'[ \']', '', data[0])
            current_location = re.sub(r'[ \']', '', data[1])
            hidden_location = re.sub(r'[\']', '', data[2])
            last_message_id = int(re.sub(r'[ \']', '', data[3]))
            end_game = int(re.sub(r'[ \']', '', data[4]))
            
            if last_message_id is not 0:
                await bot.delete_message(message.from_user.id, last_message_id)
                await cursor.execute("UPDATE command SET last_hint_id={} WHERE user_id={}".format(0, message.from_user.id))
                await conn.commit()

            if message.text == config.blitz:
                if re.search(config.blitz, hidden_location) is None:
                    btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask12')
                    kb_Task = InlineKeyboardMarkup().add(btnTask)
                    await bot.send_photo(message.from_user.id, open('legend/legend_blitz.png', 'rb'), reply_markup=kb_Task)
                    await bot.send_photo(chat_id, open('legend/legend_blitz.png', 'rb'))
                    if re.search(config.scientist, hidden_location) is None:
                        await cursor.execute("UPDATE command SET hidden_location='{}' WHERE user_id={}".format(config.blitz, message.from_user.id))
                    else:
                        await cursor.execute("UPDATE command SET hidden_location='{}' WHERE user_id={}".format(config.scientist + ';' + config.blitz, message.from_user.id))
                    await conn.commit()
                else:
                    if end_game == 0:
                        await bot.send_message(message.from_user.id, config.say_you_already_passed_location + config.blitz)
                    else:
                        await bot.send_message(message.from_user.id, config.say_you_end_game)
            if message.text == config.scientist:
                if re.search(config.scientist, hidden_location) is None:
                    btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask13')
                    kb_Task = InlineKeyboardMarkup().add(btnTask)
                    await bot.send_photo(message.from_user.id, open('legend/legend_scientist.png', 'rb'), reply_markup=kb_Task)
                    await bot.send_photo(chat_id, open('legend/legend_scientist.png', 'rb'))
                    if re.search(config.blitz, hidden_location) is None:
                        await cursor.execute("UPDATE command SET hidden_location='{}' WHERE user_id={}".format(config.scientist, message.from_user.id))
                    else:
                        await cursor.execute("UPDATE command SET hidden_location='{}' WHERE user_id={}".format(config.blitz + ';' + config.scientist, message.from_user.id))
                    await conn.commit()
                else:
                    if end_game == 0:
                        await bot.send_message(message.from_user.id, config.say_you_already_passed_location + config.scientist)
                    else:
                        await bot.send_message(message.from_user.id, config.say_you_end_game)

            if message.text == config.say_continue_location or message.text == config.say_restart:
                if end_game == 0:
                    sql_get_location_number = "SELECT " + current_location + " \
                                                 FROM locations v_loc \
                                                 JOIN command v_com on (v_com.color = v_loc.location_color) \
                                                WHERE user_id={}".format(message.from_user.id)
                    await cursor.execute(sql_get_location_number)
                    current_location = re.sub(r'[\)\(\']', '', str(await cursor.fetchone()))[:-1]
                    if config.location_one in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask1')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_one.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_one.png', 'rb'))
                    if config.location_two in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask2')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_two.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_two.png', 'rb'))
                    if config.location_three in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask3')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_three.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_three.png', 'rb'))
                    if config.location_four in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask4')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_four.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_four.png', 'rb'))
                    if config.location_five in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask5')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_five.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_five.png', 'rb'))
                    if config.location_six in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask6')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_six.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_six.png', 'rb'))
                    if config.location_seven in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask7')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_seven.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_seven.png', 'rb'))
                    if config.location_eight in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask8')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_eight.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_eight.png', 'rb'))
                    if config.location_nine in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask9')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_nine.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_nine.png', 'rb'))
                    if config.location_ten in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask10')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_ten.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_ten.png', 'rb'))
                    if config.location_eleven in current_location:
                        btnTask = InlineKeyboardButton(config.say_get_task, callback_data='btnGetTask11')
                        kb_Task = InlineKeyboardMarkup().add(btnTask)
                        await bot.send_photo(message.from_user.id, open('legend/legend_eleven.png', 'rb'), reply_markup=kb_Task)
                        await bot.send_photo(chat_id, open('legend/legend_eleven.png', 'rb'))
                else:
                    await bot.send_message(message.from_user.id, config.say_you_end_game)

@dp.callback_query_handler(regexp = r'^btnGetTask\w*')
async def process_send_additional_location_data(call: types.CallbackQuery):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            sql_get_chat_id = "SELECT v_loc.chat_id, v_com.next_location, v_com.current_location, v_com.color \
                                FROM locations v_loc \
                                JOIN command v_com on (v_com.color = v_loc.location_color) \
                                WHERE user_id={}".format(call.message.chat.id)
            await cursor.execute(sql_get_chat_id)
            data = re.split(r',', re.sub(r'[\)\(]', '', str(await cursor.fetchone())))
            chat_id = re.sub(r'[ \']', '', data[0])
            next_location = re.sub(r'[ \']', '', data[1])
            current_location = re.sub(r'[ \']', '', data[2])
            color_command = re.sub(r'[ \']', '', data[3])

            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, None, None)
            if call.data == 'btnGetTask12':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_dop_blitz1, option=config.options_task_blitz1.get('option'), answer=config.options_task_blitz1.get('answer'), location_number=current_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.blitz)
            if call.data == 'btnGetTask13':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_dop_scientist, open_period=420, option=config.options_task_scientist.get('option'), answer=config.options_task_scientist.get('answer'), location_number=current_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.scientist)
            if call.data == 'btnGetTask1':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_one+'_'+config.task_number1, option=config.options_task_one1.get('option'), answer=config.options_task_one1.get('answer'), hint_number=kb.kb_HintOne_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_one)
            if call.data == 'btnGetTask2':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_two+'_'+config.task_number1, option=config.options_task_two1.get('option'), answer=config.options_task_two1.get('answer'), hint_number=kb.kb_HintTwo_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_two)
            if call.data == 'btnGetTask3':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_three+'_'+config.task_number1, option=config.options_task_three1.get('option'), answer=config.options_task_three1.get('answer'), hint_number=kb.kb_HintThree_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_three)
            if call.data == 'btnGetTask4':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_four+'_'+config.task_number1, option=config.options_task_four1.get('option'), answer=config.options_task_four1.get('answer'), hint_number=kb.kb_HintFour_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_four)
            if call.data == 'btnGetTask5':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_five+'_'+config.task_number1, option=config.options_task_five1.get('option'), answer=config.options_task_five1.get('answer'), hint_number=kb.kb_HintFive_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_five)
            if call.data == 'btnGetTask6':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_six+'_'+config.task_number1, option=config.options_task_six1.get('option'), answer=config.options_task_six1.get('answer'), hint_number=kb.kb_HintSix_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_six)
            if call.data == 'btnGetTask7':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_seven+'_'+config.task_number1, option=config.options_task_seven1.get('option'), answer=config.options_task_seven1.get('answer'), hint_number=kb.kb_HintSeven_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_seven)
            if call.data == 'btnGetTask8':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_eight+'_'+config.task_number1, option=config.options_task_eight1.get('option'), answer=config.options_task_eight1.get('answer'), hint_number=kb.kb_HintEight_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_eight)
            if call.data == 'btnGetTask9':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_nine+'_'+config.task_number1, option=config.options_task_nine1.get('option'), answer=config.options_task_nine1.get('answer'), hint_number=kb.kb_HintNine_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_nine)
            if call.data == 'btnGetTask10':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_ten+'_'+config.task_number1, option=config.options_task_ten1.get('option'), answer=config.options_task_ten1.get('answer'), hint_number=kb.kb_HintTen_1, location_number=next_location, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_ten)
            if call.data == 'btnGetTask11':
                await quiz_poll(user_id=call.message.chat.id, delete_message=False, chat_id=chat_id, task=config.task_eleven+'_'+config.task_number1, open_period=480, option=config.options_task_eleven.get('option'), answer=config.options_task_eleven.get('answer'), hint_number=kb.kb_HintEleven_1, cursor=cursor, conn=conn)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_start_location + config.location_eleven)

async def quiz_poll(user_id=0, delete_message=True, last_hint_id=None, correct_answer=None, coins_command=None, coin=None, artifact=None, artifact_command=None, chat_id=0, end_date=None, task=None, open_period=None, option=None, answer=None, hint_number=None, location_number=None, cursor=None, conn=None):
    try:
        await cursor.execute("SELECT * FROM poll WHERE user_id={}".format(user_id))        
        data = await cursor.fetchone()
        if data is None:
            await cursor.execute("INSERT INTO poll VALUES ({},{},'{}',{})".format(user_id, 0, '', 0))
            await conn.commit()
    except Exception:
        await cursor.execute("CREATE TABLE poll (user_id INTEGER, poll_id INTEGER, question TEXT, correct_answer INTEGER)")
        await cursor.execute("INSERT INTO poll VALUES ({},{},'{}',{})".format(user_id, 0, '', 0))
        await conn.commit()

    if delete_message is True and int(last_hint_id) is not 0:
        await bot.delete_message(user_id, last_hint_id)
        await cursor.execute("UPDATE command SET last_hint_id={} WHERE user_id={}".format(0, user_id))
        await conn.commit()

    if correct_answer is False:
        await bot.send_message(user_id, config.coins_number + str(coins_command))
    if correct_answer is True:
        await cursor.execute("UPDATE command SET coins={} WHERE user_id={}".format(coins_command + coin, user_id))
        if artifact is not None:
            await cursor.execute("UPDATE command SET artifact={} WHERE user_id={}".format(artifact_command + 1, user_id))
            await bot.send_photo(user_id, open('artifact/' + artifact + '.png', 'rb'), config.artifact_received)
        await bot.send_message(user_id, config.coins_number + str(coins_command + coin))
        await conn.commit()

    kb_startLocation = None
    if location_number is not None:
        if 'two' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_two', next_location='location_three' WHERE user_id={}".format(user_id)
        if 'three' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_three', next_location='location_four' WHERE user_id={}".format(user_id)
        if 'four' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_four', next_location='location_five' WHERE user_id={}".format(user_id)
        if 'five' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_five', next_location='location_six' WHERE user_id={}".format(user_id)
        if 'six' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_six', next_location='location_seven' WHERE user_id={}".format(user_id)
        if 'seven' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_seven', next_location='location_eight' WHERE user_id={}".format(user_id)
        if 'eight' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_eight', next_location='location_nine' WHERE user_id={}".format(user_id)
        if 'nine' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_nine', next_location='location_ten' WHERE user_id={}".format(user_id)
        if 'ten' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_ten', next_location='location_eleven' WHERE user_id={}".format(user_id)
        if 'eleven' in location_number:
            sql_insert_location = "UPDATE command SET current_location='location_eleven' WHERE user_id={}".format(user_id)
        await cursor.execute(sql_insert_location)
        await conn.commit()

        sql_get_location_number = "SELECT " + location_number + " \
                                     FROM locations v_loc \
                                     JOIN command v_com on (v_com.color = v_loc.location_color) \
                                    WHERE user_id={}".format(user_id)
        await cursor.execute(sql_get_location_number)
        btnStartLocation = KeyboardButton(config.start_location + re.sub(r'[\)\(\']', '', str(await cursor.fetchone()))[:-1])
        kb_startLocation = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btnStartLocation)

    if task is not None:
        if kb_startLocation is not None:
            await bot.send_photo(user_id, open('task/' + task + '.png', 'rb'), reply_markup=kb_startLocation)
        else:
            await bot.send_photo(user_id, open('task/' + task + '.png', 'rb'))
        await bot.send_photo(chat_id, open('task/' + task + '.png', 'rb'))
        if 'dop' in task:
            if end_date is None:
                end_date = calendar.timegm((datetime.utcnow() + timedelta(minutes=6)).timetuple())
            poll_data = await bot.send_poll(chat_id=user_id, question=task, options=option, is_anonymous=False, type='quiz', correct_option_id=answer, close_date=end_date)
            await cursor.execute("UPDATE command SET end_date={} WHERE user_id={}".format(end_date, user_id))
        else:
            if end_date is None:
                end_date = calendar.timegm((datetime.utcnow() + timedelta(minutes=15)).timetuple())
            if open_period is None:
                poll_data = await bot.send_poll(chat_id=user_id, question=task, options=option, is_anonymous=False, type='quiz', correct_option_id=answer, close_date=end_date)
            else:
                poll_data = await bot.send_poll(chat_id=user_id, question=task, options=option, is_anonymous=False, type='quiz', correct_option_id=answer, open_period=open_period)
            last_hint_id = await bot.send_message(user_id, config.hints, reply_markup=hint_number)
            await cursor.execute("UPDATE command SET end_date={}, last_hint_id={} WHERE user_id={}".format(end_date, last_hint_id.message_id, user_id))

        await cursor.execute("UPDATE poll SET poll_id={}, question='{}', correct_answer={} WHERE user_id={}".format(poll_data.poll.id, task, answer, user_id))
        await conn.commit()

@dp.poll_answer_handler()
async def process_poll_handler(quiz_answer: types.Poll):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor: 
            sql_get_poll_data = "SELECT v_poll.question, v_poll.correct_answer, v_loc.chat_id, v_com.coins, \
                                        v_com.artifact, v_com.last_hint_id, v_com.end_date, v_com.color \
                                FROM poll v_poll JOIN command v_com on (v_com.user_id = v_poll.user_id) \
                                JOIN locations v_loc on (v_loc.location_color=v_com.color) \
                                WHERE v_poll.user_id={} and \
                                        v_poll.poll_id={}".format(quiz_answer.user.id, quiz_answer.poll_id)
            await cursor.execute(sql_get_poll_data)
            poll_data = re.split(r',', re.sub(r'[\)\(]', '', str(await cursor.fetchone())))
            question = re.sub(r'[ \']', '', poll_data[0])
            if re.sub(r' ', '', poll_data[1]) == str(quiz_answer.option_ids[0]):
                correct_answer = True
            else:
                correct_answer = False

            chat_id = re.sub(r' ', '', poll_data[2])
            coins_command = int(re.sub(r' ', '', poll_data[3]))
            artifact_command = int(re.sub(r' ', '', poll_data[4]))
            last_hint_id = re.sub(r' ', '', poll_data[5])
            end_date = re.sub(r' ', '', poll_data[6])
            color_command = re.sub(r'[ \']', '', poll_data[7])

            if question == config.task_one+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_one1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_one+'_'+config.task_number2, option=config.options_task_one2.get('option'), answer=config.options_task_one2.get('answer'), hint_number=kb.kb_HintOne_2, cursor=cursor, conn=conn)
            if question == config.task_one+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_one2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_one+'_'+config.task_number3, option=config.options_task_one3.get('option'), answer=config.options_task_one3.get('answer'), hint_number=kb.kb_HintOne_3, cursor=cursor, conn=conn)
            if question == config.task_one+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_one3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_one+'_'+config.task_number4, option=config.options_task_one4.get('option'), answer=config.options_task_one4.get('answer'), hint_number=kb.kb_HintOne_4, cursor=cursor, conn=conn)
            if question == config.task_one+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_one4.get('coin'), chat_id=chat_id, artifact='artifact_one', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_one + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_two+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_two1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_two+'_'+config.task_number2, option=config.options_task_two2.get('option'), answer=config.options_task_two2.get('answer'), hint_number=kb.kb_HintTwo_2, cursor=cursor, conn=conn)
            if question == config.task_two+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_two2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_two+'_'+config.task_number3, option=config.options_task_two3.get('option'), answer=config.options_task_two3.get('answer'), hint_number=kb.kb_HintTwo_3, cursor=cursor, conn=conn)
            if question == config.task_two+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_two3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_two+'_'+config.task_number4, option=config.options_task_two4.get('option'), answer=config.options_task_two4.get('answer'), hint_number=kb.kb_HintTwo_4, cursor=cursor, conn=conn)
            if question == config.task_two+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_two4.get('coin'), chat_id=chat_id, artifact='artifact_two', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_two + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_three+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_three1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_three+'_'+config.task_number2, option=config.options_task_three2.get('option'), answer=config.options_task_three2.get('answer'), hint_number=kb.kb_HintThree_2, cursor=cursor, conn=conn)
            if question == config.task_three+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_three2.get('coin'), chat_id=chat_id, artifact='artifact_three', artifact_command=artifact_command, end_date=end_date, task=config.task_three+'_'+config.task_number3, option=config.options_task_three3.get('option'), answer=config.options_task_three3.get('answer'), hint_number=kb.kb_HintThree_3, cursor=cursor, conn=conn)
            if question == config.task_three+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_three3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_three+'_'+config.task_number4, option=config.options_task_three4.get('option'), answer=config.options_task_three4.get('answer'), hint_number=kb.kb_HintThree_4, cursor=cursor, conn=conn)
            if question == config.task_three+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_three4.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_three + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_four+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_four1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_four+'_'+config.task_number2, option=config.options_task_four2.get('option'), answer=config.options_task_four2.get('answer'), hint_number=kb.kb_HintFour_2, cursor=cursor, conn=conn)
            if question == config.task_four+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_four2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_four+'_'+config.task_number3, option=config.options_task_four3.get('option'), answer=config.options_task_four3.get('answer'), hint_number=kb.kb_HintFour_3, cursor=cursor, conn=conn)
            if question == config.task_four+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_four3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_four+'_'+config.task_number4, option=config.options_task_four4.get('option'), answer=config.options_task_four4.get('answer'), hint_number=kb.kb_HintFour_4, cursor=cursor, conn=conn)
            if question == config.task_four+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_four4.get('coin'), chat_id=chat_id, artifact='artifact_four', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_four + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_five+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_five1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_five+'_'+config.task_number2, option=config.options_task_five2.get('option'), answer=config.options_task_five2.get('answer'), hint_number=kb.kb_HintFive_2, cursor=cursor, conn=conn)
            if question == config.task_five+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_five2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_five+'_'+config.task_number3, option=config.options_task_five3.get('option'), answer=config.options_task_five3.get('answer'), hint_number=kb.kb_HintFive_3, cursor=cursor, conn=conn)
            if question == config.task_five+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_five3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_five+'_'+config.task_number4, option=config.options_task_five4.get('option'), answer=config.options_task_five4.get('answer'), hint_number=kb.kb_HintFive_4, cursor=cursor, conn=conn)
            if question == config.task_five+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_five4.get('coin'), chat_id=chat_id, artifact='artifact_five', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_five + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_six+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_six1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_six+'_'+config.task_number2, option=config.options_task_six2.get('option'), answer=config.options_task_six2.get('answer'), hint_number=kb.kb_HintSix_2, cursor=cursor, conn=conn)
            if question == config.task_six+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_six2.get('coin'), chat_id=chat_id, artifact='artifact_six', artifact_command=artifact_command, end_date=end_date, task=config.task_six+'_'+config.task_number3, option=config.options_task_six3.get('option'), answer=config.options_task_six3.get('answer'), hint_number=kb.kb_HintSix_3, cursor=cursor, conn=conn)
            if question == config.task_six+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_six3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_six+'_'+config.task_number4, option=config.options_task_six4.get('option'), answer=config.options_task_six4.get('answer'), hint_number=kb.kb_HintSix_4, cursor=cursor, conn=conn)
            if question == config.task_six+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_six4.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_six + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_seven+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_seven1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_seven+'_'+config.task_number2, option=config.options_task_seven2.get('option'), answer=config.options_task_seven2.get('answer'), hint_number=kb.kb_HintSeven_2, cursor=cursor, conn=conn)
            if question == config.task_seven+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_seven2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_seven+'_'+config.task_number3, option=config.options_task_seven3.get('option'), answer=config.options_task_seven3.get('answer'), hint_number=kb.kb_HintSeven_3, cursor=cursor, conn=conn)
            if question == config.task_seven+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_seven3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_seven+'_'+config.task_number4, option=config.options_task_seven4.get('option'), answer=config.options_task_seven4.get('answer'), hint_number=kb.kb_HintSeven_4, cursor=cursor, conn=conn)
            if question == config.task_seven+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_seven4.get('coin'), chat_id=chat_id, artifact='artifact_seven', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_seven + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_eight+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_eight1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_eight+'_'+config.task_number2, option=config.options_task_eight2.get('option'), answer=config.options_task_eight2.get('answer'), hint_number=kb.kb_HintEight_2, cursor=cursor, conn=conn)
            if question == config.task_eight+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_eight2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_eight+'_'+config.task_number3, option=config.options_task_eight3.get('option'), answer=config.options_task_eight3.get('answer'), hint_number=kb.kb_HintEight_3, cursor=cursor, conn=conn)
            if question == config.task_eight+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_eight3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_eight+'_'+config.task_number4, option=config.options_task_eight4.get('option'), answer=config.options_task_eight4.get('answer'), hint_number=kb.kb_HintEight_4, cursor=cursor, conn=conn)
            if question == config.task_eight+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_eight4.get('coin'), chat_id=chat_id, artifact='artifact_eight', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_eight + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_nine+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_nine1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_nine+'_'+config.task_number2, option=config.options_task_nine2.get('option'), answer=config.options_task_nine2.get('answer'), hint_number=kb.kb_HintNine_2, cursor=cursor, conn=conn)
            if question == config.task_nine+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_nine2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_nine+'_'+config.task_number3, option=config.options_task_nine3.get('option'), answer=config.options_task_nine3.get('answer'), hint_number=kb.kb_HintNine_3, cursor=cursor, conn=conn)
            if question == config.task_nine+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_nine3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_nine+'_'+config.task_number4, option=config.options_task_nine4.get('option'), answer=config.options_task_nine4.get('answer'), hint_number=kb.kb_HintNine_4, cursor=cursor, conn=conn)
            if question == config.task_nine+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_nine4.get('coin'), chat_id=chat_id, artifact='artifact_nine', artifact_command=artifact_command, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_nine + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_ten+'_'+config.task_number1:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_ten1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_ten+'_'+config.task_number2, option=config.options_task_ten2.get('option'), answer=config.options_task_ten2.get('answer'), hint_number=kb.kb_HintTen_2, cursor=cursor, conn=conn)
            if question == config.task_ten+'_'+config.task_number2:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_ten2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_ten+'_'+config.task_number3, option=config.options_task_ten3.get('option'), answer=config.options_task_ten3.get('answer'), hint_number=kb.kb_HintTen_3, cursor=cursor, conn=conn)
            if question == config.task_ten+'_'+config.task_number3:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_ten3.get('coin'), chat_id=chat_id, artifact='artifact_ten', artifact_command=artifact_command, end_date=end_date, task=config.task_ten+'_'+config.task_number4, option=config.options_task_ten4.get('option'), answer=config.options_task_ten4.get('answer'), hint_number=kb.kb_HintTen_4, cursor=cursor, conn=conn)
            if question == config.task_ten+'_'+config.task_number4:
                await quiz_poll(user_id=quiz_answer.user.id, last_hint_id=last_hint_id, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_ten4.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.location_ten + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_dop_blitz1:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz1.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz2, option=config.options_task_blitz2.get('option'), answer=config.options_task_blitz2.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz2:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz2.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz3, option=config.options_task_blitz3.get('option'), answer=config.options_task_blitz3.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz3:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz3.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz4, option=config.options_task_blitz4.get('option'), answer=config.options_task_blitz4.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz4:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz4.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz5, option=config.options_task_blitz5.get('option'), answer=config.options_task_blitz5.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz5:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz5.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz6, option=config.options_task_blitz6.get('option'), answer=config.options_task_blitz6.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz6:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz6.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz7, option=config.options_task_blitz7.get('option'), answer=config.options_task_blitz7.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz7:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz7.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz8, option=config.options_task_blitz8.get('option'), answer=config.options_task_blitz8.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz8:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz8.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz9, option=config.options_task_blitz9.get('option'), answer=config.options_task_blitz9.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz9:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz9.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz10, option=config.options_task_blitz10.get('option'), answer=config.options_task_blitz10.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz10:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz10.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz11, option=config.options_task_blitz11.get('option'), answer=config.options_task_blitz11.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz11:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz11.get('coin'), chat_id=chat_id, end_date=end_date, task=config.task_dop_blitz12, option=config.options_task_blitz12.get('option'), answer=config.options_task_blitz12.get('answer'), cursor=cursor, conn=conn)
            if question == config.task_dop_blitz12:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_blitz12.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.blitz + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_dop_scientist:
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_scientist.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), color_command + config.admin_end_location + config.scientist + config.end_coins_number + str(coins_command) + config.end_artifact_number + str(artifact_command))

            if question == config.task_eleven+'_'+config.task_number1:
                if correct_answer is True:
                    await bot.send_message(quiz_answer.user.id, config.end_quiz)    
                await quiz_poll(user_id=quiz_answer.user.id, delete_message=False, correct_answer=correct_answer, coins_command=coins_command, coin=config.options_task_eleven.get('coin'), chat_id=chat_id, cursor=cursor, conn=conn)
                await bot.send_message(quiz_answer.user.id, config.end_location)

                await cursor.execute("SELECT color, coins, artifact, start_time FROM command WHERE user_id={}".format(quiz_answer.user.id))
                command_data = re.split(r',', re.sub(r'[\)\(]', '', str(await cursor.fetchone())))
                color_command = re.sub(r'[ \']', '', command_data[0])
                coins_command = re.sub(r' ', '', command_data[1])
                artifact_command = re.sub(r' ', '', command_data[2])
                running_time = re.split(r'\.', str(datetime.now() - datetime.fromtimestamp(int(re.sub(r' ', '', command_data[3])))), 1)[0]

                await bot.send_message(os.environ.get('ADMIN_CHAT_ID'), color_command + config.admin_end_location + config.location_eleven + config.end_coins_number + coins_command + config.end_artifact_number + strartifact_command + config.end_running_time + str(running_time))
                await bot.send_message(quiz_answer.user.id, config.say_you_end_game + config.end_coins_number + coins_command + config.end_artifact_number + artifact_command + config.end_running_time + str(running_time))
                await bot.send_message(chat_id, config.say_you_end_game + config.end_coins_number + coins_command + config.end_artifact_number + artifact_command + config.end_running_time + str(running_time))
                await bot.send_message(os.environ.get('RESULT_CHAT_ID'), 'Цвет команды: ' + color_command + config.end_coins_number + coins_command + config.end_artifact_number + artifact_command + config.end_running_time + str(running_time))
                await cursor.execute("UPDATE command SET hidden_location='{}', end_game={} WHERE user_id={}".format(config.scientist + ';' + config.blitz, 1, quiz_answer.user.id))
                await conn.commit()

async def send_hint_data(call, last_hint_id, coins_command, hint_data, hint_cost, cursor, conn):
    if coins_command >= hint_cost:
        await cursor.execute("UPDATE command SET coins={} WHERE user_id={}".format(coins_command - hint_cost, call.message.chat.id))
        await conn.commit()
        if hint_data in ('hint_three2', 'hint_nine10'):
            await bot.send_photo(call.message.chat.id, open('hint/' + hint_data + '.png', 'rb'))
        else:
            await bot.send_message(call.message.chat.id, hint_data)

        inline_list = []
        btn_list = re.findall(r'btnHint\w+', str(call.message.reply_markup))
        coin_list = re.findall(r'За \d+ \w+', str(call.message.reply_markup))
        for btn in btn_list:
            for coin in coin_list:
                inline_list.append({'button':btn, 'coin':coin})
                coin_list.remove(coin)
                break

        inline_list = [d for d in inline_list if d.get('button') != call.data]
        if len(inline_list) == 2:
            bthHint1 = InlineKeyboardButton(inline_list[0]['coin'], callback_data=inline_list[0]['button'])
            bthHint2 = InlineKeyboardButton(inline_list[1]['coin'], callback_data=inline_list[1]['button'])

            await bot.edit_message_reply_markup(call.message.chat.id, last_hint_id, None, InlineKeyboardMarkup().add(bthHint1, bthHint2))
        if len(inline_list) == 1:
            bthHint1 = InlineKeyboardButton(inline_list[0]['coin'], callback_data=inline_list[0]['button'])

            await bot.edit_message_reply_markup(call.message.chat.id, last_hint_id, None, InlineKeyboardMarkup().add(bthHint1))
        if len(inline_list) == 0:
            await bot.delete_message(call.message.chat.id, last_hint_id)
            await cursor.execute("UPDATE command SET last_hint_id={} WHERE user_id={}".format(0, call.message.chat.id))
            await conn.commit()
    else:
        await bot.send_message(call.message.chat.id, config.lack_coins + config.coins_number + str(coins_command))

@dp.callback_query_handler(regexp = r'^btnHint\w\w*')
async def process_check_task(call: types.CallbackQuery):
    async with aiosqlite3.connect("quizbot.db") as conn:
        async with conn.cursor() as cursor:     
            await cursor.execute("SELECT last_hint_id, coins FROM command WHERE user_id={}".format(call.message.chat.id))
            command_data = re.split(r',', re.sub(r'[\'\)\(]', '', str(await cursor.fetchone())))
            last_hint_id = re.sub(r' ', '', command_data[0])
            coins_command = int(re.sub(r' ', '', command_data[1]))

            if call.data == 'btnHintOne_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one1, 1, cursor, conn)
            if call.data == 'btnHintOne_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one2, 3, cursor, conn)
            if call.data == 'btnHintOne_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one3, 5, cursor, conn)
            if call.data == 'btnHintOne_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one4, 1, cursor, conn)
            if call.data == 'btnHintOne_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one5, 3, cursor, conn)
            if call.data == 'btnHintOne_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one6, 5, cursor, conn)
            if call.data == 'btnHintOne_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one7, 1, cursor, conn)
            if call.data == 'btnHintOne_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one8, 3, cursor, conn)
            if call.data == 'btnHintOne_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one9, 5, cursor, conn)
            if call.data == 'btnHintOne_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one10, 1, cursor, conn)
            if call.data == 'btnHintOne_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one11, 3, cursor, conn)
            if call.data == 'btnHintOne_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_one12, 5, cursor, conn)

            if call.data == 'btnHintTwo_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two1, 1, cursor, conn)
            if call.data == 'btnHintTwo_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two2, 3, cursor, conn)
            if call.data == 'btnHintTwo_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two3, 5, cursor, conn)
            if call.data == 'btnHintTwo_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two4, 1, cursor, conn)
            if call.data == 'btnHintTwo_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two5, 3, cursor, conn)
            if call.data == 'btnHintTwo_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two6, 5, cursor, conn)
            if call.data == 'btnHintTwo_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two7, 1, cursor, conn)
            if call.data == 'btnHintTwo_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two8, 3, cursor, conn)
            if call.data == 'btnHintTwo_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two9, 5, cursor, conn)
            if call.data == 'btnHintTwo_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two10, 1, cursor, conn)
            if call.data == 'btnHintTwo_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two11, 3, cursor, conn)
            if call.data == 'btnHintTwo_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_two12, 5, cursor, conn)

            if call.data == 'btnHintThree_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three1, 1, cursor, conn)
            if call.data == 'btnHintThree_2':
                await send_hint_data(call, last_hint_id, coins_command, 'hint_three2', 3, cursor, conn)
            if call.data == 'btnHintThree_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three3, 5, cursor, conn)
            if call.data == 'btnHintThree_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three4, 1, cursor, conn)
            if call.data == 'btnHintThree_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three5, 3, cursor, conn)
            if call.data == 'btnHintThree_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three6, 5, cursor, conn)
            if call.data == 'btnHintThree_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three7, 1, cursor, conn)
            if call.data == 'btnHintThree_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three8, 3, cursor, conn)
            if call.data == 'btnHintThree_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three9, 5, cursor, conn)
            if call.data == 'btnHintThree_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three10, 1, cursor, conn)
            if call.data == 'btnHintThree_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three11, 3, cursor, conn)
            if call.data == 'btnHintThree_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_three12, 5, cursor, conn)

            if call.data == 'btnHintFour_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four1, 1, cursor, conn)
            if call.data == 'btnHintFour_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four2, 3, cursor, conn)
            if call.data == 'btnHintFour_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four3, 5, cursor, conn)
            if call.data == 'btnHintFour_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four4, 1, cursor, conn)
            if call.data == 'btnHintFour_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four5, 3, cursor, conn)
            if call.data == 'btnHintFour_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four6, 5, cursor, conn)
            if call.data == 'btnHintFour_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four7, 1, cursor, conn)
            if call.data == 'btnHintFour_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four8, 3, cursor, conn)
            if call.data == 'btnHintFour_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four9, 5, cursor, conn)
            if call.data == 'btnHintFour_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four10, 1, cursor, conn)
            if call.data == 'btnHintFour_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four11, 3, cursor, conn)
            if call.data == 'btnHintFour_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_four12, 5, cursor, conn)

            if call.data == 'btnHintFive_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five1, 1, cursor, conn)
            if call.data == 'btnHintFive_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five2, 3, cursor, conn)
            if call.data == 'btnHintFive_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five3, 5, cursor, conn)
            if call.data == 'btnHintFive_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five4, 1, cursor, conn)
            if call.data == 'btnHintFive_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five5, 3, cursor, conn)
            if call.data == 'btnHintFive_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five6, 5, cursor, conn)
            if call.data == 'btnHintFive_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five7, 1, cursor, conn)
            if call.data == 'btnHintFive_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five8, 3, cursor, conn)
            if call.data == 'btnHintFive_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five9, 5, cursor, conn)
            if call.data == 'btnHintFive_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five10, 1, cursor, conn)
            if call.data == 'btnHintFive_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five11, 3, cursor, conn)
            if call.data == 'btnHintFive_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_five12, 5, cursor, conn)

            if call.data == 'btnHintSix_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six1, 1, cursor, conn)
            if call.data == 'btnHintSix_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six2, 3, cursor, conn)
            if call.data == 'btnHintSix_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six3, 5, cursor, conn)
            if call.data == 'btnHintSix_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six4, 1, cursor, conn)
            if call.data == 'btnHintSix_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six5, 3, cursor, conn)
            if call.data == 'btnHintSix_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six6, 5, cursor, conn)
            if call.data == 'btnHintSix_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six7, 1, cursor, conn)
            if call.data == 'btnHintSix_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six8, 3, cursor, conn)
            if call.data == 'btnHintSix_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six9, 5, cursor, conn)
            if call.data == 'btnHintSix_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six10, 1, cursor, conn)
            if call.data == 'btnHintSix_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six11, 3, cursor, conn)
            if call.data == 'btnHintSix_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_six12, 5, cursor, conn)

            if call.data == 'btnHintSeven_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven1, 1, cursor, conn)
            if call.data == 'btnHintSeven_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven2, 3, cursor, conn)
            if call.data == 'btnHintSeven_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven3, 5, cursor, conn)
            if call.data == 'btnHintSeven_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven4, 1, cursor, conn)
            if call.data == 'btnHintSeven_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven5, 3, cursor, conn)
            if call.data == 'btnHintSeven_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven6, 5, cursor, conn)
            if call.data == 'btnHintSeven_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven7, 1, cursor, conn)
            if call.data == 'btnHintSeven_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven8, 3, cursor, conn)
            if call.data == 'btnHintSeven_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven9, 5, cursor, conn)
            if call.data == 'btnHintSeven_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven10, 1, cursor, conn)
            if call.data == 'btnHintSeven_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven11, 3, cursor, conn)
            if call.data == 'btnHintSeven_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_seven12, 5, cursor, conn)

            if call.data == 'btnHintEight_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight1, 1, cursor, conn)
            if call.data == 'btnHintEight_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight2, 3, cursor, conn)
            if call.data == 'btnHintEight_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight3, 5, cursor, conn)
            if call.data == 'btnHintEight_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight4, 1, cursor, conn)
            if call.data == 'btnHintEight_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight5, 3, cursor, conn)
            if call.data == 'btnHintEight_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight6, 5, cursor, conn)
            if call.data == 'btnHintEight_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight7, 1, cursor, conn)
            if call.data == 'btnHintEight_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight8, 3, cursor, conn)
            if call.data == 'btnHintEight_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight9, 5, cursor, conn)
            if call.data == 'btnHintEight_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight10, 1, cursor, conn)
            if call.data == 'btnHintEight_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight11, 3, cursor, conn)
            if call.data == 'btnHintEight_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eight12, 5, cursor, conn)

            if call.data == 'btnHintNine_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine1, 1, cursor, conn)
            if call.data == 'btnHintNine_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine2, 3, cursor, conn)
            if call.data == 'btnHintNine_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine3, 5, cursor, conn)
            if call.data == 'btnHintNine_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine4, 1, cursor, conn)
            if call.data == 'btnHintNine_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine5, 3, cursor, conn)
            if call.data == 'btnHintNine_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine6, 5, cursor, conn)
            if call.data == 'btnHintNine_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine7, 1, cursor, conn)
            if call.data == 'btnHintNine_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine8, 3, cursor, conn)
            if call.data == 'btnHintNine_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine9, 5, cursor, conn)
            if call.data == 'btnHintNine_10':
                await send_hint_data(call, last_hint_id, coins_command, 'hint_nine10', 1, cursor, conn)
            if call.data == 'btnHintNine_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine11, 3, cursor, conn)
            if call.data == 'btnHintNine_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_nine12, 5, cursor, conn)

            if call.data == 'btnHintTen_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten1, 1, cursor, conn)
            if call.data == 'btnHintTen_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten2, 3, cursor, conn)
            if call.data == 'btnHintTen_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten3, 5, cursor, conn)
            if call.data == 'btnHintTen_4':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten4, 1, cursor, conn)
            if call.data == 'btnHintTen_5':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten5, 3, cursor, conn)
            if call.data == 'btnHintTen_6':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten6, 5, cursor, conn)
            if call.data == 'btnHintTen_7':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten7, 1, cursor, conn)
            if call.data == 'btnHintTen_8':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten8, 3, cursor, conn)
            if call.data == 'btnHintTen_9':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten9, 5, cursor, conn)
            if call.data == 'btnHintTen_10':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten10, 1, cursor, conn)
            if call.data == 'btnHintTen_11':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten11, 3, cursor, conn)
            if call.data == 'btnHintTen_12':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_ten12, 5, cursor, conn)

            if call.data == 'btnHintEleven_1':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eleven1, 1, cursor, conn)
            if call.data == 'btnHintEleven_2':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eleven2, 3, cursor, conn)
            if call.data == 'btnHintEleven_3':
                await send_hint_data(call, last_hint_id, coins_command, config.hint_eleven3, 5, cursor, conn)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)