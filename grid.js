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
    init: function() {
        this.ben = new Player("Ben", true);
        this.brian = new Player("Brian", false);
        $('.good_guy_choice').click(function(e){
            $('.scorebox.win1, .scorebox.loss1').toggleClass('win1 loss1');
            $('.scorebox.win2, .scorebox.loss2').toggleClass('win2 loss2');
            $('.scorebox.win3, .scorebox.loss3').toggleClass('win3 loss3');
            $('.scorebox.win4, .scorebox.loss4').toggleClass('win4 loss4');
            $('.good_guy_choice').toggleClass('good_guy bad_guy');
            ben.is_good_guy = !ben.is_good_guy;
            brian.is_good_guy = !brian.is_good_guy;
        });
        /* Ben is the default good guy, unless told otherwise. */
        if (location.hash == '#brian') {
            $('.bad_guy').click();
        }
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
        delta = abs(delta);
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
        return (game.away.name in teams) ? game.away : game.home;
    },
    build_team_row: function(team) {
        return $('<tr>')
            .append($('<td>').attr('class', 'team_name').text(team.name))
            .append($('<td>').attr('class', 'game_score').text(team.score));
    },
    build_table: function(game) {
        var away_row = this.build_team_row(game.away);
        var home_row = this.build_team_row(game.home);
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
        for (var game in games) {
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
    name = "",
    is_good_guy = "",
    current_wins = "",
    final_wins = "",
    teams = "",
    init: function(name, is_good_guy) {
        this.name = name;
        this.is_good_guy = is_good_guy;
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
    init: function(home_team, away_team, time_left) {
        this.home_team = home_team;
        this.away_team = away_team;
        this.time_left = time_left;
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