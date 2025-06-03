import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def prepare_data(movies_df):
    """
    Prepare the movies data for content-based filtering by cleaning and combining features.
    
    Args:
        movies_df (pd.DataFrame): DataFrame containing movies with at least genres column
        
    Returns:
        pd.DataFrame: Processed DataFrame with combined features
    """
    # Create a copy to avoid modifying the original dataframe
    df = movies_df.copy()
    
    # Fill missing values with empty strings for required columns
    df['genres'] = df['genres'].fillna('')
    
    # Clean up the genres (replace | with space)
    df['genres'] = df['genres'].str.replace('|', ' ')
    
    # Initialize combined features with genres
    df['combined_features'] = df['genres']
    
    # Add cast and director if available
    if 'cast' in df.columns:
        df['cast'] = df['cast'].fillna('')
        df['combined_features'] += ' ' + df['cast']
    
    if 'director' in df.columns:
        df['director'] = df['director'].fillna('')
        df['combined_features'] += ' ' + df['director']
    
    return df

def build_content_based_model(movies_df):
    """
    Build a content-based recommendation model using TF-IDF and cosine similarity.
    
    Args:
        movies_df (pd.DataFrame): DataFrame containing movies with genres
        
    Returns:
        tuple: (processed DataFrame, cosine similarity matrix)
    """
    try:
        # Try to load and merge credits data
        try:
            credits_df = pd.read_csv('data/credits.csv')
            df = movies_df.merge(credits_df[['movieId', 'cast', 'director']], 
                               on='movieId', 
                               how='left')
        except Exception as e:
            print(f"Could not load credits data: {str(e)}")
            df = movies_df
    
        # Prepare data
        df = prepare_data(df)
        
        # Create TF-IDF vectorizer
        tfidf = TfidfVectorizer(stop_words='english')
        
        # Create TF-IDF matrix
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        
        # Compute cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        return df, cosine_sim
    except Exception as e:
        print(f"Error building content-based model: {str(e)}")
        # Return a basic model using only genres
        df = prepare_data(movies_df)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        return df, cosine_sim

def get_recommendations(title, movies_df, cosine_sim):
    """
    Get movie recommendations based on title similarity.
    
    Args:
        title (str): Title of the movie to get recommendations for
        movies_df (pd.DataFrame): Processed movies DataFrame
        cosine_sim (np.ndarray): Cosine similarity matrix
        
    Returns:
        list: List of tuples containing (title, similarity_score)
    """
    try:
        # Get the index of the movie that matches the title
        idx = movies_df[movies_df['title'].str.lower() == title.lower()].index[0]
        
        # Get similarity scores for all movies
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 5 most similar movies (excluding the movie itself)
        sim_scores = sim_scores[1:6]
        
        # Get movie indices and scores
        movie_indices = [i[0] for i in sim_scores]
        similarity_scores = [i[1] for i in sim_scores]
        
        # Return movie titles and similarity scores
        recommendations = [
            (movies_df.iloc[idx]['title'], score) 
            for idx, score in zip(movie_indices, similarity_scores)
        ]
        
        return recommendations
    except IndexError:
        print(f"Movie '{title}' not found in the database.")
        return []
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return []

def get_similar_movies(movie_id, movies_df, cosine_sim):
    """
    Get movie recommendations based on movie ID.
    
    Args:
        movie_id (int): ID of the movie to get recommendations for
        movies_df (pd.DataFrame): Processed movies DataFrame
        cosine_sim (np.ndarray): Cosine similarity matrix
        
    Returns:
        list: List of dictionaries containing similar movie information
    """
    try:
        # Get the index of the movie that matches the ID
        idx = movies_df[movies_df['movieId'] == movie_id].index[0]
        
        # Get similarity scores for all movies
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 5 most similar movies (excluding the movie itself)
        sim_scores = sim_scores[1:6]
        
        # Get movie indices and scores
        similar_movies = []
        for i, score in sim_scores:
            movie = movies_df.iloc[i]
            similar_movies.append({
                'movieId': movie['movieId'],
                'title': movie['title'],
                'genres': movie['genres'],
                'similarity_score': score,
                'year': movie.get('year', ''),
                'poster_path': movie.get('poster_path', '')
            })
        
        return similar_movies
    except IndexError:
        print(f"Movie ID {movie_id} not found in the database.")
        return []
    except Exception as e:
        print(f"Error getting similar movies: {str(e)}")
        return []
