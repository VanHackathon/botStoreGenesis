import shopify
import sys
import os
import json
from sets import Set

print('rodou algo')


SHOP_NAME = 
API_KEY = 
PASSWORD = 

shop_url = "https://%s:%s@%s.myshopify.com/admin" % (API_KEY, PASSWORD,SHOP_NAME)
shopify.ShopifyResource.set_site(shop_url)


# Get the current shop
shop = shopify.Shop.current()

print(shop)
# Get a specific product
products = shopify.Product.find()

print(products)

count = shopify.Product.count()

print('count={}',count)


product_types = Set()
    
for product in products:
    string = product.to_json()
    data = json.loads(string)
    product_types.add(data['product']['product_type'])
    print(data['product']['title'])





