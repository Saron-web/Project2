def filter_by_diet(data, diet):
    return [i for i in data if i.get("diet") == diet]

def search_by_keyword(data, keyword):
    return [i for i in data if keyword.lower() in i.get("name", "").lower()]

def paginate(data, page, size):
    start = (page - 1) * size
    end = start + size
    return data[start:end]
