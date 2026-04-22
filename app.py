from flask import Flask, render_template, request, redirect
from azure.cosmos import CosmosClient
import os
import uuid

app = Flask(__name__)

COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")

DATABASE_NAME = "MessageBoardDB"
CONTAINER_NAME = "Messages"

client = CosmosClient(COSMOS_URI, COSMOS_KEY)

db = client.create_database_if_not_exists(id=DATABASE_NAME)

container = db.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key={"paths": ["/username"], "kind": "Hash"}
)

@app.route("/")
def index():
    messages = list(container.query_items(
        query="SELECT * FROM c ORDER BY c._ts DESC",
        enable_cross_partition_query=True
    ))
    return render_template("index.html", messages=messages)

@app.route("/add", methods=["POST"])
def add_message():
    username = request.form["username"]
    message = request.form["message"]

    container.create_item({
        "id": str(uuid.uuid4()),
        "username": username,
        "message": message
    })

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
