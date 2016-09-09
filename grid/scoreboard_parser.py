from HTMLParser import HTMLParser

from parsed_game import ParsedGame

class ScoreboardParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.games = []
        self.cur_game = None
        self.get_data = False
        self.get_name = False
        self.overwrite = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.cur_game = []
        elif tag == 'td':
            if ('class', 'team') in attrs:
                self.get_name = True
            elif ('class', 'total-score') in attrs:
                self.get_data = True
            elif ('class', 'gameStatus') in attrs:
                self.get_data = True
            elif ('class', 'finalStatus') in attrs:
                self.get_data = True
                self.overwrite = True
        elif tag == 'a' and self.get_name:
            for name, value in attrs:
                if name == 'href':
                    self.cur_game.append(value.split("/")[4])
                    self.get_name = False
    def handle_endtag(self, tag):
        if tag == 'table':
            self.games.append(ParsedGame(self.cur_game))
    def handle_data(self, data):
        if not self.get_data:
            return
        if self.overwrite:
            self.cur_game[-1] = data.strip()
        else:
            self.cur_game.append(data.strip())
        self.get_data = False
        self.overwrite = False
    
            
