from flask import Flask, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
app=Flask(__name__)
sia=SentimentIntensityAnalyzer()
@app.get("/")
def home():
    return jsonify(service="Best Cars sentiment analyzer",status="ok")
@app.get("/analyze/<path:input_txt>")
def analyze_sentiment(input_txt):
    score=sia.polarity_scores(input_txt)["compound"]
    return jsonify(sentiment="positive" if score>=0.05 else "negative" if score<=-0.05 else "neutral",score=score)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5050)
