exit()
##### retired ####
import csv, urllib.request
import pymysql
from pymysql.converters import escape_string
from time import sleep
import time    
import os
import subprocess
import datetime
from bs4 import BeautifulSoup
import string
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from settings import *
from config import *


def clean(xstr):
    xstr=xstr.replace("%","%%")   
    clean_string = ''.join(c for c in xstr if c in string.printable and c.isprintable())
    return(clean_string)

def cleanhtml(xstr):
    xstr=xstr.replace("%","%%")   ## format chars
    soup = BeautifulSoup(xstr, features="html.parser")
    cleaned_html_str = soup.prettify()
    return(cleaned_html_str)

def get_size(size):
    numbers = re.findall(r'\d+\.?\d*', size)
    length, width, height = 0, 0, 0
    if len(numbers) == 1:
        length = float(numbers[0])
    elif len(numbers) == 2:
        length, width = float(numbers[0]), float(numbers[1])
    elif len(numbers) >= 3:
        length, width, height = float(numbers[0]), float(numbers[1]), float(numbers[2])
    return (length, width, height)


def supcat_save(cname,cpath,supplier_id=1):  
    global connection
    connect()
    names = cname.split(" > ")
    paths = cpath.split(" > ")
    if len(names)==len(paths):
        cats=[]
        cnt=0
        for cat in names:
            parent=0
            if cnt>0:
                parent=paths[cnt-1]    
            cats.append([paths[cnt],cat,parent])
            cnt=cnt+1
        for row in cats:
            catid=row[0]
            catname=row[1].encode('utf-8')
            catparent=row[2]
            sqlexec('insert ignore into supplier_categories SET id=%s,name=%s,parent_id=%s,supplier_id=%s',(catid,catname,catparent,str(supplier_id)))

def brand_save(brand):
    brand_id=sqlfirst('SELECT id FROM brands WHERE name = %s limit 0,1',(brand))
    if brand_id is None:
       sqlexec('INSERT IGNORE INTO brands (name) VALUES (%s)',(brand)) 
       brand_id=sqlfirst('SELECT id FROM brands WHERE name = %s limit 0,1',(brand))
    return brand_id


def vidaxl_save(record):
    global connection
    connect()
    from pymysql.converters import escape_string
    vidaxl=1
    query=''    
    #dbfields=["link","","","",    #          
    #          "properties","description","","","product_title","","","","nofpackages","parcel","","",
    #          "","","","","","","","deliverytime","dispatchtime"]
    # record['brand']   id required
    
    vatrate=20
    brand_id=brand_save(record['brand'])
    dropscat_id=0 # bizim category kodumuz sonradan update yapilabilir
    status=1 #  stok ve fiyat durumuna : 9 ise islem suruyor demek 9 kalirsa islem sonunda kaldirmak lazim
    # supplier categories kategoriler 
    supcat_save(clean(record['category']),record['categoryidpath'],vidaxl)

    (length,width,height)=get_size(record['size'])
     
    query+='name="'+escape_string(clean(record['title']))+'",'
    query+='description="'+escape_string(cleanhtml(record['html']))+'",'
    query+='sku="'+escape_string(str(record['sku']))+'",'
    #query+='mpn="'+escape_string(record['sku'])+'",'
    query+='supplier_reference="'+escape_string(str(record['sku']))+'",'
    #query+='model="'+escape_string(record[''])+'",'
    query+='ean="'+escape_string(str(record['ean']))+'",'
    query+='weight="'+escape_string(record['weight'])+'",'
    query+='length="'+escape_string(str(length))+'",'
    query+='width="'+escape_string(str(width))+'",'
    query+='height="'+escape_string(str(height))+'",'
    query+='color="'+escape_string(clean(record['color']))+'",'    
    query+='gender="'+escape_string(clean(record['gender']))+'",'
    query+='volume="'+escape_string(clean(record['volume']))+'",' 
    query+='diameter="'+escape_string(clean(record['diameter']))+'",' 

    query+='price_buy="'+escape_string(record['b2bprice'])+'",'  ## vat add
    query+='price_sell="'+escape_string(record['price_sell'])+'",'
    query+='vat_rate="'+escape_string(str(vatrate))+'",'
    query+='quantity="'+escape_string(str(record['stock']))+'",'
    query+='brand_id="'+escape_string(str(brand_id))+'",'
    query+='category_id="'+escape_string(str(dropscat_id))+'",'
    query+='supplier_id="'+escape_string(str(vidaxl))+'",'
    query+='supplier_category_id="'+escape_string(str(record['categoryid']))+'",'
    #query+='date_added="'+escape_string(record[''])+'",' otomatik zaten
    query+='date_modified=current_timestamp(),'
    query+='status="'+escape_string(str(status))+'",'
    query+='dispatchmin="'+escape_string(str(record['dispatchtime']))+'",'
    query+='dispatchmax="'+escape_string(str(record['dispatchtime']))+'",'
    query+='deliverymin="'+escape_string(str(record['deliverytime']))+'",'
    query+='deliverymax="'+escape_string(str(record['deliverytime']))+'",'

    query=query[:-1]

    product_id=sqlfirst('select id from products where supplier_id=%s and supplier_reference=%s limit 0,1',(str(vidaxl),str(record['sku'])))
    if product_id==None: 
        query = 'INSERT ignore into products set '+ query         
        product_id=sqlexec(query)
    else:
        query = 'update products set '+ query + " where id=%s "
        sqlexec(query,(product_id))
    if product_id==None:
        product_id=sqlfirst('select id from products where supplier_id=%s and supplier_reference=%s limit 0,1',(str(vidaxl),str(record['sku'])))

    #imagesave
    icnt=0
    while icnt<12:
        icnt+=1
        imageurl=record['image'+str(icnt)].strip()
        if imageurl!='':
            sqlexec('insert ignore into product_images set product_id=%s, image_url=%s, position=%s',(product_id,imageurl,icnt))
        
    #return('<br>'+str(record))
    return(str(product_id)+", ")
    



def vidaxl():    
    global connection    
    connect()
    sqlexec("update products set status=9,quantity=0 where supplier_id=1") 
    msg=''
    msg+='Started '+time.strftime("%Y%m%d-%H%M%S")
    url = vidaxl_url
    cnt=0
    dbfields=["link","sku","title","category","image1","image2","image3","image4","image5","image6","image7","image8","image9","image10","image11","properties","description","color","weight","image12","product_title","stock","b2bprice","ean","nofpackages","parcel","html","gender","diameter","size","brand","categoryid","categoryidpath","volume","price_sell","deliverytime","dispatchtime"]
    ## csv columns
    #['Link', 'SKU', 'Title', 'Category', 'Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Image 6', 'Image 7', 'Image 8', 'Image 9', 'Image 10', 'Image 11', 'Properties', 'Description', 'Color', 'Weight', 'Image 12', 'Product_title', 'Stock', 'B2B price', 'EAN', 'Number_of_packages', 'Parcel_or_pallet', 'HTML_description', 'Gender', 'Diameter', 'Size', 'Brand', 'Category_id', 'Category_id_path', 'Product_volume', 'Webshop price', 'estimated_total_delivery_time', 'estimated_dispatch_time']
    #    0       1       2       3           4           5           6         7         8           9           10         11        12         13          14          15            16            17       18         19          20             21          22       23          24                  25                     26               27        28        29      30          31              32                  33                  34                  35                              36

    #if not os.path.exists("vidaxltest.txt"):
    print("download started")
    response = urllib.request.urlopen(url)
    print("download completed")
    lines = [l.decode('utf-8') for l in response.readlines()]
    #with open("vidaxltest.txt", "w", encoding="utf-8") as f:
    #    for line in lines:
    #        f.write(line)
    #msg+="<br>Saved to vidaxltest.txt"        
    #else:
    #    with open("vidaxltest.txt", "r", encoding="utf-8") as f:
    #       lines = [line.rstrip("\n") for line in f]
    #    msg+="<br>Load from disk vidaxltest.txt"        
    cr = csv.reader(lines, delimiter = ',')
    total=len(lines)
    msg+="<br>total rows="+str(total)
    print("total rows="+str(total))
    for row in cr:
        cnt=cnt+1
        perc=int(cnt*100/total)
        if cnt>1 and int(row[1])>0:
            xcol=0
            record={}
            try: 
                for fld in dbfields:                            
                    if fld=="price_sell" and row[xcol]=='':                   
                        row[xcol]='0.00'  # correction                   
                    if fld=="weight" or fld=="volume":
                        row[xcol]=row[xcol].replace(",",".")   # fix wrong decimal symbol         
                    record[fld]=row[xcol]      
                    xcol+=1            
                msg+=vidaxl_save(record)    
                if cnt % 1000 == 0:
                    percentage = cnt / total * 100
                    print(f"Processed {cnt} rows, {percentage:.2f}% complete") 
                    connection.commit()                
            except Exception as e:
                print(row)
                timestr = time.strftime("%Y%m%d-%H%M%S")
                with open('suppliers/errors/products_'+str(cnt)+'_'+timestr+'.txt', 'w') as f:
                        f.write(str(e)+' *****data:***'+str(str(row).encode('utf-8')))  
    return(msg)
 
