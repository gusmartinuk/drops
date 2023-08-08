from sp_api.api import Catalog
from sp_api.base import SellingApiException, Marketplaces
from sp_config import SP_API_CREDENTIALS

def get_inventory():
    try:
        catalog_api = Catalog(credentials=SP_API_CREDENTIALS, marketplace=Marketplaces.GB)  # Amazon UK marketplace
        items = catalog_api.list_items()
        return items
    except SellingApiException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    inventory = get_inventory()
    if inventory:
        print(inventory.payload)
