import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import json
import time

class AdidasChecker:
    def __init__(self):
        self.headers = {
            'authority': 'www.adidas.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'glassversion': 'c38d8d4',
            'referer': 'https://www.adidas.com/us/4dfwd-2-shoes/HQ1039.html',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'x-instana-l': '1,correlationType=web;correlationId=b3968a47ae8e95b1',
            'x-instana-s': 'b3968a47ae8e95b1',
            'x-instana-t': 'b3968a47ae8e95b1'
        }
    def catalog(self):
        self.skus = []
        next_page = True
        r = requests.get('https://www.adidas.com/us/4d-shoes', headers=self.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        sneakers = soup.find('div',class_='plp-grid___1FP1J')
        sneakers = soup.find_all('div', 'grid-item')
        for sneaker in sneakers:
            self.skus.append(sneaker['data-grid-id'])
            
        next_button = soup.find('div',class_='pagination___1AiDh')
        next_button = soup.find_all('a',class_='active')
        next_button_link = next_button[1].get('href')
        while next_page:
            url = 'https://www.adidas.com' + next_button_link
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.content, "html.parser")
            sneakers = soup.find('div',class_='plp-grid___1FP1J')
            sneakers = soup.find_all('div', 'grid-item')
            for sneaker in sneakers:
                self.skus.append(sneaker['data-grid-id'])
            if len(soup.find_all(text='Next')) > 0:
                continue
            else:
                next_page = False

        print('The number of 4D sneakers available in the Adidas Catalog: ' + str(len(self.skus)))

    def search(self):
        retail_prices = []
        sale_prices = []
        colorways = []
        special_launches = []
        special_launch_types = []

        for i in self.skus:
            item_details = f'https://www.adidas.com/api/search/product/{i}?sitePath=us'
            r = requests.get(item_details,headers=self.headers)
            response_json = r.json()
            retail_price = response_json['price']
            sale_price = response_json['salePrice']
            colorway = response_json['color']
            is_special_launch = response_json['isSpecialLaunch']
            special_launch_type = response_json['specialLaunchType']
            
            retail_prices.append(retail_price)
            sale_prices.append(sale_price)
            colorways.append(colorway)
            special_launches.append(is_special_launch)
            special_launch_types.append(special_launch_type)

        sneakers = [self.skus, retail_prices, sale_prices, colorways, special_launches, special_launch_types]
        adidas_df = pd.concat([pd.Series(x) for x in sneakers], axis=1)
        adidas_df.rename(columns={0:'SKU',1:'Retail_Price',2:'Sale_Price',3:'Sneaker_Colorway',4:'Special_Launch',5:'Special_Launch_Type'},inplace=True)
        adidas_df['On_Sale'] = np.where((adidas_df['Retail_Price'] > adidas_df['Sale_Price']),0,1)
        adidas_df['Percentage_On_Sale'] = round((adidas_df['Retail_Price'] - adidas_df['Sale_Price'])/(adidas_df['Retail_Price']),2)*100

        adidas_df.to_csv('4d_adidas_inventory.csv',index=False)

    def inventory_availability(self):
        stock_available = []

        for i in self.skus:
            response = requests.get(f'https://www.adidas.com/api/products/{i}/availability', headers=self.headers)
            response_json = response.json()
            try:
                availability = response_json['variation_list']
                for j in availability:
                    stock_available.append(j)
            except:
                print('no stock for: ' + str(i))
                continue
                
        stock_df = pd.DataFrame(stock_available)
        stock_df['sku'] = stock_df['sku'].apply(lambda x: x.split('_', 1)[0])

        stock_df.to_csv('4d_adidas_inventory_w_stock.csv',index=False)

a = AdidasChecker()
a.catalog()
a.search()
a.inventory_availability()