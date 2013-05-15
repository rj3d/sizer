from .models import FSUser, FSNode

def _recursively_populate_folder(dropbox_client, path, parent, user):
    metadata = dropbox_client.metadata(path)
    fsn = FSNode()
    fsn.user = user
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
                c.user = user
                c.size = child_metadata['bytes']
                c.name = child_metadata['path'].split('/')[-1]
                c.full_path = child_metadata['path']
                c.parent = fsn
                c.is_dir = False
                temp_size += c.size
                c.save()
            else:
                child_dir = _recursively_populate_folder(dropbox_client, child_metadata['path'], fsn, user)
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
    root = _recursively_populate_folder(dropbox_client, '/', None, user)
    fsu.root = root
    fsu.complete = True
    fsu.save()
    return fsu

def _update_fs(user, dropbox_client, delta_dict):
    return user.fs #TODO Actually replace with an update function


def get_or_update_fs(user, dropbox_client):
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

# Given a starting node, returns a dict containing the metadata for the node and all children
# for  the specified number of layers
def get_fs_dict(node, depth=None):
    cur_dict = {}
    cur_dict["name"] = node.name
    cur_dict["id"] = node.id
    cur_dict["value"] = node.size
    cur_dict["is_dir"] = node.is_dir
    if depth:
        depth -= 1
    if node.is_dir and not depth == 0:
        cur_dict["children"] = []
        children = FSNode.objects.filter(parent=node)
        for child in children:
            cur_dict["children"].append(get_fs_dict(child, depth))
    return cur_dict
