(function($) {
			$.fn.jStockTicker = function(options) {
				if (typeof (options) == 'undefined') {
					options = {};
				}
				var settings = $.extend( {}, $.fn.jStockTicker.defaults, options);
				var $ticker = $(this);
				var $wrap = null;
				settings.tickerID = $ticker[0].id;
				$.fn.jStockTicker.settings[settings.tickerID] = {};

				if ($ticker.parent().get(0).className != 'wrap') {
					$wrap = $ticker.wrap("<div class='wrap'></div>");
				}

				var $tickerContainer = null;
				if ($ticker.parent().parent().get(0).className != 'container') {
					$tickerContainer = $ticker.parent().wrap(
							"<div class='container1'></div>");
				}
				
				var node = $ticker[0].firstChild;
				var next;
				while(node) {
					next = node.nextSibling;
					if(node.nodeType == 3) {
						$ticker[0].removeChild(node);
					}
					node = next;
				}
				
				var shiftLeftAt = $ticker.children().get(0).offsetWidth;
				$.fn.jStockTicker.settings[settings.tickerID].shiftLeftAt = shiftLeftAt;
				$.fn.jStockTicker.settings[settings.tickerID].left = 0;
				$.fn.jStockTicker.settings[settings.tickerID].runid = null;
				$ticker.width(2 * screen.availWidth);
				
				function startTicker() {
					stopTicker();
					
					var params = $.fn.jStockTicker.settings[settings.tickerID]; 
					params.left -= settings.speed;
					if(params.left <= params.shiftLeftAt * -1) {
						params.left = 0;
						$ticker.append($ticker.children().get(0));
						params.shiftLeftAt = $ticker.children().get(0).offsetWidth;
					}
					
					$ticker.css('left', params.left + 'px');
					params.runId = setTimeout(arguments.callee, settings.interval);
					
					$.fn.jStockTicker.settings[settings.tickerID] = params;
				}
				
				function stopTicker() {
					var params = $.fn.jStockTicker.settings[settings.tickerID];
					if (params.runId)
						clearTimeout(params.runId);
					
					params.runId = null;
					$.fn.jStockTicker.settings[settings.tickerID] = params;
				}
				
				function updateTicker() {			
					stopTicker();
					startTicker();
				}
				
				$ticker.hover(stopTicker,startTicker);		
				startTicker();
			};

			$.fn.jStockTicker.settings = {};
			$.fn.jStockTicker.defaults = {
				tickerID :null,
				url :null,
				speed :0,
				interval :2
			};
		})(jQuery);
    
$(window).load(function () {
            StockPriceTicker();
            setInterval(function() {StockPriceTicker();} , 60000);
        });
        function StockPriceTicker() {
            /*var Symbol = "", CompName = "", Price = "", ChnageInPrice = "", PercentChnageInPrice = ""; 
			var	CNames = 'TECHM.NS,BPCL.NS,HEROMOTOC.NS,BAJAJ-AUTO-EQ.NS,HINDUNILVR-EQ.NS,LUPIN.NS,POWERGRID.NS,ITC.NS,GAIL.NS,NTPC.NS,TCS.NS,ULTRACEMC.NS,IDEA.NS,M&M.NS,INFY.NS,CIPLA.NS,WIPRO.NS,HDFC.NS,CAIRN.NS,MARUTI.NS,RELIANCE.NS,BHARTIART.NS,ZEEL.NS,ONGC.NS,LT.NS,ASIANPAIN.NS,PNB.NS,TATAPOWER.NS,COALINDIA.NS,BHEL.NS,DRREDDY.NS,YESBANK.NS,SUNPHARMA.NS,GRASIM.NS,AXISBANK.NS,AMBUJACEM.NS,BANKBAROD.NS,TATASTEEL.NS,KOTAKBANK.NS,NMDC.NS,INDUSINDBK-EQ.NS,HDFCBANK.NS,VEDL-EQ.NS,BOSCHLTD.NS,ACC.NS,TATAMOTOR.NS,HCLTECH.NS,ICICIBANK.NS,SBIN.NS,HINDALCO.NS'
            var flickerAPI = "http://finance.yahoo.com/webservice/v1/symbols/%5Ensei,"+CNames+"/quote?format=json&view=detail&callback=?";
            var StockTickerHTML = "";
            
            var StockTickerXML = (jq).getJSON(flickerAPI, function(data) {
            var stock_data=data.list.resources;*/
            var StockTickerHTML = "";
            for(i=0;i<50;i++){
            	      //curr=stock_data[i].resource.fields;
                    Symbol = "lol";
                    CompName = "laugh out loud";
                    Price = "10";
                    ChnageInPrice = "5";
                    PercentChnageInPrice = "2";
                    
                    var PriceClass = "GreenText", PriceIcon="up_green";
                    if(parseFloat(ChnageInPrice) < 0) { PriceClass = "RedText"; PriceIcon="down_red"; }
                    StockTickerHTML = StockTickerHTML + "<span class='" + PriceClass + "'>";
                    StockTickerHTML = StockTickerHTML + "<span class='quote'>" + CompName + " (" + Symbol + ")</span> ";
                    
                    StockTickerHTML = StockTickerHTML + parseFloat(Price).toFixed(2) + " ";
                    StockTickerHTML = StockTickerHTML + "<span class='" + PriceIcon + "'></span>" + parseFloat(Math.abs(ChnageInPrice)).toFixed(2) + " (";
                    StockTickerHTML = StockTickerHTML + parseFloat( Math.abs(PercentChnageInPrice.split('%')[0])).toFixed(2) + "%)</span>";
                }
				
                $("#dvStockTicker").html(StockTickerHTML);
                $("#dvStockTicker").jStockTicker({interval: 34, speed: 3});
//            });
        }