import logging
import sys
from datetime import datetime
from pathlib import Path
import time

from config import API_KEY, DEFAULT_EXCEL_PATH
from riot.api import RiotAPI
from stats.extractor import extract_team_stats
from excel.writer import update_excel_with_stats
from utils.logger import setup_logging
from utils.helpers import parse_tournament_code, is_match_id

def main():
    # Setup logging
    logger = setup_logging()
    logger.info("=== Starting LoL Tournament Stats ===")
    
    # Check if API key is set
    if not API_KEY:
        logger.error("Error: RIOT_API_KEY not found in .env file")
        print("Error: RIOT_API_KEY not found in .env file")
        return
    
    logger.info(f"Using API key: {API_KEY[:5]}... (truncated)")
    
    # Initialize Riot API client
    riot_api = RiotAPI()
    
    # Ask for Excel file path
    excel_path = input("Enter the path to the Excel file (leave blank for a new file): ").strip()
    if not excel_path:
        excel_path = DEFAULT_EXCEL_PATH
    
    logger.info(f"Excel file path: {excel_path}")
    
    # Get tournament codes or match IDs from user
    print("Enter tournament codes or match IDs (one per line, leave blank to finish):")
    codes = []
    while True:
        code = input().strip()
        if not code:
            break
        codes.append(code)
    
    if not codes:
        logger.error("No codes provided. Exiting.")
        print("No codes provided. Exiting.")
        return
    
    logger.info(f"Processing {len(codes)} codes: {codes}")
    print(f"Processing {len(codes)} codes...")
    
    # Process each code
    all_match_stats = []
    
    for code in codes:
        logger.info(f"Processing code: {code}")
        print(f"Processing code: {code}")
        
        # Check if this is a match ID rather than a tournament code
        if is_match_id(code):
            # Direct match ID
            match_id = code
            day = input(f"Enter day number for match {match_id}: ").strip() or "1"
            match_num = input(f"Enter match number for match {match_id}: ").strip() or "1"
            
            logger.info(f"Using direct match ID: {match_id} (Day {day}, Match {match_num})")
            
            # Get match data
            match_data = riot_api.get_match_data(match_id)
            if not match_data:
                logger.error(f"Could not get match data for {match_id}")
                print(f"Could not get match data for {match_id}")
                continue
            
            # Get timeline data
            timeline_data = riot_api.get_match_timeline(match_id)
            if not timeline_data:
                logger.error(f"Could not get timeline data for {match_id}")
                print(f"Could not get timeline data for {match_id}")
                continue
            
        else:
            # Tournament code
            tournament_code = code
            parsed_code = parse_tournament_code(tournament_code)
            day = parsed_code["day"]
            match_num = parsed_code["match"]
            
            logger.info(f"Using tournament code: {tournament_code} (Day {day}, Match {match_num})")
            
            # Try to get match ID from tournament code
            match_ids = riot_api.get_match_by_tournament_code(tournament_code)
            
            if not match_ids:
                logger.warning(f"No match found for tournament code {tournament_code}")
                print(f"No match found for tournament code {tournament_code}")
                
                # Ask if user wants to provide a match ID directly
                use_direct = input("Would you like to provide a match ID directly for this tournament code? (y/n): ").strip().lower()
                if use_direct == 'y':
                    match_id = input("Enter match ID (e.g. EUW1_12345678): ").strip()
                    if not match_id:
                        continue
                    
                    logger.info(f"Using manually entered match ID: {match_id}")
                    
                    # Get match data directly
                    match_data = riot_api.get_match_data(match_id)
                    timeline_data = riot_api.get_match_timeline(match_id)
                else:
                    continue
            else:
                # Use the first match from the tournament code
                match_id = match_ids[0]
                logger.info(f"Found match ID: {match_id}")
                
                # Try to get tournament-specific match data
                match_data = riot_api.get_match_data_for_tournament(match_id, tournament_code)
                
                # Fallback to regular match data if tournament API fails
                if not match_data:
                    logger.info("Tournament match data not available, trying regular match data...")
                    match_data = riot_api.get_match_data(match_id)
                
                # Get timeline data
                timeline_data = riot_api.get_match_timeline(match_id)
        
        # Check if we have both match and timeline data
        if not match_data or not timeline_data:
            logger.error(f"Missing required data for match {match_id}")
            print(f"Missing required data for match {match_id}")
            continue
        
        logger.info("Successfully retrieved match and timeline data")
        
        # Get team IDs
        team_ids = []
        for p in match_data["info"]["participants"]:
            if p["teamId"] not in team_ids:
                team_ids.append(p["teamId"])
        
        logger.info(f"Found team IDs: {team_ids}")
        
        # Extract stats for each team
        for team_id in team_ids:
            team_stats = extract_team_stats(match_data, timeline_data, team_id)
            
            if team_stats:
                all_match_stats.append({
                    "day": day,
                    "match": match_num,
                    "code": code,
                    "match_id": match_id,
                    "team_id": team_id,
                    "team_stats": team_stats
                })
                logger.info(f"Added stats for team ID {team_id} with {len(team_stats)} players")
            else:
                logger.warning(f"No stats extracted for team ID {team_id}")
        
        # Rate limiting
        time.sleep(1.2)
    
    # Check if we collected any stats
    if not all_match_stats:
        logger.error("No match stats collected. Nothing to write to Excel.")
        print("No match stats collected. Nothing to write to Excel.")
        return
    
    logger.info(f"Total match stats collected: {len(all_match_stats)}")
    
    # Update Excel file with stats
    update_excel_with_stats(excel_path, all_match_stats)
    print(f"Excel file updated: {excel_path}")
    logger.info("=== LoL Tournament Stats completed successfully ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        logging.getLogger().info("Operation cancelled by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Check the log file for details")
        logging.getLogger().critical(f"Unhandled exception: {str(e)}", exc_info=True)