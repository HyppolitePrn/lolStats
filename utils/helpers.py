import re
import logging

logger = logging.getLogger(__name__)

def parse_tournament_code(code):
    """Parse tournament code to extract information (day, match number, etc.)"""
    logger.info(f"Parsing tournament code: {code}")
    
    # Extract region prefix if present
    region_match = re.match(r'^([A-Z]{2,4})', code)
    region = region_match.group(1) if region_match else ""
    
    # Check if there's any day identifier in the code
    day_match = re.search(r'DAY(\d+)', code, re.IGNORECASE)
    # Check if there's any match identifier in the code
    match_match = re.search(r'MATCH(\d+)', code, re.IGNORECASE)
    
    # If not found in the code, ask the user
    if not day_match:
        day = input(f"Enter day number for tournament code {code}: ").strip()
        if not day:
            day = "1"  # Default to day 1 if not specified
    else:
        day = day_match.group(1)
        
    if not match_match:
        match_num = input(f"Enter match number for tournament code {code}: ").strip()
        if not match_num:
            match_num = "1"  # Default to match 1 if not specified
    else:
        match_num = match_match.group(1)
    
    logger.debug(f"Parsed code: day={day}, match={match_num}, region={region}")
    
    return {
        "day": day,
        "match": match_num,
        "code": code,
        "region": region
    }

def is_match_id(code):
    """Determine if a code is a match ID rather than a tournament code"""
    # Match IDs usually contain an underscore
    return "_" in code