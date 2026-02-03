import requests
import streamlit as st

class TMDbHelper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    @st.cache_data
    def search_movie(_self, title, year=None):
        """Search for a movie and return poster path"""
        try:
            # Clean the title (remove year in parentheses if present)
            clean_title = title.split('(')[0].strip()
            
            # Search for movie
            search_url = f"{_self.base_url}/search/movie"
            params = {
                'api_key': _self.api_key,
                'query': clean_title
            }
            
            if year:
                params['year'] = year
            
            response = requests.get(search_url, params=params, timeout=5)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    # Return the first result's poster path
                    poster_path = results[0].get('poster_path')
                    if poster_path:
                        return f"{_self.image_base_url}{poster_path}"
            
            return None
        except Exception as e:
            return None
    
    def get_poster_url(self, title):
        """Get poster URL for a movie title"""
        # Extract year from title if present (e.g., "Toy Story (1995)")
        year = None
        if '(' in title and ')' in title:
            try:
                year_str = title.split('(')[-1].split(')')[0]
                if year_str.isdigit():
                    year = int(year_str)
            except:
                pass
        
        return self.search_movie(title, year)