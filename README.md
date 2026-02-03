# 🎬 MovieMatch

AI-powered movie recommendation platform with personalized suggestions and achievement badges!

## Features
- 🎥 86,000+ movies from MovieLens dataset
- 🤖 AI-powered personalized recommendations using SVD
- 🏆 Achievement badge system
- 👥 Find users with similar movie taste
- ⭐ Half-star rating precision
- 🎨 Beautiful dark-themed UI

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python, SQLite
- **ML Algorithm:** SVD (Singular Value Decomposition) Collaborative Filtering
- **APIs:** TMDb for movie posters
- **Libraries:** scikit-surprise, pandas, numpy

## Live Demo
Coming soon!

## How It Works
1. Users rate movies they've watched
2. AI analyzes rating patterns using SVD
3. System recommends movies based on similar users' preferences
4. Users earn badges for rating milestones

## Local Installation
```bash
git clone https://github.com/YOUR_USERNAME/movie-match.git
cd movie-match
pip install -r requirements.txt
streamlit run app.py
```

## Author
Created as a portfolio project showcasing ML/AI skills