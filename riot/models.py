class Match:
    """Model for a League of Legends match"""
    
    def __init__(self, match_data, timeline_data=None):
        self.match_data = match_data
        self.timeline_data = timeline_data
        self.metadata = match_data.get("metadata", {})
        self.info = match_data.get("info", {})
        self.match_id = self.metadata.get("matchId", "unknown")
        self.participants = self.info.get("participants", [])
        self.teams = self.info.get("teams", [])
        
    @property
    def game_creation(self):
        """Get the game creation timestamp"""
        return self.info.get("gameCreation", 0)
    
    @property
    def game_duration(self):
        """Get the game duration in seconds"""
        return self.info.get("gameDuration", 0)
    
    @property
    def game_duration_minutes(self):
        """Get the game duration in minutes"""
        return self.game_duration / 60
    
    @property
    def game_mode(self):
        """Get the game mode"""
        return self.info.get("gameMode", "Unknown")
    
    @property
    def team_ids(self):
        """Get a list of team IDs in the match"""
        team_ids = []
        for p in self.participants:
            team_id = p.get("teamId")
            if team_id and team_id not in team_ids:
                team_ids.append(team_id)
        return team_ids
    
    def get_team_participants(self, team_id):
        """Get all participants for a specific team"""
        return [p for p in self.participants if p.get("teamId") == team_id]
    
    def get_participant_by_id(self, participant_id):
        """Get a participant by their ID"""
        for p in self.participants:
            if p.get("participantId") == participant_id:
                return p
        return None