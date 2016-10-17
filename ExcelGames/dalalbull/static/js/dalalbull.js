var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var url = window.location.host;
var page_url = 'http://' +url +'/dalalbull'; 

var nifty_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/nifty-channel/",null,{automaticOpen :false});
nifty_sock.automaticOpen = false;

var leaderboard_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/leaderboard-channel/",null,{automaticOpen :false}); 
leaderboard_sock.automaticOpen = false;

var graph_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/graph-channel/",null,{automaticOpen :false});  
graph_sock.automaticOpen = false;

var portfolio_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/portfolio-channel/",null,{automaticOpen :false}); 
portfolio_sock.automaticOpen = false;

var sell_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/sell-channel/",null,{automaticOpen :false});  
sell_sock.automaticOpen = false;


var ticker_sock = new ReconnectingWebSocket(ws_scheme + '://' + url + "/ticker-channel/",null,{automaticOpen :false});  
ticker_sock.automaticOpen = false;


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function onReceiveNiftyDataInitial(data)
{
	$('#nifty').attr("data-value",""+data.current_price);
	$('#nifty-change').text(data.change);
}

function onReceiveNiftyData(data)
{
	$('#nifty').text(data.current_price);
	$('#nifty-change').text(data.change);
}


function onReceivePortfolioDataInitial(data)
{
	$('#networth').attr("data-value",""+data.net_worth);
    $('#rank').attr("data-value",""+data.rank);
    $('#cash-balance').text(""+data.cash_bal);
    $('#margin').attr("data-value",""+data.margin);
    $('#transactions').text(""+data.total_transactions);
    $('#players').text(""+data.total_users);
}
function onReceivePortfolioData(data)
{
	//console.log("Data received!"+JSON.stringify(data));
	$('#networth').text(""+data.net_worth);
    $('#rank').text(""+data.rank);
    $('#cash-balance').text(""+data.cash_bal);
    $('#margin').text(""+data.margin);
    $('#transactions').text(""+data.total_transactions);
    $('#players').text(""+data.total_users);
}


function onReceiveLeaderboardData(data)
{
	
	data = data.leaderboard_data;
	var leaderboard_element = $('#leaderboard');
	leaderboard_element.html('');

	for(var i=0; i<data.length; ++i )
	{
		toper_data = data[i];
		var outer = $('<div class="media p-l-5"></div>');
		var profile_pic = $('<img width="40" alt="">').attr("src",toper_data.image_url); 
		var image = $('<div class="pull-left"></div>').html(profile_pic);
		outer.append(image);
		var details = $('<div class="media-body"></div>');
		var rank = $('<a class="t-overflow marg"></a>').text(toper_data.name); 
		var networth = $('<a class="t-overflow marg" style="font-size:11px;margin-top:5px;"></a>').text(toper_data.net_worth);
		details.append(rank);
		details.append(networth);
		outer.append(details);
		leaderboard_element.append(outer);
	}
	

}


	nifty_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
		onReceiveNiftyData(data);	    
	};

	portfolio_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
	    onReceivePortfolioData(data);
	};

	leaderboard_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
	   	onReceiveLeaderboardData(data);
	};




function fillCompanyList(data)
{
	data = data.companies;
	var stock_symbols = $('#stock-info');
	var buy_stock_sym = $('#buy-comp');
	for(var sym of data)
	{
		stock_symbols.append($('<option></option>').text(sym) );
		if(sym!='NIFTY 50')
			buy_stock_sym.append($('<option></option>').text(sym));
	}
}

function dashboard(callback)
{
	//console.log("Called!!!!!!!!!!!!!!!!!!!!!!!!");
	nifty_sock.open();
	leaderboard_sock.open();
	portfolio_sock.open();
	graph_sock.open();
	$.get( page_url + '/leaderboard', onReceiveLeaderboardData);
	$.get( page_url + '/nifty', onReceiveNiftyDataInitial);
	$.get( page_url + '/portfolio', onReceivePortfolioDataInitial);
	$.get( page_url + '/nifty', onReceiveNiftyData);
	$.get( page_url + '/stockinfo',fillCompanyList);

	$("#stock-info").change(function(){
    		getCompanyDeatails($('#stock-info :selected').text());
	});

	
	sellModalEventFunctions();
	buyModalEventFunctions();
	ticker();
	graph();

	setTimeout(callback,1000);

	
}

function anim()
{
	$('.quick-stats').each(function(){
                        var target = $(this).find('h2');
                        var toAnimate = $(this).find('h2').attr('data-value');
                        var type = $(this).find('h2').attr('data-type');
                        // Animate the element's value from x to y:
                        
                        $({someValue: 0}).animate({someValue: toAnimate}, {
                            duration: 1000,
                            easing:'swing', // can be anything
                            complete: function() { 
                                if(type=="cash"){
                                    target.text((toAnimate));
                                }
                                else
                                {
                                    target.text((toAnimate)); 
                                }
                            },
                            step: function() { // called on every step
                                // Update the element's text with rounded-up value:
                                if(type=="rank"){
                                    target.text((Math.round(this.someValue)));
                                }
                                else
                                {
                                    target.text((Math.round(this.someValue*100)/100));
                                }
                            }
                        });
                    });
                  
}

function onReceiveHistoryData(data)
{
	var transactionBoard = $('#transaction-history');
	data = data.history;
	
	transactionBoard.html('');	
	
	for(var i=0; i<data.length; ++i)
	{
		var row = $('<tr></tr>');
		row.append( $('<td></td>').text(i+1) );
		row.append( $('<td></td>').text( data[i].time) );
		row.append( $('<td></td>').text(data[i].symbol) );
		row.append( $('<td></td>').text(data[i].buy_ss) );
		row.append( $('<td></td>').text(data[i].quantity) );
		row.append( $('<td></td>').text(data[i].price) );
		row.append( $('<td></td>').text(parseFloat(data[i].total).toFixed(2)));
		transactionBoard.append(row);
	}

	if(data.length==0)
	{
		$('#transaction-history-head').hide();
		$('#transaction-history-message').text("You have no transactions!");

	}
	else
	{
		$('#transaction-history-head').show();
		$('#transaction-history-message').text("");
	}




}

function getHistory()
{
	$.get(page_url+'/history',onReceiveHistoryData);
}



var companyPossibleTrans;


function sellModalEventFunctions()
{
	$('#sell-comp').change(function(){
    		setSellChoice($('#sell-comp :selected').text());
	});

	$('#seller-form').submit(function(event){

		
		var data={
			company : $('#sell-comp :selected').text(),
			quantity : $('#num-shares').val(),
			tradeType : $('#sell-trans-type :selected').text(),
			pending : $('#pending-price').val(),
			csrfmiddlewaretoken : getCookie('csrftoken')
		}
		
		if( data.company == '---' || data.quantity=='' || data.tradeType=='---')
		{	
			$('#seller-message').text("Invalid Data in form!");
		}
		else{

			$.post( page_url+'/submit_sell',
				data,
				function(data)
				{
					$('#seller-message').text(data.message);
				}
			);
			
		}
		event.preventDefault();
		openSellSock();
	}
	);


}

function setSellChoice( company )
{
	
	var sellChoice = $('#sell-trans-type');
	sellChoice.html('<option disabled selected>---</option>');
	for(var transType of companyPossibleTrans[company])
	{	
		
		sellChoice.append( $('<option></option>').text(transType) );
	}
}

function onReceiveSellData(data)
{
	
	companyPossibleTrans = {};
	var sellData = data.trans;
	var sellTable = $('#sell-table');
	sellTable.html('');
	var sellComp = $('#sell-comp');
	sellComp.html('<option selected disabled> </option>');
	$('#sell-trans-type').html('<option disabled selected> </option>');
	for(var dat of sellData)
	{
		if( dat.company in companyPossibleTrans)
			companyPossibleTrans[dat.company].push(dat.type_of_trans);		
		else
		{
			sellComp.append( $('<option></option>').text(dat.company) );
			companyPossibleTrans[dat.company] = [ dat.type_of_trans ];
		}
		var row = $('<tr></tr>');
		row.append( $('<td></td>').text( dat.company ) );
		
		row.append( $('<td></td>').text( dat.type_of_trade ) );
		row.append( $('<td></td>').text( dat.share_in_hand ) );
		row.append( $('<td></td>').text( dat.current_price ) );
		row.append( $('<td></td>').text( String( parseFloat(dat.gain).toFixed(2) ) +"%" ));
		sellTable.append(row);
	}

}


sell_sock.onmessage = function(message)
{
	var data = JSON.parse(message.data);
	onReceiveSellData(data);
	
}

function openSellSock()
{
	if(!isTime())
	{
		$('#sell-frame').hide();
		$('#seller-message').text("Market closed");
		$('#sell-form-button').hide();
		return ;
	}
	else{
		$('#sell-frame').show();
		$('#sell-form-button').show();
		$('#seller-message').text("");
	}
	sell_sock.open();
	$('#num-shares').val('');
	$('#pending-price').val('');
	
	$.get(page_url+'/sell',onReceiveSellData);
}

function closeSellSock()
{
	$('#seller-message').text('');
	sell_sock.close();
}


function onReceiveCompanyDetails(data)
{

	$('#c_info_open').text(data.open_price);
	$('#c_info_current').text(data.current_price);
	$('#c_info_high').text(data.high);
	$('#c_info_low').text(data.low);
	$('#c_info_change').text(data.change);
	$('#c_info_change_percent').text(data.change_per);
	$('#c_info_trade_qty').text(data.trade_Qty);
	$('#c_info_trade_value').text(data.trade_Value);

}



function getCompanyDeatails(company_symbol)
{
		
	$.post(page_url + '/companydetails',
	{
		company: company_symbol,
		csrfmiddlewaretoken : getCookie('csrftoken'),
	}, onReceiveCompanyDetails);

}



function onReceivePendingData(data)
{
	
	data = data.pending;
	var pendingDataTable = $('#pending-data');
	pendingDataTable.html('');
	i=0;
	for(var pend of data)
	{
		var row = $('<tr></tr>');
		row.append( $('<td></td>').text(pend.symbol) );
		row.append( $('<td></td>').text(pend.type) );
		row.append( $('<td></td>').text(pend.quantity) );
		row.append( $('<td></td>').text(pend.current_price) );
		row.append( $('<td></td>').text(pend.value) );
		var cancel_button = $('<button type="button" class="btn btn-sm btn-alt" style="font-size:10px;padding: 2px 10px 2px;">CANCEL</button>').attr("onclick","cancel("+pend.id+",'"+pend.symbol+"')");
		row.append( $('<td style="padding-top: 6px;"></td').append(cancel_button) );
		row.attr("id","pending-data-"+pend.id);
		pendingDataTable.append(row);
	}
	if(data.length==0)
	{
		$('#pending-data-head').hide();
		$('#pending-data-message').text("You have no pending transactions!");
	}
	else
	{
		$('#pending-data-head').show();
		$('#pending-data-message').text("");
	}

}

function getPendingData()
{
	$.get( page_url + '/pending' , onReceivePendingData);
}



function cancel(id,symbol)
{
	$.post(page_url+'/cancels',
	{
		iddel : id,
		company : symbol
	},  
	function(data){
		$('#pending-data-'+id).remove();
		if(document.getElementById('pending-data').length==0)
			$('#pending-data-head').hide();
		
		$('#pending-data-head').hide();
		$('#pending-data-message').text(data.message); 
	})
}



var buy_data={ pending : false };

function calBrokerage()
{
	
	var tdv = parseFloat( $('#buy-total-value').text() );
	var brokerage;
	if(buy_data.no_trans<100)
        brokerage=(0.5/100)*tdv; 
    else if(buy_data.no_trans<1000)
        brokerage=(1.0/100)*tdv;
    else
        brokerage=(1.5/100)*tdv;
    $('#buy_brokerage').text(brokerage.toFixed(2));

}
function onReceiveCurrentPrice(data)
{
	 	
	 	$('#cur_buy_price').text('Current Price: '+data.curr_price);

		buy_data.curr_price = data.curr_price;
		buy_data.cash_bal = data.cash_bal;

		buy_data.no_trans = data.no_trans ;
		buy_data.quantity = 0;

		$('#buy-cash-bal').text(data.cash_bal);
	

	if(!buy_data.pending)
	{
		buy_data.t_curr_price = buy_data.curr_price;	
		$('#buy_trade_price').text(buy_data.t_curr_price);

		var qty = $('#buy-quantity').val();
		
		if( qty!='' )
	    {
	    	var k = parseFloat(buy_data.t_curr_price*$('#buy-quantity').val());
			$('#buy-total-value').text( k.toFixed(2) );
			$('#buy_margin').text( (k/2).toFixed(2) );
			calBrokerage();
	    }
	}

}

function resetTransactionDetails()
{
	if(!isTime())
	{
		$('#buy-frame').hide();
		$('#buy-message').text("Market closed");
		$('#buy-form-button').hide();
		return;
	}
	else
	{
		$('#buy-frame').show();
		$('#buy-form-button').show();
		$('#buy-message').text("");
	}
	$('#cur_buy_price').text('Current Price: ');
	$('#buy_comp_sym').text('-');
	$('#buy_no_shares').text('-');
	$('#buy-type-of-trade').text( $('#buy-trans-type :selected').text() );
	$('#buy-total-value').text('-');
	$('#buy_brokerage').text('-');
	$('#buy_trade_price').text( '-' );
	$('#buy_margin').text('-');
	$('#buy-cash-bal').text('-');

	$('#buy-comp').get(0).selectedIndex = 0;
	$('#buy-trans-type').get(0).selectedIndex = 0;


	$('#buy-quantity').val(null);
	$('#buy-pending-price').val(null);

	if($('#buy-trans-type :selected').text()=="Buy")
		$('#buy_margin').hide();
	else
		$('#buy_margin').show();

	$('#buy-message').text('');



}

function checkPendingPrice()
{
	var inp = $('#buy-pending-price').val();
	var pending_price = buy_data.t_curr_price = parseFloat(inp);
				
	var curr_price = buy_data.curr_price;
	var per_x = 0.05*curr_price;
	
	var type_of_trans = $('#buy-trans-type :selected').text();
	var t = curr_price - per_x;
	var k = curr_price + per_x;
	var message ="";
	if( type_of_trans=="Buy" && ( pending_price > curr_price || pending_price <= t) )
			message= "Pending Price for Buying should be less than and maximum of 5% below Current Price";
	else 
		if( type_of_trans=="Short Sell" && (pending_price < curr_price || pending_price >= k) )
			message = "Pending Price for Short Selling should be greater than and maximum of 5% above Current Price"

	if(message!="")
		$('#buy-message').text(message);
	else
		$('#buy-message').text('');
}


function getCurrentPrice(company_symbol)
{
	$.post( page_url + '/currPrice',
	{
		company : company_symbol,
		csrfmiddlewaretoken : getCookie('csrftoken'),
	},
	onReceiveCurrentPrice
	);
}

function buyModalEventFunctions()
{
	$('#buy-comp').change(function(){
			var sym = $('#buy-comp :selected').text();
    		getCurrentPrice(sym);
    		$('#buy_comp_sym').text(sym);
	});

	$('#buy-quantity').change(function(){
    		$('#buy_no_shares').text($('#buy-quantity').val());
    		buy_data.quantity = $('#buy-quantity').val();
    		if( 'curr_price' in buy_data )
    		{
    			var k = parseFloat(buy_data.t_curr_price*$('#buy-quantity').val());
    			$('#buy-total-value').text( k.toFixed(2) );
    			$('#buy_margin').text( (k/2).toFixed(2) );
    			calBrokerage();
    		}
	});

	$('#buy-trans-type').change(function(){
			var type_of_trans = $('#buy-trans-type :selected').text();
    		$('#buy-type-of-trade').text( type_of_trans);
    		
    		if( type_of_trans=="Buy" )
    			$('#buy_margin').hide();
    		else
    			$('#buy_margin').show();
    		if($('#buy-pending-price').val()!="")
    			checkPendingPrice();
    		
	});

	$('#buy-pending-price').change( 
		function(){
			var inp = $('#buy-pending-price').val();
			if(inp=="")
				buy_data.t_curr_price = buy_data.curr_price;
			else
				checkPendingPrice();

			$('#buy_trade_price').text(buy_data.t_curr_price);
				
				var k = parseFloat(buy_data.t_curr_price*$('#buy-quantity').val());
    			$('#buy-total-value').text( k.toFixed(2) );
    			$('#buy_margin').text( (k/2).toFixed(2) );
    			calBrokerage();

		}
	);
	
	$('#buy-form').submit(
		
		function(event)
		{
			$('#buy-form-button').hide();
			var data={
				company : $('#buy-comp :selected').text(),
				quantity : $('#buy-quantity').val(),
				b_ss : $('#buy-trans-type :selected').text(),
				csrfmiddlewaretoken : getCookie('csrftoken'),
				pending : $('#buy-pending-price').val(),
			}
			
			$.post( page_url+'/submit_buy',
				data,
				function(data)
				{
					$('#buy-message').text(data.message);
					$('#buy-form-button').show();
				}
			);
				
			
			event.preventDefault();
		}
		);
	
}


function isTime()
{
	return true;
	var x = new Date();
	var time = x.getUTCHours()*60 + x.getUTCMinutes();
	var day = x.getDay();
	if( (time>=225 && time<600) && ( day>=1 && day<=5 ) )
		return true;
	return false;
}


function plotGraph(d) {
	d1 = d.graph_data;

	//This is mock data         Delete below line
	d1 =[ [4, "8848.45"], [9, "8855.30"], [14, "8859.10"], [19, "8855.65"], [24, "8864.85"], [29, "8867.20"], [34, "8861.95"], [39, "8861.60"], [44, "8867.00"], [49, "8862.95"], [54, "8854.40"], [59, "8861.05"], [64, "8860.00"], [69, "8860.45"], [74, "8861.40"], [79, "8857.80"], [84, "8857.55"], [89, "8858.10"], [94, "8856.50"], [99, "8857.75"], [104, "8862.70"], [109, "8864.95"], [114, "8863.85"], [119, "8862.80"], [124, "8862.00"], [129, "8860.85"], [134, "8866.75"], [139, "8870.70"], [144, "8865.80"], [149, "8867.65"], [154, "8867.40"], [160, "8866.85"], [165, "8870.10"], [169, "8866.95"], [174, "8868.70"], [179, "8867.50"], [184, "8868.15"], [189, "8868.35"], [194, "8873.10"], [199, "8870.60"], [204, "8865.55"], [210, "8868.95"], [214, "8868.25"], [219, "8869.60"], [224, "8868.15"], [229, "8862.35"], [234, "8860.90"], [239, "8863.65"], [244, "8863.10"], [249, "8866.30"], [254, "8866.85"], [259, "8863.70"], [264, "8861.60"], [269, "8862.10"], [274, "8861.95"], [279, "8860.60"], [284, "8857.95"], [289, "8859.75"], [294, "8868.85"], [299, "8866.20"], [304, "8865.30"], [310, "8856.75"], [314, "8857.45"], [320, "8860.90"], [326, "8859.20"], [331, "8855.15"], [336, "8843.60"], [341, "8847.60"], [345, "8848.45"], [350, "8842.20"], [355, "8828.85"], [361, "8829.60"], [366, "8830.35"], [371, "8823.65"]];
  

  var g_max=0,g_min=100000000;
	
	for(e of d1)
	{
		if(e[1]<g_min)
			g_min = e[1];
		if(e[1]>g_max)
			g_max = e[1];
	}
    


    if ($('#line-chart')[0]) {
        
        $.plot('#line-chart', [ {
            data: d1,
            label: "Data",

        },],

            {
                series: {
                    lines: {
                        show: true,
                        lineWidth: 1,
                        fill: 0.25,
                    },

                    color: 'rgba(255,255,255,0.7)',
                    shadowSize: 0,
                    points: {
                        show: true,
                    }
                },

                yaxis: {
                	min: g_min,
                    max: g_max,
                    tickColor: 'rgba(255,255,255,0.15)',
                    tickDecimals: 0,
                    font :{
                        lineHeight: 13,
                        style: "normal",
                        color: "rgba(255,255,255,0.8)",
                    },
                    shadowSize: 0,
                },
                xaxis: {
                	min:0,
                    max:375,
                    tickColor: 'rgba(255,255,255,0)',
                    tickDecimals: 0,
                    font :{
                        lineHeight: 13,
                        style: "normal",
                        color: "rgba(255,255,255,0.8)",
                    }
                },
                grid: {
                    borderWidth: 1,
                    borderColor: 'rgba(255,255,255,0.25)',
                    labelMargin:10,
                    hoverable: true,
                    clickable: true,
                    mouseActiveRadius:6,
                },
                legend: {
                    show: false
                }
            });

        $("#line-chart").bind("plothover", function (event, pos, item) {
            if (item) {
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                $("#linechart-tooltip").html(item.series.label + " of " + x + " = " + y).css({top: item.pageY+5, left: item.pageX+5}).fadeIn(200);
            }
            else {
                $("#linechart-tooltip").hide();
            }
        });

        $("<div id='linechart-tooltip' class='chart-tooltip'></div>").appendTo("body");
    }

}


function plotTicker(data)
{
	data = data.tickerData;
	StockTickerHTML = "";
	for(var stock of data){
        CompName = stock.name;
        Price = parseFloat(stock.current_price).toFixed(2);
        PercentChnageInPrice = parseFloat(stock.change_per).toFixed(2);
        
        var PriceClass = "GreenText", PriceIcon="up_green";
        if(PercentChnageInPrice < 0) { PriceClass = "RedText"; PriceIcon="down_red"; }
        StockTickerHTML = StockTickerHTML + "<span class='" + PriceClass + "'>";
        StockTickerHTML = StockTickerHTML + "<span class='quote'>" + CompName + "</span> ";
        
        StockTickerHTML = StockTickerHTML + Price + " ";
        StockTickerHTML = StockTickerHTML + "<span class='" + PriceIcon + "'></span>";
        StockTickerHTML = StockTickerHTML + Math.abs(PercentChnageInPrice) + "%</span>";
    }
	
    $("#dvStockTicker").html(StockTickerHTML);
    $("#dvStockTicker").jStockTicker({interval: 34, speed: 3});
}

    
function ticker () {
            $.get(page_url+'/ticker',plotTicker);
           	ticker_sock.open();
           	ticker_sock.onmessage = function(message){
           		plotTicker( JSON.parse(message.data) );
           	}

        }


function graph()
{
	$.get( page_url + '/graph',plotGraph);
	graph_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
	   	plotGraph(data);
	};
}
        
        