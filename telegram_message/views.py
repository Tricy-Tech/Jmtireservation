from django.conf import settings
from django.shortcuts import render
from telegram import Bot

def send_telegram_message(request):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = '99782817'
    message = "Hello from Django!"

    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

    return render(request, 'message_sent.html')

import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events
 
  
# get your api_id, api_hash, token
# from telegram as described above
def telegram_sent(request):
    
    api_id = '28470437'
    api_hash = '86bced47d85337597d210b0d2acd663a'
    token = '6162722753:AAGx7st0uowpSD39G6hUYFLZcQ7LHmiGCv8'
    message = "Hello from Django!"
    
    # your phone number
    phone = '601120649735'
    
    # creating a telegram session and assigning
    # it to a variable client
    client = TelegramClient('session', api_id, api_hash)
    
    # connecting and building the session
    client.connect()
    
    # in case of script ran first time it will
    # ask either to input token or otp sent to
    # number or sent or your telegram id
    if not client.is_user_authorized():
    
        client.send_code_request(phone)
        
        # signing in the client
        client.sign_in(phone, input('Enter the code: '))
    
    
    try:
        # receiver user_id and access_hash, use
        # my user_id and access_hash for reference
        receiver = InputPeerUser('user_id', 'user_hash')
    
        # sending message using telegram client
        client.send_message(receiver, message, parse_mode='html')
    except Exception as e:
        
        # there may be many error coming in while like peer
        # error, wrong access_hash, flood_error, etc
        print(e);
    
    # disconnecting the telegram session
    client.disconnect()
    
    return render (request, 'message_sent.html')
