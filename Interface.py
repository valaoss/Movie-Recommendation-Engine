import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Movie Browser",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import sys
import os
import pandas as pd
import random
from pathlib import Path
import re
import base64
import json
import math
from typing import List, Dict, Any
import time

# Add project root to path to find 'utils' and 'model' modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocess import load_data, merge_data
from model.recommender import build_content_based_model, get_recommendations, get_similar_movies
from app.utils.movie_utils import get_movie_details

# Initialize session state for pagination
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'movies_per_page' not in st.session_state:
    st.session_state.movies_per_page = 20
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"

# Custom CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* Main theme */
    :root {
        --rose-gold: #b76e79;
        --rose-gold-hover: #c98891;
        --shadow-color: rgba(183, 110, 121, 0.05);
        --background-dark: #141414;
        --background-light: #1f1f1f;
        --text-primary: #e5e5e5;
        --text-secondary: #999;
        --border-color: #333;
    }

    .stApp {
        background-color: var(--background-dark) !important;
        font-family: 'Montserrat', sans-serif;
        padding: 0 4%;
    }
    
    /* Search container styling */
    .search-container {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
    }
    
    /* Search bar styling */
    .stTextInput > div > div > input {
        background-color: var(--background-dark) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-family: 'Montserrat', sans-serif !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        height: 46px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--rose-gold) !important;
        box-shadow: 0 0 0 2px rgba(183, 110, 121, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary) !important;
        font-style: italic !important;
    }
    
    /* Search button styling */
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: var(--rose-gold) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        height: 46px !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background-color: var(--rose-gold-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Clear button styling */
    .stButton > button[data-baseweb="button"][kind="secondary"] {
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        height: 46px !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button[data-baseweb="button"][kind="secondary"]:hover {
        border-color: var(--text-primary) !important;
        color: var(--text-primary) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Search results text */
    .search-results {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 1rem 0;
        padding: 0.5rem 1rem;
        background-color: var(--background-light);
        border-radius: 4px;
        border: 1px solid var(--border-color);
    }
    
    /* Typography */
    h1, h2, h3, .movie-title {
        font-family: 'Montserrat', sans-serif;
        color: #e5e5e5;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: transparent;
        color: #e5e5e5;
        border: 1px solid #404040;
        border-radius: 2px;
        padding: 0.3rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 400;
        transition: all 0.2s ease;
        margin: 0;
    }
    
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #666;
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #666;
    }

    .stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background-color: var(--rose-gold-hover);
        border-color: var(--rose-gold-hover);
    }
    
    /* Category buttons */
    .category-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0 2rem 0;
        padding: 1rem;
        background-color: var(--background-light);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .category-buttons .stButton button {
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        border-radius: 20px;
        transition: all 0.2s ease;
        text-transform: none;
        font-weight: 400;
        min-width: 80px;
    }
    
    .category-buttons .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: var(--text-secondary);
        transform: translateY(-1px);
    }
    
    .category-buttons .stButton button[data-baseweb="button"][kind="primary"] {
        background-color: var(--rose-gold);
        border-color: var(--rose-gold);
        color: white;
    }
    
    .category-buttons .stButton button[data-baseweb="button"][kind="primary"]:hover {
        background-color: var(--rose-gold-hover);
        border-color: var(--rose-gold-hover);
    }
    
    /* Movie grid */
    .movie-grid {
        display: grid;
        grid-template-columns: repeat(5, 105px);
        grid-auto-rows: 158px;
        gap: 1rem;
        justify-content: center;
        margin: 0 auto;
    }
    
    .movie-card {
        width: 105px !important;
        height: 158px !important;
        background: transparent;
        border-radius: 2px;
        overflow: hidden;
        transition: transform 0.2s ease;
        border: none;
        box-shadow: none;
        cursor: pointer;
        position: relative;
    }
    
    .movie-poster-container {
        width: 100%;
        height: 100%;
        position: relative;
        background: #141414;
    }
    
    .movie-poster {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .movie-poster.error {
        background: #f8f9fa url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTIxIDV2MTRoLTE4di0xNGgydjEyaDE0di0xMmgyem0tOSA5di0xMmg5djEyaC05eiIgZmlsbD0iI2NjYyIvPjwvc3ZnPg==') center no-repeat;
    }
    
    .movie-info {
        padding: 0.25rem;
        background: rgba(0, 0, 0, 0.8);
        opacity: 0;
        transition: opacity 0.2s ease;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: left;
    }
    
    .movie-card:hover .movie-info {
        opacity: 1;
    }
    
    .movie-title {
        font-size: 0.65rem;
        font-weight: 400;
        margin: 0;
        color: #fff;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        line-height: 1.2;
    }
    
    .movie-meta {
        color: #999;
        font-size: 0.6rem;
        margin-top: 0.15rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        line-height: 1.2;
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0 0.5rem 0;
    }
    
    h1, h2 {
        font-size: 1.2rem;
        font-weight: 500;
        margin: 0;
        color: #e5e5e5;
    }
    
    /* Load more button */
    .load-more-container {
        width: calc(5 * 105px + 4 * 1rem); /* Match grid width */
        display: flex;
        gap: 1rem;
        justify-content: center;
        padding-top: 0.5rem;
        margin: 0 auto;
    }
    
    .load-more-button {
        background-color: transparent;
        color: #e5e5e5;
        padding: 0.5rem 1rem;
        border: 1px solid #404040;
        border-radius: 2px;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    
    .load-more-button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #666;
    }
    
    /* Netflix badges */
    .badge {
        position: absolute;
        top: 0.25rem;
        right: 0.25rem;
        background-color: rgba(255, 0, 0, 0.8);
        color: white;
        padding: 0.15rem 0.3rem;
        font-size: 0.6rem;
        border-radius: 2px;
        z-index: 1;
    }
    
    /* Hide Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Container for centering the grid */
    .grid-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
    }

    /* Movie modal */
    .movie-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #181818;
        padding: 2rem;
        border-radius: 8px;
        width: 90%;
        max-width: 800px;
        z-index: 1000;
        display: none;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }
    
    .movie-modal.show {
        display: block;
    }
    
    .modal-content {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 2rem;
        color: #fff;
    }
    
    .modal-poster {
        width: 300px;
        height: 450px;
        object-fit: cover;
        border-radius: 4px;
    }
    
    .modal-info {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .modal-title {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }
    
    .modal-metadata {
        display: flex;
        gap: 1rem;
        color: #999;
        font-size: 0.9rem;
    }
    
    .modal-scores {
        display: flex;
        gap: 2rem;
        margin: 1rem 0;
    }
    
    .score-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .score-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #fff;
    }
    
    .score-label {
        color: #999;
        font-size: 0.9rem;
    }
    
    .modal-credits {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .credit-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .credit-label {
        color: #999;
        font-size: 0.9rem;
    }
    
    .credit-value {
        color: #fff;
    }
    
    .modal-close {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: none;
        border: none;
        color: #fff;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
        line-height: 1;
    }
    
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 999;
        display: none;
    }
    
    .modal-backdrop.show {
        display: block;
    }

    /* Search bar container */
    .search-bar-container {
        background-color: rgba(31, 31, 31, 0.9);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid #333;
    }
    
    /* Make buttons more prominent */
    .stButton > button {
        height: 46px !important;  /* Match input field height */
    }

    /* Custom CSS for top navigation bar */
    .top-nav {
        position: fixed;
        top: 0;
        right: 0;
        left: 0;
        height: 68px;
        background-color: rgba(20, 20, 20, 0.95);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 4%;
        z-index: 1000;
        border-bottom: 1px solid #333;
    }
    
    .nav-logo {
        color: #e50914;
        font-size: 24px;
        font-weight: 600;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-search {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .search-input {
        background-color: #141414;
        border: 1px solid #333;
        color: #fff;
        padding: 8px 12px;
        border-radius: 4px;
        width: 240px;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #e50914;
        width: 300px;
    }
    
    .search-button {
        background-color: #e50914;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s ease;
    }
    
    .search-button:hover {
        background-color: #f40612;
    }
    
    .main-content {
        margin-top: 88px;
        padding: 0 4%;
    }

    /* Add styles for search container */
    .search-container {
        margin-bottom: 2rem;
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(5px);
    }

    .modal-content {
        background-color: #1f1f1f;
        margin: 5% auto;
        padding: 2rem;
        border: 1px solid #333;
        width: 80%;
        max-width: 900px;
        border-radius: 8px;
        position: relative;
    }

    .modal-grid {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 2rem;
        align-items: start;
    }

    .modal-poster img {
        width: 100%;
        border-radius: 4px;
    }

    .modal-details {
        color: #e5e5e5;
    }

    .modal-details h2 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 2rem;
        color: #fff;
    }

    .modal-details p {
        margin: 0.5rem 0;
        font-size: 1rem;
        color: #ccc;
    }

    .close {
        position: absolute;
        right: 1rem;
        top: 1rem;
        color: #666;
        font-size: 2rem;
        font-weight: bold;
        cursor: pointer;
        transition: color 0.2s ease;
    }

    .close:hover {
        color: #fff;
    }

    .imdb-link {
        display: inline-block;
        background-color: #f5c518;
        color: #000;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 4px;
        font-weight: 600;
        margin-top: 1rem;
        transition: background-color 0.2s ease;
    }

    .imdb-link:hover {
        background-color: #ffdb4d;
    }

    /* Movie info right panel styles */
    .movie-info-sidebar {
        background-color: var(--background-light);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        position: sticky;
        top: 88px;
        margin-left: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .movie-info-sidebar h3 {
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 500;
        margin: 0 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .movie-info-sidebar p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0.75rem 0;
        line-height: 1.4;
    }
    
    .movie-info-sidebar strong {
        color: var(--text-primary);
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .movie-info-sidebar a {
        color: var(--rose-gold);
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    .movie-info-sidebar a:hover {
        color: var(--rose-gold-hover);
        text-decoration: underline;
    }

    /* Back button styling */
    .movie-info-sidebar .stButton button {
        width: 100%;
        margin-top: 1rem;
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .movie-info-sidebar .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: var(--text-secondary);
        transform: translateY(-1px);
    }

    /* Search results styling */
    .search-result-container {
        background-color: var(--background-light);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }

    .search-result-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .search-result-container img {
        border-radius: 4px;
        transition: transform 0.2s ease;
        cursor: pointer;
    }

    .search-result-container img:hover {
        transform: scale(1.02);
    }

    .search-result-container h3 {
        color: var(--text-primary);
        margin: 0 0 1rem 0;
        font-size: 1.4rem;
        font-weight: 500;
    }

    .search-result-container p {
        color: var(--text-secondary);
        margin: 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .search-result-container strong {
        color: var(--text-primary);
        font-weight: 500;
    }

    /* Movie details section */
    .movie-details {
        background-color: var(--background-light);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 2rem;
        margin-top: 1rem;
    }

    .movie-details h3 {
        color: var(--text-primary);
        font-size: 1.6rem;
        font-weight: 600;
        margin: 0 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }

    .movie-details p {
        color: var(--text-secondary);
        margin: 0.75rem 0;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Button styling */
    .view-details-btn, .back-btn {
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-top: 1rem;
    }

    .view-details-btn:hover, .back-btn:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: var(--text-secondary);
        transform: translateY(-1px);
    }

    .back-btn {
        background-color: var(--rose-gold);
        border-color: var(--rose-gold);
    }

    .back-btn:hover {
        background-color: var(--rose-gold-hover);
        border-color: var(--rose-gold-hover);
    }

    /* Links styling */
    .movie-details a {
        color: var(--rose-gold);
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .movie-details a:hover {
        color: var(--rose-gold-hover);
        text-decoration: underline;
    }

    .movie-info-sidebar h4 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 500;
        margin: 1.5rem 0 1rem 0;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }

    .movie-info-sidebar .recommendations {
        margin-top: 1rem;
    }

    .movie-info-sidebar .recommendation-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .movie-info-sidebar .recommendation-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }

    .movie-info-sidebar .recommendation-title {
        color: var(--text-primary);
        font-size: 0.9rem;
        margin: 0;
    }

    .movie-info-sidebar .recommendation-score {
        color: var(--rose-gold);
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: auto;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_movies(max_movies=1000):
    """Load and cache the movie dataset with posters"""
    try:
        # Load movies
        movies_df = pd.read_csv('data/movies.csv')
        
        # Load posters
        posters_df = pd.read_csv('data/posters_with_titles.csv')
        
        # Clean up movie titles for matching
        movies_df['clean_title'] = movies_df['title'].str.replace(r'\s*\(\d{4}\)\s*$', '', regex=True)
        movies_df['year'] = movies_df['title'].str.extract(r'\((\d{4})\)').iloc[:, 0]
        
        # Create a poster lookup dictionary
        poster_dict = dict(zip(posters_df['title'], posters_df['poster']))
        
        # Add poster paths to movies dataframe
        def get_poster_path(title):
            safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_')).rstrip()
            path = f"data/processed_posters/{safe_title}.jpg"
            return path if os.path.exists(path) else None
            
        movies_df['poster_path'] = movies_df['clean_title'].apply(get_poster_path)
        
        # Only keep movies that have posters
        movies_df = movies_df[movies_df['poster_path'].notna()]
        
        # Clean up genres
        movies_df['genres'] = movies_df['genres'].fillna('')
        
        # Sort by year (newest first) and limit to max_movies
        movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce')
        movies_df = movies_df.sort_values('year', ascending=False).head(max_movies)
        
        st.sidebar.write(f"Total movies with posters: {len(movies_df)}")
        
        return movies_df
    except Exception as e:
        st.error(f"Error loading movies: {str(e)}")
        return pd.DataFrame()

def get_categories(movies_df):
    """Extract unique categories/genres from movies"""
    genres = []
    for movie_genres in movies_df['genres'].str.split('|'):
        if isinstance(movie_genres, list):
            genres.extend(movie_genres)
    return sorted(list(set(genres)))

def filter_movies_by_category(movies_df, category):
    """Filter movies by category/genre"""
    if category == "All":
        return movies_df
    return movies_df[movies_df['genres'].str.contains(category, na=False)]

def get_page_of_movies(movies_df, page, per_page):
    """Get a specific page of movies"""
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    return movies_df.iloc[start_idx:end_idx]

@st.cache_data
def get_image_base64(poster_path):
    """Cache base64 encoded images"""
    try:
        with open(poster_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            return f"data:image/jpeg;base64,{img_data}"
    except:
        return ""

@st.cache_data
def get_movie_details(movie_id):
    """Get detailed movie information including cast, director, and ratings"""
    try:
        # Load ratings
        ratings_df = pd.read_csv('data/ratings.csv')
        
        # Load links to get IMDb ID
        links_df = pd.read_csv('data/links.csv')
        
        # Get average rating and number of ratings
        movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]
        avg_rating = movie_ratings['rating'].mean()
        num_ratings = len(movie_ratings)
        
        # Get IMDb ID
        movie_link = links_df[links_df['movieId'] == movie_id]
        if not movie_link.empty:
            imdb_id = str(movie_link.iloc[0]['imdbId']).zfill(7)  # Pad with zeros to 7 digits
            imdb_url = f"https://www.imdb.com/title/tt{imdb_id}/"
            st.markdown(f"[View on IMDb]({imdb_url})")
        
        # Try to get credits info
        try:
            credits_df = pd.read_csv('data/credits.csv')
            movie_credits = credits_df[credits_df['movieId'] == movie_id]
            if not movie_credits.empty:
                director = movie_credits.iloc[0]['director']
                cast = movie_credits.iloc[0]['cast'].split('|')[:5]  # Get top 5 cast members
            else:
                director = "View on IMDb for details"
                cast = []
        except:
            director = "View on IMDb for details"
            cast = []
            
        return {
            'rating': round(avg_rating, 1) if not pd.isna(avg_rating) else None,
            'num_ratings': num_ratings,
            'director': director,
            'cast': cast,
            'imdb_id': f"tt{imdb_id}" if 'imdb_id' in locals() else None
        }
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return None

def render_movie_card(movie, index):
    """Render a single movie card with error handling for images"""
    movie_id = str(movie['movieId'])  # Convert to string for data attribute
    title = movie.get('clean_title', movie.get('title', 'Unknown Title'))
    year = int(movie.get('year', 0)) if pd.notna(movie.get('year')) else ''
    genres = movie.get('genres', '').replace('|', ' • ')
    
    # Get poster path - we know it exists because we filtered for it
    poster_path = movie['poster_path']
    
    # Convert local file path to base64 for embedding
    try:
        with open(poster_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            img_src = f"data:image/jpeg;base64,{img_data}"
    except:
        return ""
    
    return f"""
    <div class="movie-card" onclick="selectMovie('{movie_id}')">
        <div class="movie-poster-container">
            <img 
                class="movie-poster" 
                src="{img_src}"
                alt="{title}"
                loading="lazy"
                decoding="async"
            >
            <div class="movie-info">
                <h3 class="movie-title">{title}</h3>
                <div class="movie-meta">
                    {year} • {genres}
                </div>
            </div>
        </div>
    </div>
    """

def show_movie_details(movie_id, movies_df):
    """Show movie details and recommendations"""
    movie = movies_df[movies_df['movieId'] == int(movie_id)].iloc[0]
    
    # Get IMDb ID
    links_df = pd.read_csv('data/links.csv')
    movie_link = links_df[links_df['movieId'] == int(movie_id)]
    if not movie_link.empty:
        imdb_id = str(movie_link.iloc[0]['imdbId']).zfill(7)
        imdb_url = f"https://www.imdb.com/title/tt{imdb_id}/"
    else:
        imdb_id = "Not available"
        imdb_url = None

    # Create two columns - one for the movie grid and one for details
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("""
        <div class="movie-info-sidebar">
            <h3>Movie Information</h3>
        """, unsafe_allow_html=True)
        
        if imdb_url:
            st.markdown(f"<p><strong>IMDb:</strong> <a href='{imdb_url}' target='_blank'>tt{imdb_id}</a></p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p><strong>IMDb:</strong> {imdb_id}</p>", unsafe_allow_html=True)
        
        st.markdown(f"<p><strong>Release Year:</strong> {movie['year']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Genre:</strong> {movie['genres'].replace('|', ' • ')}</p>", unsafe_allow_html=True)
        
        # Get similar movies
        if st.session_state.recommendation_model is not None:
            processed_df, cosine_sim = st.session_state.recommendation_model
            similar_movies = get_similar_movies(movie_id, processed_df, cosine_sim)
            
            if similar_movies:
                st.markdown("<h4>Similar Movies You Might Like</h4>", unsafe_allow_html=True)
                st.markdown('<div class="recommendations">', unsafe_allow_html=True)
                
                for similar in similar_movies:
                    title = similar['title']
                    score = similar['similarity_score']
                    movie_id = similar['movieId']
                    
                    # Create a clickable recommendation item
                    if st.markdown(f"""
                        <div class="recommendation-item" onclick="selectMovie('{movie_id}')">
                            <span class="recommendation-title">{title}</span>
                            <span class="recommendation-score">{score:.0%} match</span>
                        </div>
                    """, unsafe_allow_html=True):
                        st.session_state.selected_movie_id = movie_id
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add a back button
        if st.button("← Back"):
            st.session_state.selected_movie_id = None
            st.rerun()

def search_movies(df, search_query):
    """Search for movies in the dataframe"""
    if not search_query:
        return df
        
    search_query = search_query.lower()
    
    # Search in both original title and clean title
    mask = (
        df['title'].str.lower().str.contains(search_query, na=False, regex=False) |
        df['clean_title'].str.lower().str.contains(search_query, na=False, regex=False)
    )
    
    results = df[mask]
    
    # Debug information
    st.sidebar.write("Search Debug Info:")
    st.sidebar.write(f"Search query: '{search_query}'")
    st.sidebar.write(f"Total movies before search: {len(df)}")
    st.sidebar.write(f"Movies found: {len(results)}")
    if len(results) > 0:
        st.sidebar.write("First 5 matching titles:")
        for title in results['title'].head():
            st.sidebar.write(f"- {title}")
    
    return results

def render_search_results(filtered_movies):
    """Render search results in a grid layout with details"""
    # Add click handler for movie selection
    if 'selected_search_movie' not in st.session_state:
        st.session_state.selected_search_movie = None

    for idx, movie in filtered_movies.iterrows():
        st.markdown('<div class="search-result-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Create a clickable container for the poster
            st.image(
                movie['poster_path'],
                width=200,
                use_container_width=True,
                output_format="auto"
            )
            # Add a click button below the image
            if st.button("Select Movie", key=f"select_{movie['movieId']}", type="primary"):
                st.session_state.selected_search_movie = movie['movieId']
                st.rerun()
        
        with col2:
            # If this movie is selected, show detailed information
            if st.session_state.selected_search_movie == movie['movieId']:
                st.markdown('<div class="movie-details">', unsafe_allow_html=True)
                
                # Movie title and year
                title = movie.get('clean_title', movie.get('title', 'Unknown Title'))
                year = movie.get('year', '')
                st.markdown(f"<h3>{title} ({year})</h3>", unsafe_allow_html=True)
                
                # Get additional movie details
                details = get_movie_details(movie['movieId'])
                if details:
                    # IMDb link
                    if details.get('imdb_id'):
                        imdb_url = f"https://www.imdb.com/title/{details['imdb_id']}/"
                        st.markdown(f"<p><strong>IMDb:</strong> <a href='{imdb_url}' target='_blank'>View on IMDb</a></p>", unsafe_allow_html=True)
                    
                    # Genres
                    genres = movie.get('genres', '').replace('|', ' • ')
                    st.markdown(f"<p><strong>Genres:</strong> {genres}</p>", unsafe_allow_html=True)
                    
                    # Rating
                    if details.get('rating'):
                        st.markdown(f"<p><strong>Rating:</strong> ⭐ {details['rating']}/5 ({details['num_ratings']} ratings)</p>", unsafe_allow_html=True)
                    
                    # Director
                    if details.get('director'):
                        st.markdown(f"<p><strong>Director:</strong> {details['director']}</p>", unsafe_allow_html=True)
                    
                    # Cast
                    if details.get('cast'):
                        st.markdown("<p><strong>Cast:</strong></p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{' • '.join(details['cast'])}</p>", unsafe_allow_html=True)
                    
                    # Add a back button
                    if st.button("← Back to Search Results", key=f"back_{movie['movieId']}", type="secondary"):
                        st.session_state.selected_search_movie = None
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Show basic information for unselected movies
                title = movie.get('clean_title', movie.get('title', 'Unknown Title'))
                year = movie.get('year', '')
                st.markdown(f"<h3>{title} ({year})</h3>", unsafe_allow_html=True)
                
                # Genres
                genres = movie.get('genres', '').replace('|', ' • ')
                st.markdown(f"<p><strong>Genres:</strong> {genres}</p>", unsafe_allow_html=True)
                
                # Add a "View Details" button
                if st.button("View Details", key=f"view_{movie['movieId']}", type="primary"):
                    st.session_state.selected_search_movie = movie['movieId']
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Initialize session state variables
    if 'movie_count' not in st.session_state:
        st.session_state.movie_count = 1000
    if 'movies_per_page' not in st.session_state:
        st.session_state.movies_per_page = 20
    if 'selected_movie_id' not in st.session_state:
        st.session_state.selected_movie_id = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'is_searching' not in st.session_state:
        st.session_state.is_searching = False
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All"
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    if 'recommendation_model' not in st.session_state:
        st.session_state.recommendation_model = None

    # Load movies
    movies_df = load_movies(max_movies=st.session_state.movie_count)
    if movies_df.empty:
        st.error("No movies available")
        return

    # Build recommendation model if not already built
    if st.session_state.recommendation_model is None:
        with st.spinner('Building recommendation model...'):
            processed_df, cosine_sim = build_content_based_model(movies_df)
            st.session_state.recommendation_model = (processed_df, cosine_sim)

    # Show movie details in sidebar if a movie is selected
    if st.session_state.selected_movie_id:
        show_movie_details(st.session_state.selected_movie_id, movies_df)

    # Add JavaScript for movie selection
    st.markdown("""
    <script>
    function selectMovie(movieId) {
        // Use Streamlit's setComponentValue to update the selected movie
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: movieId
        }, '*');
    }
    </script>
    """, unsafe_allow_html=True)

    # Custom CSS for top navigation bar
    st.markdown("""
    <style>
    .top-nav {
        position: fixed;
        top: 0;
        right: 0;
        left: 0;
        height: 68px;
        background-color: rgba(20, 20, 20, 0.95);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 4%;
        z-index: 1000;
        border-bottom: 1px solid #333;
    }
    
    .nav-logo {
        color: #e50914;
        font-size: 24px;
        font-weight: 600;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-search {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .search-input {
        background-color: #141414;
        border: 1px solid #333;
        color: #fff;
        padding: 8px 12px;
        border-radius: 4px;
        width: 240px;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #e50914;
        width: 300px;
    }
    
    .search-button {
        background-color: #e50914;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s ease;
    }
    
    .search-button:hover {
        background-color: #f40612;
    }
    
    .main-content {
        margin-top: 88px;
        padding: 0 4%;
    }
    </style>
    
    <div class="top-nav">
        <a href="/" class="nav-logo">
            <span>🎬</span>
            <span>MovieFlix</span>
        </a>
        <div class="nav-search">
            <input type="text" id="search-input" class="search-input" placeholder="Search movies...">
            <button onclick="handleSearch()" class="search-button">Search</button>
        </div>
    </div>
    
    <script>
    function handleSearch() {
        const searchInput = document.getElementById('search-input');
        const searchValue = searchInput.value;
        if (searchValue) {
            // Update Streamlit state
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: searchValue
            }, '*');
        }
    }
    
    // Add event listener for Enter key
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Add search container
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("", placeholder="Search movies...", key="search_input", label_visibility="collapsed")
    with col2:
        if st.button("Search", type="primary"):
            st.session_state.search_query = search_query
            st.session_state.page_number = 1
            st.session_state.is_searching = True
    with col3:
        if st.button("Clear", type="secondary"):
            st.session_state.search_query = ""
            st.session_state.is_searching = False
            st.session_state.page_number = 1
            st.session_state.selected_category = "All"

    # Add genre filter buttons
    categories = ["All"] + get_categories(movies_df)
    st.markdown('<div class="category-buttons">', unsafe_allow_html=True)
    
    # Create columns for the category buttons
    num_cols = 8  # Number of buttons per row
    cols = st.columns(num_cols)
    
    # Distribute category buttons across columns
    for i, category in enumerate(categories):
        with cols[i % num_cols]:
            if st.button(
                category,
                key=f"cat_{category}",
                type="secondary" if category != st.session_state.selected_category else "primary",
                use_container_width=True
            ):
                st.session_state.selected_category = category
                st.session_state.page_number = 1
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Show movie grid or search results
    if st.session_state.search_query:
        filtered_movies = search_movies(movies_df, st.session_state.search_query)
        if len(filtered_movies) > 0:
            st.markdown(f'<div class="search-results">Found {len(filtered_movies)} movies matching "{st.session_state.search_query}"</div>', 
                       unsafe_allow_html=True)
            render_search_results(filtered_movies)
        else:
            st.warning(f'No movies found matching "{st.session_state.search_query}"')
    else:
        filtered_movies = filter_movies_by_category(movies_df, st.session_state.selected_category)
        st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
        for idx, movie in get_page_of_movies(filtered_movies, st.session_state.page_number, st.session_state.movies_per_page).iterrows():
            st.markdown(render_movie_card(movie, idx), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Load more buttons
        st.markdown('<div class="load-more-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        # Show load more movies button if we haven't loaded all available movies
        with col1:
            if st.session_state.movie_count < 9959:  # Total number of movies in dataset
                if st.button("Load More Movies", key="load_more_movies", use_container_width=True):
                    st.session_state.movie_count += 1000
                    st.rerun()
        
        # Show load more pages button if there are more pages in current set
        with col2:
            total_pages = math.ceil(len(filtered_movies) / st.session_state.movies_per_page)
            remaining = len(filtered_movies) - st.session_state.page_number * st.session_state.movies_per_page
            if st.session_state.page_number < total_pages:
                if st.button(
                    f"Next Page ({remaining} more)",
                    key="load_more_pages",
                    use_container_width=True
                ):
                    st.session_state.page_number += 1
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Add modal styles to the existing CSS
    st.markdown("""
    <style>
    /* ... existing styles ... */

    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(5px);
    }

    .modal-content {
        background-color: #1f1f1f;
        margin: 5% auto;
        padding: 2rem;
        border: 1px solid #333;
        width: 80%;
        max-width: 900px;
        border-radius: 8px;
        position: relative;
    }

    .modal-grid {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 2rem;
        align-items: start;
    }

    .modal-poster img {
        width: 100%;
        border-radius: 4px;
    }

    .modal-details {
        color: #e5e5e5;
    }

    .modal-details h2 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 2rem;
        color: #fff;
    }

    .modal-details p {
        margin: 0.5rem 0;
        font-size: 1rem;
        color: #ccc;
    }

    .close {
        position: absolute;
        right: 1rem;
        top: 1rem;
        color: #666;
        font-size: 2rem;
        font-weight: bold;
        cursor: pointer;
        transition: color 0.2s ease;
    }

    .close:hover {
        color: #fff;
    }

    .imdb-link {
        display: inline-block;
        background-color: #f5c518;
        color: #000;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 4px;
        font-weight: 600;
        margin-top: 1rem;
        transition: background-color 0.2s ease;
    }

    .imdb-link:hover {
        background-color: #ffdb4d;
    }
    </style>

    <script>
    function toggleModal(modalId) {
        var modal = document.getElementById(modalId);
        if (modal.style.display === "block") {
            modal.style.display = "none";
            document.body.style.overflow = "auto";
        } else {
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
        }
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
            document.body.style.overflow = "auto";
        }
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
