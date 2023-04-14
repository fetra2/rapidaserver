/**control de login */
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
function login(){
    const username = document.getElementById('exampleInputEmail1')
    const password = document.getElementsByName('password');
    if(username.value == "" ){
       document.getElementById('mess').innerHTML = "Vous devez completer toutes les champs"
    }
    return false;
}
/**control de login */
$(document).ready(function(){
    $(".slide-toggle").click(function(){
        $(".box").animate({
            width: "toggle"
        });
    });
});


$(document).ready(function(){
    var current_fs, next_fs, previous_fs; //fieldsets
    var opacity;
    $("fieldset").css({
        'display': 'none',
        'position': 'relative'
    });
    $("#fs-1").show();
    $(".next").click(function(){
        current_fs = $(this).parent();
        next_fs = $(this).parent().next();
        //next_fs = $(this).parent().child();
        
        //Add Class Active to progressbar li
        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
        
        //show the next fieldset
        next_fs.show();
        //hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now) {
                // for making fielset appear animation
                opacity = 1 - now;
                
                current_fs.css({
                'display': 'none',
                'position': 'relative'
                });
                next_fs.css({'opacity': opacity});
            },
            duration: 600
        });
    });
    $(".previous").click(function(){
    
        current_fs = $(this).parent();
        previous_fs = $(this).parent().prev();
        
        //Remove class active
        $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
        
        //show the previous fieldset
        previous_fs.show();
        
        //hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now) {
            // for making fielset appear animation
            opacity = 1 - now;
            
            current_fs.css({
            'display': 'none',
            'position': 'relative'
            });
            previous_fs.css({'opacity': opacity});
            },
            duration: 600
        });
    });
    
    $('.radio-group .radio').click(function(){
    $(this).parent().find('.radio').removeClass('selected');
    $(this).addClass('selected');
    });
    
    $(".submit").click(function(){
        $('#registration_form').submit();
        //return false;
    })

    $(function() {
        $('[data-toggle="tooltip"]').tooltip()
    })
    
});

$(document).ready(function(){
    $("#titreCom").click(function(){
    $("#ContentCom").slideToggle("slow");
    });
});
document.querySelector('.img__btn').addEventListener('click', function() {
  document.querySelector('.cont').classList.toggle('s--signup');
});
/*detailcartitem */
var loading = function(isLoading) {
    if (isLoading) {
      // Disable the button and show a spinner
      document.querySelector("button").disabled = true;
      document.querySelector("#spinner").classList.remove("hidden");
      document.querySelector("#button-text").classList.add("hidden");
    } else {
      document.querySelector("button").disabled = false;
      document.querySelector("#spinner").classList.add("hidden");
      document.querySelector("#button-text").classList.remove("hidden");
    }
  };