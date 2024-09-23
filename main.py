#!/usr/lib/python3 python
# -*- coding: utf-8 -*-
import os
import sys
import config
import db
import random
import datetime
import vk_api
import telebot
import telebot.types as types
import threading
import traceback
import urllib.request as ur
import re
import time
import pprint
from vk_token import vk_token
from vk_token import tg_token
from PIL import Image  # Для преобразования изображений из webp в PNG

config.initConfig()

module = sys.modules[__name__]


# Код настоятельно рекомендуется читать снизу вверх!

#    _______        _     
#   |__   __|      | |    
#      | | ___  ___| |__  
#      | |/ _ \/ __| '_ \ 
#      | |  __/ (__| | | |
#      |_|\___|\___|_| |_|
#                         
#   Технические функции

# Получаем текущее время
def current_time():
    delta = datetime.timedelta(hours=3)
    utc = datetime.timezone.utc
    fmt = '%H:%M'
    time = (datetime.datetime.now(utc) + delta)
    timestr = time.strftime(fmt)
    return timestr


# Получение имени пользователя
def getUserName(msg):
    # Для приёма личных сообщений когда пишут через группу
    if int(msg.get('from_id')) < 0:
        return None
    else:
        dataname = module.vk.users.get(user_ids=msg.get('from_id'))
        name = str(dataname[0]['first_name'] + ' ' + dataname[0]['last_name'])
    return name


def getUserTName(msg):
    if msg.last_name is None:
        userName = str(msg.first_name)
    else:
        userName = str(msg.first_name + " " + msg.last_name)
    return userName


# Проверка на наличие аттачментов в сообщении
def checkAttachments(msg, idd):
    if not (msg.get('attachments')):
        return False
    transferAttachmentsToTelegram(idd, getAttachments(msg))
    return True


# Получаем аттачменты из сообщения ВК
def getAttachments(msg):
    attachList = []

    for att in msg['attachments'][0:]:

        attType = att.get('type')

        attachment = att[attType]

        if attType == 'photo':  # Проверка на тип фотографии
            for photoType in attachment.get('sizes')[0:]:
                if photoType.get('type') == 'x':  # <=604x604
                    attachments = photoType.get('url')
                if photoType.get('type') == 'y':  # >605x605
                    attachments = photoType.get('url')
                if photoType.get('type') == 'z':  # <=1280x720
                    attachments = photoType.get('url')
                if photoType.get('type') == 'w':  # >1280x720
                    attachments = photoType.get('url')  # <=2560x1440

        elif attType == 'doc':  # Проверка на тип документа:
            # Про типы документов можно узнать тут: https://vk.com/dev/objects/doc
            docType = attachment.get('type')
            if docType != 3 and docType != 4 and docType != 5:
                attType = 'other'
            if attachment.get('url'):
                attachments = attachment.get('url')

        elif attType == 'sticker':  # Проверка на стикеры:
            for sticker in attachment.get('images')[0:]:
                # Можно 256 или 512, но будет слишком огромная пикча
                if sticker.get('width') == 128:
                    attachments = sticker.get('url')

        elif attType == 'audio':
            attachments = str('𝅘𝅥𝅮 ' + attachment.get('artist') + ' - ' +
                              attachment.get('title') + ' 𝅘𝅥𝅮')
            attType = 'other'

        elif attType == 'audio_message':
            attachments = attachment.get('link_ogg')

        elif attType == 'video':

            ownerId = str(attachment.get('owner_id'))
            videoId = str(attachment.get('id'))
            accesskey = str(attachment.get('access_key'))

            fullURL = str(ownerId + '_' + videoId + '_' + accesskey)

            attachments = module.vk.video.get(videos=fullURL)['items'][0].get('player')

        elif attType == 'graffiti':
            attType = 'other'
            attachments = attachment.get('url')

        elif attType == 'link':
            attType = 'other'
            attachments = attachment.get('url')

        elif attType == 'wall':
            attType = 'other'
            attachments = 'https://vk.com/wall'
            from_id = str(attachment.get('from_id'))
            post_id = str(attachment.get('id'))
            attachments += from_id + '_' + post_id

        elif attType == 'wall_reply':
            attType = 'other'
            attachments = 'https://vk.com/wall'
            owner_id = str(attachment.get('owner_id'))
            reply_id = str(attachment.get('id'))
            post_id = str(attachment.get('post_id'))
            attachments += owner_id + '_' + post_id
            attachments += '?reply=' + reply_id

        elif attType == 'poll':
            attType = 'other'
            attachments = 'https://vk.com/poll'
            owner_id = str(attachment.get('owner_id'))
            poll_id = str(attachment.get('id'))
            attachments += owner_id + '_' + poll_id
        # Неизвестный тип?
        else:
            attachments = None

        attachList.append({'type': attType,
                           'link': attachments})

    # print( attachList )

    return attachList


# Проверка чата ВК на различные события
def checkEvents(msg, chatid):
    if not (msg['last_message'].get('action')):
        return None  # И так сойдёт

    event = msg['last_message']['action'].get('type')
    userName = getUserName(msg['last_message'])

    # Ниже проверям наш чат на различные события
    # См. https://vk.com/dev/objects/message

    if event == 'chat_title_update':
        eObject = str(msg['last_message']['action'].get('text'))
        mbody = " *** " + userName + " изменил(а) название беседы на " + eObject + " ***"

    elif event == 'chat_invite_user':
        dataname = module.vk.users.get(user_ids=msg['last_message']['action'].get('member_id'))
        eObject = str(dataname[0]['first_name'] + ' ' + dataname[0]['last_name'])
        mbody = " *** " + userName + " пригласил(а) в беседу " + eObject + " ***"

    elif event == 'chat_kick_user':
        dataname = module.vk.users.get(user_ids=msg['last_message']['action'].get('member_id'))
        eObject = str(dataname[0]['first_name'] + ' ' + dataname[0]['last_name'])
        mbody = " *** " + userName + " кикнул(а) из беседы " + eObject + " ***"

    elif event == 'chat_photo_update':
        mbody = " *** " + userName + " обновил(а) фото беседы: ***"

    elif event == 'chat_photo_remove':
        mbody = " *** " + userName + " удалил(а) фото беседы! ***"

    elif event == 'chat_pin_message':
        eObject = str(msg['last_message']['action'].get('message'))
        if (eObject):
            mbody = " *** " + userName + " закрепил(а): " + eObject + " ***"
        else:
            mbody = " *** " + userName + " закрепил(а) сообщение! ***"

    elif event == 'chat_unpin_message':
        mbody = " *** " + userName + " открепил(а) сообщение! ***"

    elif event == 'chat_create':
        print('Беседа была создана!')

    else:
        return None
    send_to_telegram(chatid, None, mbody, None, None)
    return 'NotNone'  # теперь точно не будет отсылать пустые сообщения


# Проверка на наличие перешлённых сообщений
def getFwdMessages(msg, idd):
    if not (msg.get('fwd_messages')):
        return None  # И так сойдёт

    fwdList = []
    fwdMsg = msg.get('fwd_messages')
    for f in fwdMsg:
        userName = getUserName(f)
        fwdList.append({'id': str(f.get('conversation_message_id')), 'body': f.get('text'), 'userName': userName})

        checkAttachments(f, idd)
    return fwdList


def getReplyMessage(msg, idd):
    if not (msg.get('reply_message')):
        return None

    print(f"getReplyMessage {msg.get('reply_message')}")

    replyId = str(msg.get('reply_message').get('conversation_message_id'))
    return replyId


#    _____          _ _               _
#   |  __ \        | (_)             | |      
#   | |__) |___  __| |_ _ __ ___  ___| |_ ___ 
#   |  _  // _ \/ _` | | '__/ _ \/ __| __/ __|
#   | | \ \  __/ (_| | | | |  __/ (__| |_\__ \
#   |_|  \_\___|\__,_|_|_|  \___|\___|\__|___/
#                                             
#  Функции, принимающие и отправляющие сообщения ВК <==> Telegram

def check_redirect_vk_to_telegram(msg):
    chatid = str(msg['conversation']['peer']['local_id'])
    print("checkRedirect_vk " + msg['last_message'].get('text'))

    # Проверка на существование переадресации в конфиге
    if not config.getCell("vk_" + chatid) is None:

        forwardMessage = getFwdMessages(msg['last_message'], chatid)
        replyMessage = get_reply_vk(msg['last_message'])
        messageId = str(msg['last_message'].get('conversation_message_id'))
        userName = getUserName(msg['last_message'])
        mbody = msg['last_message'].get('text')
        # Чтобы при событии не посылалось пустое сообщение

        if checkEvents(msg, chatid) is None:
            send_to_telegram(chatid, userName, mbody, forwardMessage, replyMessage)

        # Проверка на аттачменты, пересланные сообщения, видео...
        # Проверка сделана, чтобы исключить повтор картинки
        if forwardMessage is None:
            checkAttachments(msg['last_message'], chatid)

        return True
    return False


def get_reply_vk(message_data):
    try:
        replier = module.vk.users.get(user_ids=message_data['reply_message']["from_id"])[0]
        print(f"Reply: {replier['first_name']} {replier['last_name']}: {message_data['reply_message']['text']}")
        return f"<blockquote><b>{replier['first_name']} {replier['last_name']}</b>: {message_data['reply_message']['text']}</blockquote>"
    except Exception as e:
        # print(e)
        # print(traceback.format_exc())
        return None


def send_to_vk(chatid, text, fromUser, attachment):
    print("transferMessageToVK " + text)

    if config.getCell('telegram_SendName'):
        time = current_time()
        text = f'[{time} | {fromUser}]\n{text}'

    randid = random.randint(-9223372036854775808, +9223372036854775807)  # int64

    if text is None:
        text = ""

    if attachment is None:
        try:
            module.vk.messages.send(chat_id=config.getCell('t_' + chatid), message=text, random_id=randid)
        except vk_api.ApiError as error_msg:
            print(f'vk api error {error_msg}')
            module.vk.messages.send(user_id=config.getCell('t_' + chatid), message=text, random_id=randid)

    else:
        try:
            module.vk.messages.send(chat_id=config.getCell('t_' + chatid),
                                    message=text,
                                    attachment=upload_photo_vk(attachment),
                                    random_id=randid)
        except vk_api.ApiError as error_msg:
            print(f'vk api error {error_msg}')
            module.vk.messages.send(user_id=config.getCell('t_' + chatid),
                                    message=text,
                                    attachment=upload_photo_vk(attachment),
                                    random_id=randid)

    return False


def upload_photo_vk(photo):
    response = vk_api.VkUpload(module.vk).photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return f'photo{owner_id}_{photo_id}_{access_key}'


def check_redirect_telegram_to_vk(message, attachment):
    chatId = str(message.chat.id)
    fromUser = getUserTName(message.from_user)

    reply_name, reply_text = get_reply_telegram(message)

    print(f'reply {reply_name} {reply_text}')

    if reply_text is None:
        text = str(message.text or message.caption or '')
    else:
        text = f'>>>>>> {reply_name} <<\n{reply_text}\n>>>>>> \n{message.text}'

    print(f"checkRedirect_telegram {text}")

    if config.getCell('t_' + chatId) is not None:
        if config.getCell('telegram_SendOnlyFromMainTopic') and \
                getattr(message.chat, 'is_forum', False) and \
                getattr(message, 'is_topic_message', False):
            print("Not main topic, skip")
            return False

        if attachment is not None:
            print(f"download {attachment}")
            downloaded_file = module.bot.download_file(attachment)
            os.makedirs(os.path.dirname(attachment), exist_ok=True)
            with open(attachment, 'wb') as new_file:
                new_file.write(downloaded_file)

        send_to_vk(chatId, text, fromUser, attachment)

        if attachment is not None and os.path.exists(attachment):
            os.remove(attachment)

    return False


def get_reply_telegram(message):
    if message.reply_to_message is None:
        print('no reply_to_message')
        return None, None

    reply_message = message.reply_to_message
    if reply_message.forum_topic_created is not None:
        print(f'forum_topic_created {reply_message.forum_topic_created}')
        # todo remember topic
        return None, None

    name = getUserTName(reply_message.from_user)
    text = reply_message.text

    return name, text


# Посылаем простые сообщения в Telegram
# Идея: сделать в будущем наклонные столбики, теперь главное не забыть
def send_to_telegram(vk_chat_id, userName, mbody, fwdList, replyText):
    print("transferMessagesToTelegram " + mbody)

    tg_id = config.getCell('vk_' + vk_chat_id)
    tg_topic = config.getCell(f'topic_{tg_id}')

    if userName is None:
        if mbody:
            module.bot.send_message(tg_id, str(mbody), message_thread_id=tg_topic)
        return False

    time = current_time()

    timeText = f"<b>{userName}</b> <i>{time}</i>:"
    # niceText = str(time + ' | #msg' + msgId + ' | ' + userName + ': ' + mbody)

    if fwdList is not None:
        forwardText = ''
        for f in fwdList:
            forwardText = forwardText + f"<blockquote><b>{f.get('userName')}</b>: {f.get('body')}</blockquote>\n"

        module.bot.send_message(tg_id,
                                f"{timeText}\n{mbody}\n{forwardText}",
                                message_thread_id=tg_topic,
                                parse_mode="HTML")

    else:
        if replyText is not None:
            module.bot.send_message(tg_id,
                                    f"{timeText}\n{replyText}\n{mbody}",
                                    message_thread_id=tg_topic,
                                    parse_mode="HTML")
        else:
            module.bot.send_message(tg_id,
                                    f"{timeText}\n\n{mbody}",
                                    message_thread_id=tg_topic,
                                    parse_mode="HTML")


# И так сойдёт
def getVideoDirectLink(link, type):
    if type == 'videomessage':
        pattern = r'url480[^\,]+'
        response = ur.urlopen(link)
        html = response.read().decode(response.headers.get_content_charset())
        directLink = re.search(pattern, html).group(0)[9:-1].replace("\\/", "/")
    if type == 'video':
        pattern = r'url720[^\,]+'
        response = ur.urlopen(link)
        html = response.read().decode(response.headers.get_content_charset())
        directLink = re.search(pattern, html).group(0)[9:-1].replace("\\/", "/")

    return directLink


def transferAttachmentsToTelegram(idd, attachments):
    mediagr = []
    tg_id = config.getCell('vk_' + idd)
    tg_topic = config.getCell(f'topic_{tg_id}')

    for j in attachments[0:]:

        attType = j.get('type')
        link = j.get('link')

        if attType == 'photo' or attType == 'sticker':
            media = types.InputMediaPhoto(link)
            mediagr.append(media)

        elif attType == 'doc' or attType == 'gif' or attType == 'audio_message':
            module.bot.send_document(tg_id, link, message_thread_id=tg_topic)

        elif attType == 'other':
            module.bot.send_message(tg_id, link, message_thread_id=tg_topic)

        elif attType == 'video':

            # Потому что в ВК не может отправить полную ссылку на файл видео -_-
            try:
                # может если дать пинок костылём под жопу
                direct_link = getVideoDirectLink(link, 'videomessage')
                response = ur.urlopen(direct_link)
                if response.getcode() == 200:
                    videoMessage = response.read()
                    module.bot.send_video_note(tg_id, videoMessage, message_thread_id=tg_topic)
                else:
                    module.bot.send_message(tg_id, direct_link, message_thread_id=tg_topic)
            except:
                direct_link = getVideoDirectLink(link, 'video')
                media = types.InputMediaVideo(direct_link)
                mediagr.append(media)
            # на этом моменте я поставил этой функции свечку за здравие, ну а вдруг

        else:
            module.bot.send_message(tg_id, f'(Тут был {attType}, но мы его не умеем)', message_thread_id=tg_topic)
    if mediagr:
        module.bot.send_media_group(tg_id, mediagr, message_thread_id=tg_topic)

#   __      ___
#   \ \    / / |
#    \ \  / /| | __
#     \ \/ / | |/ /
#      \  /  |   < 
#       \/   |_|\_\
#                  
#


# При двухфакторной аутентификации вызывается эта функция
def auth_handler():
    key = input("Enter authentication code: ")
    # True - сохранить, False - не сохранять
    remember_device = True

    return key, remember_device


# Каптча
def captcha_handler(captcha):
    key = input("Enter Captcha {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)


def init_vk():
    login = config.getCell('vk_login')
    password = config.getCell('vk_password')
    app = config.getCell('app_id')
    token = vk_token

    print("login in vk as: " + login)
    # print("token " + token)

    global vk_session

    vk_session = vk_api.VkApi(login, app_id=app, token=token, auth_handler=auth_handler,
                              captcha_handler=captcha_handler)

    #	try:
    #		vk_session.auth(token_only=True)
    #	except vk_api.AuthError as error_msg:
    #		print( error_msg )
    #		print(traceback.format_exc())

    module.vk = vk_session.get_api()  # Важная штука

    input_vk()


def input_vk():
    last_message = 1
    while True:

        try:
            # Ставим онлайн боту, чому бы и нет?
            module.vk.account.setOnline()

            # Так надо
            time.sleep(config.getCell('sleepTime'))

            # Проверка на наличие подписчиков
            if (config.getCell('vk_AddFriends')):
                checknewfriends()
            rawMessages = module.vk.messages.getConversations(filter='unread')['items']
            if not rawMessages:
                continue
            msg = rawMessages[0]['conversation']['peer']
            if last_message != int(rawMessages[0]['conversation'].get('last_message_id')):
                if check_redirect_vk_to_telegram(rawMessages[0]):
                    last_message = int(rawMessages[0]['conversation'].get('last_message_id'))
                if config.getCell('vk_markAsReadEverything'):
                    module.vk.messages.markAsRead(messages_ids=msg['local_id'], peer_id=msg['id'])
            else:
                pass


        # Чтобы не вылетало, а работало дальше
        except BaseException as e:
            print(e)
            print(traceback.format_exc())
            print('Что-то пошло не так...')
            continue


#    _______   _                                
#   |__   __| | |                               
#      | | ___| | ___  __ _ _ __ __ _ _ __ ___  
#      | |/ _ \ |/ _ \/ _` | '__/ _` | '_ ` _ \ 
#      | |  __/ |  __/ (_| | | | (_| | | | | | |
#      |_|\___|_|\___|\__, |_|  \__,_|_| |_| |_|
#                      __/ |                    
#                     |___/                     


def listener(messages):
    for m in messages:
        pprint.pp(m.json)

        if m.content_type == 'text':
            # На команду 'Дай ID' кидает ID чата
            if m.text == 'Дай ID':
                module.bot.send_message(m.chat.id, str(m.chat.id))
                continue

            check_redirect_telegram_to_vk(m, None)

        elif m.content_type == 'sticker':

            if not (config.getCell('vk_EnableStickers')):
                return False

            print(f'sticker file {module.bot.get_file(m.sticker.file_id)}')
            filePath = module.bot.get_file(m.sticker.file_id).file_path
            check_redirect_telegram_to_vk(m, str(filePath))

        elif m.content_type == 'photo':
            print(f'photo file {module.bot.get_file(m.photo[-1].file_id)}')
            filePath = module.bot.get_file(m.photo[-1].file_id).file_path
            check_redirect_telegram_to_vk(m, str(filePath))

        else:
            m.caption = f"{m.caption}\nтут было {m.content_type}, но мы его пересылать не умеем"
            check_redirect_telegram_to_vk(m, None)


def init_telegram():
    module.bot = telebot.TeleBot(tg_token)
    print("Successfully loginned in telegram!")
    input_telegram()


def input_telegram():
    if (config.getCell('telegram_useProxy')):
        proxyType = str(config.getCell('p_type'))
        proxyUserInfo = str(config.getCell('p_user') + ':' + config.getCell('p_password'))
        proxyData = str(config.getCell('p_host') + ':' + config.getCell('p_port'))
        telebot.apihelper.proxy = {
            'http': '%s://%s@%s' % (proxyType, proxyUserInfo, proxyData),
            'https': '%s://%s@%s' % (proxyType, proxyUserInfo, proxyData)
        }

    module.bot.set_update_listener(listener)
    while True:  # Костыль на случай timeout'a
        try:
            module.bot.polling(none_stop=False)
        except BaseException as e:
            print(e)
            print(traceback.format_exc())
            print('Что-то пошло не так...')
            continue


#    ______               _
#   |  ____|             | |      
#   | |____   _____ _ __ | |_ ___ 
#   |  __\ \ / / _ \ '_ \| __/ __|
#   | |___\ V /  __/ | | | |_\__ \
#   |______\_/ \___|_| |_|\__|___/
#
# Проверка на различные события

# Проверка на заявки в друзья
def checknewfriends():
    newfriends = module.vk.friends.getRequests(out=0, count=1, need_viewed=1)  # Смотрим, если ли заявки в друзья
    if newfriends['count'] != 0:
        module.vk.friends.add(user_id=newfriends['items'])  # Добавляем человека в друзья


#     _____ _   _      _
#    / ____| | (_)    | |                
#   | (___ | |_ _  ___| | _____ _ __ ___ 
#    \___ \| __| |/ __| |/ / _ \ '__/ __|
#    ____) | |_| | (__|   <  __/ |  \__ \
#   |_____/ \__|_|\___|_|\_\___|_|  |___/
#                                        
#                                        

# Загрузка стикеров в ВК
def addStickerIntoVK(path, sticker):
    stickerList = []
    ourFile = path + sticker

    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo(ourFile + ".png", album_id=config.getCell('vk_album_id'))

    if (config.getCell('vk_detelestickers')):
        os.remove(ourFile + ".png")

    ourVK = 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])

    stickerList.append({'sticker_t': ourFile,
                        'sticker_vk': ourVK})

    return stickerList


def saveSticker(stickerURL, attachment):
    attachment = attachment.split('/')

    content = ur.urlopen(stickerURL).read()

    path = attachment[0] + '/'
    if not os.path.exists(path):
        os.makedirs(path)

    # Перекодирование из webp в png

    imageWebp = path + attachment[1]

    out = open(imageWebp, 'wb')
    out.write(content)
    out.close()

    img = Image.open(imageWebp)

    if (config.getCell('vk_sticker_EnableScale')):
        scale = config.getCell('vk_sticker_size')
        img.thumbnail((scale, scale))
    img.save(imageWebp + ".png", "PNG")
    os.remove(imageWebp)

    # print( 'Sticker saved!' )

    stickers = addStickerIntoVK(path, attachment[1])
    db.addStickerIntoDb(stickers)


# Разработчикам на заметку:
# Telegram та ещё поехавшая вещь, иногда аттачменты идут с расширением файла, иногда - без него
# Из-за этого я долго не мог понять, почему одни стикеры отправляются нормально, а другие - выдают ошибку при отправке

#    ______ _             _      
#   |  ____(_)           | |     
#   | |__   _ _ __   __ _| | ___ 
#   |  __| | | '_ \ / _` | |/ _ \
#   | |    | | | | | (_| | |  __/
#   |_|    |_|_| |_|\__,_|_|\___|
#                                
# Пихаем функции в потоки

t1 = threading.Thread(target=init_vk)
t2 = threading.Thread(target=init_telegram)

t1.start()
t2.start()
t1.join()
t2.join()
