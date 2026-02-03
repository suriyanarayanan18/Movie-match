import pandas as pd
import os

class MovieData:
    def __init__(self, data_path='ml-32m'):
        self.data_path = data_path
        self.movies_df = None
        self.ratings_df = None
        self.load_data()
    
    def load_data(self):
        """Load MovieLens 32M data"""
        print("Loading MovieLens 32M dataset (this may take a minute)...")
        
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
    results = movie_data.search_movies("Avengers")
    print(f"\nSearch results for 'Avengers': {len(results)} movies found")
    if len(results) > 0:
        print(results[['title', 'genres']].head())