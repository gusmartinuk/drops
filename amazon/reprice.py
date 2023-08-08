## retired  vidaxl/amazon_reprice.py  
exit()
# https://developer-docs.amazon.com/sp-api/docs/reports-api-best-practices
import time
from sp_api.base import Marketplaces
from sp_api.api import Products
from sp_api.api import Orders
from sp_api.api import Reports
from sp_api.base.reportTypes import ReportType
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from settings import *
from sp_api.api import Catalog, ListingsItems
from sp_api.base import SellingApiException
from decimal import Decimal
from sp_api.util import throttle_retry, load_all_pages
from config import *



def update_listing_price_and_stock(sku, price, quantity,asin):
    data ={
              "productType": "PRODUCT",
              "patches": [{
                "op":"replace",
                "path": "/attributes/purchasable_offer",
                "value": [{
                    "marketplace_id": marketplace_id,
                    "currency": 'GBP',
                    "our_price": [{
                        "schedule": [{
                            "value_with_tax": str(price)
                        }]
                    }]
                }]
            },
            {
                "op": "replace",
                "path": "/attributes/fulfillment_availability",
                "value": [{
                    "fulfillment_channel_code": "DEFAULT",
                    "quantity": str(quantity)
                }]            
            }

            ]
          } 
        # Call ListingsItems API to update the listing
    objListingItems = ListingsItems(marketplace=Marketplaces.GB,
                    credentials=credentials,
                    account='default')
    
    #print("sku=",sku)
    #print("data=",data)
    response=objListingItems.patch_listings_item(seller_id,sku, body=data)
    if response.errors is None :
        print(f"Successfully updated price and stock for SKU: {sku}")
        query="update amazon_inventory SET price=%s,stock=%s,repriced=current_timestamp() where asin=%s "
        sqlexec(query,(price,quantity,asin))           
    else:
        print(f"Error updating listing: {response}")
        query="update amazon_inventory SET error=%s,errordate=current_timestamp() where asin=%s "
        sqlexec(query,(str(response),asin))           

# Get competitors' prices
def get_item_offers(row):
    asin=row["asin"]
    try:
        objproducts=Products(marketplace=Marketplaces.GB,
                        credentials=credentials,
                        account='default')        
        xproduct=objproducts.get_item_offers(asin, "New","Consumer")
        minamazon=999999
        minmerchant=999999
        offers=xproduct.payload["Offers"]
        offercnt=0
        for offer in offers:
            if offer["SellerId"]!=seller_id:
               #print("rakip ",offer["SellerId"]," prime= ",offer["PrimeInformation"]["IsPrime"])
               if not offer["PrimeInformation"]["IsPrime"]:
                   #MERCHANT
                   minmerchant=min(offer["ListingPrice"]["Amount"]+offer["Shipping"]["Amount"],minmerchant)                   
               else:
                   minamazon=min(offer["ListingPrice"]["Amount"],minamazon) ## shipping ekleme amazona
               offercnt+=1
        if minamazon==999999:
           minamazon=0
        if minmerchant==999999:
           minmerchant=0       
#        print("amazon min=",minamazon)
#        print("merchant min=",minmerchant)
#        print("rakip teklif=",offercnt)
        minmerchant=round(Decimal(minmerchant),2)
        minamazon=round(Decimal(minamazon),2)        
        query="update amazon_inventory SET lowestpriceprime=%s,lowestpricemerchant=%s,lastchecked=current_timestamp() where asin=%s "
        sqlexec(query,(minamazon,minmerchant,asin))        
        minprice=Decimal(row["minprice"])        
        newprice=minprice*Decimal(1.50)  # max price for listing
        if newprice>min(minamazon,minmerchant): 
            if minprice<min(minamazon,minmerchant): 
                newprice=min(minamazon,minmerchant)-Decimal(0.05)
            elif minprice<minmerchant:
                newprice=minmerchant-Decimal(0.05)  
            elif minprice<minamazon:
                newprice=minmerchant-Decimal(0.05)  
            else: 
                newprice=minprice   
        newprice=Decimal(round(newprice,2))
        update_listing_price_and_stock(row["sku"], newprice, row["quantity"],row["asin"]);
        print(row["asin"]," min price=",minprice,"  old price=",row["listed_price"],"  newprice=",newprice," competitors amz,merch=",minamazon," - ",minmerchant)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        query="update amazon_inventory SET lowestpriceprime=%s,lowestpricemerchant=%s,lastchecked=current_timestamp() where asin=%s "
        sqlexec(query,(-1,-1,asin))    ## error


# Main function
def main():
    connect()
    asin_list = []
    cnt=0
    query="SELECT * FROM drops_db.list_amazon_reprice WHERE (repriced > DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY) or repriced is null) and error is null and status=1 "
    with connection.cursor() as cursor:
            cursor.execute(query)
            result=cursor.fetchall()
            if len(result)==0:
                disconnect()
                exit()
            for row in result:      
                cnt+=1
                print("[",cnt,"]***********",row["asin"],"********") 
                get_item_offers(row)
                print("*********** END OF ",row["asin"],"********")           
                time.sleep(1)      
     
if __name__ == "__main__":
    main()
    disconnect()
