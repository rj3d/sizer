from models import FSUser, Filesystem
from dropbox import client
from db.views import dropbox_user_required
import json
from django.http import HttpResponse

def _recursively_populate(dropbox_client, path, parent_id):
    metadata = dropbox_client.metadata(path)
    f = Filesystem()
    f.parent = parent_id
    if not metadata['is_dir']:
        f.is_dir = False
        f.size = metadata['bytes']
    else:
        f.is_dir = True
        temp_size = 0
        if 'contents' in metadata:
            for child_metadata in metadata['contents']:
                cur_child = _recursively_populate(dropbox_client, child_metadata['path'], f.id)
                temp_size += cur_child.size
        f.size = temp_size
    f.save()
    return f

def _populate_filesystem(user, dropbox_client):
    #If an old filesystem exists, delete the root. Then create a new one and populate
    try:
        f = user.fs
        old_root = Filesystem.objects.get(id=f.root_id)
        old_root.delete()
    except:
        f = FSUser()
        f.user = user
    f.cursor = dropbox_client.delta()['cursor']
    #Recursively populate the filesystem database
    root = _recursively_populate(dropbox_client, '/', None)
    f.root_id = root.id
    f.save()
    return f

def _update_fs(user, dropbox_client, delta_dict):
    updated = _populate_filesystem(user, dropbox_client) #TODO Actually replace with an update function
    return updated

def _get_or_update_fs(user, dropbox_client):
    try:
        f = user.fs
        c = f.cursor
        delta_dict = dropbox_client.delta(c)
        if len(delta_dict['entries']) > 0:
            f = _update_fs(user, dropbox_client, delta_dict)
    except:
        f = _populate_filesystem(user, dropbox_client)
    return f

def _get_fs_dict(root_id):
    fs = {}
    root = Filesystem.objects.get(id=root_id)
    children = Filesystem.objects.filter(parent=root.id)


@dropbox_user_required
def display_filesystem_json(request, dropbox_client):
    user = request.user
    fs_user = _get_or_update_fs(user,dropbox_client)
    fs_dict = _get_fs_dict(fs_user.root_id)
    return HttpResponse(json.dumps(fs_dict), content_type="application/json")

