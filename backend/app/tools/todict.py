def recipe_to_dict(row):
    if hasattr(row, "keys"):
        result = {
            "id": row["id"],
            "title": row["title"],
            "ingredients": row["ingredients"],
            "instructions": row["instructions"],
            "is_public": bool(row["is_public"]),
            "owner_id": row["owner_id"],
        }
        if "owner_username" in row.keys():
            result["owner_username"] = row["owner_username"]
        return result

    # ORM Recipe instance
    result = {
        "id": row.id,
        "title": row.title,
        "ingredients": row.ingredients,
        "instructions": row.instructions,
        "is_public": bool(row.is_public),
        "owner_id": row.owner_id,
    }
    # no owner_username for now from ORM
    return result