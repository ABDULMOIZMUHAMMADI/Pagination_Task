from fastapi import FastAPI, HTTPException,Query
import json
import os

app = FastAPI()

file_path = "users.json"

@app.post("/user")
def create_user(name: str, age: int, text: str):
        
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []

    if len(users) == 0:
        new_id = 1
    else:
        new_id = len(users) + 1

    new_user ={
        "ID" : new_id,
        "Name" : name,
        "Age" :age,
        "Text" : text
    }
    users.append(new_user)

    with open(file_path, "w") as f:
        json.dump(users, f, indent=4)

    return {"message": "User added successfully", "User": new_user}



@app.get("/users")
def get_users(
    limit: int = Query(10, description="Number of users to return, must be positive"),
    offset: int = Query(0, description="Starting index, must be zero or positive"),
    sort: str = Query("asc", description="asc or desc for sorting by ID")
):
    # Validation
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be zero or positive")
    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort value")    

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []
    reverse_order = True if sort == "desc" else False

    sorted_users = sorted(users,key=lambda x: x["ID"],reverse=reverse_order)
    paginated_users = sorted_users[offset: offset + limit]

    return {
    "total_users": len(users),
    "limit": limit,
    "offset": offset,
    "data": paginated_users
}

    
@app.get("/user/{user_id}")
def get_single_user(user_id: int):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []

    for user in users:
        if user["ID"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/user/{user_id}")
def delete_user(user_id : int):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []

    for user in users:
        if user["ID"] == user_id:
            users.remove(user)
        with open(file_path, "w") as f:
            json.dump(users, f, indent=4)

        return {"message": "User deleted successfully", "User": user_id}

    raise HTTPException(status_code=404, detail="User not found")

@app.put("/user/{user_id}")
def update_user(user_id: int, name: str = None, age: int = None, text: str = None):

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []

    for user in users:
        if user["ID"] == user_id:

            if name is not None:
                user["Name"] = name
            if age is not None:
                user["Age"] = age
            if text is not None:
                user["Text"] = text

            with open(file_path, "w") as f:
                json.dump(users, f, indent=4)

            return {"message": f"User with ID {user_id} updated successfully", "user": user}

    raise HTTPException(status_code=404, detail="User not found")


@app.post("/user/{user_id}/analyze")
def analyze_user_text(
    user_id: int,
    limit: int = Query(10, description="Number of analyses to return, must be positive"),
    offset: int = Query(0, description="Starting index, must be zero or positive"),
    sort: str = Query("asc", description="asc or desc for sorting by analysis_id"),
    min_words: int = Query(0, description="Minimum word count for filtering, must be zero or positive")
):
    # Validation
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be zero or positive")
    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort value")
    if min_words < 0:
        raise HTTPException(status_code=400, detail="min_words must be zero or positive")
    if min_words < 0:
        raise HTTPException(status_code=400, detail="min_words must be zero or positive")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                users = json.load(f)
            except:
                users = []
    else:
        users = []
    for user in users:
        if user["ID"] == user_id:
            analyses = user.get("Analyses", [])
            break
        else:
            raise HTTPException(status_code=404, detail="User not found")


    for user in users:
        if user["ID"] == user_id:
            user_text = user.get("Text", "")
            break
    else:
        raise HTTPException(status_code=404, detail="User not found")

    if user_text == "":
        raise HTTPException(status_code=400, detail="Text is empty")
    if len(user_text) > 200:
        raise HTTPException(status_code=400, detail="Text too long (max 200 chars)")

    word_count = len(user_text.split())
    uppercase_count = sum(1 for c in user_text if c.isupper())
    special_count = sum(1 for c in user_text if not c.isalnum() and not c.isspace())

    if "Analyses" not in user:
        user["Analyses"] = []

    analysis_id = len(user["Analyses"]) + 1

    analysis_result = {
        "analysis_id": analysis_id,
        "WordCount": word_count,
        "UppercaseCount": uppercase_count,
        "SpecialCharacterCount": special_count
    }

    user["Analyses"].append(analysis_result)

    reverse_order = True if sort == "desc" else False
    filtered_analyses = [a for a in analyses if a["WordCount"] >= min_words]


    sorted_analyses = sorted(filtered_analyses,key=lambda x: x["analysis_id"],reverse=reverse_order)
    paginated_analyses = sorted_analyses[offset: offset + limit]

    with open(file_path, "w") as f:
        json.dump(users, f, indent=4)

    return {
    "user_id": user_id,
    "total_after_filter": len(filtered_analyses),
    "limit": limit,
    "offset": offset,
    "data": paginated_analyses}
