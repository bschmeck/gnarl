function grid_init() {
    $('.good_guy_choice').click(function(e){
        $('.scorebox.win1, .scorebox.loss1').toggleClass('win1 loss1');
        $('.scorebox.win2, .scorebox.loss2').toggleClass('win2 loss2');
        $('.scorebox.win3, .scorebox.loss3').toggleClass('win3 loss3');
        $('.scorebox.win4, .scorebox.loss4').toggleClass('win4 loss4');
        $('.good_guy_choice').toggleClass('good_guy bad_guy');
    });
}

function choose_delta_class(game) {
    if (ben.is_good_guy) {
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
}

function choose_team(game, teams) {
    return (game.away.name in teams) ? game.away : game.home;
}

function build_team_row(team) {
    return $('<tr>')
        .append($('<td>').attr('class', 'team_name').text(team.name))
        .append($('<td>').attr('class', 'game_score').text(team.score));
}

function build_table(game) {
    away_row = build_team_row(game.away);
    home_row = build_team_row(game.home);
    time_row = $('<tr>')
        .append($('<td>'))
        .append($('<td>').attr('class', 'time'));
    $('<table>').attr('class', 'score')
        .append(away_row)
        .append(time_row)
        .append(home_row);
}

function update_game(game) {
    var box = $('#' + game.id);
    
    box.innerHTML(build_table(game));
    ben_team = choose_team(game, ben.teams);
    brian_team = choose_team(game, brian.teams);
    box.attr('class', choose_delta_class(game));
}

function update_wins() {
    $("#ben_wins > .total").text(ben.total_wins);
    $("#ben_wins > .wins").text(ben.final_wins);
    $("#brian_wins > .total").text(brian.total_wins);
    $("#brian_wins > .wins").text(brian.final_wins);
}

function update_grid(games) {
    ben.reset_wins();
    brian.reset_wins();
    for (var game in games) {
        update_game(game);
        ben.update(game);
        brian.update(game);
    }
    update_win_totals();
}