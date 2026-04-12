import streamlit as st
import pickle
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for attractive styling
st.markdown("""
    <style>
    /* Navigation Bar */
    .nav-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        height: 200px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .nav-bar h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
    }
    
    /* Movie Cards */
    .movie-card {
        transition: transform 0.3s ease;
        cursor: pointer;
    }
    
    .movie-card:hover {
        transform: scale(1.05);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Search Box */
    .stSelectbox {
        border-radius: 10px;
    }
    
    /* Section Headers */
    h2, h3 {
        color: #667eea;
        font-weight: 700;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# TMDB API configuration
API_KEY = os.getenv('TMDB_API_KEY')

@st.cache_data
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=credits"
        response = requests.get(url)
        data = response.json()
        
        # Get poster
        poster_path = data.get('poster_path')
        poster = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
        
        # Get overview
        overview = data.get('overview', 'No overview available.')
        
        # Get genres
        genres = [genre['name'] for genre in data.get('genres', [])]
        
        # Get cast (top 5)
        credits = data.get('credits', {})
        cast_list = credits.get('cast', [])
        cast = [actor['name'] for actor in cast_list[:5]]
        
        # Get director
        crew_list = credits.get('crew', [])
        director = next((person['name'] for person in crew_list if person['job'] == 'Director'), 'Unknown')
        
        return {
            'poster': poster,
            'overview': overview,
            'genres': genres,
            'cast': cast,
            'director': director
        }
    except:
        return {
            'poster': "https://via.placeholder.com/500x750?text=No+Poster",
            'overview': 'No overview available.',
            'genres': [],
            'cast': [],
            'director': 'Unknown'
        }

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        
        recommended_movies = []
        recommended_posters = []
        
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            movie_details = fetch_movie_details(movie_id)
            recommended_posters.append(movie_details['poster'])
        
        return recommended_movies, recommended_posters
    except:
        return [], []

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None

# Navigation Bar with background
st.markdown("""
    <div class="nav-bar" style="
        background: linear-gradient(rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9)), 
                    url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200') center/cover;
        background-blend-mode: overlay;
    ">
        <h1>🎬 CineMatch</h1>
        <p style="color: white; margin: 0; font-size: 1.1rem;">Discover Your Next Favorite Movie</p>
    </div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3,  = st.columns([1, 1, 1])
with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()
with col2:
    if st.button("🔍 Find-Movies", use_container_width=True):
        st.session_state.page = 'search'
        st.rerun()
with col3:
    if st.button("ℹ️ About", use_container_width=True):
        st.session_state.page = 'about'
        st.rerun()

st.markdown("---")

# HOME PAGE
if st.session_state.page == 'home':
    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Welcome to CineMatch</h2>
            <p style="font-size: 1.2rem; color: #666;">Your personal movie recommendation engine powered by AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Popular Movies Section
    st.markdown("### 🔥 Trending Movies")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get top 20 movies
    top_movies = movies.head(20)
    
    # Display in grid (5 columns x 4 rows)
    cols_per_row = 5
    for i in range(0, 20, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(top_movies):
                movie_data = top_movies.iloc[idx]
                with cols[j]:
                    movie_details = fetch_movie_details(movie_data.movie_id)
                    st.image(movie_details['poster'], use_container_width=True)
                    st.markdown(f"<p style='text-align: center; font-weight: 600;'>{movie_data.title}</p>", unsafe_allow_html=True)
                    if st.button("View details", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_movie = movie_data.title
                        st.session_state.page = 'recommendations'
                        st.rerun()

# SEARCH/RECOMMENDATIONS PAGE
elif st.session_state.page == 'search':
    st.markdown("### 🔍 Find Similar Movies")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_movie = st.selectbox(
            "Search for a movie:",
            movies['title'].values,
            index=None,
            placeholder="Type or select a movie name..."
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search", key="search_button", use_container_width=True):
            if selected_movie:
                st.session_state.selected_movie = selected_movie
                st.session_state.page = 'recommendations'
                st.rerun()
            else:
                st.warning("Please select a movie first!")
    
    # Show all movies in a grid for browsing
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📚 Browse All Movies")
    
    # Pagination
    movies_per_page = 20
    total_pages = len(movies) // movies_per_page + (1 if len(movies) % movies_per_page > 0 else 0)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center;'>Page {st.session_state.current_page + 1} of {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", disabled=st.session_state.current_page >= total_pages - 1):
            st.session_state.current_page += 1
            st.rerun()
    
    start_idx = st.session_state.current_page * movies_per_page
    end_idx = min(start_idx + movies_per_page, len(movies))
    page_movies = movies.iloc[start_idx:end_idx]
    
    cols_per_row = 5
    for i in range(0, len(page_movies), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(page_movies):
                movie_data = page_movies.iloc[idx]
                with cols[j]:
                    movie_details = fetch_movie_details(movie_data.movie_id)
                    st.image(movie_details['poster'], use_container_width=True)
                    st.markdown(f"<p style='text-align: center; font-weight: 600;'>{movie_data.title}</p>", unsafe_allow_html=True)
                    if st.button("Select", key=f"browse_{start_idx + idx}", use_container_width=True):
                        st.session_state.selected_movie = movie_data.title
                        st.session_state.page = 'recommendations'
                        st.rerun()

# RECOMMENDATIONS PAGE
elif st.session_state.page == 'recommendations':
    if st.session_state.selected_movie:
        # Back button
        if st.button("⬅️ Back to Search"):
            st.session_state.page = 'search'
            st.rerun()
        
        st.markdown(f"### 🎬 Movies Similar to '{st.session_state.selected_movie}'")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show selected movie with details
        st.markdown("#### Selected Movie:")
        try:
            selected_movie_data = movies[movies['title'] == st.session_state.selected_movie].iloc[0]
            movie_details = fetch_movie_details(selected_movie_data.movie_id)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie_details['poster'], use_container_width=True)
            with col2:
                st.markdown(f"<h2 style='color: #667eea;'>{st.session_state.selected_movie}</h2>", unsafe_allow_html=True)
                
                st.markdown(f"**Director:** {movie_details['director']}")
                
                if movie_details['genres']:
                    st.markdown(f"**Genres:** {', '.join(movie_details['genres'])}")
                
                if movie_details['cast']:
                    st.markdown(f"**Cast:** {', '.join(movie_details['cast'])}")
                
                st.markdown("**Overview:**")
                st.write(movie_details['overview'])
        except:
            pass
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("#### 🎯 Recommended For You:")
        
        # Get recommendations
        names, posters = recommend(st.session_state.selected_movie)
        
        if names:
            # Display in 2 rows of 5 movies each
            for row in range(2):
                cols = st.columns(5)
                for idx, col in enumerate(cols):
                    movie_idx = row * 5 + idx
                    if movie_idx < len(names):
                        with col:
                            st.image(posters[movie_idx], use_container_width=True)
                            st.markdown(f"<p style='text-align: center; font-weight: 600; font-size: 1rem;'>{names[movie_idx]}</p>", unsafe_allow_html=True)
                            if st.button("View Details", key=f"rec_{movie_idx}", use_container_width=True):
                                st.session_state.selected_movie = names[movie_idx]
                                st.rerun()
        else:
            st.error("Could not find recommendations for this movie.")
    else:
        st.warning("No movie selected. Please go to Search page.")
        if st.button("Go to Search"):
            st.session_state.page = 'search'
            st.rerun()

# ABOUT PAGE
elif st.session_state.page == 'about':
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>About CineMatch</h2>
            <p style="font-size: 1.1rem; color: #666; max-width: 800px; margin: 2rem auto;">
                CineMatch is an intelligent movie recommendation system that uses advanced machine learning 
                algorithms to suggest movies based on your preferences. Our system analyzes movie features 
                including genres, cast, crew, and keywords to find the perfect matches for you.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
                <h3>🎯 Accurate</h3>
                <p>Powered by content-based filtering for precise recommendations</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
                <h3>⚡ Fast</h3>
                <p>Get instant recommendations with our optimized algorithm</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
                <h3>📚 Vast Library</h3>
                <p>Access thousands of movies from our extensive database</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666; border-top: 1px solid #eee; margin-top: 3rem;">
        <p>Made with ❤️ using Streamlit | © 2024 CineMatch</p>
    </div>
""", unsafe_allow_html=True)
