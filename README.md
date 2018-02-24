# Vk-to-telegram-transfer-bot

### Описание
Многофункциональный, написанный одной ногой на питоне бот для пересылки сообщений из ВК в Telegram и наоборот. Изначально он планировался исключительно для личного пользования, однако я передумал и решил выложить в общий доступ в связи с тем, что, возможно, он может кому-то понадобиться.

### Возможности:
  - Пересылка текстовых сообщений из ВК в Telegram и наоборот
  - Пересылка изображений/стикеров/аудио/видео/документов/голосовых сообщений (Только из ВК в Telegram!)
  - Пересылка стикеров из Telegram в ВК
  - Поддержка личных сообщений и групповых чатов
  - Удобный файл конфигурации
  - Пока что всё, но список будет пополняться ¯\_(ツ)_/¯

### Установка
Для работы вам понадобиться:

- [Python 3](https://https://www.python.org/ftp/python/3.4.6/Python-3.4.6.tgz) ( лично я использовал 3.4.6 )
-  Git клиент ( я использую [Git Bash](https://https://git-scm.com/download/win ) )
- Аккаунт в ВК ( будем использовать в   качестве ботинка )
- Бот в Telegram ( можно создать через [BotFather](https://t.me/BotFather) )
- (При желании) Хостинг, на котором будет работать бот (Например, PythonAnywhere)

Для начала займёмся установкой скрипта. Открываем Git и пишем:

```sh
git clone https://github.com/Whiletruedoend/Vk-to-telegram-transfer-bot
pip3 install -r requirements.txt
или же (если вдруг не сработало):
python -m pip install -r requirements.txt
```

Внимание! Бот не проверялся на Linux'e, так что может работать некорректно!

### Настройка бота
Все настройки будут производиться в файле config.py
Для начала откроем его и вставим логин и пароль от аккаунта в ВК (таблицы ‘vk_login’ и ‘vk_password’ ) и токен бота в Telegram’e ( таблица ‘telegram_token’ )

Далее мы будем настраивать чат для передачи сообщений. Для этого необходимо:
1)	Создать чат в Telegram’e
2)	Добавить туда бота
3)	Написать ‘Дай ID’, после чего бот должен написать вам ID чата
4)	Взять ID чата/пользователя, откуда/куда будут пересылаться сообщения
5)	Добавить в конфиг поля:
```sh
	setCell( "vk_<chatid/userid>", '-<telegramid>' )
	setCell( "t_-<telegramid>", '<chatid/userid>' )
```
, где <chatid/userid> - локальный ID чата для бота (!), либо ID пользователя, с которым будет связан чат в Telegram’e, а -<telegramid> - тот самый ID чата, который мы получили, прописав команду ‘Дай ID’. Отбратите внимание, что -<telegramid> всегда идёт с минусом в начале, кроме того, знаки <> прописывать не нужно!
‘Живой пример’:

```sh
	setCell( "vk_1", '-249416176' )
	setCell( "t_-249416176", '1' )
```
Здесь мы видим, что для аккаунта ВК из чата 1 все сообщения будут пересылаться в чат '-249416176' в Telegram, и наоборот. Надеюсь, всё понятно, по какому принципу нужно всё делать.
P.S. Я дальнейшем я планирую облегчить систему создания тоннелей ВК <===> телега, но, пока что, пусть всё останется так.

### Важно!

У бота в Telegram должен быть:

1) Отключен режим приватности ( Bot Father —> Ваш бот —> Bot Settings —> Group Privacy —> Turn **Off** )
2) Включена поддержка групповых чатов ( Bot Father —> Ваш бот —> Bot Settings —> Allow groups? Turn groups **On** )


[Пример настройки бота (Видео)](https://my.mixtape.moe/yyobxs.mp4)

### Планы на будущее
 - ~~Доработать отправку картинок ( Сейчас устроено так, что если отправлено несколько фоточек в ВК, то в телегу придёт только первая)~~ *Done!*
 - ~~Улучшить отображение пересланных сообщений ( сейчас это еле работает, спасибо хоть на этом)~~ *Done!*
 - ~~Сделать реагирование на различные события (Ex. при обновлении аватарки чата в ВК, инвайте/кике пользователя, бот оповещал об этом в Telegram )~~ *Done!*
 - ~~При отправке стикера из Telegram в ВК он конвертировался из формата webp в png и отправлялся как картинка ( Я уже знаю как это можно сделать, но не могу найти годный конвертер )~~ *Done!*
 - Настроить передачу картинок/видео/файлов/документов из Telegram в ВК
 - На самом деле планов дофига, но было бы неплохо сделать хотя бы это...
 
### Обратная связь
Если у вас есть какие-то идеи или собственные наработки, или же просто вопросы по поводу работоспособности кода, то вы всегда можете обратиться ко мне по следующим адресам:
- [Telegram](https://t.me/Whiletruedoend)
- [Discord](https://discord.gg/aQ97ndF)

### Скриншоты

![Скриншот 1](https://i.imgur.com/87oOXs4.gif)

![Скриншот 2](https://i.imgur.com/5VOyeLb.png)