import shopify
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
import sys
import os
import json
import time


class CreateShopBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if chat_type == 'private' and content_type == 'text':
            text = msg['text']
            if text == '/create' or text == '/start':   #user may be restarting flow
                text=''
                # Connect to Shopify to get shop
                shop_url = "https://%s:%s@%s.myshopify.com/admin" % (API_KEY, PASSWORD,SHOP_NAME)
                shopify.ShopifyResource.set_site(shop_url)
                
                # Get the current shop
                shop = shopify.Shop.current()
                print(shop)
                
                # Get all products to create menu
                products = shopify.Product.find()
                print(products)
                count = 0;

                keyboardbuttons = []
                
                for product in products:
                    string = product.to_json()
                    data = json.loads(string)
                    print(data['product']['title'])
                    keyboardbuttons.append([KeyboardButton(text=data['product']['title'])])
                    count = count+1;
    
                #text = 'Welcome to {}! - Choose an action below:'.format(data['product']['vendor'])
                #text = 'Welcome to {}! - Choose a product below:'.format(data['product']['vendor'])
            
                #markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Confirm')], [KeyboardButton(text='Cancel')]], one_time_keyboard=True)
                markup = ReplyKeyboardMarkup(keyboard=keyboardbuttons, one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Welcome to {}! - Choose a product below:'.format(data['product']['vendor']), reply_markup=markup)
            #elif self.shopify_api_key == '':
                #self.shopify_api_key = text
                #text = 'Great! Now send me your Shopify API password'

            if text != None and text != '':
                bot.sendMessage(chat_id=chat_id, text=text)



#keep this order
API_KEY = sys.argv[1]
PASSWORD = sys.argv[2]
SHOP_NAME = sys.argv[3]
TOKEN = sys.argv[4]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, CreateShopBot, timeout=sys.maxint),
])

bot.message_loop()

print 'Listening...'
while True:
    time.sleep(10)
    
