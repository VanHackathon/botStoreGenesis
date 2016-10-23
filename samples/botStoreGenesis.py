import shopify
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
import sys
import os
import json
import time
from sets import Set
import re
from geopy.geocoders import Nominatim

emoji_page_with_curl = u'\U0001F4C3'
emoji_memo = u'\U0001F4DD'
emoji_credit_card = u'\U0001F4B3'
emoji_white_check_mark = u'\u2705'
emoji_x = u"\u274C"
emoji_convenience_store = u"\U0001F3EA"
emoji_world_map = u"\U0001F5FA"

#can_postcode = r'/^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/'
#can_add = r'[ABCEGHJKLMNPRSTVXY]\d[A-Z] \d[A-Z]\d'
#us_postcode = r'^\d{5}(?:[-\s]\d{4})?$'
#us_add = r'\b\d{1,3}(?:\s[a-zA-Z\u00C0-\u017F]+)+'


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

        self.currentProductIndex = 0
        self.maxProductPage = 5
        self.previousType = ''

    @staticmethod
    def remove_tags(text):
        return re.compile(r'<[^>]+>').sub('', text)

    def print_products(self, chat_id, type, startIndex):
        count = 0
        maxidx = 0
        # print('startIndex:{}'.format(startIndex))
        for idx, product in enumerate(self.products[startIndex:]):
            # print(idx, product)
            maxidx = idx
            # for product in self.products:
            if count < self.maxProductPage:
                string = product.to_json()
                data = json.loads(string)
                # print('type:{}'.format(type))
                if data['product']['product_type'] == type:
                    count += 1
                    # print(count)
                    image = data['product']['image']
                    if image != None:
                        imageURL = data['product']['image']['src']
                        bot.sendPhoto(chat_id, imageURL, caption=data['product']['title'] + '\n' + '/Code' + str(
                            data['product']['id']) + '\n$' + data['product']['variants'][0]['price'])
                    else:
                        bot.sendMessage(chat_id, data['product']['title'] + '\n' + '/Code' + str(data['product']['id'])
                                        + '\n$' + data['product']['variants'][0]['price'])
                if count == self.maxProductPage:
                    self.currentProductIndex = idx + startIndex
        if count == self.maxProductPage and maxidx > self.currentProductIndex:
            markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='More Products')]],
                                         one_time_keyboard=True)
            bot.sendMessage(chat_id, 'Click \"More Products\" to view more ', reply_markup=markup)

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        print(msg)

        if chat_type == 'private' and (content_type == 'text' or content_type == 'location'):
            text = ""
            if content_type == 'text': text = msg['text']
            # Start store
            if text == '/create' or text == '/start' or text == emoji_x+' Cancel':   #user may be restarting flow
                self.currentNameStr = ''
                self.currentTypeStr = ''
                self.currentDetailStr = ''
                self.currentPriceStr = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_memo+' List Categories')]], one_time_keyboard=True)
                bot.sendMessage(chat_id, 'Welcome to {} '.format(self.shopName) + emoji_convenience_store + ' - What do you want to do?', reply_markup=markup)

            # List Products Categories
            elif text == emoji_memo+' List Categories':
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
            elif text != "" and (text in self.product_types or text == 'More Products'):
                bot.sendMessage(chat_id, 'Click on product code to select: ')
                if text != 'More Products':
                    self.previousType = text
                    self.currentProductIndex = 0
                else:
                    self.currentProductIndex += 1
                self.print_products(chat_id, self.previousType, self.currentProductIndex)

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
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_credit_card+' Pay')]], one_time_keyboard=True)

                detailedString = 'Item: ' + self.currentNameStr \
                                 + '\nType: ' + self.currentTypeStr \
                                 + '\nDetails: ' + CreateShopBot.remove_tags(self.currentDetailStr) \
                                 + '\nPrice: $' + self.currentPriceStr
                bot.sendMessage(chat_id, detailedString, reply_markup=markup)

            # Show Product Details By Code
            elif text[:5] == '/Code': #remember to put all / commands before this elif
                # Name: title
                #
                # Type: product_type
                #
                # Details: body_html
                #
                # Price:$variants[0].price
                #
                # Buy  button

                bot.sendChatAction(chat_id=chat_id, action='typing')

                productById = shopify.Product.find(text[5:])
                string = productById.to_json()
                data = json.loads(string)

                self.currentNameStr =  data['product']['title']
                self.currentTypeStr = data['product']['product_type']
                self.currentDetailStr = data['product']['body_html']
                self.currentPriceStr = data['product']['variants'][0]['price']

                # text = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_credit_card+' Pay')]], one_time_keyboard=True)

                detailedString = 'Item: ' + self.currentNameStr \
                                 + '\nType: ' + self.currentTypeStr \
                                 + '\nDetails: ' + CreateShopBot.remove_tags(self.currentDetailStr) \
                                 + '\nPrice: $' + self.currentPriceStr
                bot.sendMessage(chat_id, detailedString, reply_markup=markup)


            # Show Shipping Addresses
            elif text == emoji_credit_card+' Pay' or text == emoji_x+ ' Wrong Address':
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_world_map + ' My Default Address'), KeyboardButton(text=emoji_world_map + ' Choose a Location'), KeyboardButton(text=emoji_world_map + ' Send Your Current Location', request_location=True)]], one_time_keyboard=True)

                addressString = "Where Should we Ship to?"
                bot.sendMessage(chat_id, addressString, reply_markup=markup)

            # Wait For Location
            elif text == emoji_world_map+ ' Choose a Location':
                # clear keyboard

                addressString = 'Ok, send me the location'
                bot.sendMessage(chat_id, addressString) # Wait For Location

            # My Addresses
            #elif text == emoji_temp + ' My Addresses':

             #   markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_temp + ' Address #1'),  KeyboardButton(text=emoji_temp + ' Address #2'), KeyboardButton(text=emoji_temp + ' Address #3')]], one_time_keyboard=True)

              #  addressString = "Where Should we Ship to?"
               # bot.sendMessage(chat_id, addressString, reply_markup=markup)

            # Write Address
            #elif text == emoji_temp + ' Write Address':
            # clear keyboard

            #   addressString = 'Ok, write me your address.'
            #    bot.sendMessage(chat_id, addressString) # Wait For Location

            # Write Zipcode
            #elif re.search(can_postcode, text)
                #    # clear keyboard

                #geolocator = Nominatim()
                #location = geolocator.geocode(text)

                #locationString = 'Cool'
                #bot.sendMessage(chat_id, locationString) # Wait For Location

            # Location sent
            elif content_type == 'location':
                # clear keyboard
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_white_check_mark + ' Correct Address'), KeyboardButton(text=emoji_x + ' Wrong Address')]], one_time_keyboard=True)
                geolocator = Nominatim()
                latiLong = str(msg['location']['latitude']) +", " + str(msg['location']['longitude'])
                location = geolocator.reverse(latiLong)

                bot.sendMessage(chat_id, "Is the following address correct?\n\n" + location.address, reply_markup=markup)

            # Show Payment Confirmation Question
            elif text == emoji_white_check_mark + ' Correct Address' or emoji_world_map+ " My Default Address" in text: #or re.search(can_add, text) or re.search(us_add, text):
                # text = ''
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=emoji_white_check_mark+' Confirm'),KeyboardButton(text=emoji_x+' Cancel')]], one_time_keyboard=True)

                confirmationString = 'Item: ' + self.currentNameStr + ' $' + self.currentPriceStr \
                                     + '\n\nConfirm purchase?'
                bot.sendMessage(chat_id, confirmationString, reply_markup=markup)

            # Show Payment Confirmation Question
            elif text == emoji_white_check_mark+' Confirm':
                # text = ''
                bot.sendMessage(chat_id, 'Thanks for buying at {} '.format(self.shopName) + emoji_convenience_store
                                + ', your {} will be delivered at your address!'.format(self.currentNameStr))

            #if text != None and text != '':
                #bot.sendMessage(chat_id=chat_id, text=text)



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
