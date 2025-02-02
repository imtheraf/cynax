import time
import os
import requests
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

HEADLINES_URL = "https://newsapi.org/v2/top-headlines?category=technology&apiKey=ac8ae18ab3424ef183a04ddc865c980d"
EVERYTHING_URL = "https://newsapi.org/v2/everything?q=technology&sortBy=publishedAt&apiKey=ac8ae18ab3424ef183a04ddc865c980d"

headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}

headlines_data = None
everything_data = None

def fetch_and_store_news():
    global headlines_data, everything_data
    while True:
        try:
            # Fetch top headlines
            headlines_response = requests.get(HEADLINES_URL, headers=headers)
            if headlines_response.status_code == 200:
                headlines_data = headlines_response.json()
            
            # Fetch everything news
            everything_response = requests.get(EVERYTHING_URL, headers=headers)
            if everything_response.status_code == 200:
                everything_data = everything_response.json()
        
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        time.sleep(3600)  # Wait 1 hour before fetching again

@app.route("/headlines", methods=["GET"])
def get_headlines():
    if headlines_data:
        return jsonify(headlines_data)
    return jsonify({"error": "No data available"}), 404

@app.route("/everything", methods=["GET"])
def get_everything():
    if everything_data and "articles" in everything_data:
        page = request.args.get("page", default=1, type=int)
        page_size = request.args.get("pageSize", default=5, type=int)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_articles = everything_data["articles"][start:end]
        return jsonify({"articles": paginated_articles})
    return jsonify({"error": "No data available"}), 404

if __name__ == "__main__":
    # Start the news fetching in a separate thread
    threading.Thread(target=fetch_and_store_news, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 locally if PORT is not set
    app.run(debug=True, host="0.0.0.0", port=port)
