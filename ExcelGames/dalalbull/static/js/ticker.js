
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
    
