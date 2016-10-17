from django.conf.urls import url

from . import views

urlpatterns = [

	url(r'^$', views.index, name='index'),
	url(r'^dashboard$', views.dashboard, name='dashboard'),	
	url(r'^sell$', views.sell, name='sell'),	
	url(r'^pending$', views.pending, name='pending'),	
	url(r'^ticker$', views.ticker, name='ticker'),
	url(r'^cancels$', views.cancels, name='cancels'),	
	url(r'^submit_buy$', views.submit_buy, name='submit'),
	url(r'^submit_sell$', views.submit_sell, name='submit'),				
	url(r'^currPrice$', views.currPrice, name='currentPrice'),					
	url(r'^history$', views.history, name='history'),								
	url(r'^stockinfo$', views.stockinfo, name='stockinfo'),		
	url(r'^companydetails$', views.companydetails, name='companydetails'),
	url(r'^portfolio$', views.portfolioView, name='portfolio'),
	url(r'^graph$', views.graphView, name='graph'),	
	url(r'^leaderboard$', views.leaderboard, name='leaderboard'),	
	url(r'^nifty$', views.nifty, name='nifty'),	

	#url(r'^channels$', views.testChannels, name='aboutus'),	
]