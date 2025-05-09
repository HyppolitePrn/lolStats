import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API config
API_KEY = os.getenv("RIOT_API_KEY")
DEFAULT_REGION = os.getenv("RIOT_REGION", "americas")
DEFAULT_ROUTE = os.getenv("RIOT_REGIONAL_ROUTE", "na1")

# Region mappings
REGION_MAP = {
    "euw": "europe",
    "eun": "europe",
    "na": "americas",
    "kr": "asia",
    "jp": "asia",
    "br": "americas",
    "lan": "americas",
    "las": "americas",
    "oce": "sea",
    "ru": "europe",
    "tr": "europe"
}

# Excel config
DEFAULT_EXCEL_PATH = "tournament_stats.xlsx"
SHEET_NAME = "Tournament Stats"

# Colors for Excel
COLORS = {
    "header": "1F4E78",
    "day": "D9EAD3",
    "match": "FCE5CD",
    "win": "C6EFCE",
    "loss": "FFC7CE"
}