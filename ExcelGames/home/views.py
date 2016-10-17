from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client, crypt
from datetime import datetime
from .models import User

CLIENT_ID = "648816388900-j2r6l2jib6srjg9njt31ku0eka34vg3s.apps.googleusercontent.com"
# Create your views here.


@csrf_exempt
def index(request):
    return render(request, 'home/index.html')


@csrf_exempt
def token_signin(request):
    # (Receive token by HTTPS POST)
    try:
        idinfo = client.verify_id_token(request.POST.get('idtoken'), CLIENT_ID)
        if idinfo['aud'] not in [CLIENT_ID]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError:
        return HttpResponse('failed')
    u, obj = User.objects.get_or_create(user_id=idinfo['sub'], name=idinfo['name'], email=idinfo['email'], image_url=idinfo['picture'])
    request.session['logged_in'] = True
    request.session['uid'] = u.user_id
    request.session['prof_img'] = u.image_url
    request.session['name'] = u.name
    return HttpResponse('success')


@csrf_exempt
def signout(request):
    request.session.flush()
    return HttpResponse('loggedout')



