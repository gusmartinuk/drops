import requests
import json
import pymysql
import datetime
from pymysql.cursors import DictCursor
import sys
import time
from datetime import datetime

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from settings import *
from config import *



# Configure your Keepa API key
connect()

# Function to get product details and offers by EAN and save to the MySQL table
def get_product_details_and_offers(ean, product_id, domain):
    # domain 2 UK    
    search_url = f"https://api.keepa.com/product/?key={KEEP_API_KEY}&domain={domain}&code={ean}&history=1&update=24&rating=0&stats=0&offers=20&only-live-offers=1"

    response = requests.get(search_url)
    jdata = response.json()

    # products = api.query(ean, domain=domain)    
    #with open('research/debug/'+str(ean)+'_debug.json', 'w') as file:
    #    json.dump(jdata, file, indent=4, default=str)       
    
    tokensleft=jdata["tokensLeft"]    
    asin=''
    saved=False
    #print("step 1")
    if "products" in jdata:        
        #print("step 2")
        for product in jdata["products"]:                            
            #print("step 3")
            if 'asin' in product:
                #print("step 4")
                print('asin=',product["asin"])
                #print(product["type"])
                #print(product["brand"])
                #print(product["productGroup"])
                #print(product["partNumber"])
                #sqlexec("delete from amazon_product_offers where asin=%s ",(product["asin"]))
                if "offers" in product and not product['offers'] is None:
                    for offer in product['offers']:
                        price, shipping=offer["offerCSV"][-2:]
                        if price>0:
                           price=price/100
                        if shipping>0:
                           shipping=shipping/100   
                        #if offer["sellerId"]=="A30DC7701CXIBH":
                            #print("Amazon EU offer,maybe free delivery ")
                        #print(offer["sellerId"],"offer: ",price,"=",shipping," prime=",offer["isPrime"]," amazon=",offer["isAmazon"]," isFBA=",offer["isFBA"])
                        query="insert ignore into amazon_product_offers set asin=%s, seller=%s, price=%s, shipping=%s, isprime=%s, isamazon=%s, isfba=%s, updated=current_timestamp() "
                        sqlexec(query,(product["asin"],offer["sellerId"],price,shipping,offer["isPrime"],offer["isAmazon"],offer["isFBA"]))
                sqlexec("delete from amazon_product_salesrank where asin=%s ",(product["asin"]))
                if "salesRanks" in product and not product["salesRanks"] is None:
                    for catid, ranklist in product["salesRanks"].items():
                        rank = ranklist[-1]
                        print(product["asin"],"  sales rank cat:",catid,"  rank:", rank)                      
                        query="insert ignore into amazon_product_salesrank set asin=%s,cat_id=%s,salesrank=%s"
                        sqlexec(query,(product["asin"],catid,rank))

                parentcat=0    
                if "categoryTree" in product and not product["categoryTree"] is None:
                    for ct in product["categoryTree"]:
                        #print(ct["catId"]," ",ct["name"]," ",parentcat)     
                        parentcat=ct["catId"]
                        query="insert ignore into amazon_categories set id=%s,name=%s,parent_id=%s"
                        sqlexec(query,(ct["catId"],ct["name"],parentcat))
                        sonid=ct["catId"]
                    query="insert ignore into amazon_product_categories set asin=%s,cat_id=%s"
                    sqlexec(query,(product["asin"],sonid))           
                #print("step 5")
                query = "INSERT INTO amazon_products (product_id, asin, ean) "
                query+= "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE updated = current_timestamp()"                       
                #print("product save 1:", product_id,product["asin"],ean)
                sqlexec(query,(product_id,product["asin"],ean))
                saved=True
    if not saved:        
        #print("step 7")        
        query = "INSERT INTO amazon_products (product_id, asin, ean) "
        query+= "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE updated = current_timestamp()"                       
        #print("product save 3:", product_id,'X',ean)
        sqlexec(query,(product_id,'X',ean))

    #print("step 8")
    connection.commit()    
    return(tokensleft)

xcnt=0
print("*****************restart***********************")
while True:
    connect()
    try:
        query='SELECT p1.id, p1.ean FROM products p1 left outer join amazon_products p2 on p1.id=p2.product_id and p1.ean=p2.ean where quantity>0 and p2.asin is null limit 0,50'
        with connection.cursor() as cursor:
            cursor.execute(query)
            result=cursor.fetchall()
            if len(result)==0:
                disconnect()
                exit()
            for row in result:       
                domain=2        
                xcnt+=1
                current_datetime = datetime.now()
                print(current_datetime,"  counter=",xcnt,"   ",row['ean'], row['id'])
                #try:
                token=get_product_details_and_offers(row['ean'], row['id'], domain)     
                print("token=",token)
                if token<20:    
                    time.sleep(30)         
                #except:
                #    time.sleep(30)    
                #    print("wait error 30 sec")        
    except Exception as e:
        print("sql query read error wait 10 sec: "+str(e))   
        connection.commit()
        time.sleep(10)    
    try:            
        connection.commit()
    except Exception as e:
        print("commit error:"+str(e))
    try:
        connection.close()
    except Exception as e:
        print("close error:"+str(e))            
    exit()
