import pandas as pd
import numpy as np

# Define genre hierarchies and sub-genres
GENRE_HIERARCHY = {
    'Action': ['Martial Arts', 'Superhero', 'Spy', 'Adventure', 'Military', 'Disaster'],
    'Drama': ['Period Drama', 'Social Drama', 'Political Drama', 'Family Drama', 'Medical Drama'],
    'Comedy': ['Romantic Comedy', 'Dark Comedy', 'Slapstick', 'Satire', 'Parody'],
    'Sci-Fi': ['Space Opera', 'Cyberpunk', 'Time Travel', 'Post-Apocalyptic', 'AI/Robot'],
    'Horror': ['Supernatural', 'Psychological', 'Slasher', 'Monster', 'Gothic'],
    'Romance': ['Historical Romance', 'Contemporary Romance', 'Melodrama'],
    'Thriller': ['Psychological Thriller', 'Crime Thriller', 'Political Thriller', 'Mystery'],
    'Fantasy': ['High Fantasy', 'Urban Fantasy', 'Dark Fantasy', 'Magical Realism'],
    'Animation': ['Anime', '3D Animation', 'Stop Motion', 'Family Animation'],
    'Documentary': ['Nature', 'Historical', 'Biographical', 'Social Issue', 'Science'],
    'Crime': ['Film Noir', 'Heist', 'Detective', 'True Crime', 'Gangster'],
    'Adventure': ['Exploration', 'Survival', 'Quest', 'Treasure Hunt'],
    'Western': ['Spaghetti Western', 'Contemporary Western', 'Classic Western'],
    'Musical': ['Broadway Adaptation', 'Dance', 'Rock Musical', 'Classical'],
    'War': ['World War', 'Civil War', 'Modern Warfare', 'Resistance'],
    'Family': ['Children', 'Coming of Age', 'Educational', 'Holiday'],
}

def enhance_genres(movies_df):
    """
    Enhance the genre information of movies by adding sub-genres and related tags.
    
    Args:
        movies_df (pd.DataFrame): DataFrame containing movie information with 'genres' column
        
    Returns:
        pd.DataFrame: DataFrame with enhanced genre information
    """
    # Create a copy to avoid modifying the original dataframe
    enhanced_df = movies_df.copy()
    
    # Create new columns for enhanced genres and tags
    enhanced_df['enhanced_genres'] = ''
    enhanced_df['genre_tags'] = ''
    
    def expand_genres(genre_string):
        if pd.isna(genre_string):
            return [], []
            
        genres = genre_string.split('|')
        enhanced_genres = set(genres)  # Start with main genres
        genre_tags = set()
        
        # Add sub-genres based on main genres
        for genre in genres:
            if genre in GENRE_HIERARCHY:
                # Add all sub-genres for this main genre
                genre_tags.update(GENRE_HIERARCHY[genre])
                
        return list(enhanced_genres), list(genre_tags)
    
    # Apply the enhancement to each movie
    for idx, row in enhanced_df.iterrows():
        enhanced_genres, tags = expand_genres(row['genres'])
        enhanced_df.at[idx, 'enhanced_genres'] = '|'.join(enhanced_genres)
        enhanced_df.at[idx, 'genre_tags'] = '|'.join(tags)
    
    return enhanced_df

def get_genre_vector(genre_string, tag_string):
    """
    Create a combined genre and tag vector for a movie.
    
    Args:
        genre_string (str): String of genres separated by '|'
        tag_string (str): String of tags separated by '|'
        
    Returns:
        str: Combined string of genres and tags for TF-IDF processing
    """
    genres = [] if pd.isna(genre_string) else genre_string.split('|')
    tags = [] if pd.isna(tag_string) else tag_string.split('|')
    
    # Combine genres and tags with different weights
    # Main genres get more weight by repetition
    genre_vector = ' '.join(g.lower() for g in genres * 3)
    tag_vector = ' '.join(t.lower() for t in tags)
    
    return f"{genre_vector} {tag_vector}" 