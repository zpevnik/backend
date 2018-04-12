from server.constants import PERMISSION


def check_perm(user, obj, visibility=False, editing=False):
    if editing:
        # user can edit given objects only if it belongs to him
        # or if he is designated editor
        return user.is_editor() or obj.get_owner() == user.get_id()

    if visibility:
        if obj.get_visibility() == PERMISSION.PUBLIC:
            return True
        return obj.get_owner() == user.get_id()

    return True
