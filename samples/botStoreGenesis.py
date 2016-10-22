import shopify
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
import sys
import os
import json
import time
from sets import Set


class CreateShopBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # Connect to Shopify to get shop
        shop_url = "https://%s:%s@%s.myshopify.com/admin" % (API_KEY, PASSWORD,SHOP_NAME)
        shopify.ShopifyResource.set_site(shop_url)

        # Get the current shop name
        self.shopName = ''
        shop = shopify.Shop.current()
        self.jsonShop = json.loads(shop.to_json())
        self.shopName = self.jsonShop['shop']['name']
                
        # Get all categories to create menu
        self.product_types = Set()
        products = shopify.Product.find()                
        for product in products:
            string = product.to_json()
            data = json.loads(string)
            self.product_types.add(data['product']['product_type'])

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if chat_type == 'private' and content_type == 'text':
            text = msg['text']
            # Start store
            if text == '/create' or text == '/start':   #user may be restarting flow
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='List Categories')]], one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Welcome to {}! - What do you want to do?'.format(self.shopName), reply_markup=markup)                                

            # List Products Categories
            elif text == 'List Categories':
                text=''
                keyboardbuttons = []
                for types in self.product_types:
                    keyboardbuttons.append([KeyboardButton(text=types)])
                markup = ReplyKeyboardMarkup(keyboard=keyboardbuttons, one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Choose the product type:', reply_markup=markup)
                
            # Show Category Product
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
    
