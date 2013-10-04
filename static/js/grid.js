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
    ben_games: 0,
    brian: "",
    brian_games: 0,
    interval: 0,
    scores_url: "scores/",
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
        $('.good_guy_choice').click(this.proxy(function(e){
            $('.scorebox.win1, .scorebox.loss1').toggleClass('win1 loss1');
            $('.scorebox.win2, .scorebox.loss2').toggleClass('win2 loss2');
            $('.scorebox.win3, .scorebox.loss3').toggleClass('win3 loss3');
            $('.scorebox.win4, .scorebox.loss4').toggleClass('win4 loss4');
            $('.good_guy_choice').toggleClass('good_guy bad_guy');
            this.ben.is_good_guy = !this.ben.is_good_guy;
            this.brian.is_good_guy = !this.brian.is_good_guy;
            this.update_wins();
        }));

        /* Ben is the default good guy, unless told otherwise. */
        if (location.hash == '#brian') {
            $('.bad_guy').click();
        }

        /* Pull down the game data. */
        $.get(this.scores_url, this.proxy(this.got_scores), "json");
    },
    got_scores: function(data) {
        /* Turn JSON into an array of games. */
        var games = this.parse_scores(data);
        this.update_grid(games);
        if (this.interval > 0) {
            setTimeout(this.proxy(function() {
                $.get(this.scores_url, this.proxy(this.got_scores), "json");
            }), this.interval);
        }
    },
    parse_scores: function(data) {
        games = [];
        for (var i=0; i < data.length; i++) {
            games.push(new Game(data[i].fields));
        }
        return games;
    },
    choose_week_class: function() {
        // Return the relevant class for the week overall.
        // First compare the number of final wins for a player
        // to their opponent's maximum number of wins.  The week
        // is over if one player has more final wins than their
        // opponents max.  If the week is still up in the air
        // then compare picked_wins, which is the number of correctly
        // picked games, both final and in-progress.
        var good_guy;
        var bad_guy;
        if (this.ben.is_good_guy) {
            good_guy = this.ben;
            bad_guy = this.brian;
        } else {
            good_guy = this.brian;
            bad_guy = this.ben;
        }

        if (good_guy.picked_finals > bad_guy.max_wins) {
            return "win4";
        } else if (bad_guy.picked_finals > good_guy.max_wins) {
            return "loss4";
        }

        var delta = good_guy.picked_wins - bad_guy.picked_wins;
        // We want to return '{win|loss}delta' with the exception
        // that -3 <= delta <= 3.
        if (delta > 3) {
            delta = 3;
        } else if (delta < -3) {
            delta = -3;
        }

        if (delta < 0) {
            return 'loss' + Math.abs(delta);
        } else if (delta > 0) {
            return 'win' + delta;
        } else {
            return 'tied';
        }
    },
    choose_delta_class: function(game) {
        var ben_team = this.ben.choose_team(game);
        var brian_team = this.brian.choose_team(game);
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
        } else if (delta == 0 && game.is_final()) {
            /* Handle a tie. */
            if ((this.ben.is_good_guy && game.picker == this.ben.name.toUpperCase()) ||
                (this.brian.is_good_guy && game.picker == this.brian.name.toUpperCase())) {
                ret = 'loss';
            } else {
                ret = 'win';
            }
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
    build_team_row: function(team, picked) {
        var team_class = picked ? 'team_name picked_team' : 'team_name';
        return $('<tr>')
            .append($('<td>').attr('class', team_class).text(team.name))
            .append($('<td>').attr('class', 'game_score').text(team.score));
    },
    build_table: function(game) {
        var away_row = this.build_team_row(game.away_team, game.away_picked());
        var home_row = this.build_team_row(game.home_team, game.home_picked());
        var time_row = $('<tr>')
            .append($('<td>'))
            .append($('<td>').attr('class', 'time').text(game.time_left));
        return $('<table>').attr('class', 'score')
            .append(away_row)
            .append(time_row)
            .append(home_row);
    },
    display_game: function(game) {
        var box = $('<div>').attr('class', 'box scorebox');
    
        box.html(this.build_table(game));
        box.addClass(this.choose_delta_class(game));
        if (game.lock) {
            box.addClass("lock");
        }
        if (game.anti_lock) {
            box.addClass("anti_lock");
        }
        if (game.picker == "BEN") {
            $('#ben_games').append(box);
            this.ben_games++;
            if (this.ben_games % 2 == 0) {
                this.insert_clear_div('#ben_games');
            }
        } else {
            $('#brian_games').append(box);
            this.brian_games++;
            if (this.brian_games % 2 == 0) {
                this.insert_clear_div('#brian_games');
            }
        }
    },
    current_win_totals: function() {
        var wins = this.ben.is_good_guy ? this.ben.current_wins : this.brian.current_wins;
        var losses = this.ben.is_good_guy ? this.brian.current_wins : this.ben.current_wins;
        var ties = this.ben_games + this.brian_games - wins - losses;
        return wins + "-" + losses + "-" + ties;
    },
    final_win_totals: function() {
        var wins = this.ben.is_good_guy ? this.ben.final_wins : this.brian.final_wins;
        var losses = this.ben.is_good_guy ? this.brian.final_wins : this.ben.final_wins;
        return wins + "-" + losses;
    },
    update_wins: function() {
        $("#current_wins").text(this.current_win_totals());
        $("#final_wins").text(this.final_win_totals());
        $("#ben_wins > .current").text(this.ben.picked_wins);
        $("#ben_wins > .wins").text(this.ben.picked_finals);
        $("#ben_wins > .max_wins").text(this.ben.max_wins);
        $("#brian_wins > .current").text(this.brian.picked_wins);
        $("#brian_wins > .wins").text(this.brian.picked_finals);
        $("#brian_wins > .max_wins").text(this.brian.max_wins);
        $("#scoreboard").removeClass("win1 win2 win3 win4 loss1 loss2 loss3 loss4 tied");
        $("#scoreboard").addClass(this.choose_week_class());
    },
    insert_clear_div: function(selector) {
        $(selector).append($("<div>").addClass("clear"));
    },
    update_grid: function(games) {
        this.ben.reset_wins();
        this.ben_games = 0;
        this.brian.reset_wins();
        this.brian_games = 0;
        $(".games").empty();
        for (var i=0; i < games.length; i++) {
            game = games[i];
            this.display_game(game);
            this.ben.update(game);
            this.brian.update(game);
        }
        this.update_wins();
    }
});
            
// Player.init(name, is_good_guy);
var Player = new Class;
Player.include({
    name: "",
    is_good_guy: "",
    current_wins: 0,
    final_wins: 0,
    teams: "",
    max_wins: 0,
    picked_wins: 0,
    picked_finals: 0,
    init: function(name, is_good_guy, teams) {
        this.name = name;
        this.is_good_guy = is_good_guy;
        this.teams = teams;
        this.reset_wins();
    },
    reset_wins: function() {
        this.current_wins = 0;
        this.final_wins = 0;
        this.picked_wins = 0;
        this.picked_finals = 0;
        this.max_wins = this.teams.length / 2;
    },
    update: function(game) {
        /* Figure out who's winner.  Nothing to do if it's a tie and the game isn't final. */
        var delta = game.home_team.score - game.away_team.score;
        if (delta == 0 && !game.is_final()) {
            return;
        }
        /* Is the winning team our team? Nothing to do if it isn't. */
        var good_team = this.choose_team(game, this.teams);
        var winner = delta > 0 ? game.home_team : game.away_team;
        if (delta == 0) {
            /* Did we pick this game?  If so, tie == loss, o/w tie == win. */
            if (this.name.toUpperCase() == game.picker) {
                winner = 'loss';
            } else {
                winner = good_team;
            }
        }
        if (winner == good_team) {
            this.current_wins++;
            if (game.is_final()) {
                this.final_wins++;
            }
        }
        /* Did we pick this game?  If so, update pick totals. */
        if (this.name.toUpperCase() == game.picker) {
            if (winner.name == game.picked_team) {
                this.picked_wins++;
                if (game.is_final()) {
                    this.picked_finals++;
                }
            } else if (game.is_final()) {
                this.max_wins--;
            }
        }
    },
    choose_team: function(game) {
        return (this.teams.indexOf(game.away_team.name) > -1) ? game.away_team : game.home_team;
    }
});

var Game = new Class;
Game.include({
    anti_lock: false,
    away_team: "",
    home_team: "",
    lock: false,
    picker: '',
    picked_team: '',
    time_left: "",
    init: function(data) {
        this.home_team = new Team(data['home_team'], data['home_score']);
        this.away_team = new Team(data['away_team'], data['away_score']);
        this.time_left = data['time_left'];
        this.lock = data['lock'];
        this.anti_lock = data['anti_lock'];
        this.picker = data['picker'];
        this.picked_team = data['picked_team'];
    },
    is_final: function() {
        return this.time_left == "Final";
    },
    away_picked: function() {
        return this.picked_team == this.away_team.name;
    },
    home_picked: function() {
        return this.picked_team == this.home_team.name;
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
