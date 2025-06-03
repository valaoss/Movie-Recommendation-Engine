import os
import requests
from dotenv import load_dotenv
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np

# Load environment variables
load_dotenv()

# TMDB API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def validate_api_key():
    """
    Validate the TMDB API key
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not TMDB_API_KEY:
        return False, """
        🎬 Welcome to the Movie Recommendation Engine!

        To get started, you need to set up your TMDB API key:

        1. Create a free account at https://www.themoviedb.org/
        2. Go to Settings -> API and request an API key
        3. Create a file named `.env` in the project root directory
        4. Add this line to the file:
           TMDB_API_KEY=your_api_key_here
        5. Replace 'your_api_key_here' with your actual API key
        6. Restart the application

        Need help? Feel free to ask!
        """
        
    try:
        test_url = f"{TMDB_BASE_URL}/authentication/token/new"
        response = requests.get(test_url, params={'api_key': TMDB_API_KEY})
        if response.status_code == 200:
            return True, ""
        else:
            return False, """
            ❌ Invalid API key. Please check that:
            1. Your API key is correct in the .env file
            2. You've copied the entire key without any extra spaces
            3. The key is active on your TMDB account
            """
    except requests.exceptions.RequestException:
        return False, "Unable to connect to TMDB API. Please check your internet connection."

def get_similar_movies(movie_id):
    """
    Get similar movies and recommendations for a given movie ID from TMDB
    
    Args:
        movie_id (int): TMDB movie ID
        
    Returns:
        list: List of similar movies with their details
    """
    try:
        # Get similar movies
        similar_url = f"{TMDB_BASE_URL}/movie/{movie_id}/similar"
        recommendations_url = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations"
        
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': 1
        }
        
        # Fetch both similar movies and recommendations
        similar_response = requests.get(similar_url, params=params)
        recommendations_response = requests.get(recommendations_url, params=params)
        
        similar_response.raise_for_status()
        recommendations_response.raise_for_status()
        
        similar_data = similar_response.json()
        recommendations_data = recommendations_response.json()
        
        # Combine and deduplicate results
        all_movies = []
        seen_ids = set()
        
        for movie in similar_data.get('results', []) + recommendations_data.get('results', []):
            if movie['id'] not in seen_ids and movie.get('poster_path'):
                seen_ids.add(movie['id'])
                all_movies.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_path': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie['poster_path'] else None,
                    'release_date': movie.get('release_date', ''),
                    'vote_average': movie.get('vote_average', 0),
                    'overview': movie.get('overview', ''),
                    'similarity_type': 'TMDB Recommendation'
                })
        
        # Sort by vote average and return top 10
        return sorted(all_movies, key=lambda x: x['vote_average'], reverse=True)[:10]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching similar movies: {str(e)}")
        return []

def get_movie_details_from_web(title, year=None):
    """
    Search for movie information using web search
    
    Args:
        title (str): Movie title to search for
        year (str, optional): Release year to narrow down search
        
    Returns:
        dict: Movie details including information from web search
    """
    search_query = f"{title} {year if year else ''} movie cast director plot rating"
    
    try:
        # Use web search to get movie information
        search_results = web_search(
            search_term=search_query,
            explanation="Searching for movie details using web search"
        )
        
        if not search_results:
            return None
            
        # Extract relevant information from search results
        movie_info = {
            'title': title,
            'release_date': year if year else '',
            'plot': '',
            'directors': [],
            'cast': [],
            'rating': '',
            'genres': []
        }
        
        # Process search results to extract information
        for result in search_results:
            text = result.get('snippet', '').lower()
            
            # Extract plot
            if 'plot' in text or 'synopsis' in text or 'story' in text:
                movie_info['plot'] = result.get('snippet', '')
            
            # Extract director
            if 'directed by' in text or 'director' in text:
                # Look for director pattern
                text = result.get('snippet', '')
                if 'directed by' in text.lower():
                    director = text.split('directed by')[1].split('.')[0].strip()
                    movie_info['directors'].append(director)
            
            # Extract cast
            if 'starring' in text or 'cast' in text:
                # Look for cast pattern
                text = result.get('snippet', '')
                if 'starring' in text.lower():
                    cast = text.split('starring')[1].split('.')[0].strip()
                    actors = [actor.strip() for actor in cast.split(',')]
                    movie_info['cast'].extend(actors)
            
            # Extract rating
            if 'rating' in text or 'rated' in text:
                if 'imdb' in text.lower() and '/10' in text:
                    # Try to find IMDb rating pattern (e.g., "7.5/10")
                    import re
                    rating_match = re.search(r'(\d+\.?\d*)/10', text)
                    if rating_match:
                        movie_info['rating'] = float(rating_match.group(1))
            
            # Extract genres
            genre_keywords = ['action', 'drama', 'comedy', 'thriller', 'horror', 
                            'romance', 'sci-fi', 'adventure', 'fantasy', 'animation',
                            'documentary', 'crime', 'mystery']
            for genre in genre_keywords:
                if genre in text.lower() and genre not in movie_info['genres']:
                    movie_info['genres'].append(genre.title())
        
        # Clean up the data
        movie_info['directors'] = list(set(movie_info['directors']))[:2]  # Keep top 2 directors
        movie_info['cast'] = list(set(movie_info['cast']))[:5]  # Keep top 5 cast members
        movie_info['genres'] = list(set(movie_info['genres']))  # Remove duplicates
        
        return movie_info
        
    except Exception as e:
        print(f"Error fetching movie details from web: {str(e)}")
        return None

def load_local_movies():
    """Load and cache the local movie dataset"""
    try:
        movies_df = pd.read_csv('data/movies.csv')
        return movies_df
    except Exception as e:
        print(f"Error loading local movie database: {str(e)}")
        return None

def load_movie_data():
    """Load and cache all necessary movie data"""
    try:
        movies_df = pd.read_csv('data/movies.csv')
        links_df = pd.read_csv('data/links.csv')
        ratings_df = pd.read_csv('data/ratings.csv')
        tags_df = pd.read_csv('data/tags.csv')
        
        # Merge relevant information
        movie_data = movies_df.copy()
        
        # Add average rating
        avg_ratings = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
        movie_data = movie_data.merge(avg_ratings, on='movieId', how='left')
        
        # Add tags
        tags_grouped = tags_df.groupby('movieId')['tag'].apply(list).reset_index()
        movie_data = movie_data.merge(tags_grouped, on='movieId', how='left')
        
        # Add external IDs
        movie_data = movie_data.merge(links_df, on='movieId', how='left')
        
        return movie_data
    except Exception as e:
        print(f"Error loading movie data: {str(e)}")
        return None

def find_best_match(title, year, movies_df):
    """
    Find the best matching movie in the dataset
    
    Args:
        title (str): Movie title to search for
        year (str or None): Release year if available
        movies_df (pd.DataFrame): Movie dataset
        
    Returns:
        pd.Series: Best matching movie row or None
    """
    if movies_df is None:
        return None
    
    best_match = None
    best_score = 0
    
    # Clean input title
    clean_title = title.lower().strip()
    
    for idx, row in movies_df.iterrows():
        movie_title = row['title']
        movie_year = None
        
        # Extract year from title if present
        if '(' in movie_title and ')' in movie_title:
            movie_year = movie_title[-5:-1]  # Extract year from (YYYY)
            movie_title = movie_title[:-7].strip()  # Remove (YYYY)
        
        # Calculate title similarity
        similarity = fuzz.ratio(clean_title, movie_title.lower())
        
        # If year is provided, boost score for matching year
        if year and movie_year and year == movie_year:
            similarity += 20
        
        if similarity > best_score:
            best_score = similarity
            best_match = row
    
    return best_match if best_score > 80 else None

def get_movie_details(title, year=None):
    """
    Get movie details from local dataset
    
    Args:
        title (str): Movie title to search for
        year (str, optional): Release year to narrow down search
        
    Returns:
        dict: Movie details from local dataset
    """
    # Load movie data
    movies_df = load_movie_data()
    
    if movies_df is None:
        return None
    
    # Find best match
    movie = find_best_match(title, year, movies_df)
    
    if movie is None:
        return None
    
    # Extract year from title
    release_year = None
    if '(' in movie['title'] and ')' in movie['title']:
        release_year = movie['title'][-5:-1]
    
    # Extract genres
    genres = movie['genres'].split('|') if movie['genres'] else []
    
    # Create movie info dictionary
    movie_info = {
        'title': movie['title'],
        'release_date': release_year,
        'genres': genres,
        'rating': round(float(movie['mean']) if not pd.isna(movie['mean']) else 0, 1),
        'vote_count': int(movie['count']) if not pd.isna(movie['count']) else 0,
        'plot': '',  # We don't have plot in the dataset
        'directors': [],  # We don't have director info
        'cast': [],  # We don't have cast info
        'tags': movie['tag'] if not pd.isna(movie['tag']) else [],
        'imdb_id': f"tt{str(int(movie['imdbId'])).zfill(7)}" if not pd.isna(movie['imdbId']) else None,
        'tmdb_id': int(movie['tmdbId']) if not pd.isna(movie['tmdbId']) else None
    }
    
    return movie_info 