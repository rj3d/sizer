from dropbox import client, rest, session
from dropbox.rest import ErrorResponse

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render

from models import DBUser

# Based off of http://djangosnippets.org/snippets/2715/

DROPBOX_REQUEST_SESSION_KEY = 'dropbox_request_token3'  # random temp storage name


def _saveAccessToken(user, oauth_token):
    try:
        d = user.db
    except:
        d = DBUser()
        d.user = user
    d.access_token = oauth_token.key
    d.access_token_secret = oauth_token.secret
    d.save()


def _dropboxConnect(request, db_sess):
    request_token = db_sess.obtain_request_token()
    request.session[DROPBOX_REQUEST_SESSION_KEY] = request_token
    url = db_sess.build_authorize_url(request_token, request.build_absolute_uri())
    return HttpResponseRedirect(url)


def dropbox_user_required(func):
    @login_required
    def _dropbox_wrap(request, *args, **kwargs):
        _keys = settings.DROPBOX_SETTINGS
        db_sess = session.DropboxSession(_keys['app_key'], _keys['app_secret'], _keys['type'])
        try:
            if request.session.has_key(DROPBOX_REQUEST_SESSION_KEY):
                oauth_access_token = db_sess.obtain_access_token(request.session.pop(DROPBOX_REQUEST_SESSION_KEY))
                _saveAccessToken(request.user, oauth_access_token)
            else:
                access_token = request.user.db.access_token
                access_token_secret = request.user.db.access_token_secret
                db_sess.set_token(access_token, access_token_secret)
            db_c = client.DropboxClient(db_sess)
        except ObjectDoesNotExist:
            return _dropboxConnect(request, db_sess)
        try:
            return func(request, *args, dropbox_client=db_c, **kwargs)
        except ErrorResponse, e:
            if e.status == 401:
                _dropboxConnect(request, db_sess)# re authentication needed
            else:
                raise e # let django log the exception that the user did not handle

    return _dropbox_wrap

@dropbox_user_required
def display_dropbox_user_info(request, dropbox_client):
    account_info = dropbox_client.account_info()
    context = {'account_info': account_info}
    return render(request, 'test.html', context)