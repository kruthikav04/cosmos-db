from flask import Flask, render_template, request, redirect
from azure.cosmos import CosmosClient
import os
import uuid

app = Flask(__name__)

# ✅ Use environment variables (IMPORTANT)
ENDPOINT = os.getenv("COSMOS_URI")
KEY = os.getenv("COSMOS_KEY")

DATABASE_NAME = "MessageBoardDB"
CONTAINER_NAME = "Messages"

# ✅ Create client
client = CosmosClient(ENDPOINT, KEY)

# ✅ Create DB if not exists
database = client.create_database_if_not_exists(id=DATABASE_NAME)

# ✅ Correct partition key format
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key={"paths": ["/userId"], "kind": "Hash"}
)

@app.route("/")
def home():
    # ✅ Use query instead of read_all_items
    items = list(container.query_items(
        query="SELECT * FROM c ORDER BY c._ts DESC",
        enable_cross_partition_query=True
    ))
    return render_template("index.html", messages=items)

@app.route("/add", methods=["POST"])
def add_message():
    user = request.form["user"]   # make sure HTML uses name="user"
    message = request.form["message"]

    container.create_item({
        "id": str(uuid.uuid4()),
        "userId": user,
        "message": message
    })

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
