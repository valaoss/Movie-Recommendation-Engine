# 🎬 Movie Recommendation Engine

Content-based movie recommender with a Streamlit UI. Pick a movie and get similar titles based on genre, cast, crew and keywords (TF-IDF + cosine similarity). Posters and details come from the TMDB API.

> 🇹🇷 Seçilen filme tür, oyuncu, yönetmen ve anahtar kelime benzerliğine göre öneri yapan, içerik tabanlı film öneri sistemi (TF-IDF + kosinüs benzerliği). Arayüz Streamlit ile yazıldı.

## Tech
Python · pandas · scikit-learn · Streamlit · TMDB API

## Structure
```
app/        Streamlit interface + TMDB helpers
model/      recommender (TF-IDF, similarity)
utils/      data loading, genre features, poster processing
scripts/    poster fetching script
data/       datasets (MovieLens CSVs, not committed)
```

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env      # add your TMDB API key
python main.py
```
Download the [MovieLens dataset](https://grouplens.org/datasets/movielens/) and put `movies.csv`, `ratings.csv`, `links.csv`, `tags.csv` into `data/`.
