import pandas as pd
import os

class MovieData:
    def __init__(self, data_path='ml-100k'):
        self.data_path = data_path
        self.movies_df = None
        self.ratings_df = None
        self.load_data()
    
    def load_data(self):
        """Load MovieLens data - auto-detect format"""
        print(f"Loading MovieLens dataset from {self.data_path}...")
        
        # Check if it's 100k or larger dataset
        if os.path.exists(os.path.join(self.data_path, 'u.item')):
            # ml-100k format
            self.load_data_100k()
        elif os.path.exists(os.path.join(self.data_path, 'movies.csv')):
            # ml-32m format
            self.load_data_32m()
        else:
            raise FileNotFoundError(f"No valid MovieLens dataset found in {self.data_path}")
    
    def load_data_100k(self):
        """Load MovieLens 100K data"""
        print("Loading ml-100k dataset...")
        
        # Load movies
        movies_file = os.path.join(self.data_path, 'u.item')
        
        # Column names for u.item
        movie_cols = ['movie_id', 'title', 'release_date', 'video_release_date',
                      'imdb_url', 'unknown', 'Action', 'Adventure', 'Animation',
                      'Children', 'Comedy', 'Crime', 'Documentary', 'Drama',
                      'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
                      'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
        
        self.movies_df = pd.read_csv(
            movies_file,
            sep='|',
            encoding='latin-1',
            names=movie_cols,
            index_col='movie_id'
        )
        
        # Clean up title
        self.movies_df['title'] = self.movies_df['title'].str.strip()
        
        # Create a genre string for each movie
        genre_cols = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                     'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
                     'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                     'Thriller', 'War', 'Western']
        
        self.movies_df['genres'] = self.movies_df[genre_cols].apply(
            lambda row: ', '.join([col for col, val in row.items() if val == 1]),
            axis=1
        )
        
        # Load ratings
        ratings_file = os.path.join(self.data_path, 'u.data')
        self.ratings_df = pd.read_csv(
            ratings_file,
            sep='\t',
            names=['user_id', 'movie_id', 'rating', 'timestamp']
        )
        
        print(f"✅ Loaded {len(self.movies_df)} movies")
        print(f"✅ Loaded {len(self.ratings_df)} ratings")
    
    def load_data_32m(self):
        """Load MovieLens 32M data"""
        print("Loading ml-32m dataset (this may take a minute)...")
        
        # Load movies
        movies_file = os.path.join(self.data_path, 'movies.csv')
        self.movies_df = pd.read_csv(movies_file)
        
        # Set movie_id as index
        self.movies_df.set_index('movieId', inplace=True)
        
        # Parse genres (they're in format "Action|Adventure|Sci-Fi")
        # Create binary columns for each genre
        all_genres = set()
        for genres_str in self.movies_df['genres']:
            if pd.notna(genres_str) and genres_str != '(no genres listed)':
                for genre in genres_str.split('|'):
                    all_genres.add(genre)
        
        # Create binary columns for genres
        for genre in all_genres:
            self.movies_df[genre] = self.movies_df['genres'].apply(
                lambda x: 1 if pd.notna(x) and genre in x else 0
            )
        
        # Load ratings
        ratings_file = os.path.join(self.data_path, 'ratings.csv')
        print("Loading ratings (32M ratings - this will take 1-2 minutes)...")
        self.ratings_df = pd.read_csv(ratings_file)
        
        # Rename columns to match our existing code
        self.ratings_df.rename(columns={
            'userId': 'user_id',
            'movieId': 'movie_id',
            'timestamp': 'timestamp'
        }, inplace=True)
        
        print(f"✅ Loaded {len(self.movies_df)} movies")
        print(f"✅ Loaded {len(self.ratings_df)} ratings")
    
    def get_movie_by_id(self, movie_id):
        """Get movie details by ID"""
        if movie_id in self.movies_df.index:
            return self.movies_df.loc[movie_id]
        return None
    
    def get_all_movies(self):
        """Get all movies"""
        return self.movies_df
    
    def search_movies(self, query):
        """Search movies by title"""
        query = query.lower()
        matches = self.movies_df[
            self.movies_df['title'].str.lower().str.contains(query, na=False)
        ]
        return matches
    
    def get_movies_by_genre(self, genre):
        """Get movies by genre"""
        if genre in self.movies_df.columns:
            return self.movies_df[self.movies_df[genre] == 1]
        return pd.DataFrame()
    
    def get_random_movies(self, n=20):
        """Get random movies"""
        return self.movies_df.sample(n=min(n, len(self.movies_df)))


# Test the movie data loader
if __name__ == "__main__":
    movie_data = MovieData()
    
    # Test getting a movie
    movie = movie_data.get_movie_by_id(1)
    if movie is not None:
        print(f"\nMovie #1: {movie['title']}")
        print(f"Genres: {movie['genres']}")
    
    # Test search
    results = movie_data.search_movies("Star Wars")
    print(f"\nSearch results for 'Star Wars': {len(results)} movies found")
    if len(results) > 0:
        print(results[['title', 'genres']].head())