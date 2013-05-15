from django.http import HttpResponse
from django.shortcuts import render_to_response
from db.utilities import dropbox_user_required
from .models import FSNode
from .utilities import get_or_update_fs, get_fs_dict
import json


@dropbox_user_required
def render_filesystem_json(request, dropbox_client):
    user = request.user
    fs_user = get_or_update_fs(user, dropbox_client)
    if 'depth' in request.REQUEST and 'id' in request.REQUEST:
        node = FSNode.objects.get(id=int(request.REQUEST['id'])) #TODO Put int() in try/except block
        fs_dict = get_fs_dict(node, int(request.REQUEST['depth']))
    else:
        fs_dict = get_fs_dict(fs_user.root)
    return HttpResponse(json.dumps(fs_dict), content_type="application/json")

@dropbox_user_required
def render_zoomable_treemap(request, dropbox_client):
    return render_to_response('zoomable_treemap.html')

@dropbox_user_required
def render_treemap(request, dropbox_client):
    return render_to_response('treemap.html')

@dropbox_user_required
def render_my_treemap(request, dropbox_client):
    return render_to_response('my_treemap.html')

@dropbox_user_required
def render_sunburst(request, dropbox_client):
    return render_to_response('sunburst.html')
