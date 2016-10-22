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
        self.products = shopify.Product.find()
        self.productsNames = []
        for product in self.products:
            string = product.to_json()
            data = json.loads(string)
            self.productsNames.append(data['product']['title'])
            self.product_types.add(data['product']['product_type'])

        self.currentNameStr = ''
        self.currentTypeStr = ''
        self.currentDetailStr = ''
        self.currentPriceStr = ''

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if chat_type == 'private' and content_type == 'text':
            text = msg['text']
            # Start store
            if text == '/create' or text == '/start' or text == 'Cancel':   #user may be restarting flow
                self.currentNameStr = ''
                self.currentTypeStr = ''
                self.currentDetailStr = ''
                self.currentPriceStr = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='List Categories')]], one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Welcome to {}! - What do you want to do?'.format(self.shopName), reply_markup=markup)                                

            # List Products Categories
            elif text == 'List Categories':
                # text=''
                keyboardbuttons = []
                for types in self.product_types:
                    keyboardbuttons.append([KeyboardButton(text=types)])
                markup = ReplyKeyboardMarkup(keyboard=keyboardbuttons, one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Choose the product type:', reply_markup=markup)
                
            # Show Category Product
            # elif text in self.product_types:
            #     keyboardCurrentProductsBtns = []
            #     for product in self.products:
            #         string = product.to_json()
            #         data = json.loads(string)
            #         if data['product']['product_type'] == text:
            #             keyboardCurrentProductsBtns.append([KeyboardButton(text=data['product']['title'])])
            #     # text = ''
            #     markup = ReplyKeyboardMarkup(keyboard=keyboardCurrentProductsBtns, one_time_keyboard=True)
            #     bot.sendMessage(chat_id, 'Choose product: ', reply_markup=markup)

            # Show Category Product As Texts
            elif text in self.product_types:
                bot.sendMessage(chat_id, 'Click on product code to select: ')

                for product in self.products:
                    string = product.to_json()
                    data = json.loads(string)
                    if data['product']['product_type'] == text:
                        image = data['product']['image']
                        print image
                        if image != None:
                            imageURL = data['product']['image']['src']
                            bot.sendPhoto(chat_id, imageURL, caption=data['product']['title'] + '\n' + '/' + str(data['product']['id']) + '\n' + data['product']['variants'][0]['price'])
                        else:
                            bot.sendMessage(chat_id, data['product']['title'] + '\n' + '/'+str(data['product']['id'])
                                            + '\n' + data['product']['variants'][0]['price'])

            # Show Product Details
            elif text in self.productsNames:
                # Name: title
                #
                # Type: product_type
                #
                # Details: body_html
                #
                # Price:$variants[0].price
                #
                # Buy  button
                for product in self.products:
                    string = product.to_json()
                    data = json.loads(string)

                    if data['product']['title'] == text:
                        self.currentNameStr = text
                        self.currentTypeStr = data['product']['product_type']
                        self.currentDetailStr = data['product']['body_html']
                        self.currentPriceStr = data['product']['variants'][0]['price']

                # text = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Pay')]], one_time_keyboard=True)

                detailedString = 'Item: ' + self.currentNameStr \
                                 + '\nType: ' + self.currentTypeStr \
                                 + '\nDetails: ' + self.currentDetailStr \
                                 + '\nPrice: $' + self.currentPriceStr
                bot.sendMessage(chat_id, detailedString, reply_markup=markup)

            # Show Product Details By Code
            elif text[0] == '/': #remember to put all / commands before this elif
                # Name: title
                #
                # Type: product_type
                #
                # Details: body_html
                #
                # Price:$variants[0].price
                #
                # Buy  button
                productById = shopify.Product.find(text[1:])
                string = productById.to_json()
                data = json.loads(string)

                self.currentNameStr =  data['product']['title']
                self.currentTypeStr = data['product']['product_type']
                self.currentDetailStr = data['product']['body_html']
                self.currentPriceStr = data['product']['variants'][0]['price']

                # text = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Pay')]], one_time_keyboard=True)

                detailedString = 'Item: ' + self.currentNameStr \
                                 + '\nType: ' + self.currentTypeStr \
                                 + '\nDetails: ' + self.currentDetailStr \
                                 + '\nPrice: $' + self.currentPriceStr
                bot.sendMessage(chat_id, detailedString, reply_markup=markup)


            # Show Payment Confirmation Question
            elif text == 'Pay':
                # text = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Confirm'),KeyboardButton(text='Cancel')]], one_time_keyboard=True)

                confirmationString = 'Item: ' + self.currentNameStr + ' $' + self.currentPriceStr \
                                     + '\n\nConfirm purchase?'
                bot.sendMessage(chat_id, confirmationString, reply_markup=markup)

            # Show Payment Confirmation Question
            elif text == 'Confirm':
                # text = ''
                bot.sendMessage(chat_id, 'Thanks for buying at {}, your {} will be delivered at your address!'.format(self.shopName,self.currentNameStr ))

            #if text != None and text != '':
                #bot.sendMessage(chat_id=chat_id, text=text)



#keep this order
#API_KEY = sys.argv[1]
API_KEY = "f0238210a5210edbd943d49526cba54e"
#PASSWORD = sys.argv[2]
PASSWORD = "f50bd1e9c9e87befc956ac0677acd359"
#SHOP_NAME = sys.argv[3]
SHOP_NAME = "vanhackathonstore-2"
#TOKEN = sys.argv[4]
TOKEN="260558085:AAFXp5xENhne000dQm9t2Iv8ksq8_XK7ySU"


bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, CreateShopBot, timeout=sys.maxint),
])

bot.message_loop()

print 'Listening...'
while True:
    time.sleep(10)
    
