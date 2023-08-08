import csv, urllib.request
from pymysql.converters import escape_string
from time import sleep
import time    
from bs4 import BeautifulSoup
import ftplib
import os
import glob
import string
from settings import *
from config import *

def empty_temp():
    folder_path = "suppliers/temp"
    # get a list of all files in the folder
    files = os.listdir(folder_path)
    # loop over each file and remove it
    for file in files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)

def clean(xstr):
    xstr=xstr.replace("%","%%")   
    clean_string = ''.join(c for c in xstr if c in string.printable and c.isprintable())
    return(clean_string)

def cleanhtml(xstr):
    xstr=xstr.replace("%","%%")   ## format karakteri, olmazsa bozuyor
    soup = BeautifulSoup(xstr, features="html.parser")
    cleaned_html_str = soup.prettify()
    return(cleaned_html_str)

def attrib_save(attrib,value,product_id):
    attrib_id=sqlfirst('SELECT id FROM attributes WHERE name = %s limit 0,1',(attrib))
    if attrib_id is None:
       sqlexec('INSERT IGNORE INTO attributes (name) VALUES (%s)',(attrib)) 
       attrib_id=sqlfirst('SELECT id FROM attributes WHERE name = %s limit 0,1',(attrib))
    sqlexec('INSERT IGNORE INTO product_attributes (product_id,attribute_id,value) VALUES (%s,%s,%s)',(product_id,attrib_id,value)) 



def bigbuy_save(record):
    global connection
    connect()
    from pymysql.converters import escape_string
    bigbuy=2
    query=''    
    vatrate=20 # ?? 21 olabilir mi
    brand_id=sqlfirst('SELECT br.id FROM bigbuy_brands bb left outer join brands br on bb.name=br.name where bb.id=%s',(record['sup_brand_id']))
    dropscat_id=0 # later update our category
    status=1 #  stock and price
    string = record['category']
    elements = string.split(',')
    supcatid = elements[-1].strip()

    color=''  
    if record['attrib1']=="Colour":
        color=record['value1']
        record['attrib1']=''
    elif record['attrib2']=="Colour":
        color=record['value2']    
        record['attrib2']=''
     
    query+='name="'+escape_string(clean(record['title']))+'",'
    query+='description="'+escape_string(cleanhtml(record['html']))+'",'
    query+='sku="'+escape_string(record['sku'])+'",'
    #query+='mpn="'+escape_string(record['sku'])+'",'
    query+='supplier_reference="'+escape_string(record['sku'])+'",'
    #query+='model="'+escape_string(record[''])+'",'
    query+='ean="'+escape_string(str(record['ean']))+'",'
    query+='weight="'+escape_string(record['weight'])+'",'
    query+='length="'+escape_string(str(record['depth']))+'",'
    query+='width="'+escape_string(str(record['width']))+'",'
    query+='height="'+escape_string(str(record['height']))+'",'

    query+='color="'+escape_string(clean(color))+'",'    
    #query+='gender="'+escape_string(clean(record['gender']))+'",'
    #query+='volume="'+escape_string(clean(record['volume']))+'",' 
    #query+='diameter="'+escape_string(clean(record['diameter']))+'",' 

    query+='price_buy="'+escape_string(record['pvd'])+'",'  ## vat add 
    query+='price_sell="'+escape_string(record['price'])+'",'
    query+='vat_rate="'+escape_string(str(record['iva']))+'",'
    query+='quantity="'+escape_string(str(record['stock']))+'",'
    query+='brand_id="'+escape_string(str(brand_id))+'",'
    query+='category_id="'+escape_string(str(dropscat_id))+'",'
    query+='supplier_id="'+escape_string(str(bigbuy))+'",'
    query+='supplier_category_id="'+escape_string(str(supcatid))+'",'
    query+='date_modified=current_timestamp(),'
    query+='status="'+escape_string(str(status))+'",'
    query+='dispatchmin="'+escape_string(str(1))+'",'
    query+='dispatchmax="'+escape_string(str(3))+'",'
    query+='deliverymin="'+escape_string(str(3))+'",'
    query+='deliverymax="'+escape_string(str(5))+'",'

    query=query[:-1]

    product_id=sqlfirst('select id from products where supplier_id=%s and supplier_reference=%s limit 0,1',(str(bigbuy),str(record['sku'])))
    if product_id==None: 
        query = 'INSERT ignore into products set '+ query         
        product_id=sqlexec(query)
    else:
        query = 'update products set '+ query + " where id=%s "
        sqlexec(query,(product_id))
    if product_id==None:
        product_id=sqlfirst('select id from products where supplier_id=%s and supplier_reference=%s limit 0,1',(str(bigbuy),str(record['sku'])))

    #imagesave 
    icnt=0
    while icnt<8:
        icnt+=1
        imageurl=record['image'+str(icnt)].strip()
        if imageurl!='':
            sqlexec('insert ignore into product_images set product_id=%s, image_url=%s, position=%s',(product_id,imageurl,icnt))
    if record['video']!='0':
        icnt+=1
        sqlexec('insert ignore into product_images set product_id=%s, image_url=%s, position=%s',(product_id,'https://www.youtube.com/watch?v='+record['video'],icnt))
        
    #return('<br>'+str(record))
     
    if record['attrib1']!='':
       attrib_save(record['attrib1'],record['value1'],product_id) 
    if record['attrib2']!='':
       attrib_save(record['attrib2'],record['value2'],product_id) 

    return(str(product_id)+", ")



def bigbuy():    
    # shipping_costs.csv needs load and update
    # category_en.csv all categories
    #  D icin =IFERROR(INDEX($A$1:$A$1000,MATCH($E3,$C$1:$C$1000,0)),"")
    #  F icin =CONCATENATE("(",A3,",2,'",C3,"',",D3,"),")    
    #   A   B   C                       D       E            F  
    #  2400	2	Decoration and Lighting	2399	Home Garden	(2400,2,'Decoration and Lighting',2399),								

    global connection
    connect()
    msg=''
    msg+='Started '+time.strftime("%Y%m%d-%H%M%S")
    """
    ftp = ftplib.FTP("www.dropshippers.com.es")
    ftp.login(f"{bigbuy_username}", "{bigbuy_password}")
    remote_dir = "/files/products/csv/standard"
    local_dir = "suppliers/temp"
    empty_temp()
    # change directory to the remote directory
    ftp.cwd(remote_dir)


    # get a list of all files that match the wildcard pattern
    #file_list = ftp.nlst("*pattern*")
    file_list = ftp.nlst("*_en.csv")

    # loop through the file list and download each file
    for file_name in file_list:        
        local_file_path = local_dir+'/'+file_name
        with open(local_file_path, "wb") as local_file:
            ftp.retrbinary("RETR " + file_name, local_file.write)
        msg+=" "+file_name+","
    # close the FTP connection
    ftp.quit()    
    """

    folder_path = "suppliers/temp"
    wildcard_pattern = "product*_en.csv"  # product files

    dbfields=["sku", "category", "title", "attrib1", "attrib2", "value1", "value2", "html", "sup_brand_id", "feature", "price", "pvp_bigbuy", "pvd", "iva", "video", "ean" ,"width", "height", "depth", "weight", "stock", "date_add", "date_upd", "image1", "image2", "image3", "image4", "image5", "image6", "image7", "image8", "condition", "intrastat" ]
    
    
    
    ## csv columns
    #    0       1       2       3           4           5           6         7         8           9           10         11        12         13          14          15            16            17       18         19          20             21          22       23          24                  25                     26               27        28        29      30          31              32    
    #   ID  ;CATEGORY; NAME; ATTRIBUTE1; ATTRIBUTE2;   VALUE1;   VALUE2;  DESCRIPTION;  BRAND;    FEATURE;    PRICE;   PVP_BIGBUY;   PVD;        IVA;      VIDEO;      EAN13;         WIDTH;       HEIGHT;   DEPTH;    WEIGHT;     STOCK;        DATE_ADD;   DATE_UPD; IMAGE1;     IMAGE2;             IMAGE3;                 IMAGE4;         IMAGE5;   IMAGE6;   IMAGE7; IMAGE8;    CONDITION;      INTRASTAT
    # construct the full path to the files that match the wildcard pattern

    files_to_trans = os.path.join(folder_path, wildcard_pattern)
    # loop over each file and remove it
    gencnt=0
    gentotal=0
    for file_path in glob.glob(files_to_trans):
        msg+=" <br>   "+file_path
        with open(file_path, "r", encoding="utf-8") as f:
             lines = [line.rstrip("\n") for line in f]

        cr = csv.reader(lines, delimiter = ';')
        total=len(lines)
        gentotal+=total-1
        msg+="<br>"+file_path+", total rows="+str(total)
        cnt=0
        for row in cr:
            cnt+=1
            gencnt+=1
            perc=int(cnt*100/total)
            if cnt>1 and len(row)>0 and row[31]=='NEW':
                xcol=0
                record={}
                #try:                 
                for fld in dbfields:                            
                    record[fld]=row[xcol]      
                    xcol+=1            
                msg+=bigbuy_save(record)            
                #msg+="<br>"+str(record)            
                #except Exception as e:
                #    print(row)
                #    timestr = time.strftime("%Y%m%d-%H%M%S")
                #    with open('suppliers/errors/products_'+str(gencnt)+'_'+timestr+'.txt', 'w') as f:
                #            f.write(str(e)+' *****data:***'+str(str(row).encode('utf-8')))  
            #if cnt>20:
            #    return(msg)                 
    msg+="<h3> total products="+str(gentotal)+"</h3>"    
    return(msg)