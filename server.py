import time
import os
import requests
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

API_KEY = "ac8ae18ab3424ef183a04ddc865c980d"
HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
EVERYTHING_URL = "https://newsapi.org/v2/everything"

headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}

headlines_data = {}
everything_data = {}

def fetch_and_store_news():
    global headlines_data, everything_data
    while True:
        try:
            # Fetch top headlines
            headlines_response = requests.get(HEADLINES_URL, params={"category": "technology", "apiKey": API_KEY}, headers=headers)
            if headlines_response.status_code == 200:
                headlines_data["technology"] = headlines_response.json()

            # Fetch everything news
            everything_response = requests.get(EVERYTHING_URL, params={"q": "technology", "sortBy": "publishedAt", "apiKey": API_KEY}, headers=headers)
            if everything_response.status_code == 200:
                everything_data["technology"] = everything_response.json()

        except Exception as e:
            print(f"Error fetching news: {e}")

        time.sleep(3600)  # Wait 1 hour before fetching again

def paginate_data(data, page, page_size):
    if "articles" in data:
        if page == "all":
            return data["articles"]
        
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size
        end = start + page_size
        return data["articles"][start:end]
    return []

@app.route("/headlines", methods=["GET"])
def get_headlines():
    category = request.args.get("category", default="technology")  # Get the category parameter from request
    if category in headlines_data:
        page = request.args.get("page", default=1)
        page_size = request.args.get("pageSize", default=5)
        paginated_articles = paginate_data(headlines_data[category], page, page_size)
        return jsonify({"articles": paginated_articles})
    return jsonify({"error": "No data available for this category"}), 404

@app.route("/everything", methods=["GET"])
def get_everything():
    category = request.args.get("category", default="technology")  # Get the category parameter from request
    if category in everything_data:
        page = request.args.get("page", default=1)
        page_size = request.args.get("pageSize", default=5)
        paginated_articles = paginate_data(everything_data[category], page, page_size)
        return jsonify({"articles": paginated_articles})
    return jsonify({"error": "No data available for this category"}), 404

if __name__ == "__main__":
    # Start the news fetching in a separate thread
    threading.Thread(target=fetch_and_store_news, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 locally if PORT is not set
    app.run(debug=True, host="0.0.0.0", port=port)
