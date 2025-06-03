import pandas as pd
import numpy as np
from pathlib import Path
from .genre_enhancer import enhance_genres, get_genre_vector

def load_data():
    """
    Load and preprocess movie and rating data with optimizations
    """
    # Define data paths
    data_dir = Path("data")
    movies_path = data_dir / "movies.csv"
    ratings_path = data_dir / "ratings.csv"
    
    # Load movies with only necessary columns
    movies = pd.read_csv(
        movies_path,
        usecols=['movieId', 'title', 'genres'],
        dtype={
            'movieId': 'int32',
            'title': 'str',
            'genres': 'str'
        }
    )
    
    # Load ratings with only necessary columns and optimize dtypes
    ratings = pd.read_csv(
        ratings_path,
        usecols=['userId', 'movieId', 'rating'],
        dtype={
            'userId': 'int32',
            'movieId': 'int32',
            'rating': 'float32'
        }
    )
    
    return movies, ratings

def merge_data(movies, ratings):
    """
    Merge movies and ratings data efficiently
    """
    # Merge only necessary columns
    df = pd.merge(
        ratings[['movieId', 'rating']],
        movies[['movieId', 'title']],
        on='movieId'
    )
    
    # Optimize memory usage
    df = df.astype({
        'movieId': 'int32',
        'rating': 'float32'
    })
    
    return df
