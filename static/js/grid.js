var Class = function() {
    var klass = function() {
        this.init.apply(this, arguments);
    };
    klass.prototype.init = function(){};

    // Shortcut to access prototype
    klass.fn = klass.prototype;
    // Shortcut to access class
    klass.fn.parent = klass;

    // Adding class properties
    klass.extend = function(obj) {
        var extended = obj.extended;
        for (var i in obj) {
            klass[i] = obj[i];
        }
        if (extended) extended(klass);
    };

    // Adding instance properties
    klass.include = function(obj) {
        var included = obj.included;
        for (var i in obj) {
            klass.fn[i] = obj[i];
        }
        if (included) included(klass);
    };

    klass.proxy = function(func) {
        var self = this;
        return (function() {
            return func.apply(self, arguments);
        });
    };
    klass.fn.proxy = klass.proxy;

    return klass;
};

var Grid = new Class;
Grid.include({
    ben: "",
    brian: "",
    interval: 0,
    init: function(ben_teams, brian_teams, interval) {
        this.ben = new Player("Ben", true, ben_teams);
        this.brian = new Player("Brian", false, brian_teams);
        this.interval = interval;
    },
    configAjax: function() {
        $(document).ajaxSend(function(event, xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            function sameOrigin(url) {
                // url could be relative or scheme relative or absolute
                var host = document.location.host; // host + port
                var protocol = document.location.protocol;
                var sr_origin = '//' + host;
                var origin = protocol + sr_origin;
                // Allow absolute or scheme relative URLs to same origin
                return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                    // or any other URL that isn't scheme relative or absolute i.e relative.
                    !(/^(\/\/|http:|https:).*/.test(url));
            }
            function safeMethod(method) {
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }

            if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        });
    },
    start: function() {
        this.configAjax();

        /* Link up event handlers. */
        $('.good_guy_choice').click(function(e){
            $('.scorebox.win1, .scorebox.loss1').toggleClass('win1 loss1');
            $('.scorebox.win2, .scorebox.loss2').toggleClass('win2 loss2');
            $('.scorebox.win3, .scorebox.loss3').toggleClass('win3 loss3');
            $('.scorebox.win4, .scorebox.loss4').toggleClass('win4 loss4');
            $('.good_guy_choice').toggleClass('good_guy bad_guy');
            this.ben.is_good_guy = !this.ben.is_good_guy;
            this.brian.is_good_guy = !this.brian.is_good_guy;
        });

        /* Ben is the default good guy, unless told otherwise. */
        if (location.hash == '#brian') {
            $('.bad_guy').click();
        }

        /* Start checking for updated scores. */
        if (this.interval > 0) {
            setInterval(this.proxy(function() {
                var scores_url = "scores/";
                $.get(scores_url, this.proxy(function(data) {
                    /* Turn JSON into an array of games. */
                    var games = this.parse_scores(data);
                    this.update_grid(games);
                }), "json");
            }), this.interval);
        }
    },
    parse_scores: function(data) {
        game_data = $.parseJSON(data);
        games = [];
        for (var i=0; i < game_data.length; i++) {
            games.push(new Game(game_data[i].fields));
        }
        return games;
    },
    choose_delta_class: function(game) {
        var ben_team = this.choose_team(game, this.ben.teams);
        var brian_team = this.choose_team(game, this.brian.teams);
        if (this.ben.is_good_guy) {
            delta = ben_team.score - brian_team.score;
        } else {
            delta = brian_team.score - ben_team.score;
        }

        /* Choose win/loss/tie. */
        var ret = 'tied';
        if (delta < 0) {
            ret = 'loss';
        } else if (delta > 0) {
            ret = 'win';
        }

        /* Set level of win/loss. */
        delta = Math.abs(delta);
        if (game.is_final()) {
            ret += '4';
        } else if (delta > 14) {
            ret += '4';
        } else if (delta > 7) {
            ret += '3';
        } else if (delta > 3) {
            ret += '2';
        } else if (delta > 0) {
            ret += '1';
        }
        return ret;
    },
    choose_team: function(game, teams) {
        return (game.away_team.name in teams) ? game.away_team : game.home_team;
    },
    build_team_row: function(team) {
        return $('<tr>')
            .append($('<td>').attr('class', 'team_name').text(team.name))
            .append($('<td>').attr('class', 'game_score').text(team.score));
    },
    build_table: function(game) {
        var away_row = this.build_team_row(game.away_team);
        var home_row = this.build_team_row(game.home_team);
        var time_row = $('<tr>')
            .append($('<td>'))
            .append($('<td>').attr('class', 'time').text(game.time_left));
        $('<table>').attr('class', 'score')
            .append(away_row)
            .append(time_row)
            .append(home_row);
    },
    update_game: function(game) {
        var box = $('#' + game.id);
    
        box.innerHTML(this.build_table(game));
        box.attr('class', this.choose_delta_class(game));
    },
    update_wins: function() {
        $("#ben_wins > .current").text(this.ben.current_wins);
        $("#ben_wins > .wins").text(this.ben.final_wins);
        $("#brian_wins > .current").text(this.brian.current_wins);
        $("#brian_wins > .wins").text(this.brian.final_wins);
    },
    update_grid: function(games) {
        this.ben.reset_wins();
        this.brian.reset_wins();
        for (var i=0; i < games.length; i++) {
            game = games[i];
            this.update_game(game);
            this.ben.update(game);
            this.brian.update(game);
        }
        this.update_win_totals();
    }
});
            
// Player.init(name, is_good_guy);
var Player = new Class;
Player.include({
    name: "",
    is_good_guy: "",
    current_wins: "",
    final_wins: "",
    teams: "",
    init: function(name, is_good_guy, teams) {
        this.name = name;
        this.is_good_guy = is_good_guy;
        this.teams = teams;
        this.reset_wins();
    },
    reset_wins: function() {
        this.current_wins = 0;
        this.final_wins = 0;
    },
    update: function(game) {
        /* Figure out who's winner.  Nothing to do if it's a tie. */
        var delta = game.home_team.score - game.away_team.score;
        if (delta == 0) {
            return;
        }
        /* Is the winning team our team? Nothing to do if it isn't. */
        var good_team = this.choose_team(game, this.teams);
        var winner = delta > 0 ? game.home_team : game.away_team;
        if (winner != good_team) {
            return;
        }
        this.current_wins += 1;
        if (game.is_final()) {
            this.final_wins += 1;
        }
    }
});

var Game = new Class;
Game.include({
    home_team: "",
    away_team: "",
    time_left: "",
    init: function(data) {
        this.home_team = new Team(data['home_team'], data['home_score']);
        this.away_team = new Team(data['away_team'], data['away_score']);
        this.time_left = data['time_left'];
    },
    is_final: function() {
        this.time_left == "Final";
    }
});

var Team = new Class;
Team.include({
    name: "",
    score: "",
    init: function(name, score) {
        this.name = name;
        this.score = score;
    }
});