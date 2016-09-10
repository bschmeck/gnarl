from HTMLParser import HTMLParser

from parsed_game import ParsedGame

class ScoreboardParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.games = []
        self.cur_game = None
        self.stop_at = None
        self.get_data = False
        self.get_name = False
        self.data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and self.has_class(attrs, 'live-update'):
            self.cur_game = []
        elif tag == 'div' and self.has_class(attrs, 'game-status'):
            self.get_data = True
            self.stop_at = 'div'
        elif tag == 'td':
            if ('class', 'team') in attrs:
                self.get_name = True
            elif ('class', 'total-score') in attrs:
                self.get_data = True
                self.stop_at = 'td'
        elif tag == 'a' and self.get_name:
            for name, value in attrs:
                if name == 'href':
                    self.cur_game.append(value.split("/")[6])
                    self.get_name = False
    def handle_endtag(self, tag):
        if tag == 'table':
            self.games.append(ParsedGame(self.cur_game))
        elif tag == self.stop_at:
            self.get_data = False
            self.stop_at = None
            self.cur_game.append(self.data)
            self.data = ''
    def handle_data(self, data):
        if not self.get_data:
            return
        self.data += data.strip()

    def has_class(self, attrs, class_name):
        for name, value in attrs:
            if name != 'class':
                continue
            classes = value.split(' ')
            return class_name in classes
        return False
