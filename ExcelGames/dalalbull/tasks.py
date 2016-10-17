from __future__ import absolute_import

from celery import shared_task
from ExcelGames.celery import app

import urllib2
import json
import datetime
from .models import User,Portfolio,Stock_data,Transaction,History,Pending,Old_Stock_data

from .consumers import sellDataPush,niftyChannelDataPush,leaderboardChannelDataPush,graphDataPush,portfolioDataPush,tickerDataPush


#Deletes all old stock data

#======Tasks======#


@shared_task
def tq(): 	
	print("Stock Update");	
	stockdata()
	print("Orders");	
	orders()
	return 

@shared_task
def dq(): 
	print("Graph Values Update");
	oldstockdata()
	return 

@shared_task
def net():
    print("Networth Update");
    networth()
    return


@shared_task
def broadcastNiftyData():
	if isGoodTime():
		print("Nifty data broadcasted!")
		niftyChannelDataPush()
	else:
		print("Not the time for nifty broadcast")


@shared_task
def broadcastLeaderboardData():
	if isGoodTime():
		print("Leaderboard data broadcasted!")
		leaderboardChannelDataPush()
	else:
		print("Not the time for leaderboard broadcast")

@shared_task
def broadcastGraphData():
	if isGoodTime():
		print("Grap data broadcasted!")
		graphDataPush()
	else:
		print("Not the time for graph broadcast")


@shared_task
def broadcastSellData():
	if isGoodTime():
		print("Sellers data broadcasted!")
		sellDataPush()
	else:
		print("Not the time for sell broadcast")

@shared_task
def broadcastPortfolioData():
	if isGoodTime():
		print("Portfolio data broadcasted!")
		portfolioDataPush()
	else:
		print("Not the time for portfolio broadcast")





@shared_task
def broadcastTickerData():
	if isGoodTime():
		print("Ticker data broadcasted!")
		tickerDataPush()
	else:
		print("Not the time for ticker broadcast")



#==========Utility Functions========#
				
#==========Sell/Short-Cover========#        
def sell_sc(username,symbol,quantity,typ):
	qnty=float(quantity)
	try:
		price = float(Stock_data.objects.get(symbol=symbol).current_price)
		port = Portfolio.objects.get(user_id=username)
		cash_bal = float(port.cash_bal)
		no_trans = float(port.no_trans)
		margin = float(port.margin)
		
		if(typ=="Sell"):
			b_ss="Buy"
		else:
			b_ss="Short Sell"
		
		try:
			t=Transaction.objects.get(symbol=symbol,user_id=username,buy_ss=b_ss)
			old_quantity = float(t.quantity)
			old_value = float(t.value)
			
			if(quantity<=old_quantity):
				new_quantity=old_quantity-qnty
				old_total=(old_value/old_quantity)*qnty
				new_value=old_value-old_total;
				if(new_quantity==0):
					t.delete()
				else:
					t.quantity=new_quantity
					t.value=new_value
					t.save()
				try:
					port = Portfolio.objects.get(user_id=username)
					old_cash_bal = float(port.cash_bal)
					margin =float(port.margin)
					no_trans = float(port.no_trans)
					if(typ == "Short Cover"):
						sc_profit=old_total-qnty*price
						cash_bal=old_cash_bal+sc_profit
						margin=(margin-(old_value/2))+(new_value/2)
					elif(typ == "Sell"):
						cash_bal=old_cash_bal+(qnty*price)						
					no_trans=no_trans+1
					if(no_trans<=100):
						brokerage=((0.5/100)*price)*qnty
					elif(no_trans<=1000):
						brokerage=((1/100)*price)*qnty
					else:
						brokerage=((1.5/100)*price)*qnty
					
					print("\nupdating portfolio")
					cash_bal-=brokerage
					port.cash_bal=cash_bal
					port.margin=margin
					port.no_trans=no_trans
					port.save()
					print("Pending order completed")
					history=History(user_id=username,time=datetime.datetime.now(),symbol=symbol,buy_ss=typ,quantity=qnty,price=price)
					history.save()
					return True
				except Portfolio.DoesNotExist:
					print("Error fetching portfolio")
		except Transaction.DoesNotExist:
			print("Error fetching from transactions ")
			return False
	except Stock_data.DoesNotExist:
		return False
	return False
#==========Buy/Short-Sell========#
def buy_ss(username,symbol,quantity,typ):	
	qnty=float(quantity)
	try:
		price = float(Stock_data.objects.get(symbol=symbol).current_price)
		port = Portfolio.objects.get(user_id=username)
		cash_bal = float(port.cash_bal)
		no_trans = float(port.no_trans)
		margin = float(port.margin)
		if(no_trans+1<=100):
			brokerage=((0.5/100)*price)*qnty
		else:
			if(no_trans+1<=1000):
				brokerage=((1/100)*price)*qnty
			else:
				brokerage=((1.5/100)*price)*qnty
		if(((cash_bal-margin-brokerage)>0 and (cash_bal-margin-brokerage)>=(price*qnty) and typ == "Buy") or ((cash_bal-margin-brokerage)>=((price*qnty)/2) and typ == "Short Sell")):
			try:
				trans = Transaction.objects.get(user_id=username,symbol=symbol,buy_ss=typ)
				old_qnty = float(trans.quantity)
				value = float(trans.value)
				value +=(qnty*price)
				new_qnty = old_qnty + qnty
				trans.quantity=new_qnty
				trans.value=value
				trans.save()
				print("Pending order completed")
			except Transaction.DoesNotExist:
				value = qnty*price
				trans = Transaction(user_id=username,symbol=symbol,buy_ss=typ,quantity=qnty,value=value)
				trans.save()
				print("Pending order completed")  					
			if(typ =="Buy"): 
				cash_bal_up = cash_bal-(qnty*price)
				margin_up = margin
			else:
				if(typ =="Short Sell"): 
					cash_bal_up = cash_bal
					margin_up = margin+(qnty*price)/2
			cash_bal_up -= brokerage
			no_trans+=1
			port.cash_bal=cash_bal_up
			port.margin=margin_up
			port.no_trans=no_trans
			port.save()
			history=History(user_id=username,time=datetime.datetime.now(),symbol=symbol,buy_ss=typ,quantity=qnty,price=price)
			history.save()
			return True
	except Stock_data.DoesNotExist:
		return False	
	return False

#===============Orders=================#
def orders():
	ret=False
	if(datetime.datetime.now().strftime("%A")!='Sunday' and datetime.datetime.now().strftime("%A")!='Saturday'):
		if((datetime.datetime.now().time()>=datetime.time(hour=9,minute=00,second=00))) and (datetime.datetime.now().time()<=datetime.time(hour=9,minute=01,second=00)):
			Old_Stock_data.objects.all().delete()
	if((datetime.datetime.now().time()>=datetime.time(hour=9,minute=06,second=00))) and (datetime.datetime.now().time()<=datetime.time(hour=9,minute=06,second=30)):
		oldstockdata()
	if(datetime.datetime.now().time()>=datetime.time(hour=15,minute=30,second=00)):
		try:
			day_endq=Transaction.objects.filter(buy_ss='Short Sell')
			for i in day_endq :
				username = i.user_id 
				symbol = i.symbol
				quantity = i.quantity
				type_temp = "Short Cover";
				print("Short Cover")
				ret= sell_sc(username,symbol,quantity,type_temp)		
		except Transaction.DoesNotExist :
			print("No Transactions")   		
		Pending.objects.all().delete()
	else:
		try:
			pending_ord = Pending.objects.all()
			for i in pending_ord :
				idn = i.id
				username = i.user_id
				symbol = i.symbol
				typ = i.buy_ss
				quantity = i.quantity
				price = i.value
				try:
					stock_qry = Stock_data.objects.get(symbol=symbol)
					current_price  = stock_qry.current_price
					if(current_price >0):
						if(current_price<=price):
							if(typ == "Buy"):
								ret= buy_ss(username,symbol,quantity,typ)
							else:
								if(typ == "Short Cover"):
									ret=sell_sc(username,symbol,quantity,typ)
						else:
							if(current_price>=price):
								if(typ == "Sell"):
									ret=sell_sc(username,symbol,quantity,typ)
								else:
									if(typ == "Short Sell"):
										ret=buy_ss(username,symbol,quantity,typ)
						if(ret==True):
							ret=False
							del_query = Pending.objects.get(id=idn,user_id=username,symbol=symbol,buy_ss=typ,quantity=quantity,value=price)
							del_query.delete()
				except Stock_data.DoesNotExist:
					print("Company Not Listed")
		except Pending.DoesNotExist:
			print("No Pending Orders")	

#========Networth Update========#
def networth():
	u = User.objects.all()
	for k in u:
		try:
			i=Portfolio.objects.get(user_id=k.user_id)	
			net_worth=float(i.cash_bal)
			try:
				trans=Transaction.objects.filter(user_id=i.user_id,buy_ss='Buy')
				for j in trans:
					try:
						current_price = float(Stock_data.objects.get(symbol=j.symbol).current_price)
						net_worth+=current_price*float(j.quantity)
					except Stock_data.DoesNotExist:
						print("Company Not Listed")
				i.net_worth = net_worth
				i.save()
			except Transaction.DoesNotExist:
				print("No Transactons")
		except Portfolio.DoesNotExist:
			print("Fail")
	return

#=======Stock Database Update=========#

def stockdata():

	symbolmap={}
	symbolmap['NIFTY 50']=0                        
	symbolmap['INFY'] = 1
	symbolmap['TECHM'] = 2
	symbolmap['TCS'] = 3
	symbolmap['RELIANCE'] = 4
	symbolmap['HCLTECH'] = 5
	symbolmap['WIPRO'] = 6
	symbolmap['COALINDIA'] = 7
	symbolmap['KOTAKBANK'] = 8
	symbolmap['HDFCBANK'] = 9
	symbolmap['EICHERMOT'] = 10
	symbolmap['HDFC'] = 11
	symbolmap['ASIANPAINT'] = 12
	symbolmap['IDEA'] = 13
	symbolmap['HINDUNILVR'] = 14
	symbolmap['BHARTIARTL'] = 15
	symbolmap['MARUTI'] = 16
	symbolmap['SUNPHARMA'] = 17
	symbolmap['CIPLA'] = 18
	symbolmap['POWERGRID'] = 19
	symbolmap['ONGC'] = 20
	symbolmap['GRASIM'] = 21
	symbolmap['INDUSINDBK'] = 22
	symbolmap['DRREDDY'] = 23
	symbolmap['ICICIBANK'] = 24
	symbolmap['HEROMOTOCO'] = 25
	symbolmap['ULTRACEMCO'] = 26
	symbolmap['GAIL'] = 27
	symbolmap['INFRATEL'] = 28
	symbolmap['LUPIN'] = 29
	symbolmap['ITC'] = 30
	symbolmap['AUROPHARMA'] = 31
	symbolmap['BAJAJ-AUTO'] = 32
	symbolmap['BOSCHLTD'] = 33
	symbolmap['ZEEL'] = 34
	symbolmap['TATAMTRDVR'] = 35
	symbolmap['M&M'] = 36
	symbolmap['TATAMOTORS'] = 37
	symbolmap['AXISBANK'] = 38
	symbolmap['LT'] = 39
	symbolmap['NTPC'] = 40
	symbolmap['BPCL'] = 41
	symbolmap['TATAPOWER'] = 42
	symbolmap['SBIN'] = 43
	symbolmap['BHEL'] = 44
	symbolmap['ACC'] = 45
	symbolmap['ADANIPORTS'] = 46
	symbolmap['AMBUJACEM'] = 47
	symbolmap['TATASTEEL'] = 48
	symbolmap['BANKBARODA'] = 49
	symbolmap['YESBANK'] = 50
	symbolmap['HINDALCO'] = 51                        
	now = datetime.datetime.now()
	#print 'Reached here!'
	if(now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):
		print 'Reached here!'
		start_time=datetime.time(hour=9,minute=15,second=00)
		end_time=datetime.time(hour=15,minute=30,second=00)
		now = datetime.datetime.now().time()

		#print 'S={},E={},N={}'.format(start_time,end_time,now)
		
		#print ( (start_time<now) and (now<end_time) )
		
		if (start_time < now < end_time):
			print 'Reached here!2'
			try :
				url='http://nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json'
				CNames = 'INFY.NS,TECHM.NS,TCS.NS,RELIANCE.NS,HCLTECH.NS,WIPRO.NS,COALINDIA.NS,KOTAKBANK.NS,HDFCBANK.NS,EICHERMOT.NS,HDFC.NS,ASIANPAIN.NS,IDEA.NS,HINDUNILVR-EQ.NS,BHARTIART.NS,MARUTI.NS,SUNPHARMA.NS,CIPLA.NS,POWERGRID.NS,ONGC.NS,GRASIM.NS,INDUSINDBK-EQ.NS,DRREDDY.NS,ICICIBANK.NS,HEROMOTOC.NS,ULTRACEMC.NS,GAIL.NS,INFRATEL.NS,LUPIN.NS,ITC.NS,AUROPHARM.NS,BAJAJ-AUTO-EQ.NS,BOSCHLTD.NS,ZEEL.NS,TATAMTRDVR.NS,M&M.NS,TATAMOTOR.NS,AXISBANK.NS,LT.NS,NTPC.NS,BPCL.NS,TATAPOWER.NS,SBIN.NS,BHEL.NS,ACC.NS,ADANIPORTS.NS,AMBUJACEM.NS,TATASTEEL.NS,BANKBAROD.NS,YESBANK.NS,HINDALCO.NS'
				yurl='http://finance.yahoo.com/webservice/v1/symbols/%5Ensei,'+CNames+'/quote?format=json&view=detail'
				hdr = {'User-Agent': "Mozilla/5.0 (Linux; Android 6.0.1; MotoG3 Build/MPI24.107-55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.81 Mobile Safari/537.36",
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
						'Accept-Encoding': 'none',
						'Accept-Language': 'en-US,en;q=0.8',
						'Connection': 'keep-alive'}
				req = urllib2.Request(url, headers=hdr) 
				response = urllib2.urlopen( req )
				yreq = urllib2.Request(yurl, headers=hdr)
				yresponse = urllib2.urlopen( yreq )
				yahoo = {}
				yahoo = json.load(yresponse)
				json_data=json.load(response)
				print 'This is it: '+str(yahoo)[:100]
				print(yahoo['list']['resources'][0]['resource']['fields']['price'])
				company=json_data['latestData'][0]
				try :
					company=json_data['latestData'][0]
					c=Stock_data.objects.get(symbol='NIFTY 50')
					print("Not this problem!")
					c.current_price=yahoo['list']['resources'][symbolmap['NIFTY 50']]['resource']['fields']['price']
					c.high=company['high'].replace(",","")
					c.low=company['low'].replace(",","")
					c.open_price=company['open'].replace(",","")
					c.change=company['ch'].replace(",","")
					c.change_per=company['per'].replace(",","")
					c.trade_Qty=json_data['trdVolumesum'].replace(",","")
					c.trade_Value=json_data['trdValueSum'].replace(",","")
					c.save() 	
				except Stock_data.DoesNotExist :
					print("--Stock_data.DoesNotExist--1")
					c=Stock_data(symbol=company['indexName'],
						current_price=company['ltp'].replace(",",""),
						high=company['high'].replace(",",""),
						low=company['low'].replace(",",""),
						open_price=company['open'].replace(",",""),
						change=company['ch'].replace(",",""),
						change_per=company['per'].replace(",",""),
						trade_Qty=json_data['trdVolumesum'].replace(",",""),
						trade_Value=json_data['trdValueSum'].replace(",","")
						)
					c.save()		    		
				for company in json_data['data']:
					try :						
						c=Stock_data.objects.get(symbol=company['symbol'])
						c.current_price=yahoo['list']['resources'][symbolmap[company['symbol']]]['resource']['fields']['price']
						c.high=company['high'].replace(",","")
						c.low=company['low'].replace(",","")
						c.open_price=company['open'].replace(",","")
						c.change=company['ptsC'].replace(",","")
						c.change_per=company['per'].replace(",","")
						c.trade_Qty=company['trdVol'].replace(",","")
						c.trade_Value=company['ntP'].replace(",","")
						c.save()
					except Stock_data.DoesNotExist :
						print("--Stock_data.DoesNotExist--")
						c=Stock_data(symbol=company['symbol'],current_price=company['ltP'].replace(",",""),high=company['high'].replace(",",""),low=company['low'].replace(",",""),open_price=company['open'].replace(",",""),change=company['ptsC'].replace(",",""),change_per=company['per'].replace(",",""),trade_Qty=company['trdVol'].replace(",",""),trade_Value=company['ntP'].replace(",",""))
						c.save()		    		
			except urllib2.HTTPError, e:
					print 'URL ERROR'
					print e.fp.read()


#==================STOCK UPDATE FOR GRAPH=============

def oldstockdata():
	symbolmap={}
	symbolmap['NIFTY 50']=0                        
	symbolmap['INFY'] = 1
	symbolmap['TECHM'] = 2
	symbolmap['TCS'] = 3
	symbolmap['RELIANCE'] = 4
	symbolmap['HCLTECH'] = 5
	symbolmap['WIPRO'] = 6
	symbolmap['COALINDIA'] = 7
	symbolmap['KOTAKBANK'] = 8
	symbolmap['HDFCBANK'] = 9
	symbolmap['EICHERMOT'] = 10
	symbolmap['HDFC'] = 11
	symbolmap['ASIANPAINT'] = 12
	symbolmap['IDEA'] = 13
	symbolmap['HINDUNILVR'] = 14
	symbolmap['BHARTIARTL'] = 15
	symbolmap['MARUTI'] = 16
	symbolmap['SUNPHARMA'] = 17
	symbolmap['CIPLA'] = 18
	symbolmap['POWERGRID'] = 19
	symbolmap['ONGC'] = 20
	symbolmap['GRASIM'] = 21
	symbolmap['INDUSINDBK'] = 22
	symbolmap['DRREDDY'] = 23
	symbolmap['ICICIBANK'] = 24
	symbolmap['HEROMOTOCO'] = 25
	symbolmap['ULTRACEMCO'] = 26
	symbolmap['GAIL'] = 27
	symbolmap['INFRATEL'] = 28
	symbolmap['LUPIN'] = 29
	symbolmap['ITC'] = 30
	symbolmap['AUROPHARMA'] = 31
	symbolmap['BAJAJ-AUTO'] = 32
	symbolmap['BOSCHLTD'] = 33
	symbolmap['ZEEL'] = 34
	symbolmap['TATAMTRDVR'] = 35
	symbolmap['M&M'] = 36
	symbolmap['TATAMOTORS'] = 37
	symbolmap['AXISBANK'] = 38
	symbolmap['LT'] = 39
	symbolmap['NTPC'] = 40
	symbolmap['BPCL'] = 41
	symbolmap['TATAPOWER'] = 42
	symbolmap['SBIN'] = 43
	symbolmap['BHEL'] = 44
	symbolmap['ACC'] = 45
	symbolmap['ADANIPORTS'] = 46
	symbolmap['AMBUJACEM'] = 47
	symbolmap['TATASTEEL'] = 48
	symbolmap['BANKBARODA'] = 49
	symbolmap['YESBANK'] = 50
	symbolmap['HINDALCO'] = 51                        
	now = datetime.datetime.now()
	if(now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):
		start_time=datetime.time(hour=9,minute=15,second=00)
		end_time=datetime.time(hour=15,minute=30,second=00)
		now = datetime.datetime.now().time()
		if(start_time<now<end_time):
			try :
				url='http://nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json'
				CNames = 'INFY.NS,TECHM.NS,TCS.NS,RELIANCE.NS,HCLTECH.NS,WIPRO.NS,COALINDIA.NS,KOTAKBANK.NS,HDFCBANK.NS,EICHERMOT.NS,HDFC.NS,ASIANPAIN.NS,IDEA.NS,HINDUNILVR-EQ.NS,BHARTIART.NS,MARUTI.NS,SUNPHARMA.NS,CIPLA.NS,POWERGRID.NS,ONGC.NS,GRASIM.NS,INDUSINDBK-EQ.NS,DRREDDY.NS,ICICIBANK.NS,HEROMOTOC.NS,ULTRACEMC.NS,GAIL.NS,INFRATEL.NS,LUPIN.NS,ITC.NS,AUROPHARM.NS,BAJAJ-AUTO-EQ.NS,BOSCHLTD.NS,ZEEL.NS,TATAMTRDVR.NS,M&M.NS,TATAMOTOR.NS,AXISBANK.NS,LT.NS,NTPC.NS,BPCL.NS,TATAPOWER.NS,SBIN.NS,BHEL.NS,ACC.NS,ADANIPORTS.NS,AMBUJACEM.NS,TATASTEEL.NS,BANKBAROD.NS,YESBANK.NS,HINDALCO.NS'
				yurl='http://finance.yahoo.com/webservice/v1/symbols/%5Ensei,'+CNames+'/quote?format=json&view=detail'
				hdr = {'User-Agent': "Mozilla/5.0 (Linux; Android 6.0.1; MotoG3 Build/MPI24.107-55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.81 Mobile Safari/537.36",
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
						'Accept-Encoding': 'none',
						'Accept-Language': 'en-US,en;q=0.8',
						'Connection': 'keep-alive'}
				req = urllib2.Request(url, headers=hdr) 
				response = urllib2.urlopen( req )
				yreq = urllib2.Request(yurl, headers=hdr)
				yresponse = urllib2.urlopen( yreq )
				yahoo = {}
				yahoo = json.load(yresponse)
				json_data=json.load(response)
				#print(yahoo['list']['resources'][0]['resource']['fields']['price'])
				company=json_data['latestData'][0]
				try :
					company=json_data['latestData'][0]
					c=Old_Stock_data(symbol="NIFTY 50",
						current_price=yahoo['list']['resources'][symbolmap['NIFTY 50']]['resource']['fields']['price'])
					c.save() 	
				except :
				    print("Exception1")	    		
				for company in json_data['data']:
					try :					
						c=Old_Stock_data(symbol=company['symbol'],
							current_price=yahoo['list']['resources'][symbolmap[company['symbol']]]['resource']['fields']['price']
							)
						c.save()
					except :
						print("Exception2")
						x=0	    		
			except urllib2.HTTPError, e:
				print e.fp.read()




def isGoodTime():
	now = datetime.datetime.now()
	if(now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):
		start_time=datetime.time(hour=9,minute=15,second=00)
		end_time=datetime.time(hour=15,minute=30,second=00)
		now = datetime.datetime.now().time()
		if(start_time<=now<end_time):
			return True

	return False


