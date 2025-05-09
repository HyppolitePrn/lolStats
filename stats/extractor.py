import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def find_opponent_participant_id(match_data, timeline_data, player_participant_id, player_position, player_team_id):
    """Find the participant ID of the direct opponent"""
    logger.debug(f"Finding opponent for participant ID: {player_participant_id}, position: {player_position}")
    
    if not match_data or not timeline_data:
        logger.warning("Missing match data or timeline data")
        return None
    
    info = match_data["info"]
    
    # First try to find opponent by position (for Summoner's Rift games)
    for p in info["participants"]:
        if (p["participantId"] != player_participant_id and 
            p["teamId"] != player_team_id and
            p["teamPosition"] == player_position and 
            p["teamPosition"] != ""):
            logger.debug(f"Found opponent by position: {p['participantId']}")
            return p["participantId"]
    
    # If no position match, find opponent by lane from timeline
    if timeline_data.get("info", {}).get("frames", []) and player_position and player_position != "":
        for participant in timeline_data["info"]["participants"]:
            if (participant["participantId"] != player_participant_id and
                "lane" in participant and
                participant["lane"] == player_position):
                logger.debug(f"Found opponent by lane: {participant['participantId']}")
                return participant["participantId"]
    
    # Last resort: pick a random opponent
    for p in info["participants"]:
        if p["teamId"] != player_team_id:
            logger.debug(f"Using random opponent: {p['participantId']}")
            return p["participantId"]
    
    logger.warning("Could not find opponent")
    return None

def extract_player_stats(match_data, timeline_data, participant_id):
    """Extract stats for a specific player by participant ID"""
    logger.info(f"Extracting stats for participant ID: {participant_id}")
    
    if not match_data or not timeline_data:
        logger.warning("Missing match data or timeline data")
        return None
    
    try:
        metadata = match_data["metadata"]
        info = match_data["info"]
        
        # Find player data by participant ID
        player_data = None
        for p in info["participants"]:
            if p["participantId"] == participant_id:
                player_data = p
                break
        
        if not player_data:
            logger.warning(f"Could not find player data for participant ID: {participant_id}")
            return None
        
        logger.debug(f"Found player data: {player_data.get('summonerName')}")
        
        player_participant_id = player_data["participantId"]
        player_position = player_data.get("teamPosition", "")
        player_team = player_data["teamId"]
        
        # Find opponent
        opponent_participant_id = find_opponent_participant_id(
            match_data, timeline_data, player_participant_id, player_position, player_team)
        
        # Calculate game duration in minutes
        game_duration = info.get("gameDuration", 0)
        game_duration_minutes = game_duration / 60
        
        # Calculate DPM (Damage Per Minute)
        damage = player_data.get("totalDamageDealtToChampions", 0)
        dpm = round(damage / game_duration_minutes, 2) if game_duration_minutes > 0 else 0
        
        # Calculate VPM (Vision Per Minute)
        vision_score = player_data.get("visionScore", 0)
        vpm = round(vision_score / game_duration_minutes, 2) if game_duration_minutes > 0 else 0
        
        # Calculate CS Per Minute
        minions = player_data.get("totalMinionsKilled", 0)
        neutral_minions = player_data.get("neutralMinionsKilled", 0)
        total_cs = minions + neutral_minions
        cs_per_minute = round(total_cs / game_duration_minutes, 2) if game_duration_minutes > 0 else 0
        
        # Calculate Kill Participation
        kills = player_data.get("kills", 0)
        assists = player_data.get("assists", 0)
        
        team_kills = 0
        for p in info["participants"]:
            if p["teamId"] == player_team:
                team_kills += p.get("kills", 0)
        
        if team_kills > 0:
            kill_participation = round(100 * (kills + assists) / team_kills, 2)
            kill_participation = min(kill_participation, 100)
        else:
            kill_participation = 0
        
        logger.debug(f"Calculated KP: {kill_participation}%")
        
        # Extract gold difference at 15 minutes
        gold_diff_15 = "N/A"
        # Extract exp difference at 15 minutes
        exp_diff_15 = "N/A"
        frames = timeline_data.get("info", {}).get("frames", [])
        
        if opponent_participant_id and frames:
            frame_15_min_timestamp = 15 * 60 * 1000
            
            if frames and frames[-1]["timestamp"] < frame_15_min_timestamp:
                frame_15 = frames[-1]
                logger.debug(f"Game shorter than 15 min, using last frame at {frame_15['timestamp'] / 60000} min")
            else:
                for frame in frames:
                    if frame["timestamp"] >= frame_15_min_timestamp:
                        frame_15 = frame
                        logger.debug(f"Found frame at 15 min: {frame_15['timestamp'] / 60000} min")
                        break
            
            if 'frame_15' in locals():
                player_frame = frame_15["participantFrames"].get(str(player_participant_id), {})
                opponent_frame = frame_15["participantFrames"].get(str(opponent_participant_id), {})
                
                if player_frame and opponent_frame:
                    # Gold difference
                    if "totalGold" in player_frame and "totalGold" in opponent_frame:
                        player_gold = player_frame["totalGold"]
                        opponent_gold = opponent_frame["totalGold"]
                        gold_diff_15 = player_gold - opponent_gold
                        logger.debug(f"Gold diff at 15: {gold_diff_15}")
                    
                    # Experience difference
                    if "xp" in player_frame and "xp" in opponent_frame:
                        player_xp = player_frame["xp"]
                        opponent_xp = opponent_frame["xp"]
                        exp_diff_15 = player_xp - opponent_xp
                        logger.debug(f"Exp diff at 15: {exp_diff_15}")
        
        # Extract solo kills
        solo_kills = 0
        for frame in frames:
            for event in frame.get("events", []):
                if (event["type"] == "CHAMPION_KILL" and 
                    event.get("killerId") == player_participant_id and 
                    len(event.get("assistingParticipantIds", [])) == 0):
                    solo_kills += 1
        
        logger.debug(f"Solo kills: {solo_kills}")
        
        # Get player's summoner name
        summoner_name = player_data.get("summonerName", "Unknown")
        
        # Extract relevant data
        match_stats = {
            "matchId": metadata["matchId"],
            "summonerName": summoner_name,
            "gameCreation": datetime.fromtimestamp(info["gameCreation"] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "gameDate": datetime.fromtimestamp(info["gameCreation"] / 1000).strftime('%Y-%m-%d'),
            "gameTime": datetime.fromtimestamp(info["gameCreation"] / 1000).strftime('%H:%M:%S'),
            "gameDuration": round(game_duration_minutes, 2),
            "gameMode": info.get("gameMode", "Unknown"),
            "champion": player_data.get("championName", "Unknown"),
            "championLevel": player_data.get("champLevel", 0),
            "position": player_position,
            "kills": kills,
            "deaths": player_data.get("deaths", 0),
            "assists": assists,
            "kda": "Perfect" if player_data.get("deaths", 0) == 0 else round((kills + assists) / player_data.get("deaths", 1), 2),
            "DPM": dpm,
            "VPM": vpm,
            "CSperMin": cs_per_minute,
            "goldDiffAt15": gold_diff_15,
            "expDiffAt15": exp_diff_15,
            "soloKills": solo_kills,
            "killParticipation": f"{kill_participation}%",
            "win": player_data.get("win", False),
        }
        
        logger.info(f"Successfully extracted stats for {summoner_name}")
        return match_stats
        
    except Exception as e:
        logger.error(f"Error extracting player stats: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def extract_team_stats(match_data, timeline_data, team_id):
    """Extract stats for all players on a specific team"""
    logger.info(f"Extracting team stats for team ID: {team_id}")
    
    team_stats = []
    
    if not match_data:
        logger.warning("No match data available")
        return team_stats
    
    info = match_data["info"]
    
    # Get all participant IDs for the team
    team_participant_ids = []
    for p in info["participants"]:
        if p["teamId"] == team_id:
            team_participant_ids.append(p["participantId"])
    
    logger.debug(f"Found {len(team_participant_ids)} participants for team {team_id}")
    
    # Extract stats for each team member
    for participant_id in team_participant_ids:
        player_stats = extract_player_stats(match_data, timeline_data, participant_id)
        if player_stats:
            team_stats.append(player_stats)
    
    logger.info(f"Extracted stats for {len(team_stats)}/{len(team_participant_ids)} team members")
    return team_stats