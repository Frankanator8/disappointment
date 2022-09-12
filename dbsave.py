import json
import datetime


def db_as_dict(db):
    dict = {}
    for key, item in db.items():
        dict[key] = db_to_python(item)
    return dict


def db_to_python(item):
    if item.__class__.__name__ == "ObservedDict":
        ret = {}
        for key, subitem in item.items():
            ret[key] = db_to_python(subitem)

    elif item.__class__.__name__ == "ObservedList":
        ret = []
        for subitem in item:
            ret.append(db_to_python(subitem))

    else:
        ret = item

    return ret


def save_dict(dict):
    with open(
            f"db_backups/backup_{datetime.datetime.now().strftime('%m.%d.%Y %H.%M.%S')}",
            "w") as f:
        json.dump(dict, f)


def load_save(save, db):
    with open(save) as f:
        dict = json.load(f)

    for key, value in dict.items():
        db[key] = value
