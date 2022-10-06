import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import json
import time

class Goat:
    def __init__(self):
        self.headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Origin': 'https://www.goat.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
        }
    def goat_get_sneaker_ids(self):
        response = requests.get('https://ac.cnstrc.com/search/Adidas%204d?c=ciojs-client-2.29.11&key=key_XT7bjdbvjgECO5d8&i=38ef97e5-83d0-45aa-b26e-9316ed8ddc24&s=5&page=1&num_results_per_page=200&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_3&_dt=1664914504596',headers=self.headers)
        response_json = response.json()

        self.sneaker_ids = []
        for i in response_json['response']['results']:
            self.sneaker_ids.append(i['data']['id'])

    def goat_get_products(self):

        sneaker_titles = []
        sneaker_release_dates = []
        sneaker_retail_prices = []
        sneaker_skus = []
        sneaker_models = []
        sneaker_colorways = []

        for i in self.sneaker_ids:
            data = {'query':'','facetFilters':[f'product_template_id:{i}']}
            data = json.dumps(data)
            response = requests.post('https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)%3B%20Browser%20(lite)&x-algolia-api-key=ac96de6fef0e02bb95d433d8d5c7038a&x-algolia-application-id=2FWOTDVM2O', headers=self.headers, data=data)
            response_json = response.json()['hits'][0]
            title = response_json['name']
            release_date = response_json['release_date']
            retail_price = response_json['retail_price_cents']
            sku = response_json['sku']
            colorway = response_json['details']
            model = response_json['silhouette']
            sneaker_titles.append(title)
            sneaker_release_dates.append(release_date)
            sneaker_retail_prices.append(retail_price)
            sneaker_skus.append(sku)
            sneaker_models.append(model)
            sneaker_colorways.append(colorway)

        sneakers = [sneaker_titles, sneaker_release_dates, sneaker_retail_prices, sneaker_skus, sneaker_models, sneaker_colorways]
        goat_df = pd.concat([pd.Series(x) for x in sneakers], axis=1)
        goat_df.rename(columns={0:'Sneaker_Name',1:'Release_Date',2:'Retail_Price',3:'SKU',4:'Sneaker_Model',5:'Sneaker_Colorway'},inplace=True)

        # Filling blank release dates

        goat_df['Release_Date'] = goat_df['Release_Date'].fillna('1960-01-01')
        goat_df['Release_Date'] = pd.to_datetime(goat_df['Release_Date'])
        goat_df['Release_Date'] = goat_df['Release_Date'].apply(lambda x: x.date())

        # Setting correct retail prices (GOAT stores in cents)
        goat_df['Retail_Price'] = np.where((goat_df['Retail_Price'] == 0.0),goat_df['Retail_Price'],goat_df['Retail_Price']/100)

        # Sorting dates
        goat_df.sort_values('Release_Date',ascending=False,inplace=True)

        goat_df.to_csv('4d_goat_inventory.csv',index=False)

g = Goat()
g.goat_get_sneaker_ids()
g.goat_get_products()