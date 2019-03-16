jQuery(function ($) {
    //switch between themes 

    $('[data-theme]').click(function (event) {
        $('[data-theme]').removeClass("selected");
        $(this).addClass("selected");
        setTheme($(this).attr('data-theme'));
        Cookies.set("theme", $(this).attr('data-theme'), { expires: 9999 });
    });

    // switch between background images

    $('[data-bg]').click(function (event) {
        $('[data-bg]').removeClass("selected");
        $(this).addClass("selected");
        setBackground($(this).attr('data-bg'));
        Cookies.set("sidebar_bg", $(this).attr('data-bg'), { expires: 9999 });
    });

    // toggle background image
    $("#toggle-bg").change(function (e) {
        e.preventDefault();
        setSidebarBgVisible(e.currentTarget.checked);
        Cookies.set("sidebar_show_bg", e.currentTarget.checked, { expires: 9999 });
    });
});
function setSidebarBgVisible(visibility) {
    if (visibility) {
        $('.page-wrapper').addClass("sidebar-bg");
    } else {
        $('.page-wrapper').removeClass("sidebar-bg");
    }
}

function setTheme(theme) {
    var themes = "chiller-theme ice-theme cool-theme light-theme";

    $('.page-wrapper').removeClass(themes);
    $('.page-wrapper').addClass(theme);
}

function setBackground(bg) {
    var bgs = "bg1 bg2 bg3 bg4";

    $('.page-wrapper').removeClass(bgs);
    $('.page-wrapper').addClass(bg);
}
