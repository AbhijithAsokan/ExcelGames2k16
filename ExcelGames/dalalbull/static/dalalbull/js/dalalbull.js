var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var url = window.location.host;
var page_url = 'http://' +url; 

// SOCKETS
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


	nifty_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
	    $('#nifty-data').text(""+data.current_price);
	};

	portfolio_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data);
	    $('#networth').text(""+data.net_worth);
	    $('#rank').text(""+data.rank)
	    $('#cash-balance').text(""+data.cash_bal);
	    $('#margin').text(""+data.margin);
	    $('#transactions').text(""+data.total_no);
	};

	leaderboard_sock.onmessage = function(message) {
	    var data = JSON.parse(message.data).leaderboard_data;
	   	var leaderboard_table_body = $('#leaderboard-data');
	   	leaderboard_table_body.html('');

	   	var tableRow;

	   	for(var item of data)
	   	{
	   		tableRow = $('<tr></tr>');
	   		tableRow.append( $('<td></td>').text(item.name) );
	   		tableRow.append( $('<td></td>').text(item.net_worth) );
	   		leaderboard_table_body.append(tableRow);
	   	}

	};


var setDashboard =function(data)
{
	console.log("Reached here!");
	console.log(data);
	var tableRow;

	// Filling top gainers table
	var topGainers = data.topGainers;
	var topGainersTable = $('#top-gainers');

	for(var companyDetails of topGainers)
	{
		tableRow = $('<tr></tr>');
		tableRow.append( $('<td></td>').text(""+companyDetails.name) );
		tableRow.append( $('<td></td>').text(companyDetails.change_per+"%") ); 
		topGainersTable.append(tableRow);	
	}

	// Filling top losers table
	var topLosers = data.topLosers;
	var topLosersTable = $('#top-losers');

	for(var companyDetails of topLosers)
	{
		tableRow = $('<tr></tr>');
		tableRow.append( $('<td></td>').text(""+companyDetails.name) );
		tableRow.append( $('<td></td>').text(companyDetails.change_per+"%") ); 
		topLosersTable.append(tableRow);	
	}

	// Filling most active (value) table
	var mostActiveVal = data.mostActiveVal;
	var mostActiveValTable = $('#most-active-val');

	for(var companyDetails of mostActiveVal)
	{
		tableRow = $('<tr></tr>');
		tableRow.append( $('<td></td>').text(""+companyDetails.name) );
		tableRow.append( $('<td></td>').text(""+companyDetails.trade_val) ); 
		mostActiveValTable.append(tableRow);	
	}


	// Filling top active (volume) table
	var mostActiveVol = data.mostActiveVol;
	var mostActiveVolTable = $('#most-active-vol');

	for(var companyDetails of topLosers)
	{
		tableRow = $('<tr></tr>');
		tableRow.append( $('<td></td>').text(""+companyDetails.name) );
		tableRow.append( $('<td></td>').text(""+companyDetails.trade_qty) ); 
		mostActiveVolTable.append(tableRow);	
	}


}



function dashboard()
{
	nifty_sock.open();
	leaderboard_sock.open();
	portfolio_sock.open();
	graph_sock.open();

	$.get(page_url + '/dashboard',setDashboard);
}







$(document).ready( dashboard());





