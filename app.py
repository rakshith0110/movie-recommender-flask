from flask import Flask, render_template, request
import pickle
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change_this_secret_for_prod")

# load models / data once at startup
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
movies = pickle.load(open(os.path.join(MODEL_DIR, "movie_list.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(MODEL_DIR, "similarity.pkl"), "rb"))

# Use env var for security in production
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")

def fetch_poster(movie_id):
    """Return full poster URL from TMDB for a given movie_id."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        poster_path = data.get("poster_path")
        if not poster_path:
            return None
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    except Exception:
        return None

def recommend(movie_title, top_k=5):
    """Return (titles_list, posters_list) for top_k recommendations."""
    try:
        index = movies[movies['title'] == movie_title].index[0]
    except Exception:
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1: top_k+1]:
        movie_idx = i[0]
        recommended_movie_names.append(movies.iloc[movie_idx].title)
        movie_id = movies.iloc[movie_idx].movie_id
        poster_url = fetch_poster(movie_id)
        recommended_movie_posters.append(poster_url)

    return recommended_movie_names, recommended_movie_posters

@app.route("/", methods=["GET", "POST"])
def index():
    movie_list = list(movies['title'].values)
    recommended = []
    posters = []
    selected_movie = None

    if request.method == "POST":
        selected_movie = request.form.get("movie")
        if selected_movie:
            recommended, posters = recommend(selected_movie, top_k=5)

    # create list-of-tuples to iterate easily in Jinja
    recommendations = list(zip(recommended, posters))

    return render_template(
        "index.html",
        movie_list=movie_list,
        recommendations=recommendations,
        selected_movie=selected_movie
    )

if __name__ == "__main__":
    app.run(debug=True)
