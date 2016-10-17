from django.shortcuts import render,redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt
from django.views.decorators.cache import never_cache 
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse,HttpResponseRedirect
from ExcelGames import settings
from pytz import timezone
import urllib2
import json
import datetime
import re
from .models import User,Portfolio,History,Pending,Transaction,Old_Stock_data,Stock_data
from home.models import User as HomeUser


def index(request):
    if 'logged_in' in request.session:
        if request.session['logged_in']:
            user_id = request.session['uid']
            if not User.objects.filter(user_id=user_id).exists():

                home_user = HomeUser.objects.get(user_id=user_id)
                
                User.objects.create(
                    user_id=home_user.user_id,
                    name=home_user.name,
                    email = home_user.email,
                    image_url = home_user.image_url,
                    )
                
                Portfolio.objects.create(
                user_id=user_id,
                net_worth=1000000.00,
                cash_bal=1000000.00,
                )
                
            request.session['is_dalalbull_user'] = True
            request.session['dalalbull_uid'] = user_id
            
            return render(request,'index.html',
                {
                    'user': User.objects.get(user_id = user_id),
                }
                )

    return HttpResponseRedirect("/")


#======Dashboard======#
@ensure_csrf_cookie
@never_cache
def dashboard(request):
    
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        
        total_users = User.objects.count()

        data_to_send = {
            # 'user_id': request.session['dalalbull_uid'],
            # 'username' : username,
            'total_users' : total_users,
            'stockholdings':getStockholdings(request.session['dalalbull_uid']),
            'topGainers' : getTopGainers(),
            'topLosers' : getTopLosers(),
            'mostActiveVol' : getMostActiveVolume(),
            'mostActiveVal' : getMostActiveValue(),
        }

        return JsonResponse(data_to_send)
    
    else:
        return  HttpResponseForbidden("Access Denied")



def nifty(request):
    return JsonResponse(niftyData())

def portfolioView(request):
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        return JsonResponse(portfolio(request.session['dalalbull_uid'] )) 


def leaderboard(request):
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        return JsonResponse(leaderboardData()) 

def graphView(request):
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        return JsonResponse( graph('NIFTY 50')) 


    
    
#======STOCKINFO======#
'''
Page stock information.
List of all companies.
'''
@csrf_exempt
def stock_symbols():  
        stocks=Stock_data.objects.all()    
        companies =[]                      
        for c in stocks:
            companies.append(c.symbol)

        data_to_send = {
            'companies' : companies,
            }
        return data_to_send

@csrf_exempt
def stockinfo(request):                            
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        data_to_send = stock_symbols()
        return JsonResponse(data_to_send)
            
    return  HttpResponseForbidden("Access Denied")
#======Company Info=====#

'''
Information about each company.
Post data format:
    {
        'company' : ___,
    }
'''

def companydetails(request):
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:                                
        company = request.POST['company']
        try:
            data_to_send = Stock_data.objects.get(symbol=company).as_dict()
            return JsonResponse(data_to_send)
        except:
            return JsonResponse({ 
                'result' : 'wrong company name!'}
                )
    return  HttpResponseForbidden("Access Denied")


#======Buy/Short-Sell======#

# buy() removed, since it is same as company info 


#======Submit-Buy======#

@ensure_csrf_cookie
def submit_buy(request):
    '''
    POST DATA Format:
    {
        'quantity': ,
        'b_ss' :     ,   # options ['Buy' or 'Short Sell']
        'company' : ,
        'pending' : ,
    }

    '''

    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        cclose = isWrongTime()
        if(cclose):
            return JsonResponse({ 'cclose': cclose, 'message': 'Wrong time', })
        quantity_invalid=False
        msg=""
        cash_bal=0
        margin=0
        data=request.POST
        if(len(data)!=0):

            qnty_test = data['quantity']

            if(not is_number(qnty_test)):
                quantity_invalid=True
            else:
                qnty_test=int(float(data['quantity']))
                if(qnty_test <= 0):
                    quantity_invalid=True


            if not quantity_invalid :

                company=data['company'] 
                if(company != "none" and company !="" ):
                    quantity=qnty_test
                    if (is_number(data['pending'])):
                        pending_price=float(data['pending'])
                    else :
                        pending_price=""
                    if (data['b_ss'] == 'Buy' or data['b_ss'] == 'Short Sell'):
                        b_ss=data['b_ss']
                    else:
                        b_ss = ""   
                    try :
                        stocks=Stock_data.objects.get(symbol=company)                   
                        portfolio = Portfolio.objects.get(user_id=request.session['dalalbull_uid'])
                        old_cash_bal = float(portfolio.cash_bal)
                        current_price=float(stocks.current_price)
                        no_trans = portfolio.no_trans
                        if(no_trans+1<=100):
                                brokerage=((0.5/100)*current_price)*float(quantity) 
                        elif(no_trans+1<=1000):                     
                                brokerage=((1/100)*current_price)*float(quantity)
                        else :                      
                                brokerage=((1.5/100)*current_price)*float(quantity)


                        if(quantity_invalid or b_ss=="" or company=='NIFTY 50'):
                            msg= "Invalid Data"
                        else :                          
                            if((pending_price!="") and current_price!=pending_price):
                                    percentager = 0.05 * current_price
                                    t=current_price-percentager
                                    l=current_price+percentager
                                    q=False
                                    if(pending_price > current_price or pending_price <= t ):
                                        q=True
                                    r=False
                                    if(pending_price < current_price or pending_price >= l ):
                                        r=True

                                    if(not is_number(pending_price) or pending_price<0):
                                        msg= "Invalid Data"                                                            
                                    else:
                                        if(b_ss=='Buy' and q):
                                        	msg= "Pending Price for Buying should be less than and maximum of 5% below Current Price"
                                        elif b_ss == "Short Sell" and r:
                                            msg = "Pending Price for Short Selling should be greater than and maximum of 5% above Current Price"
                                        else:
                                        	p=Pending(user_id=request.session['dalalbull_uid'],
                                                symbol=company,
                                                buy_ss=b_ss,
                                                quantity=quantity,
                                                value=pending_price,
                                                time=datetime.datetime.now().time()
                                                )
                                        	p.save()
                                        	msg= "You have made a Pending Order to "+b_ss+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
                            else:
                                if(((old_cash_bal-float(portfolio.margin)-brokerage)<=0) or ((old_cash_bal-float(portfolio.margin)-brokerage)< current_price*float(quantity) and b_ss=="Buy") or (((old_cash_bal-float(portfolio.margin)-brokerage) < (current_price*float(quantity)/2)) and b_ss=="Short Sell")):
                                    msg= "You do not have enough Cash Balance for this transaction"
                                    return JsonResponse({ 'message': msg, })
                                else:
                                    if(((old_cash_bal-float(portfolio.margin)-brokerage)<=0) or ((old_cash_bal-float(portfolio.margin)-brokerage)< current_price*float(quantity) and b_ss=="Buy") or (((old_cash_bal-float(portfolio.margin)-brokerage) < (current_price*float(quantity)/2)) and b_ss=="Short Sell")):
                                        msg= "You do not have enough Cash Balance for this transaction"
                                        return JsonResponse({ 'message': msg, })
                                    try:
                                        t=Transaction.objects.get(
                                            user_id=request.session['dalalbull_uid'],
                                            symbol=company,
                                            buy_ss=b_ss,
                                            )
                                        old_quantity=float(t.quantity)
                                        old_val=float(t.value)
                                        new_val=old_val+(float(quantity)*current_price)
                                        new_quantity=old_quantity+float(quantity)
                                        t.quantity=new_quantity
                                        t.value=new_val
                                        t.buy_ss=b_ss
                                        if(b_ss=="Buy"):
                                            cash_bal=old_cash_bal-(float(quantity)*current_price)
                                            margin = float(portfolio.margin)
                                        else:
                                            cash_bal = old_cash_bal
                                            margin = float(portfolio.margin)+(float(quantity)*current_price)/2
                                        cash_bal -= brokerage
                                        no_trans+=1
                                        portfolio.cash_bal=cash_bal
                                        portfolio.margin=margin
                                        portfolio.no_trans=no_trans
                                        portfolio.save()
                                        kp=0
                                        while (kp<25):
                                        	portfolio2 = Portfolio.objects.get(
                                                user_id=request.session['dalalbull_uid']
                                                )
                                        	if (portfolio2.cash_bal!=portfolio.cash_bal):
                                        		portfolio.save()
                                        	else:
                                        		break
                                        	kp=kp+1
                                        t.save()
                                    except Transaction.DoesNotExist:
                                        new_val=float(quantity)*current_price
                                        t=Transaction(user_id=request.session['dalalbull_uid'],
                                            symbol=company,
                                            buy_ss=b_ss,
                                            quantity=quantity,
                                            value=new_val)

                                        if(b_ss=="Buy"):
                                            cash_bal=old_cash_bal-(float(quantity)*current_price)
                                            margin = float(portfolio.margin)
                                        else:
                                            cash_bal = old_cash_bal
                                            margin = float(portfolio.margin)+(float(quantity)*current_price)/2
                                        cash_bal -= brokerage
                                        no_trans+=1
                                        portfolio.cash_bal=cash_bal
                                        portfolio.margin=margin
                                        portfolio.no_trans=no_trans
                                        portfolio.save()
                                        kp=0
                                        while (kp<25):
                                            portfolio2 = Portfolio.objects.get(
                                                user_id=request.session['dalalbull_uid']
                                                )
                                            if (portfolio2.cash_bal!=portfolio.cash_bal):
                                                portfolio.save()
                                            else:
                                                break
                                            kp=kp+1
                                        t.save()
                                    history=History(user_id=request.session['dalalbull_uid'],
                                        time=datetime.datetime.now().time(),
                                        symbol=company,
                                        buy_ss=b_ss,
                                        quantity=quantity,
                                        price=stocks.current_price
                                        )
                                    history.save()
                                    if(b_ss=="Buy"):
                                        msg+= "You have successfully bought "+str(quantity)+" shares of '"+company+"' at " +'RS. ' +str(stocks.current_price) +"  per share. Your Cash Balance is RS. "+str(portfolio.cash_bal)
                                    elif(b_ss=="Short Sell"):
                                        msg="You have successfully short sold "+str(quantity)+" shares of '"+company+"' at '" +'RS. '+str(stocks.current_price)+" per share"
                                    msg = msg + "You have paid "+ 'RS. '+str(brokerage)+" as brokerage for the transaction"

                    except Stock_data.DoesNotExist:
                        msg= "Requested Company '"+str(company)+"' is not listed"
                else:   
                    msg = "Invalid Data"
            else:
                msg= "Invalid Data "                    
        else:       
            msg= "Please enter valid data in the necessary fields"
        print msg
        return JsonResponse({ 'message': msg, })

    return JsonResponse({ 'message': 'Not logged in.', })


#=======Sell/Short-Cover=====#

    # company       :   temp['symbol']=i.symbol
    # type of trade :   temp['buy_ss']=i.buy_ss
    # share in hand :   temp['old_quantity']=float(i.quantity)
    # current price :   str(s.current_price)
    # gain          :   temp['prof_per']
    # type of trans :   temp['disp']  


@ensure_csrf_cookie
def sell(request):

    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        data_to_send = sell_data(request.session['dalalbull_uid'])
        return JsonResponse(data_to_send)



def sell_data(user_id):                      

    cclose = isWrongTime()
    no_stock=False
    transactions=[]
    data={}
    data_array={}
    d=[]
    k=0
    s =set()
    if not isWrongTime():
        try:
            t = Transaction.objects.filter(user_id=user_id)
            for i in t:
                temp={}

                temp['old_quantity']=float(i.quantity)
                temp['old_value']=float(i.value)

                temp['buy_ss']=i.buy_ss
                temp['symbol']=i.symbol

                try:
                    s = Stock_data.objects.get(symbol=temp['symbol'])
                except:
                    continue

                if(temp['buy_ss']=='Buy'):
                    temp['profit']=float(s.current_price)-(temp['old_value']/temp['old_quantity'])
                else:
                    temp['profit']=(temp['old_value']/temp['old_quantity'])-float(s.current_price)
                

                temp['prof_per']=(temp['profit']/(temp['old_value']/temp['old_quantity']))*100
                
                               
                if(temp['buy_ss']=='Buy'):
                    temp['disp']='Sell'
                else:
                    temp['disp']='Short Cover'

                transactions.append(
                    {
                        'company' : temp['symbol'],
                        'type_of_trade' : temp['buy_ss'],
                        'share_in_hand' : temp['old_quantity'],
                        'current_price' : str(s.current_price),
                        'gain' : temp['prof_per'],
                        'type_of_trans' : temp['disp']
                    })


            if(len(transactions)==0):
                no_stock=True

        except Transaction.DoesNotExist:
            no_stock=True 

    data = {
    'cclose' : cclose,
    'no_stock': no_stock,
    'trans':transactions,
    }


    return data






#======Submit-Sell======#
@ensure_csrf_cookie
def submit_sell(request):

    ''' POST DATA format:

        {
                'company'   : __ ,   #symbol
                'quantity'  : __ ,   #from formdata in sell()
                'tradeType' : __ ,   #this was sent to you in sell() [ 'Sell' or 'Short Cover']
                'pending'   : __ ,   #from formdata in sell()
        }

    '''
    print request.POST
    cclose = isWrongTime()         
    msg=""
    transactions=[]
    data = request.POST
    data_array={}
    d=[]
    dat={}
    quantity_invalid = False
    pp_invalid = False
    retDat=[]
    k=0
    if(cclose):
        return JsonResponse({'cclose': True})
    
    if(len(data)!=0):

        qnty_test = data['quantity']

        # checking if quantity is valid
        if(not is_number(qnty_test)):
            quantity_invalid=True
        else:
            qnty_test=int(float(data['quantity']))
            if(qnty_test < 0):
                quantity_invalid=True


        # Below steps only if quantity is valid
        if(not quantity_invalid):

            company = data['company']
            quantity = float(data['quantity'])
            pending_price = data['pending']
            s_sc = data['tradeType']


            #Check if pending_price is valid

            if(not is_number(pending_price)):
                pp_invalid=True
            else:
                pending_price=int(float(data['pending']))
                if(pending_price < 0):
                    pp_invalid=True

            print 'Is pend:'+str(pp_invalid)
            if(s_sc=="Sell"):
                b_ss="Buy"
            else:
                b_ss="Short Sell"

            try:

                s = Stock_data.objects.get(symbol=company)
                current_price=float(s.current_price)
                

                try:
                    t = Transaction.objects.get(user_id=request.session['dalalbull_uid'],
                        symbol=company,buy_ss=b_ss)

                    old_quantity=float(t.quantity)  

                    if(quantity_invalid):
                        msg = "Invalid Data"

                    elif(pending_price!="" and current_price!=pending_price):
                        
                        if(pp_invalid):
                            msg = "Invalid Data"

                        elif (s_sc=="Short Cover" and pending_price>current_price):
                            msg = "pending Price for Short Covering should be less than Current Price"
                        
                        elif (s_sc=="Sell" and pending_price<current_price):
                            msg = "Pending Price for Selling should be greater than Current Price"
                        
                        else:
                            p=Pending(user_id=request.session['dalalbull_uid'],
                                symbol=company,quantity=quantity,
                                value=pending_price,buy_ss=s_sc)
                            p.save()
                            msg = "You have made a pending order to "+str(s_sc)+" "+str(quantity)+" shares of "+str(company)+" at a desired price of"+'RS. '+str(pending_price)
                    

                    elif(quantity>old_quantity):
                        msg = "You do not own enough number of shares of the requested Company for this transaction"
                    
                    else:
                        # SUCCESS FULL SELLING CASE 
                        old_val=float(t.value)
                        new_quantity=old_quantity-quantity
                        old_total=(old_val/old_quantity)*quantity
                        new_val=old_val-old_total

                        if new_quantity==0:
                            del_t = Transaction.objects.get(
                                user_id=request.session['dalalbull_uid'],
                                symbol=company,buy_ss=b_ss)
                            del_t.delete()
                        
                        else:
                            upd_t = Transaction.objects.get(
                                user_id=request.session['dalalbull_uid'],
                                symbol=company,
                                buy_ss=b_ss
                                )
                            upd_t.quantity=new_quantity
                            upd_t.value=new_val
                            upd_t.save()
                        
                        pf= Portfolio.objects.get(user_id=request.session['dalalbull_uid'])
                        margin=float(pf.margin)

                        if(s_sc=="Short Cover"):
                            sc_profit=old_total-(quantity*current_price)
                            cash_bal=float(pf.cash_bal)+sc_profit
                            margin=(margin-(old_val/2))+(new_val/2)

                        elif(s_sc=="Sell"):
                            cash_bal=float(pf.cash_bal)+(quantity*current_price)
                        
                        no_trans = pf.no_trans+1

                        if(no_trans<=100):
                            brokerage=((0.5/100)*current_price)*quantity;

                        elif(no_trans<=1000):
                            brokerage=((1/100)*current_price)*quantity;
                        
                        else:
                            brokerage=((1.5/100)*current_price)*quantity;


                        cash_bal=cash_bal-brokerage
                        pf.cash_bal=cash_bal
                        pf.margin=margin
                        pf.no_trans=no_trans
                        pf.save()
                        kp=0
                        while (kp<25):
                            portfolio2 = Portfolio.objects.get(user_id=request.session['dalalbull_uid'])
                            if (portfolio2.cash_bal!=pf.cash_bal):
                                pf.save()
                            else:
                               break
                            kp=kp+1
                        now = datetime.datetime.now().time     

                        h=History(
                            user_id=request.session['dalalbull_uid'],
                            time=now,symbol=company,
                            buy_ss=s_sc,quantity=quantity,
                            price=s.current_price
                            )
                        h.save()

                        try:
                            pend=Pending.objects.get(
                                user_id=request.session['dalalbull_uid'],
                                symbol=company,buy_ss=s_sc
                                )

                            if(new_quantity == 0):
                                pend.delete()

                            elif(pend.quantity>new_quantity):
                                pend.quantity=new_quantity
                                pend.save()

                        except Pending.DoesNotExist:
                            print("error in Pending")
                        if(s_sc=="Sell"):
                            msg = "You have successfully sold "+str(quantity)+" shares of "+str(company)+"at"+'RS. '+str(s.current_price)+" per share."
                        else:
                            msg = "You have successfully short covered "+str(quantity)+" shares of '"+str(company)+" at "+'RS. '+str(s.current_price)+" per share"
                
                except Transaction.DoesNotExist:
                    msg="error" 

            except Stock_data.DoesNotExist:
                msg = "Requested Company '"+str(company)+"' is not listed";
        else:
            msg = "Please enter valid data"                
                        
    try:
        trow=""
        t = Transaction.objects.filter(user_id=request.session['dalalbull_uid'])
                    
        for i in t:
            temp={}
            temp['old_quantity']=float(i.quantity)
            temp['old_value']=float(i.value)
            temp['buy_ss']=i.buy_ss
            temp['symbol']=i.symbol

            if(i.buy_ss=='Buy'):
                temp['id']='Buy'
            else:
                temp['id']='Short'
                        
            try:
                s=Stock_data.objects.get(symbol=temp['symbol'])
            except Stock_data.DoesNotExist:
                continue
            

            if(temp['buy_ss']=='Buy'):
                temp['profit']=float(s.current_price)-(temp['old_value']/temp['old_quantity'])
            else:
                temp['profit']=(temp['old_value']/temp['old_quantity'])-float(s.current_price)
            
            temp['prof_per']=(temp['profit']/(temp['old_value']/temp['old_quantity']))*100
            
            if(temp['prof_per']>0):
                temp['clrclss']='uptrend'
            elif(temp['prof_per']<0):
                temp['clrclss']='dwntrend'            
            else:
                temp['clrclss']=''

            
            if(temp['buy_ss']=='Buy'):
                temp['disp']='Sell'
            else:
                temp['disp']='Short Cover'
            
            
            dat['symbol']=temp['symbol']
            dat['buy_ss']=temp['buy_ss']
            dat['old_quantiy']=temp['old_quantity']
            dat['old_value']=temp['old_value']

            transactions.append(
            {
                'company' : temp['symbol'],
                'type_of_trade' : temp['buy_ss'],
                'share_in_hand' : temp['old_quantity'],
                'current_price' : str(s.current_price),
                'gain' : temp['prof_per'],
                'type_of_trans' : temp['disp']
            })
            data_array[k]=dat
            k+=1
            
        if len(t) == 0:
            no_stock = True
        else:
            no_stock = False

        data_to_send = {
        'cclose' : cclose,
        'no_stock' : no_stock,
        'trans' : transactions,
        'message' : msg,
        }

    except Transaction.DoesNotExist:
        print d
        
    
    return JsonResponse(data_to_send)



def ticker_data():
    stocks = Stock_data.objects.all()
    tickerData = []
    for stock in stocks:
        tickerData.append({
            'name': stock.symbol,
            'current_price' : stock.current_price,
            'change_per' : stock.change_per,
            })
    return {
            'tickerData': tickerData,
        }

def ticker(request):
    return JsonResponse(ticker_data())





#=======Cancel Pending Orders=====#
'''
Data about pending transactions
'''

@ensure_csrf_cookie
def pending(request):   

    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        
        cclose = isWrongTime()
        no_stock=False

        try:
            t = Pending.objects.filter(user_id=request.session['dalalbull_uid'])
            row=[]
            for i in t:
                temp={}
                temp['quantity']=float(i.quantity)
                temp['value']=float(i.value)
                temp['type']=i.buy_ss
                temp['symbol']=i.symbol
                try:
                    s=Stock_data.objects.get(symbol=temp['symbol'])
                    temp['current_price']=(str(s.current_price))
                except Stock_data.DoesNotExist:
                    temp['current_price']='Not Listed'
                temp['id']=i.id
                row.append(temp)   
            if(len(t)>0):
                symbols = True         # DOUBT, DOUBT, DOUBT, DOUBT
            else:
                no_stock=True
        except Pending.DoesNotExist:
            no_stock=True 


        data = {
        'cclose' : cclose,
        #'time' : datetime.datetime.now(),
        'no_pending': False,    #was True
        'pending':row,
        }

        return JsonResponse(data)
    return redirect('index')

#=======Cancels========#
@csrf_exempt
def cancels(request):
    '''
    POST DATA Format:
        {
            'iddel' : .. ,  #UI obtains this from pending()
            'company' : ..,
            # 'quantity' : ..,
            # 'username' : ..,
            # 'price' : ..,
            # 'type' : ..,
        }


        Check if we need 'quantity' and 'price' 
        to filter data.
    '''

    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        cclose = isWrongTime()
        if(cclose):
            return JsonResponse({'cclose': True})
        iddel=request.POST['iddel']
        company=request.POST['company']
        # quantity=request.POST['quantity']
        username=request.session['dalalbull_uid']
        # price=request.POST['price']
        # trdtype=request.POST['type']
        msg=""
        if(iddel!="" and company !=""):
            try:
                p=Pending.objects.get(user_id=username,
                    id=iddel,
                    symbol=company,
                    )
                    #buy_ss=trdtype,
                    # quantity=quantity,
                    # value=price)
                p.delete()
                msg = "Specified pending order has been cancelled"
                
            except Pending.DoesNotExist:
                msg="Error Cancelling"
        else:
            msg="Invalid Data"
        
        data_to_send = {
        'message' : msg,
        }
        
        return JsonResponse(data_to_send)






#=======History========#
'''
    Details of all transactions.
'''
def history(request):
    
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        username = request.session['dalalbull_uid']
        hist = History.objects.filter(user_id=username)

        hf = []
        for i in hist:
            h = i.as_dict()
            h['time'] = h['time'].strftime("%a  %d %b %I:%M:%S %p")
            h['total']= (float(i.quantity) * float(i.price))
            hf.append(h)

        data = {
        'history' : hf,
        }

        return JsonResponse(data)
    return redirect('index')


   


#======To Get Current Price======#

'''
This is called when user selects the company
in buy/short sell,
UI performs the required calculations
'''


def currPrice(request):
    if 'is_dalalbull_user' in request.session and request.session['is_dalalbull_user']==True:
        user_id=request.session['dalalbull_uid']
        

        comp = request.POST['company']
        curr_price = Stock_data.objects.get(symbol=comp).current_price
        portfo = Portfolio.objects.get(user_id=user_id)
        cash_bal = portfo.cash_bal
        margin = portfo.margin
        no_trans = portfo.no_trans

        data_to_send = {
        'curr_price' : curr_price,
        'cash_bal': cash_bal,
        'margin' : margin,
        'no_trans' : no_trans
        }                    
        
        return JsonResponse(data_to_send)
    return JsonResponse({ 'result': 'not logged in!'})




def testChannels(request):
    return render(request,'test_channels.html',{})    

    
    
#==========Utility Functions========#






def getStockholdings(user_id):
    stockholdings=[]
    transactions=Transaction.objects.filter(user_id=user_id)
    for i in transactions:
        stock={}
        stock['company']=i.symbol
        stock['number']=i.quantity
        stock['type']=i.buy_ss
        stock['purchase']=(float(i.value))/(float(i.quantity))
        stock['current']=float(Stock_data.objects.get(symbol=i.symbol).current_price)
        stockholdings.append(stock)
    return stockholdings

def getTopGainers():
    gainers=[]
    stocks=Stock_data.objects.all().order_by('-change_per')[:6]                  
    k=0
    for stock in stocks:
        if(k<5):
            if(stock.symbol!='NIFTY 50'):
                gainers.append({
                    'name' : stock.symbol,
                    'change_per' : stock.change_per,
                    })
                k+=1
        else:
            break
    return gainers
    
def getTopLosers():
    losers=[]
    stocks=Stock_data.objects.all().order_by('change_per')[:6]                   ###########
    k=0
    for stock in stocks:
        if(k<5):
            if(stock.symbol!='NIFTY 50'):
                losers.append({
                    'name' : stock.symbol,
                    'change_per' : stock.change_per,
                    })
                k+=1
        else:
            break
    return losers

def getMostActiveVolume():
    active=[]
    stocks=Stock_data.objects.all().order_by('-trade_Qty')[:6]                   ###########
    k=0
    for stock in stocks:
        if(k<5):
            if(stock.symbol!='NIFTY 50'):
                active.append({
                    'name' : stock.symbol,
                    'trade_qty' : stock.trade_Qty,
                    })
                k+=1
        else:
            break
    return active

def getMostActiveValue():
    active=[]
    stocks = Stock_data.objects.all().order_by('-trade_Value')[:6]                 ###########
    k=0
    for stock in stocks:
        if(k<5):
            if(stock.symbol!='NIFTY 50'):
                active.append({
                    'name' : stock.symbol,
                    'trade_val' : stock.trade_Value,
                    })
                k+=1
        else:
            break
    return active

def getRank(user_id):
    p=Portfolio.objects.all().order_by('-net_worth')
    i=1
    for t in p:
        if(t.user_id==user_id):
            return i
        i+=1
    return 0


def isWrongTime():
    return False
    cclose=True
    now = datetime.datetime.now()

    if (now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):
        start_time=datetime.time(hour=9,minute=15,second=00)
        end_time=datetime.time(hour=15,minute=30,second=00)
        now = datetime.datetime.now().time()
        if(start_time<now<end_time):
            cclose=False

    return cclose


#=======Number=======#
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False      




########### FUNCTIONS SHARED WITH CHANNEL CONSUMER ######################


def niftyData():

    nifty= Stock_data.objects.get(symbol='NIFTY 50')

    data_to_send = {
        'current_price': float(nifty.current_price),
        'change' : float(nifty.change) , 
    }
    

    return data_to_send




def leaderboardData():
    p=Portfolio.objects.all().order_by('-net_worth')[:5]
    i=1
    l=[]
    for t in p:
        u=User.objects.get(user_id=t.user_id)
        user = {
        'name': u.name,
        'net_worth': float(t.net_worth),
        'image_url' : u.image_url,
        }      

        l.append(user);
        i+=1

    data_to_send = {
    'leaderboard_data' : l,
    }
    return data_to_send





def portfolio(user_id):
    data=[]
    dat=[]

    user=Portfolio.objects.get(user_id=user_id)
    total_no = User.objects.count() 
    total_transactions = Transaction.objects.filter(user_id=user_id).count()                            
    data_to_send = {
    'cash_bal' : user.cash_bal,
    'net_worth' : user.net_worth,
    'margin' : user.margin,
    'total_users' : total_no,
    'rank' : getRank(user_id),
    'total_transactions' : user.no_trans,
    }

    return data_to_send




def graph(company):
    graph_values=Old_Stock_data.objects.filter(symbol=company).order_by('time')
    graph_data=[]
    for i in graph_values:
        temp=[]
        timez=timezone(settings.TIME_ZONE)
        time=i.time.astimezone(timez)
        temp.append( (time.hour-9)*60 + time.minute -15 )
        temp.append( i.current_price )
        graph_data.append(temp)

    data_to_send = {
        'graph_data' : graph_data,
    }
    return data_to_send








