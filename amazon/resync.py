# retired vidaxl/amazon_rsync.py
# https://developer-docs.amazon.com/sp-api/docs/reports-api-best-practices
import time
import requests
from sp_api.base import Marketplaces
from sp_api.api import Reports
from sp_api.base.reportTypes import ReportType
from sp_api.util import load_all_pages
import csv
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from settings import *
import gzip
import io
from config import *

def urldownload(url, file_path):
    response = requests.get(url)
    content = response.content
    try:
        # Check if the content is gzip-compressed
        with gzip.open(io.BytesIO(content), 'rt', encoding='utf-8') as f:
            decompressed_content = f.read()
    except OSError:
        # If the content is not gzip-compressed, assume it's plain text
        decompressed_content = content.decode('utf-8')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(decompressed_content)




def updatelist():
    connect()
    # Replace 'filename.tsv' with the path to your TSV file
    file_path = 'temp/default_GET_MERCHANT_LISTINGS_DATA_LITE.txt'

    # Initialize an empty list to store the data
    data = []
    cnt=0
    # Open the file and read its content
    with open(file_path, 'r', encoding='utf-8') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        
        # Iterate over the rows in the TSV file
        for row in tsv_reader:
            # Add each row to the data list
            cnt+=1
            if cnt>1:
                sku,stock,price,asin=row[0],row[1],row[2],row[3]            
                print(cnt,"** ",sku,stock,price,asin)
                query="INSERT INTO amazon_inventory SET asin=%s,account=%s,stock=%s,marketplace=%s,currency=%s,price=%s,created=current_timestamp(),status=1,sku=%s "
                query+="ON DUPLICATE KEY UPDATE stock=%s,price=%s,updated=current_timestamp(),sku=%s "
                sqlexec(query,(asin,'default',stock,'GB','GBP',price,sku,stock,price,sku))
            #data.append(row)            
            #print(row)
    disconnect()
    return(cnt)




# Initialize the Reports API instance
reports_api = Reports(marketplace=Marketplaces.GB, credentials=credentials)

# Request a report with your active listings
#report_response = reports_api.create_report(reportType=ReportType.GET_MERCHANT_LISTINGS_ALL_DATA)
report_response = reports_api.create_report(reportType=ReportType.GET_MERCHANT_LISTINGS_DATA_LITE)

# Get the report ID
report_id = report_response.payload.get('reportId')

# Poll the report status until it's completed
secs=0
while True:
    report_details = reports_api.get_report(report_id)
    report_status = report_details.payload.get('processingStatus')
    
    if report_status == 'DONE':
        report_document_id = report_details.payload.get('reportDocumentId')
        print(" completed: id=",report_document_id)        
        break
    elif report_status in ('CANCELLED', 'FAILED'):
        raise Exception(f'Report processing failed with status: {report_status}')
    else:
        secs+=10
        print("wait: ", secs)
        time.sleep(10)  # Wait for 1 minute before checking the status again


# Get the report document
report_document = reports_api.get_report_document(report_document_id, download=False)

#print("Report document payload:", report_document.payload)

# Get the report content
url=report_document.payload.get("url")
urldownload(url,'temp/default_GET_MERCHANT_LISTINGS_DATA_LITE.txt')
print("Report saved and update started")
xcnt=updatelist()
print("all done ",xcnt," records has been updated/saved")