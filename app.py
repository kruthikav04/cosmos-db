from flask import Flask, render_template, request, redirect
from azure.cosmos import CosmosClient
import uuid

app = Flask(__name__)

ENDPOINT = "YOUR_COSMOS_DB_URI"
KEY = "YOUR_PRIMARY_KEY"

client = CosmosClient(ENDPOINT, KEY)

database = client.create_database_if_not_exists(id="MessageBoardDB")

container = database.create_container_if_not_exists(
    id="Messages",
    partition_key="/userId"
)

@app.route("/")
def home():
    items = list(container.read_all_items())
    return render_template("index.html", messages=items)

@app.route("/add", methods=["POST"])
def add_message():
    user = request.form["user"]
    message = request.form["message"]

    container.create_item({
        "id": str(uuid.uuid4()),
        "userId": user,
        "message": message
    })

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)