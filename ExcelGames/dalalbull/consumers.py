from channels import Group
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user
from django.core.serializers.json import DjangoJSONEncoder

import json
from .views import niftyData,sell_data,leaderboardData,graph,portfolio,ticker_data
from .models import Stock_data

import redis
from channels import Channel
redis_conn = redis.Redis("localhost", 6379)


#================ Nifty channel =======================#


def connect_to_nifty_channel(message):
	Group('nifty-channel').add(message.reply_channel)
	print("New nifty listener added!")


def disconnect_from_nifty_channel(message):
	Group('nifty-channel').discard(message.reply_channel)

def niftyChannelDataPush():

	nifty_data = niftyData()
	Group('nifty-channel').send( 
		{
			'text': json.dumps(nifty_data,cls=DjangoJSONEncoder)
		})





#================ Leaderboard channel =======================#


def connect_to_leaderboard_channel(message):
	Group('leaderboard-channel').add(message.reply_channel)
	print("New leaderboard listener added!")


def disconnect_from_leaderboard_channel(message):
	Group('leaderboard-channel').discard(message.reply_channel)

def leaderboardChannelDataPush():

	leaderboard_data = leaderboardData()
	Group('leaderboard-channel').send( 
		{
			'text': json.dumps(leaderboard_data,cls=DjangoJSONEncoder)
		})


#=============== Graph Channel =======================#

@channel_session
def connect_to_graph_channel(message):
	Group('NIFTY-50').add(message.reply_channel)
	print 'New graph listener!'


@channel_session
def disconnect_from_graph_channel(message):
	Group('NIFTY-50').discard(message.reply_channel)


def graphDataPush():
	graphData = graph('NIFTY 50')
	Group('NIFTY-50').send({
		'text': json.dumps(graphData,cls=DjangoJSONEncoder),
		})






#==================== portfolio channel ========================#


@http_session_user
def connect_to_portfolio_channel(message):
	try:
		print 'Portfolio listner added!'
		userid = message.http_session['dalalbull_uid']	
		redis_conn.hset("online-users",
			userid,
			message.reply_channel.name)
	except:
		print("user not logged in, can't connect to portfolio channel!")
		pass


@http_session_user
def disconnect_from_portfolio_channel(message):
	try:
		if 'dalalbull_uid' in message.http_session:
			userid = message.http_session['dalalbull_uid']	
			redis_conn.hdel("online-users",userid)
	except:
		pass



def portfolioDataPush():
	for userid in redis_conn.hkeys("online-users"):
		portfolioData = portfolio(userid)
		Channel( redis_conn.hget("online-users",userid)).send(
			{
			'text': json.dumps(portfolioData,cls=DjangoJSONEncoder)
			})






#======================= SELL CHANNEL ==========================#


@http_session_user
def connect_to_sell_channel(message):
	try:
		userid = message.http_session['dalalbull_uid']
		redis_conn.hset("online-sellers",
			userid,
			message.reply_channel.name)
		print 'New seller listener added!'
	except:
		print("user not logged in, can't connect to portfolio channel!")
		pass


@http_session_user
def disconnect_from_sell_channel(message):

	try:
		userid = message.http_session['dalalbull_uid']
		redis_conn.hdel("online-sellers",userid)
	except:
		pass


def sellDataPush():

	for userid in redis_conn.hkeys("online-sellers"):

		sellData = sell_data(userid)
		Channel( redis_conn.hget("online-sellers",userid) ).send(
			{
			'text' : json.dumps(sellData,cls=DjangoJSONEncoder)
			})




#================ Ticker Channel =======================#


@channel_session
def connect_to_ticker_channel(message):
	Group('Ticker').add(message.reply_channel)
	print 'New ticker listener!'


@channel_session
def disconnect_from_ticker_channel(message):
	Group('Ticker').discard(message.reply_channel)


def tickerDataPush():
	tickerData = ticker_data()
	Group('Ticker').send({
		'text': json.dumps(tickerData,cls=DjangoJSONEncoder),
		})










# #=============== Graph Channel For all companies =======================#

# @channel_session
# def connect_to_graph_channel(message):
# 	Group('NIFTY-50').add(message.reply_channel)
# 	print 'New graph listener!'
# 	redis_conn.hincrby("active-channels",'NIFTY 50',1)
# 	message.channel_session['connected-channel'] = 'NIFTY 50'



# ''' When the user sends us the company name
# we will pop the user from connected-channel queue 
# and add it to new company's channel '''

# @channel_session
# def connect_to_graph_channel_company(message):
# 	old_channel = message.channel_session['connected-channel']

# 	redis_conn.hincrby("active-channels",old_channel,-1)
# 	if redis_conn.hget("active-channels",old_channel)=='0':
# 		redis_conn.hdel("active-channels",old_channel)

# 	Group(old_channel.replace(' ','-')).discard(message.reply_channel)

# 	try:
# 		new_channel = json.loads(message['text'])['company']
# 	except:
# 		return
# 	if new_channel=="" or not Stock_data.objects.filter(symbol=new_channel).exists():
# 		return


# 	#print new_channel

# 	Group(new_channel.replace(' ','-')).add(message.reply_channel)
# 	message.channel_session['connected-channel'] = new_channel
# 	#print 'New user and channel!!!!!!!!!!!!!!!!!!!'

# 	redis_conn.hincrby("active-channels",new_channel,1)

# 	print'\n\nActive graph-channels'+str(redis_conn.hkeys("active-channels"))+'\n\n'

# 	graphData = graph(new_channel)
# 	Group(new_channel.replace(' ','-')).send({
# 		'text': json.dumps(graphData,cls=DjangoJSONEncoder)
# 		})



# @channel_session
# def disconnect_from_graph_channel(message):
# 	cur_channel = message.channel_session['connected-channel']

# 	Group(cur_channel.replace(' ','-')).discard(message.reply_channel)

# 	if redis_conn.hget("active-channels",cur_channel)!='0':
# 		redis_conn.hincrby("active-channels",cur_channel,-1)

# 	if redis_conn.hget("active-channels",cur_channel)=='0':
# 		redis_conn.hdel("active-channels",cur_channel)





# def graphDataPush():
# 	for company in redis_conn.hkeys("active-channels"):
# 		graphData = graph(company)
# 		Group(company.replace(' ','-')).send({
# 			'text': json.dumps(graphData,cls=DjangoJSONEncoder),
# 			})



# '''
# Since channel name doesn't suppport space in
# Group('channel name')
# I have replaced ' ' with '-' whenever channel name is used with Group.
# '''

