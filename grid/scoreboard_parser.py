from HTMLParser import HTMLParser

class ScoreboardParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.scores = []
        self.cur_game = None
        self.get_data = False
        self.get_name = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.cur_game = []
        elif tag == 'td':
            if ('class', 'name') in attrs:
                self.get_name = True
            elif ('class', 'finalScore') in attrs:
                self.get_data = True
            elif ('class', 'label') in attrs and ('align', 'left') in attrs:
                self.get_data = True
        elif tag == 'a' and self.get_name:
            for name, value in attrs:
                if name == 'href':
                    self.cur_game.append(value.split("/")[4])
                    self.get_name = False
    def handle_endtag(self, tag):
        if tag == 'table':
            self.scores.append(self.cur_game)
    def handle_data(self, data):
        if not self.get_data:
            return
        self.cur_game.append(data.strip())
        self.get_data = False
    
            
