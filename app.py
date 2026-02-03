import streamlit as st
import pandas as pd
from database import Database
from movie_data import MovieData
from recommender import MovieRecommender
from tmdb_helper import TMDbHelper

# Page configuration
st.set_page_config(
    page_title="MovieMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for elite dark theme
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e94560 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    /* Subheaders */
    .stMarkdown h3 {
        color: #bb86fc !important;
    }
    
    /* Text */
    p, span, label {
        color: #e0e0e0 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #e94560 0%, #533483 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff6b88 0%, #6b4fb8 100%);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.5);
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border: 2px solid #533483;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #e94560;
        box-shadow: 0 0 10px rgba(233, 69, 96, 0.3);
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border: 2px solid #533483;
        border-radius: 8px;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #533483;
    }
    
    .stSlider > div > div > div > div {
        background-color: #e94560;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #bb86fc !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #1a1a2e;
        border-left: 4px solid #bb86fc;
        color: #e0e0e0;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #1a3a1a;
        border-left: 4px solid #4caf50;
        color: #81c784;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #3a2a1a;
        border-left: 4px solid #ff9800;
        color: #ffb74d;
    }
    
    /* Error messages */
    .stError {
        background-color: #3a1a1a;
        border-left: 4px solid #f44336;
        color: #e57373;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 2px solid #533483;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560 0%, #533483 100%);
        color: white;
        border-color: #e94560;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border: 1px solid #533483;
        border-radius: 8px;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #2a2a3e;
        border-color: #e94560;
    }
    
    /* Divider */
    hr {
        border-color: #533483;
        opacity: 0.3;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #e94560 !important;
    }
    
    /* Image containers */
    [data-testid="stImage"] {
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease;
    }
    
    [data-testid="stImage"]:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 32px rgba(233, 69, 96, 0.4);
    }
    
    /* Form containers */
    [data-testid="stForm"] {
        background-color: #1a1a2e;
        border: 2px solid #533483;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Caption text */
    .stCaption {
        color: #bb86fc !important;
    }
    
    /* Column borders */
    [data-testid="column"] {
        background-color: rgba(26, 26, 46, 0.3);
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize database, movie data, and recommender (cached)"""
    db = Database()
    movie_data = MovieData()
    recommender = MovieRecommender()
    tmdb = TMDbHelper(api_key="a9162435d8107e2318b23f7b0ec61f41")
    return db, movie_data, recommender, tmdb

db, movie_data, recommender, tmdb = init_components()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'rating_submitted' not in st.session_state:
    st.session_state.rating_submitted = False
if 'browse_movies_cache' not in st.session_state:
    st.session_state.browse_movies_cache = None
if 'browse_search_query' not in st.session_state:
    st.session_state.browse_search_query = ""
if 'browse_genre_filter' not in st.session_state:
    st.session_state.browse_genre_filter = "All"
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

# Helper functions
def login_user(username, password):
    """Authenticate user"""
    success, user_id, username = db.authenticate_user(username, password)
    if success:
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.show_welcome = True
        st.session_state.page = 'welcome'
        return True
    return False

def signup_user(username, password):
    """Create new user"""
    success, user_id = db.create_user(username, password)
    if success:
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.show_welcome = True
        st.session_state.page = 'welcome'
        return True
    return False

def logout_user():
    """Logout user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.page = 'login'
    st.session_state.show_welcome = True

def rate_movie(movie_id, rating):
    """Add a rating and check for new badges"""
    db.add_rating(st.session_state.user_id, movie_id, rating)
    badges = recommender.check_and_award_badges(st.session_state.user_id)
    return badges

def display_movie_card(movie_id, movie, col, key_prefix=""):
    """Display a movie card with poster"""
    with col:
        # Get poster
        poster_url = tmdb.get_poster_url(movie['title'])
        
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            # Elite placeholder if no poster found
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #e94560 0%, #533483 100%); 
                            padding: 100px 20px; text-align: center; border-radius: 12px; 
                            color: white; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
                    <h3 style="color: white !important; margin: 0;">{movie['title']}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.subheader(movie['title'][:40] + ('...' if len(movie['title']) > 40 else ''))
        st.caption(f"🎭 {movie['genres']}")
        
        # Check if user has already rated this movie
        existing_rating = db.get_user_rating_for_movie(st.session_state.user_id, movie_id)
        
        if existing_rating:
            st.info(f"⭐ Your rating: {existing_rating}/5")
        
        # Rating selector with half-star support (0.5 - 5.0)
        rating = st.select_slider(
            f"Rate this movie",
            options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            value=float(existing_rating) if existing_rating else 3.0,
            key=f"{key_prefix}_rating_{movie_id}",
            label_visibility="collapsed"
        )
        
        button_key = f"{key_prefix}_btn_{movie_id}"
        if st.button("⭐ Submit Rating", key=button_key, use_container_width=True):
            badges = rate_movie(movie_id, rating)
            if badges:
                st.success(f"🎉 New badge(s): {', '.join(badges)}")
            else:
                st.success(f"Rated {rating}⭐!")
            st.rerun()

# Page: Login/Signup
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Elite header
        st.markdown("""
            <div style="text-align: center; padding: 40px 0;">
                <h1 style="font-size: 3.5rem; background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                           margin-bottom: 10px;">🎬 MovieMatch</h1>
                <p style="font-size: 1.2rem; color: #bb86fc; letter-spacing: 2px;">
                    YOUR ELITE MOVIE COMPANION
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
                if submit:
                    if username and password:
                        if login_user(username, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
        
        with tab2:
            st.subheader("Join MovieMatch Elite")
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username", placeholder="Pick a unique username")
                new_password = st.text_input("Choose Password", type="password", placeholder="Min 3 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                
                if submit:
                    if new_username and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords don't match!")
                        elif len(new_password) < 3:
                            st.error("Password must be at least 3 characters")
                        else:
                            if signup_user(new_username, new_password):
                                st.success("Account created successfully!")
                                st.rerun()
                            else:
                                st.error("Username already exists")
                    else:
                        st.warning("Please fill in all fields")

# Page: Welcome/Onboarding
def show_welcome_page():
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome to MovieMatch, {st.session_state.username}! 🎉
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # What is MovieMatch
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                        padding: 40px; border-radius: 12px; border: 2px solid #533483; 
                        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6); text-align: center;">
                <h2 style="color: #e94560 !important; margin-bottom: 20px;">🎬 What is MovieMatch?</h2>
                <p style="color: #e0e0e0 !important; font-size: 1.1rem; line-height: 1.8;">
                    MovieMatch is your personal AI-powered movie recommendation platform with over 86,000 movies! 
                    Rate movies, earn badges, and discover films perfectly matched to your taste!
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How it works
    st.markdown("""
        <h2 style="text-align: center; background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🚀 How It Works
        </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #e94560 0%, #533483 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; color: white;
                        box-shadow: 0 8px 24px rgba(233, 69, 96, 0.4); height: 100%;">
                <h1 style="color: white !important; font-size: 3rem; margin-bottom: 15px;">1️⃣</h1>
                <h3 style="color: white !important; margin-bottom: 15px;">Rate Movies</h3>
                <p style="color: #f0f0f0 !important; font-size: 1rem;">
                    Browse 86,000+ movies and rate them with half-star precision. 
                    The more you rate, the better your recommendations!
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #533483 0%, #bb86fc 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; color: white;
                        box-shadow: 0 8px 24px rgba(187, 134, 252, 0.4); height: 100%;">
                <h1 style="color: white !important; font-size: 3rem; margin-bottom: 15px;">2️⃣</h1>
                <h3 style="color: white !important; margin-bottom: 15px;">Earn Badges</h3>
                <p style="color: #f0f0f0 !important; font-size: 1rem;">
                    Unlock achievements as you rate! Become a Movie Buff, Cinephile, 
                    or even earn genre-specific badges.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #e94560 0%, #533483 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; color: white;
                        box-shadow: 0 8px 24px rgba(233, 69, 96, 0.4); height: 100%;">
                <h1 style="color: white !important; font-size: 3rem; margin-bottom: 15px;">3️⃣</h1>
                <h3 style="color: white !important; margin-bottom: 15px;">Get Recommendations</h3>
                <p style="color: #f0f0f0 !important; font-size: 1rem;">
                    Our AI analyzes your taste and suggests movies you'll love. 
                    Find your next favorite film!
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Badges you can earn
    st.markdown("""
        <h2 style="text-align: center; background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🏆 Badges You Can Earn
        </h2>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    badge_col1, badge_col2, badge_col3, badge_col4 = st.columns(4)
    
    badges_info = [
        ("🎬 First Steps", "Rate your first movie"),
        ("🍿 Movie Buff", "Rate 10 movies"),
        ("🎭 Cinephile", "Rate 25 movies"),
        ("⭐ Film Critic", "Rate 50 movies"),
        ("💫 Genre Fan", "80%+ ratings in one genre"),
        ("🔍 Tough Critic", "Average rating < 3.0"),
        ("😊 Optimist", "Average rating > 4.0"),
        ("🎯 And More!", "Keep rating to discover")
    ]
    
    for idx, (badge_name, badge_desc) in enumerate(badges_info):
        with [badge_col1, badge_col2, badge_col3, badge_col4][idx % 4]:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; 
                            border: 2px solid #533483; margin-bottom: 15px;">
                    <h3 style="color: #e94560 !important; font-size: 1.5rem;">{badge_name}</h3>
                    <p style="color: #bb86fc !important; font-size: 0.9rem;">{badge_desc}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Start button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎬 Start Rating Movies!", type="primary", use_container_width=True):
            st.session_state.page = 'browse'
            st.session_state.show_welcome = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Skip button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Skip Introduction", use_container_width=True):
            st.session_state.page = 'browse'
            st.session_state.show_welcome = False
            st.rerun()

# Page: Browse Movies
def show_browse_page():
    st.markdown("""
        <h1 style="background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🎥 Discover Movies
        </h1>
    """, unsafe_allow_html=True)
    
    # Search and filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search movies by title", value=st.session_state.browse_search_query, placeholder="Enter movie title...")
    with col2:
        genre_options = ["All", 'Action', 'Adventure', 'Animation', 'Children', 
                        'Comedy', 'Crime', 'Documentary', 'Drama', 
                        'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
                        'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
                        'War', 'Western', 'IMAX']
        
        try:
            current_index = genre_options.index(st.session_state.browse_genre_filter)
        except:
            current_index = 0
        
        genre_filter = st.selectbox("Filter by genre", genre_options, index=current_index)
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.browse_movies_cache = None
            st.rerun()
    
    # Check if filters changed
    filters_changed = (search_query != st.session_state.browse_search_query or 
                      genre_filter != st.session_state.browse_genre_filter)
    
    if filters_changed:
        st.session_state.browse_search_query = search_query
        st.session_state.browse_genre_filter = genre_filter
        st.session_state.browse_movies_cache = None
    
    # Get movies (use cache if available)
    if st.session_state.browse_movies_cache is None:
        if search_query:
            movies = movie_data.search_movies(search_query)
        elif genre_filter != "All":
            movies = movie_data.get_movies_by_genre(genre_filter)
        else:
            movies = movie_data.get_random_movies(30)
        
        # Cache the movies
        st.session_state.browse_movies_cache = movies
    else:
        movies = st.session_state.browse_movies_cache
    
    if len(movies) == 0:
        st.info("No movies found. Try a different search or filter.")
        return
    
    st.markdown(f"<p style='color: #bb86fc; font-size: 1.1rem;'>Showing {len(movies)} movies</p>", unsafe_allow_html=True)
    st.divider()
    
    # Display movies in a grid
    cols_per_row = 4
    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(movies):
                movie_id = movies.index[i + j]
                movie = movies.iloc[i + j]
                display_movie_card(movie_id, movie, col, key_prefix="browse")

# Page: My Profile
def show_profile_page():
    st.markdown(f"""
        <h1 style="background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            👤 {st.session_state.username}'s Profile
        </h1>
    """, unsafe_allow_html=True)
    
    # Get user's ratings and badges
    user_ratings = db.get_user_ratings(st.session_state.user_id)
    user_badges = db.get_user_badges(st.session_state.user_id)
    
    # Stats with elite styling
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; 
                        border: 2px solid #533483; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
                <p style="color: #bb86fc; font-size: 0.9rem; margin-bottom: 10px;">MOVIES RATED</p>
                <h2 style="color: #e94560; font-size: 3rem; margin: 0;">{}</h2>
            </div>
        """.format(len(user_ratings)), unsafe_allow_html=True)
    
    with col2:
        avg_rating = user_ratings['rating'].mean() if len(user_ratings) > 0 else 0
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; 
                        border: 2px solid #533483; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
                <p style="color: #bb86fc; font-size: 0.9rem; margin-bottom: 10px;">AVERAGE RATING</p>
                <h2 style="color: #e94560; font-size: 3rem; margin: 0;">{:.1f}⭐</h2>
            </div>
        """.format(avg_rating), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; 
                        border: 2px solid #533483; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
                <p style="color: #bb86fc; font-size: 0.9rem; margin-bottom: 10px;">BADGES EARNED</p>
                <h2 style="color: #e94560; font-size: 3rem; margin: 0;">{}</h2>
            </div>
        """.format(len(user_badges)), unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Badges
    st.subheader("🏆 Your Achievements")
    if len(user_badges) > 0:
        badge_cols = st.columns(min(4, len(user_badges)))
        for idx, (_, badge) in enumerate(user_badges.iterrows()):
            with badge_cols[idx % len(badge_cols)]:
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #e94560 0%, #533483 100%); 
                                padding: 25px; border-radius: 12px; text-align: center; color: white; 
                                margin-bottom: 15px; box-shadow: 0 8px 24px rgba(233, 69, 96, 0.4);
                                transition: transform 0.3s ease;">
                        <h2 style="color: white !important; font-size: 2.5rem; margin-bottom: 10px;">{badge['badge_name']}</h2>
                        <p style="color: #f0f0f0 !important; font-size: 0.95rem;">{badge['badge_description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("🎯 No badges yet. Rate more movies to unlock achievements!")
    
    st.divider()
    
    # Recently rated movies
    st.subheader("📊 Recently Rated Movies")
    if len(user_ratings) > 0:
        recent = user_ratings.head(12)
        all_movies = movie_data.get_all_movies()
        
        # Filter out invalid movie IDs first
        valid_ratings = []
        for idx, rating_row in recent.iterrows():
            movie_id = rating_row['movie_id']
            if movie_id in all_movies.index:
                valid_ratings.append(rating_row)
        
        if len(valid_ratings) == 0:
            st.info("No valid rated movies to display yet.")
        else:
            cols_per_row = 4
            for i in range(0, len(valid_ratings), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(valid_ratings):
                        rating_row = valid_ratings[i + j]
                        movie_id = rating_row['movie_id']
                        
                        try:
                            movie = all_movies.loc[movie_id]
                            
                            with col:
                                poster_url = tmdb.get_poster_url(movie['title'])
                                if poster_url:
                                    st.image(poster_url, use_container_width=True)
                                
                                st.markdown(f"<p style='color: #e0e0e0; font-weight: 600;'>{movie['title'][:30]}</p>", unsafe_allow_html=True)
                                
                                # Display rating with half-stars
                                full_stars = int(rating_row['rating'])
                                half_star = 1 if (rating_row['rating'] - full_stars) >= 0.5 else 0
                                star_display = '⭐' * full_stars + ('½' if half_star else '')
                                st.markdown(f"<p style='color: #bb86fc;'>{star_display} ({rating_row['rating']})</p>", unsafe_allow_html=True)
                        except Exception as e:
                            # Skip this movie
                            continue
    else:
        st.info("You haven't rated any movies yet!")

# Page: Recommendations
def show_recommendations_page():
    st.markdown("""
        <h1 style="background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🎯 Personalized For You
        </h1>
    """, unsafe_allow_html=True)
    
    user_ratings = db.get_user_ratings(st.session_state.user_id)
    
    if len(user_ratings) < 3:
        st.warning("⚠️ Please rate at least 3 movies to unlock personalized recommendations!")
        st.info("💡 Head to 'Browse Movies' to start rating!")
        return
    
    with st.spinner("🎬 AI is analyzing your taste..."):
        recommendations = recommender.get_recommendations_for_user(st.session_state.user_id, n=12)
    
    st.success(f"✨ Found {len(recommendations)} perfect matches for you!")
    st.divider()
    
    # Display recommendations
    cols_per_row = 4
    for i in range(0, len(recommendations), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(recommendations):
                rec = recommendations[i + j]
                
                with col:
                    # Get poster
                    poster_url = tmdb.get_poster_url(rec['title'])
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    
                    st.subheader(rec['title'][:40])
                    st.caption(f"🎭 {rec['genres']}")
                    st.markdown(f"<p style='color: #bb86fc; font-weight: 600;'>AI Predicts: {rec['predicted_rating']:.1f}⭐</p>", unsafe_allow_html=True)
                    
                    # Quick rate option with half-stars
                    rating = st.select_slider(
                        "Rate it",
                        options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                        value=4.0,
                        key=f"rec_rating_{rec['movie_id']}",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("⭐ Rate", key=f"rec_btn_{rec['movie_id']}", use_container_width=True):
                        badges = rate_movie(rec['movie_id'], rating)
                        if badges:
                            st.success(f"🎉 New badge(s): {', '.join(badges)}")
                        else:
                            st.success(f"Rated {rating}⭐!")
                        st.rerun()

# Page: Find Similar Users
def show_similar_users_page():
    st.markdown("""
        <h1 style="background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🤝 Find Your Movie Soulmates
        </h1>
    """, unsafe_allow_html=True)
    
    user_ratings = db.get_user_ratings(st.session_state.user_id)
    
    if len(user_ratings) < 5:
        st.warning("⚠️ Rate at least 5 movies to discover users with similar taste!")
        return
    
    with st.spinner("🔍 Searching for your movie soulmates..."):
        similar_users = recommender.get_similar_users(st.session_state.user_id, top_n=10)
    
    if len(similar_users) == 0:
        st.info("No similar users found yet. Keep rating movies!")
        return
    
    st.success(f"✨ Found {len(similar_users)} users with similar taste!")
    st.divider()
    
    for user in similar_users:
        with st.expander(f"👤 {user['username']} - {user['similarity']}% compatibility", expanded=False):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e94560 0%, #533483 100%); 
                                padding: 20px; border-radius: 12px; text-align: center; color: white;">
                        <h2 style="color: white !important; font-size: 2.5rem; margin: 0;">{user['similarity']}%</h2>
                        <p style="color: #f0f0f0 !important; margin-top: 10px;">Match Score</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.metric("Movies Rated", user['rating_count'])
            
            with col2:
                # Show their recent ratings
                other_user_ratings = db.get_user_ratings(user['user_id'])
                st.markdown("<p style='color: #bb86fc; font-weight: 600; font-size: 1.1rem;'>Their Favorite Movies:</p>", unsafe_allow_html=True)
                
                all_movies = movie_data.get_all_movies()
                top_rated = other_user_ratings.nlargest(5, 'rating')
                
                for _, rating_row in top_rated.iterrows():
                    try:
                        if rating_row['movie_id'] in all_movies.index:
                            movie = all_movies.loc[rating_row['movie_id']]
                            # Handle half-star display
                            full_stars = int(rating_row['rating'])
                            half_star = 1 if (rating_row['rating'] - full_stars) >= 0.5 else 0
                            star_display = '⭐' * full_stars + ('½' if half_star else '')
                            st.markdown(f"<p style='color: #e0e0e0;'>• {movie['title']} ({star_display})</p>", unsafe_allow_html=True)
                    except:
                        continue

# Main app logic
def main():
    if st.session_state.user_id is None:
        show_login_page()
    else:
        # Elite sidebar navigation
        with st.sidebar:
            st.markdown(f"""
                <div style="text-align: center; padding: 20px 0;">
                    <h2 style="background: linear-gradient(135deg, #e94560 0%, #bb86fc 100%); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        Hello, {st.session_state.username}! 👋
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            st.divider()
            
            if st.button("🎥 Browse Movies", use_container_width=True):
                st.session_state.page = 'browse'
                st.rerun()
            if st.button("👤 My Profile", use_container_width=True):
                st.session_state.page = 'profile'
                st.rerun()
            if st.button("🎯 Recommendations", use_container_width=True):
                st.session_state.page = 'recommendations'
                st.rerun()
            if st.button("🤝 Similar Users", use_container_width=True):
                st.session_state.page = 'similar'
                st.rerun()
            
            st.divider()
            
            # Show welcome button if they want to see it again
            if not st.session_state.show_welcome:
                if st.button("ℹ️ View Introduction", use_container_width=True):
                    st.session_state.page = 'welcome'
                    st.rerun()
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        
        # Show selected page
        if st.session_state.page == 'welcome':
            show_welcome_page()
        elif st.session_state.page == 'browse':
            show_browse_page()
        elif st.session_state.page == 'profile':
            show_profile_page()
        elif st.session_state.page == 'recommendations':
            show_recommendations_page()
        elif st.session_state.page == 'similar':
            show_similar_users_page()

if __name__ == "__main__":
    main()