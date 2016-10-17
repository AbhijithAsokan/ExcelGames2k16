$(document).ready(function(){
    


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


    /* --------------------------------------------------------
     Animate numbers
     -----------------------------------------------------------*/
    $('.quick-stats').each(function(){
        var target = $(this).find('h2');
        var toAnimate = $(this).find('h2').attr('data-value');
        // Animate the element's value from x to y:
        $({someValue: 0}).animate({someValue: toAnimate}, {
            duration: 1000,
            easing:'swing', // can be anything
            step: function() { // called on every step
                // Update the element's text with rounded-up value:
                target.text(commaSeparateNumber(Math.round(this.someValue)));
            }
        });

        function commaSeparateNumber(val){
            while (/(\d+)(\d{3})/.test(val.toString())){
                val = val.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
            }
            return val;
        }
    });
    
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
    $('#buy').click(function(){
        $.get('text/dalalbull-dash.txt', function(data){
            $('#main-widget').fadeOut(300, function(){
                $(this).html(data).fadeIn(400);
            });
        });
    });
        
    
});
