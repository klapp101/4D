import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import json
import time

class Stockx:
    def __init__(self):
        pass
    def stockx_get_products(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
          'referer': 'https://google.com',
          'content-type': 'application/json; charset=utf-8',
          'server': 'cloudflare'}

        url = 'https://stockx.com/api/browse?_search=4d&browseVerticals=sneakers&country=US&dataType=product&filterVersion=4&order=DESC&sort=release_date&page=1'
        continue_page = True
        sneaker_titles = []
        sneaker_release_dates = []
        sneaker_retail_prices = []
        sneaker_skus = []
        sneaker_models = []
        sneaker_colorways = []

        while continue_page:
            r = requests.get(url,headers=headers)
            response_json = r.json()

            products = response_json['Products']
            for i in products:
                title = i['title']
                release_date = i['releaseDate']
                colorway = i['colorway']
                retail_price = i['retailPrice']
                sku = i['styleId']
                sneaker_model = i['shoe']
                sneaker_titles.append(title)
                sneaker_release_dates.append(release_date)
                sneaker_retail_prices.append(retail_price)
                sneaker_skus.append(sku)
                sneaker_models.append(sneaker_model)
                sneaker_colorways.append(colorway)
            next_page = response_json['Pagination']['nextPage']
            url = 'https://stockx.com' + str(next_page)
            url = url.replace("v3/", "" )
            if url == 'https://stockx.comNone':
                continue_page = False


        sneakers = [sneaker_titles, sneaker_release_dates, sneaker_retail_prices, sneaker_skus, sneaker_models, sneaker_colorways]
        df = pd.concat([pd.Series(x) for x in sneakers], axis=1)
        df.rename(columns={0:'Sneaker_Name',1:'Release_Date',2:'Retail_Price',3:'SKU',4:'Sneaker_Model',5:'Sneaker_Colorway'},inplace=True)
        df.to_csv('4d_stockx_inventory.csv',index=False)

s = Stockx()
s.stockx_get_products()