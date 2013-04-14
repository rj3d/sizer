from models import FSUser, FSNode
from dropbox import client
from db.views import dropbox_user_required
import json
from django.http import HttpResponse

def _recursively_populate_folder(dropbox_client, path, parent):
    metadata = dropbox_client.metadata(path)
    fsn = FSNode()
    fsn.parent = parent
    fsn.name = metadata['path'].split('/')[-1]
    fsn.full_path = metadata['path']
    fsn.is_dir = True
    fsn.size = 0
    fsn.save()
    print "Recursively populating folder " + fsn.name
    temp_size = 0
    if 'contents' in metadata:
        for child_metadata in metadata['contents']:
            #Save all of the child folders now as the metadata already has all of their metadata
            if not child_metadata['is_dir']:
                c = FSNode()
                c.size = child_metadata['bytes']
                c.name = child_metadata['path'].split('/')[-1]
                c.full_path = child_metadata['path']
                c.parent = fsn
                c.is_dir = False
                temp_size += c.size
                c.save()
            else:
                child_dir = _recursively_populate_folder(dropbox_client, child_metadata['path'], fsn)
                temp_size += child_dir.size
    fsn.size = temp_size
    fsn.save()
    return fsn

def _populate_filesystem(user, dropbox_client):
    #If an old filesystem exists, delete the root. Then create a new one and populate
    try:
        fsu = user.fs
        old_root = fsu.root
        old_root.delete()
    except:
        fsu = FSUser()
        fsu.user = user
    fsu.cursor = dropbox_client.delta()['cursor']
    #Recursively populate the filesystem database
    root = _recursively_populate_folder(dropbox_client, '/', None)
    fsu.root = root
    fsu.save()
    return fsu

def _update_fs(user, dropbox_client, delta_dict):
    return user.fs #TODO Actually replace with an update function


def _get_or_update_fs(user, dropbox_client):
    print "Get or updating"
    try:
        fsu = user.fs
        c = fsu.cursor
        delta_dict = dropbox_client.delta(c)
        if len(delta_dict['entries']) > 0:
            fsu = _update_fs(user, dropbox_client, delta_dict)
    except:
        fsu = _populate_filesystem(user, dropbox_client)
    return fsu

def _recursively_generate_fs_dict(node):
    cur_dict = {}
    cur_dict["name"] = node.name
    if not node.is_dir:
        cur_dict["value"] = node.size
    else:
        cur_dict["children"] = []
        children = FSNode.objects.filter(parent=node)
        for child in children:
            cur_dict["children"].append(_recursively_generate_fs_dict(child))
    return cur_dict


def _get_fs_dict(root):
    fs_dict = _recursively_generate_fs_dict(root)
    return fs_dict

@dropbox_user_required
def display_filesystem_json(request, dropbox_client):
    user = request.user
    fs_user = _get_or_update_fs(user,dropbox_client)
    fs_dict = _get_fs_dict(fs_user.root)
    return HttpResponse(json.dumps(fs_dict), content_type="application/json")

