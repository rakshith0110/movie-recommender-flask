import pickle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "model")

movies = pickle.load(open(os.path.join(MODEL_DIR, "movie_list.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(MODEL_DIR, "similarity.pkl"), "rb"))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=18d3583f68071b10ede6ee3748b2d610"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None

def recommend(movie):
    if movie not in movies['title'].values:
        return [], []
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), key=lambda x: x[1], reverse=True)
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

@app.route("/", methods=["GET", "POST"])
def index():
    movie_list = movies['title'].values
    recommended = []
    selected_movie = None
    if request.method == "POST":
        selected_movie = request.form.get("movie")
        recommended_names, recommended_posters = recommend(selected_movie)
        recommended = zip(recommended_names, recommended_posters)
    return render_template("index.html", movie_list=movie_list, recommendations=recommended, selected_movie=selected_movie)

if __name__ == "__main__":
    app.run(debug=True)
