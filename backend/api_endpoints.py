from flask import Blueprint, request, jsonify
from .redis_cache import get_clean_data

api = Blueprint("api", __name__)

@api.route("/recipes", methods=["GET"])
def recipes():
    data = get_clean_data()

    diet = request.args.get("diet")
    keyword = request.args.get("search")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    if diet:
        data = [d for d in data if d["Diet_type"] == diet.lower()]

    if keyword:
        k = keyword.lower()
        data = [d for d in data if k in d["Recipe_name"].lower()]

    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    results = data[start:end]

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": (total + page_size - 1) // page_size,
        "results": results
    }), 200

@api.route("/diet-types", methods=["GET"])
def diet_types():
    data = get_clean_data()
    types = sorted(list({d["Diet_type"] for d in data}))
    return jsonify(types), 200
