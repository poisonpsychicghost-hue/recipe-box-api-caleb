def recipe_to_dict(row):
    result = {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"],
    }

    # safely include owner_username if it’s present in this query
    if "owner_username" in row.keys():
        result["owner_username"] = row["owner_username"]

    return result

