import requests
import logging
import re
from time import sleep
from config import API_KEY, REGION_MAP, DEFAULT_REGION

logger = logging.getLogger(__name__)

class RiotAPI:
    """Client for Riot Games API"""
    
    def __init__(self, api_key=API_KEY, default_region=DEFAULT_REGION):
        self.api_key = api_key
        self.default_region = default_region
        self.headers = {"X-Riot-Token": api_key}
    
    def get_region_from_code(self, code):
        """Extract region from tournament code or match ID"""
        # For match IDs like EUW1_123456789
        if "_" in code:
            platform_id = code.split("_")[0]
            platform_to_region = {
                "EUW1": "europe",
                "EUN1": "europe",
                "NA1": "americas",
                "KR": "asia",
                "JP1": "asia",
                "BR1": "americas",
                "LA1": "americas",
                "LA2": "americas",
                "OC1": "sea",
                "RU": "europe",
                "TR1": "europe"
            }
            if platform_id in platform_to_region:
                return platform_to_region[platform_id]
        
        # For tournament codes like EUW12345
        region_match = re.match(r'^([A-Z]{2,4})', code)
        region_code = region_match.group(1).lower() if region_match else None
        
        if region_code and region_code in REGION_MAP:
            return REGION_MAP[region_code]
        
        return self.default_region
    
    def get_match_by_tournament_code(self, tournament_code):
        """Retrieve match ID for a tournament code"""
        region = self.get_region_from_code(tournament_code)
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-tournament-code/{tournament_code}"
        
        logger.debug(f"Requesting URL: {url}")
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            match_ids = response.json()
            logger.info(f"Successfully retrieved {len(match_ids)} match IDs")
            return match_ids
        else:
            logger.error(f"Error retrieving match for tournament code {tournament_code}: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
    
    def get_match_data_for_tournament(self, match_id, tournament_code):
        """Get detailed match data for a tournament match"""
        region = self.get_region_from_code(tournament_code)
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/by-tournament-code/{tournament_code}"
        
        logger.debug(f"Requesting URL: {url}")
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            match_data = response.json()
            logger.info(f"Successfully retrieved tournament match data for {match_id}")
            return match_data
        else:
            logger.error(f"Error getting tournament match data: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
    
    def get_match_data(self, match_id):
        """Get detailed match data (non-tournament version)"""
        region = self.get_region_from_code(match_id)
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        
        logger.debug(f"Requesting URL: {url}")
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            match_data = response.json()
            logger.info(f"Successfully retrieved match data for {match_id}")
            return match_data
        else:
            logger.error(f"Error getting match data: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
    
    def get_match_timeline(self, match_id):
        """Get match timeline data"""
        region = self.get_region_from_code(match_id)
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
        
        logger.debug(f"Requesting URL: {url}")
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            timeline_data = response.json()
            logger.info(f"Successfully retrieved match timeline for {match_id}")
            return timeline_data
        else:
            logger.error(f"Error getting match timeline: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None