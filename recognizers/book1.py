pagetypes = dict()

def add_type(tid, typestr):
    try:
        if typestr in pagetypes.values():
            raise Exception("Such funcname already exists")
        else:
            pagetypes.update({tid: typestr})
    except:
        raise

add_type(1, "type1")
def type1(page):
    return False

add_type(2, "type2")
def type2(page):
    return False

add_type(3, "type3")
def type3(page):
    return True
