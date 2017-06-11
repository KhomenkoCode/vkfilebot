# -*- coding: utf-8 -*

import http.client
import json
import os
import time
import urllib
import datetime
import urllib.request
import re

import telebot
from telebot import types
from transliterate import slugify

import constants
import emoji

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts
usersMessageSearchRequest = {}
usersChoosedType = {}
usersVKresponse = {}
usersIsAlreadySearched = {}
usersCountFiles = {}

usersDownloadCommand = {}
lastChoosedFile = {}
usersDownTitle = {}
usersDownSize = {}
usersDownExt = {}
usersDownLink = {}

bot = telebot.TeleBot(constants.token)
commands = {  # command description used in the "help" command
    'start': 'Начало работы со мной',
    'help': 'Вся необходимая информация'
}

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

with open("log.txt", "a") as myfile:
    myfile.write(str(datetime.datetime.now()) + ": " + "New session" + "\n")


# Открытие соединения с VK.
def getApiConnection():
    return (http.client.HTTPSConnection("api.vk.com"))


def generateAnswer(message, offset, type):
    cid = message.chat.id
    text = message.text
    if offset == 10:
        usersIsAlreadySearched[cid] = False
    try:
        if not usersIsAlreadySearched[cid]:
            apiConnection = getApiConnection()
            cid = message.chat.id
            seachq = urllib.parse.quote(usersMessageSearchRequest[cid])
            url = '/method/docs.search?q=' + seachq + '&count=' + '500' \
                  + '&offset=' + '1' + '&access_token=' + constants.tokenVK + '&v=5.64'
        pass

        try:

            if usersIsAlreadySearched[cid]:
                vkResponse = usersVKresponse[cid]
            else:
                usersVKresponse[cid] = vkResponse = vkRequest(apiConnection, url).get("response", 0)
                usersIsAlreadySearched[cid] = True
        except (ConnectionError, http.client.BadStatusLine) as e:
            apiConnection.close()
        try:
            items = vkResponse.get("items")
            count = vkResponse.get("count")
            if count == 0:
                bot.send_message(message.chat.id, "Прости,но я ничего не нашёл")
            else:
                genereted_answer = emoji.emojiCodeDict[":white_check_mark:"] + "Найденные фаилы по запросу: " + \
                                   "'" + "<b>" + str(usersMessageSearchRequest[cid]) + "</b>" + "'" + "\n"
                # Emoji here
                data = {'count': 0}

                if type >= 1 and type <= 8:
                    for item in items:
                        if item.get("type", 0) == type:
                            item_new = {};
                            item_new['id'] = item.get("id", 0)
                            item_new['size'] = item.get("size", 0)
                            item_new['title'] = item.get("title", 0)
                            item_new['url'] = item.get("url", 0)
                            item_new['type'] = item.get("type", 0)
                            item_new['ext'] = item.get("ext", 0)
                            data[data.get('count')] = item_new
                            data['count'] = data.get('count') + 1
                        pass
                else:
                    for item in items:
                        item_new = {};
                        item_new['id'] = item.get("id", 0)
                        item_new['size'] = item.get("size", 0)
                        item_new['title'] = item.get("title", 0)
                        item_new['url'] = item.get("url", 0)
                        item_new['type'] = item.get("type", 0)
                        item_new['ext'] = item.get("ext", 0)
                        data[data.get('count')] = item_new
                        data['count'] = data.get('count') + 1
                    pass
                # jsonData = json.dumps(data)
                if offset == 1:
                    if data.get("count") == 0:
                        genereted_answer += emoji.emojiCodeDict[":no_entry:"]
                    genereted_answer += "Фаилов соотвутствующих критерию: " + str(data.get("count")) + "\n" + "\n"
                    usersCountFiles[cid] = int(data.get("count"))
                for iter in range(0, int(data.get("count"))):
                    if (offset * 5) - 5 <= iter < offset * 5:
                        genereted_answer += "<b>" + str(data.get(iter).get("title", 0) + "\n") + "</b>"

                        usersDownloadCommand["dow_" + str(cid) + str(data.get(iter).get("id", 0))] = "dow_" + str(
                            cid) + str(data.get(iter).get("id", 0))
                        usersDownTitle["dow_" + str(cid) + str(data.get(iter).get("id", 0))] = data.get(iter).get(
                            "title", 0)

                        genereted_answer += "Расширение фаила: " + "<i>" + data.get(iter).get("ext", 0) + "</i>" + "\n"
                        usersDownExt["dow_" + str(cid) + str(data.get(iter).get("id", 0))] = data.get(iter).get(
                            "ext", 0)
                        unRedirectUrl = data.get(iter).get("url", 0)
                        size = data.get(iter).get("size", 0)

                        usersDownSize["dow_" + str(cid) + str(data.get(iter).get("id", 0))] = size

                        size = float(size)  # in bytes
                        size = size / 1024.0  # in KB (Kilo Bytes)
                        size = size / 1024.0  # size in MB (Mega Bytes)
                        genereted_answer += "Размер фаила:" + "<i>" + " " "%.3f" % size + " MB" + "</i>" + "\n"

                        usersDownLink["dow_" + str(cid) + str(data.get(iter).get("id", 0))] = unRedirectUrl

                        genereted_answer += "<i>" + "Download: " + "</i>" + "/dow_" + str(cid) + str(
                            data.get(iter).get("id", 0)) + "\n" + "\n"

                        genereted_answer += emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_blue_diamond:"] + \
                                            emoji.emojiCodeDict[":small_red_triangle_down:"] + \
                                            "\n"
                pass
                return genereted_answer
            pass

        except:
            print("\n" + url)
            print("\n" + vkResponse)

    except:
        bot.send_message(message.from_user.id,
                         "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")


# Запрос к API VK.
def vkRequest(api_connection, url):
    api_connection.request('GET', url)
    vkResponse = api_connection.getresponse().read()
    vkJson = json.loads(vkResponse.decode("utf-8"))

    # Обработка Too many requests per second.
    if vkJson.get("response", 0) == 0:
        if vkJson.get("error", 0).get("error_code", 0) == 6:
            time.sleep(0.35)
            return vkRequest(api_connection, url)

    return (vkJson)


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            parsedText = urllib.parse.quote(m.text)
            with open("log.txt", "a") as myfile:  # print the sent message to the console
                myfile.write(str(datetime.datetime.now()) + ": " + str(m.chat.first_name) + " " + str(
                    m.chat.last_name) + " [" + str(m.chat.id) + "]: " + parsedText + "\n")
                print(str(str(datetime.datetime.now()) + ": " + m.chat.first_name) + " [" + str(
                    m.chat.id) + "]: " + m.text)


bot.set_update_listener(listener)  # register listener


@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        # bot.send_message(cid, "Hello, stranger, let me scan you...")
        # bot.send_message(cid, "Scanning complete, I know you now")
        command_help(m)  # show the new user the help page
    else:
        # bot.send_message(cid, "I already know you, no need for me to scan you again!")
        command_help(m)  # show the new user the help page


# func=lambda message: get_user_step(message.chat.id) == 1
@bot.message_handler(commands=usersDownloadCommand.keys())
def command_download(m):
    cid = m.chat.id
    line = re.sub('[/]', '', m.text)

    userStep[cid] = 2

    # opener = urllib.request.build_opener()
    # request = urllib.request.Request(usersDownloadCommand[line])
    # u = opener.open(request)
    # link = u.geturl()
    # site = urllib.request.urlopen(link)
    # size = site.info().get('Content-Length')
    size = usersDownSize[line]
    if size is None:
        size = 0
    size = float(size)  # in bytes
    size = size / 1024.0  # in KB (Kilo Bytes)
    size = size / 1024.0  # size in MB (Mega Bytes)

    dwTypeSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
    if size < 50:
        dwTypeSelect.row("Direct Link via VK" + emoji.emojiCodeDict[":link:"], "As File")
    else:
        dwTypeSelect.row("Direct Link via VK" + emoji.emojiCodeDict[":link:"])
    lastChoosedFile[cid] = line
    bot.send_message(cid,
                     "Выбери способ загрузки. " + '\n' + "Учти,если ВК заблокирован,то скачать по ссылке будет "
                                                         "невозможно(кроме VPN).", parse_mode="HTML",
                     reply_markup=dwTypeSelect)


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 2)
def msg_step_two(message):
    cid = message.chat.id
    text = message.text
    bot.send_chat_action(cid, 'typing')
    if text == "Direct Link via VK" + emoji.emojiCodeDict[":link:"]:

        text = "Вы получили пряму ссылку на скачивание." + "\n"
        size = usersDownSize[lastChoosedFile[cid]]
        size = float(size)  # in bytes
        size = size / 1024.0  # in KB (Kilo Bytes)
        size = size / 1024.0  # size in MB (Mega Bytes)
        text += "Имя фаила: " + "<b>" + usersDownTitle[lastChoosedFile[cid]] + "</b>" + "\n"
        text += "Размер фаила:" + "<b>" + " " "%.3f" % size + "MB" + "</b>" + "\n"
        bot.send_message(cid, usersDownLink[lastChoosedFile[cid]], parse_mode="HTML", reply_markup=hideBoard)
        userStep[cid] = 0
    elif text == "As File":
        text = "Фаил загружается и вскоре будет отправлен вам." + "\n"
        size = usersDownSize[lastChoosedFile[cid]]
        size = float(size)  # in bytes
        size = size / 1024.0  # in KB (Kilo Bytes)
        size = size / 1024.0  # size in MB (Mega Bytes)
        text += "Имя фаила: " + "<b>" + usersDownTitle[lastChoosedFile[cid]] + "</b>" + "\n"
        text += "Размер фаила:" + "<b>" + " " "%.3f" % size + "MB" + "</b>" + "\n"
        bot.send_message(cid, text, parse_mode="HTML", reply_markup=hideBoard)
        title = str(usersDownTitle[lastChoosedFile[cid]])
        line = title.split('.')
        file_name = slugify(line[0])
        if file_name is None:
            file_name = line[0]
        ext = usersDownExt[lastChoosedFile[cid]]
        urllib.request.urlretrieve(usersDownLink[lastChoosedFile[cid]], file_name + "." + ext)
        ###До сюда всё работает
        doc = open(file_name + "." + ext, 'rb')
        bot.send_document(message.from_user.id, doc, reply_markup=hideBoard)
        doc.close()
        os.remove(file_name + "." + ext)
        # bot.send_message(cid, usersDownLink[lastChoosedFile[cid]],reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid,
                         emoji.emojiCodeDict[":no_entry_sign:"] + "Не вводи всякую глупость,если я даю тебе кнопки!" +
                         emoji.emojiCodeDict[":no_entry_sign:"])
        bot.send_message(cid,
                         emoji.emojiCodeDict[":no_entry_sign:"] + "Нажмите на одну из кнопок." + emoji.emojiCodeDict[
                             ":no_entry_sign:"])


@bot.message_handler(commands=['help'])
def command_help(m):
    help_text = "Доступные следующие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    pass
    help_text = help_text + "\n" + "Для взаимодействия с ботом,просто отправь мне свой поисковый запрос,дальше выбери тип фаила," \
                                   "и способ загрузки." + "\n" + "Бот позволяет загружать фаилы из Вконтакте объёмом до 50МБ,и получать ссылки на все фаилы вне зависимости от объёма."
    bot.send_message(m.chat.id, help_text)  # send the generated help page


# @bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def show_keybord(message):
    cid = message.chat.id
    typeSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard

    typeSelect.row("Show All", "Docs" + emoji.emojiCodeDict[":page_facing_up:"])
    typeSelect.row("Books" + emoji.emojiCodeDict[":open_book:"], "Archives" + emoji.emojiCodeDict[":compression :"])
    typeSelect.row("Gif", "Pics" + emoji.emojiCodeDict[":frame_photo"])
    typeSelect.row("Audio" + emoji.emojiCodeDict[":musical_note:"], "Video" + emoji.emojiCodeDict[":video_camera:"])
    bot.send_message(cid, "Выбери тип фаила:", reply_markup=typeSelect)  # show the keyboard
    userStep[cid] = 1  # set the user to the next step (expecting a reply in the listener now)
    usersMessageSearchRequest[cid] = message.text


def pages_keyboard(offset, cid):
    """Формируем Inline-кнопки для перехода по страницам.
    """
    time.sleep(0.2)
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if usersCountFiles[cid] == 0:
        return hideBoard
    if offset > 1:
        btns.append(types.InlineKeyboardButton(
            text=emoji.emojiCodeDict[":arrow_left:"], callback_data='to_{}'.format(offset - 1)))
    if offset < (usersCountFiles[cid] / 5):
        btns.append(types.InlineKeyboardButton(
            text=emoji.emojiCodeDict[":arrow_right:"], callback_data='to_{}'.format(offset + 1)))
    keyboard.add(*btns)
    return keyboard  # возвращаем объект клавиатуры


@bot.callback_query_handler(func=lambda c: c.data)
def pages(c):
    """Редактируем сообщение каждый раз, когда пользователь переходит по
    страницам.
    """
    time.sleep(0.5)
    cid = c.message.chat.id
    try:
        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=generateAnswer(c.message, int(c.data[3:]), usersChoosedType[cid]),
            parse_mode='HTML',
            reply_markup=pages_keyboard(int(c.data[3:]), cid)),
    except:
        print("Error in inline method")


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_step_one(message):
    cid = message.chat.id
    text = message.text
    bot.send_chat_action(cid, 'typing')
    # todo добавить while`ы везде ,чтобы избежать вылета полноценного
    # todo утечка памяти при большом кол-ве пользователей,ибо надо хранить все ссылки на все фаилы

    if text == "Docs" + emoji.emojiCodeDict[
        ":page_facing_up:"]:
        try:
            usersChoosedType[cid] = 1  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(1))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    #####################2222222222222222222
    elif text == "Archives" + emoji.emojiCodeDict[":compression :"]:
        try:
            usersChoosedType[cid] = 2  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(2))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    ###########################3333333333333333333
    elif text == "Gif":
        try:
            usersChoosedType[cid] = 3  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(3))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    #########44444444444444444444
    elif text == "Pics" + emoji.emojiCodeDict[":frame_photo"]:
        try:
            usersChoosedType[cid] = 4  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(4))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    ###########555555555555555555555555555555555555555555
    elif text == "Audio" + emoji.emojiCodeDict[":musical_note:"]:
        try:
            usersChoosedType[cid] = 5  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(5))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    ###########666666666666666666666666666
    elif text == "Video" + emoji.emojiCodeDict[":video_camera:"]:
        try:
            usersChoosedType[cid] = 6  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(6))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    #########################7777777777777777777777777
    elif text == "Books" + emoji.emojiCodeDict[":open_book:"]:
        try:
            usersChoosedType[cid] = 8  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(8))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    ##########88888888888888888888
    elif text == "Show All":
        try:
            usersChoosedType[cid] = 9  # !!!!!!!!!!!!!!
            bot.send_message(message.from_user.id, "Надеюсь,тут есть,то что тебе нужно.", reply_markup=hideBoard)
            cid = message.chat.id
            generated_answer = generateAnswer(message, 1, int(9))
            bot.send_chat_action(message.from_user.id, 'typing')
            bot.send_message(message.from_user.id, generated_answer, parse_mode='HTML',
                             reply_markup=pages_keyboard(1, cid))
            userStep[cid] = 0  # reset the users step back to 0
        except:
            bot.send_message(message.from_user.id,
                             "Что-то сломалось,скоро починю." + emoji.emojiCodeDict[":pensive:"] + "\n")
            userStep[cid] = 0
        pass
    #############AAAAAAAAAAAAAAAAALLLLLLLLLLLLLLLLLLLLL
    elif text == "pussy":
        bot.send_photo(message.from_user.id, open('kitten.jpg', 'rb'), reply_markup=hideBoard)
        userStep[cid] = 1
    else:
        bot.send_message(cid,
                         emoji.emojiCodeDict[":no_entry_sign:"] + "Не вводи всякую глупость,если я даю тебе кнопки!" +
                         emoji.emojiCodeDict[":no_entry_sign:"])
        bot.send_message(cid,
                         emoji.emojiCodeDict[":no_entry_sign:"] + "Нажмите на одну из кнопок." + emoji.emojiCodeDict[
                             ":no_entry_sign:"])


@bot.message_handler(content_types=['text'])
def handle_text(message):
    isGone = True
    while (isGone):
        try:
            bot.send_chat_action(message.from_user.id, 'typing')
            cid = message.chat.id
            text = message.text
            apiConnection = getApiConnection()
            seachq = urllib.parse.quote(message.text)
            url = '/method/docs.search?q=' + seachq + '&count=' + '1000' \
                  + '&offset=' + '1' + '&access_token=' + constants.tokenVK + '&v=5.64'
            try:
                usersVKresponse[cid] = vkResponse = vkRequest(apiConnection, url).get("response", 0)
                usersIsAlreadySearched[cid] = True
            except (ConnectionError, http.client.BadStatusLine) as e:
                apiConnection.close()
            try:
                bot.send_chat_action(message.from_user.id, 'typing')  # show the bot "typing" (max. 5 secs)
                time.sleep(0.2)
                count = vkResponse.get("count")
                if count == 0:
                    bot.send_message(message.from_user.id,
                                     emoji.emojiCodeDict[":no_entry_sign:"] + "Прости,но я ничего не нашёл")
                    isGone = False
                else:
                    bot.send_message(message.from_user.id,
                                     "Я нашёл " + str(
                                         count) + " фаилов. " + "Доступны первые 1000 результатов." + "\n" + "Ну что,давай отсортируем их?")
                    show_keybord(message)
                    isGone = False
                pass
            except:
                print("\n" + url)
                print("\n" + vkResponse)
        except:
            bot.send_message(message.from_user.id, "Что-то сломалось,скоро починю.")
            pass
    pass


bot.polling(none_stop=True, interval=0)
