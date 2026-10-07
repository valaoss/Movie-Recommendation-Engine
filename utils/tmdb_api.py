import os
import requests

API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_movie_poster(movie_title):
    params = {
        "api_key": API_KEY,
        "query": movie_title
    }
    response = requests.get(TMDB_SEARCH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    return None
