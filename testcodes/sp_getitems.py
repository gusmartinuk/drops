from sp_api.base import Marketplaces
from sp_api.api import Products
from sp_api.api import Orders

from config import *

"""
objproducts=Products(marketplace=Marketplaces.GB,
                     credentials=credentials,
                     account='default')
xproducts=objproducts.get_product_pricing_for_asins(['B07FZXTDJW', 'B09J21BQVN'], MarketplaceId="A1F83G8C2ARO7P")

print(xproducts)
"""

"""
objorders = Orders(account='default',credentials=credentials,marketplace=Marketplaces.GB)
orders=objorders.get_orders(AmazonOrderIds=['205-0173297-9295570'])
print(orders)
"""

