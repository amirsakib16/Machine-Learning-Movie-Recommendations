from flask import Flask, request, jsonify, make_response
import pandas as pd
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will apply CORS to all routes




movies = pd.read_csv(r"E:\project01\Backend\tmdb_5000_movies.csv")
credit = pd.read_csv(r"E:\project01\Backend\tmdb_5000_credits.csv")
df = movies.merge(credit, on="title")
df = df[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
df.dropna(inplace=True)





@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "CORS test successful!"})

porterstemmer = PorterStemmer()

def DICTtoLST(data, cast=False, crew=False):
    try:
        parsed_data = json.loads(data)
        if not cast and not crew:
            return [item["name"].replace(" ", "").lower() for item in parsed_data]
        elif cast and not crew:
            return [item["name"].replace(" ", "").lower() for item in parsed_data][0:3]
        elif not cast and crew:
            return [item["name"].replace(" ", "").lower() for item in parsed_data if item["job"] == "Director"]
    except (json.JSONDecodeError, TypeError, KeyError):
        return []

def TXTtoLST(data):
    return [porterstemmer.stem(i.lower()) for i in data.split()]

def preprocess_df(df):
    df["genres"] = df["genres"].apply(DICTtoLST)
    df["keywords"] = df["keywords"].apply(DICTtoLST)
    df["cast"] = df["cast"].apply(lambda x: DICTtoLST(x, cast=True, crew=False))
    df["crew"] = df["crew"].apply(lambda x: DICTtoLST(x, cast=False, crew=True))
    df["overview"] = df["overview"].apply(TXTtoLST)
    df["TKN"] = df["overview"] + df["genres"] + df["keywords"] + df["cast"] + df["crew"]
    df["TKN"] = df["TKN"].apply(lambda x: " ".join(x))
    return df

df = preprocess_df(df)


count_vectorizer = CountVectorizer(max_features=5000, stop_words='english')
vector = count_vectorizer.fit_transform(df["TKN"]).toarray()
cosine_sim = cosine_similarity(vector)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    movie_name = data.get("movie")
    movie_name_lower = movie_name.lower()
    
    # Find matching movie titles in the DataFrame (case-insensitive)
    matching_movies = df[df["title"].str.lower().str.contains(movie_name_lower)]
    
    if matching_movies.empty:
        return make_response(jsonify({"error": "Movie not found."}), 404)

    # Get the index of the first matching movie
    movie_index = matching_movies.index[0]
    similarity_scores = list(enumerate(cosine_sim[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:9]

    recommended_movies = [df.iloc[i[0]]["title"] for i in similarity_scores]
    return jsonify({"recommendations": recommended_movies})
@app.route("/movies", methods=["GET"])
def get_movies():
    movie_titles = df["title"].tolist()  # Extract all movie titles
    return jsonify({"movies": movie_titles})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

