class ParsedGame:
    def __init__(self, parsed_data):
        if len(parsed_data) == 5:
            self.time_left = parsed_data[0]
            self.away_team = parsed_data[1]
            self.away_score = parsed_data[2]
            self.home_team = parsed_data[3]
            self.home_score = parsed_data[4]
        else:
            self.time_left = parsed_data[0]
            self.away_team = parsed_data[1]
            self.away_score = 0
            self.home_team = parsed_data[2]
            self.home_score = 0
        
        if self.time_left == "FINAL OT":
            self.time_left = "Final"
        elif self.time_left == "FINAL":
            self.time_left = "Final"
        elif self.time_left == "HALFTIME":
            self.time_left = "Halftime"
