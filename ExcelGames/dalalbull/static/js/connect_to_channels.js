$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var nifty_sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/nifty-channel/");  
    var i=0;
    nifty_sock.onmessage = function(message) {
        var dat = message.data;
        //console.log("Data reached!"+dat);
        i++;
        $('#nifty-count').html( "Broadcast number: "+i);
        $('#nifty-data').html (""+dat);
    };

    var nifty_sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/leaderboard-channel/");  
    var k=0;
    nifty_sock.onmessage = function(message) {
        var dat = message.data;

        //console.log("Data reached!"+dat);

        $('#leaderboard-data').html(""+dat);
        

        k++;
        $('#leaderboard-count').html( "Broadcast number: "+k);
        
    };


    var graph_sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/graph-channel/");  
    var m=0;
    graph_sock.onmessage = function(message) {
        var dat = message.data;
        //console.log("Data reached!"+dat);
        m++;
        var ele;
        $('#graph-data').html(""+dat);


        $('#graph-count').html( "Broadcast number: "+m);
         
    };


    $('#submit').on("click", function(event) {
        var message = {
            company: $('#company').find(":selected").val(),
        }
        console.log(message);
        graph_sock.send(JSON.stringify(message));
        return false;
    });



    var portfolio_sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/portfolio-channel/");  
    var q=0;
    portfolio_sock.onmessage = function(message) {
        var dat = message.data;
        console.log("Data reached!"+dat);
        q++;
        var ele;
        $('#portfolio-data').html(""+dat);


        $('#portfolio-count').html( "Broadcast number: "+q);
         
    };

    var sell_sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/sell-channel/");  
    var z=0;
    sell_sock.onmessage = function(message) {
        var dat = message.data;
        console.log("Data reached!"+dat);
        z++;
        var ele;
        $('#sell-data').html(""+dat);


        $('#sell-count').html( "Broadcast number: "+z);
         
    };


});