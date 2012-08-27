function grid_init() {
    $(".good_guy_choice").click(function(e){
        $(".scorebox.win1, .scorebox.loss1").toggleClass("win1 loss1");
        $(".scorebox.win2, .scorebox.loss2").toggleClass("win2 loss2");
        $(".scorebox.win3, .scorebox.loss3").toggleClass("win3 loss3");
        $(".scorebox.win4, .scorebox.loss4").toggleClass("win4 loss4");
        $(".good_guy_choice").toggleClass("good_guy bad_guy");
    });
}