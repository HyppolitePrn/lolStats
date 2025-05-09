import logging

logger = logging.getLogger(__name__)

def calculate_team_average(team_stats, stat_key):
    """Calculate the average of a specific stat for all team members"""
    if not team_stats:
        return 0
    
    values = []
    for player in team_stats:
        value = player.get(stat_key)
        
        # Handle percentage strings
        if isinstance(value, str) and "%" in value:
            try:
                value = float(value.replace("%", ""))
            except ValueError:
                value = None
        
        # Skip N/A or non-numeric values
        if value != "N/A" and value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    if not values:
        return 0
    
    return sum(values) / len(values)

def calculate_team_aggregates(team_stats):
    """Calculate aggregate statistics for a team"""
    if not team_stats:
        return {}
    
    # Calculate total kills, deaths, assists
    total_kills = sum(player.get("kills", 0) for player in team_stats)
    total_deaths = sum(player.get("deaths", 0) for player in team_stats)
    total_assists = sum(player.get("assists", 0) for player in team_stats)
    
    # Calculate averages
    avg_dpm = calculate_team_average(team_stats, "DPM")
    avg_vpm = calculate_team_average(team_stats, "VPM")
    avg_cs_per_min = calculate_team_average(team_stats, "CSperMin")
    
    # Get win/loss status (should be the same for all team members)
    win = any(player.get("win", False) for player in team_stats)
    
    return {
        "totalKills": total_kills,
        "totalDeaths": total_deaths,
        "totalAssists": total_assists,
        "avgDPM": round(avg_dpm, 2),
        "avgVPM": round(avg_vpm, 2),
        "avgCSPerMin": round(avg_cs_per_min, 2),
        "win": win
    }

def sort_players_by_position(team_stats):
    """Sort players by their position (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY)"""
    position_order = {
        "TOP": 1,
        "JUNGLE": 2,
        "MIDDLE": 3,
        "BOTTOM": 4,
        "UTILITY": 5,
        "": 6  # For unknown positions
    }
    
    return sorted(team_stats, key=lambda p: position_order.get(p.get("position", "").upper(), 9999))