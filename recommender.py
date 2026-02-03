import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from database import Database
from movie_data import MovieData

class MovieRecommender:
    def __init__(self):
        self.db = Database()
        self.movie_data = MovieData()
        self.model = None
        self.trainset = None
        self.train_model()
    
    def train_model(self):
        """Train the SVD recommendation model on MovieLens data"""
        try:
            print("Training recommendation model...", flush=True)
            
            # Load MovieLens ratings
            ratings_df = self.movie_data.ratings_df
            print(f"Loaded {len(ratings_df)} ratings", flush=True)
            
            # For large datasets, sample to make training faster
            if len(ratings_df) > 5000000:
                print("Sampling 2M ratings for faster training...", flush=True)
                ratings_df = ratings_df.sample(n=2000000, random_state=42)
            
            # Auto-detect rating scale based on data
            min_rating = ratings_df['rating'].min()
            max_rating = ratings_df['rating'].max()
            print(f"Rating scale detected: {min_rating} - {max_rating}", flush=True)
            
            # Prepare data for Surprise
            reader = Reader(rating_scale=(min_rating, max_rating))
            data = Dataset.load_from_df(
                ratings_df[['user_id', 'movie_id', 'rating']], 
                reader
            )
            print("Data prepared for training", flush=True)
            
            # Train on full dataset
            self.trainset = data.build_full_trainset()
            print("Building trainset complete", flush=True)
            
            # Train SVD model (optimized parameters)
            print("Training SVD model (this takes 1-3 minutes)...", flush=True)
            
            # Use different parameters based on dataset size
            if len(ratings_df) > 1000000:
                # Larger dataset - use smaller factors for speed
                self.model = SVD(n_factors=50, n_epochs=10, random_state=42, verbose=True)
            else:
                # Smaller dataset - use more factors for accuracy
                self.model = SVD(n_factors=100, n_epochs=20, random_state=42, verbose=True)
            
            self.model.fit(self.trainset)
            
            print("✅ Model trained successfully!")
        except Exception as e:
            print(f"❌ Error training model: {e}")
            raise
    
    def get_recommendations_for_user(self, user_id, n=10):
        """Get top N movie recommendations for a user"""
        # Get movies the user has already rated
        user_ratings = self.db.get_user_ratings(user_id)
        rated_movie_ids = set(user_ratings['movie_id'].values)
        
        # Get all movies
        all_movies = self.movie_data.get_all_movies()
        
        # For large datasets, only predict for a random sample of unrated movies
        unrated_movies = [mid for mid in all_movies.index if mid not in rated_movie_ids]
        
        # Sample movies to speed up predictions for large datasets
        if len(unrated_movies) > 1000:
            sample_movies = np.random.choice(unrated_movies, size=1000, replace=False)
        else:
            sample_movies = unrated_movies
        
        # Predict ratings for sampled unrated movies
        predictions = []
        for movie_id in sample_movies:
            try:
                pred = self.model.predict(user_id, movie_id)
                movie = all_movies.loc[movie_id]
                predictions.append({
                    'movie_id': movie_id,
                    'predicted_rating': pred.est,
                    'title': movie['title'],
                    'genres': movie['genres']
                })
            except:
                continue
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        return predictions[:n]
    
    def get_similar_users(self, user_id, top_n=5):
        """Find users with similar taste"""
        # Get current user's ratings
        user_ratings = self.db.get_user_ratings(user_id)
        
        if len(user_ratings) == 0:
            return []
        
        # Get all other users
        all_users = self.db.get_all_users_with_ratings()
        
        similarities = []
        
        for _, other_user in all_users.iterrows():
            other_user_id = other_user['id']
            
            # Skip self
            if other_user_id == user_id:
                continue
            
            # Calculate similarity
            similarity = self.calculate_user_similarity(user_id, other_user_id)
            
            if similarity > 0:
                similarities.append({
                    'user_id': other_user_id,
                    'username': other_user['username'],
                    'similarity': similarity,
                    'rating_count': other_user['rating_count']
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_n]
    
    def calculate_user_similarity(self, user1_id, user2_id):
        """Calculate similarity between two users using cosine similarity"""
        # Get ratings for both users
        user1_ratings = self.db.get_user_ratings(user1_id)
        user2_ratings = self.db.get_user_ratings(user2_id)
        
        # Find common movies
        common_movies = set(user1_ratings['movie_id']) & set(user2_ratings['movie_id'])
        
        if len(common_movies) < 3:  # Need at least 3 common movies
            return 0
        
        # Create rating vectors for common movies
        user1_vector = []
        user2_vector = []
        
        for movie_id in common_movies:
            r1 = user1_ratings[user1_ratings['movie_id'] == movie_id]['rating'].values[0]
            r2 = user2_ratings[user2_ratings['movie_id'] == movie_id]['rating'].values[0]
            user1_vector.append(r1)
            user2_vector.append(r2)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([user1_vector], [user2_vector])[0][0]
        
        # Convert to percentage
        return round(similarity * 100, 1)
    
    def check_and_award_badges(self, user_id):
        """Check if user deserves any new badges"""
        user_ratings = self.db.get_user_ratings(user_id)
        rating_count = len(user_ratings)
        
        badges_awarded = []
        
        # Badge 1: First Steps (rate 1 movie)
        if rating_count >= 1:
            if self.db.add_badge(user_id, "🎬 First Steps", "Rated your first movie!"):
                badges_awarded.append("🎬 First Steps")
        
        # Badge 2: Movie Buff (rate 10 movies)
        if rating_count >= 10:
            if self.db.add_badge(user_id, "🍿 Movie Buff", "Rated 10 movies!"):
                badges_awarded.append("🍿 Movie Buff")
        
        # Badge 3: Cinephile (rate 25 movies)
        if rating_count >= 25:
            if self.db.add_badge(user_id, "🎭 Cinephile", "Rated 25 movies!"):
                badges_awarded.append("🎭 Cinephile")
        
        # Badge 4: Film Critic (rate 50 movies)
        if rating_count >= 50:
            if self.db.add_badge(user_id, "⭐ Film Critic", "Rated 50 movies!"):
                badges_awarded.append("⭐ Film Critic")
        
        if rating_count >= 5:
            # Genre-specific badges
            all_movies = self.movie_data.get_all_movies()
            
            # Get user's rated movies with genres
            user_movie_ids = user_ratings['movie_id'].values
            user_movies = all_movies.loc[all_movies.index.isin(user_movie_ids)]
            
            # Count genre preferences
            genre_counts = {}
            for genre in ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 
                         'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 
                         'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']:
                if genre in user_movies.columns:
                    genre_counts[genre] = user_movies[genre].sum()
            
            # Award genre badges (if 70%+ of ratings are in that genre)
            for genre, count in genre_counts.items():
                if count >= rating_count * 0.7 and count >= 5:
                    badge_name = f"💫 {genre} Fan"
                    badge_desc = f"Loves {genre} movies!"
                    if self.db.add_badge(user_id, badge_name, badge_desc):
                        badges_awarded.append(badge_name)
        
        # Tough Critic badge (average rating < 3.0)
        if rating_count >= 10:
            avg_rating = user_ratings['rating'].mean()
            if avg_rating < 3.0:
                if self.db.add_badge(user_id, "🔍 Tough Critic", "Average rating below 3 stars"):
                    badges_awarded.append("🔍 Tough Critic")
        
        # Optimist badge (average rating > 4.0)
        if rating_count >= 10:
            avg_rating = user_ratings['rating'].mean()
            if avg_rating > 4.0:
                if self.db.add_badge(user_id, "😊 Optimist", "Average rating above 4 stars!"):
                    badges_awarded.append("😊 Optimist")
        
        return badges_awarded


# Test the recommender
if __name__ == "__main__":
    recommender = MovieRecommender()
    print("\nRecommender system ready!")