from server.constants import PERMISSION
from server.constants import permission_dict

def check_perm_aux(user, perm, user_id, unit_id):
    if perm not in permission_dict:
        return False

    if perm == PERMISSION.PUBLIC:
        return True

    if perm == PERMISSION.UNIT:
        if user.get_unit() == unit_id:
            return True
        return False

    if perm == PERMISSION.PRIVATE:
        if user.get_id() == user_id:
            return True
    return True

def check_perm(user, obj, visibility=False, editing=False):
    if visibility and not check_perm_aux(user, obj.get_visibility(),
                                         obj.get_owner(), obj.get_owner_unit()):
        return False
    if editing and not check_perm_aux(user, obj.get_edit_perm(),
                                      obj.get_owner(), obj.get_owner_unit()):
        return False
    return True