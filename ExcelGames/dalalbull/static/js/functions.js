$(document).ready(function(){
    
        /* --------------------------------------------------------
	Components
    -----------------------------------------------------------*/
   
    
    


    /* --------------------------------------------------------
	Notifications
    -----------------------------------------------------------*/
    (function(){
        $('body').on('click touchstart', '.drawer-toggle', function(e){
            e.preventDefault();
            var drawer = $(this).attr('data-drawer');

            $('.drawer:not("#'+drawer+'")').removeClass('toggled');

            if ($('#'+drawer).hasClass('toggled')) {
                $('#'+drawer).removeClass('toggled');
                $('.tick').css('display','none');
            }
            else{
                $('#'+drawer).addClass('toggled');
                $('.tick').css('display','block');
            }
        });

        //Close when click outside
        $(document).on('mouseup touchstart', function (e) {
            var container = $('.drawer, .tm-icon');
            if (container.has(e.target).length === 0) {
                $('.drawer').removeClass('toggled');
                $('.drawer-toggle').removeClass('open');
                $('.tick').css('display','none');
            }
        });

        //Close
        $('body').on('click touchstart', '.drawer-close', function(){
            $(this).closest('.drawer').removeClass('toggled');
            $('.drawer-toggle').removeClass('open');
            $('.tick').css('display','none');
        });
    })();
    
    
    $(".gameicon").click(function(){
                    $("#dock").css("bottom","-85px");
                    $("#up-arrow").css("bottom","0px");
                    $("#up-arrow").fadeIn(1000);
                });
    $("#up").hover(function(){
                    $("#dock").css("bottom","0px");
                    $("#up-arrow").css("bottom","55px");
                    $("#up-arrow").fadeOut(750);                                        
                });
    $("#dock").hover(function(){},function(){
        $("#dock").css("bottom","-85px");
        $("#up-arrow").css("bottom","0px");
        $("#up-arrow").fadeIn(1000);
    });
    
    $(document).on('click', '#dalalbull' ,function(){
        $.get('/static/text/dalalbull1.txt', function(data){
            $('#main-games').fadeOut(300, function(){
                $(this).html(data).fadeIn(400).promise().done(function(){
                    dashboard(anim);
            });
        });
    
    });
    });

       $(document).on('click', '#home' ,function(){
        $.get('/static/text/home.txt', function(data){
            $('#main-games').fadeOut(300, function(){
                $(this).html(data).fadeIn(400).promise().done(function(){
                    dashboard(anim);
            });
        });
    
    });
    });

    $(document).ready(function(){
        $.get('/static/text/home.txt', function(data){
            $('#main-games').fadeOut(300, function(){
                $(this).html(data).fadeIn(400).promise().done(function(){
                    dashboard(anim);
            });
        });
    
    });
    });   

    
});
