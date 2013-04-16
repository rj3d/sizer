from django.shortcuts import render
from .utilities import dropbox_user_required

@dropbox_user_required
def display_dropbox_user_info(request, dropbox_client):
    account_info = dropbox_client.account_info()
    context = {'account_info': account_info}
    return render(request, 'test.html', context)