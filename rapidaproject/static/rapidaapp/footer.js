$(window).scroll(foot);

function foot() {
    var tempScrollTop = $(window).scrollTop();
    //  console.log("Scroll from Top: " + tempScrollTop.toString());
    if(tempScrollTop > 20){ 
        $("footer").fadeIn("slow").addClass("show");
    }
    else{
        $("footer").fadeOut("slow").removeClass("show");
    }
    
    clearTimeout($.data(this, 'scrollTimer'));
    $.data(this, 'scrollTimer', setTimeout(function() {
        if ($('footer').is(':hover')) {
            foot();
        }
        else
        {
            $("footer").fadeOut("slow");
        }
    }, 2000));    
};

