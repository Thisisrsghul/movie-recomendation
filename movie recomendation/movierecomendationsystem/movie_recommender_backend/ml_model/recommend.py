import joblib
import pandas as pd
import os
import logging
from typing import List, Dict, Optional
from functools import lru_cache
import requests   # ✅ Required

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


class MovieRecommender:
    def __init__(self, artifacts_path='ml_model/artifacts/'):
        self.artifacts_path = artifacts_path
        self.setup_logging()
        self.load_models()
        self.setup_api_keys()

    # ---------------------------
    # Setup & Utilities
    # ---------------------------
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MovieRecommender")

    def setup_api_keys(self):
        self.tmdb_key = os.getenv('TMDB_API_KEY', '76e5893766d37f3029455900d4af1cc1')
        self.omdb_key = os.getenv('OMDB_API_KEY', '2ee5f601')

    def load_models(self):
        self.movies_df = joblib.load(os.path.join(self.artifacts_path, 'movies.pkl'))
        self.similarity = joblib.load(os.path.join(self.artifacts_path, 'similarity.pkl'))

    # ---------------------------
    # TMDB & OMDB Requests
    # ---------------------------
    @lru_cache(maxsize=200)
    def search_movie_tmdb(self, title: str):
        try:
            url = f"https://api.themoviedb.org/3/search/movie"
            params = {"api_key": self.tmdb_key, "query": title}
            r = requests.get(url, params=params, timeout=6).json()

            if r.get("results"):
                m = r["results"][0]
                return {
                    "title": m.get("title"),
                    "poster_path": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
                    "overview": m.get("overview"),
                    "vote_average": m.get("vote_average"),
                    "source": "TMDB"
                }
        except Exception as e:
            self.logger.error(f"TMDB error: {e}")
        return None

    @lru_cache(maxsize=200)
    def search_movie_omdb(self, title: str):
        try:
            url = f"http://www.omdbapi.com/?apikey={self.omdb_key}&t={title}"
            data = requests.get(url, timeout=6).json()

            if data.get("Response") == "True":
                return {
                    "title": data.get("Title"),
                    "poster_path": data.get("Poster") if data.get("Poster") != "N/A" else None,
                    "overview": data.get("Plot"),
                    "vote_average": data.get("imdbRating"),
                    "source": "OMDB"
                }
        except Exception as e:
            self.logger.error(f"OMDB error: {e}")
        return None

    # ---------------------------
    # Dataset Helper Methods
    # ---------------------------
    def find_movie_in_dataset(self, title: str) -> Optional[int]:
        matches = self.movies_df[self.movies_df['title'].str.lower() == title.lower()]
        return matches.index[0] if not matches.empty else None

    def format_movie(self, movie_row):
        return {
            "title": movie_row['title'],
            "genres": movie_row.get('genres', ''),
            "overview": movie_row.get('overview', ''),
            "poster_path": movie_row.get('poster_path', None),
            "vote_average": movie_row.get('vote_average', 0)
        }

    def recommend_for_existing_movie(self, movie_idx: int, n: int):
        distances = self.similarity[movie_idx]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
        recs = [self.format_movie(self.movies_df.iloc[i[0]]) for i in movie_list]
        return recs

    def get_popular_movies(self, n=10):
        return [
            self.format_movie(self.movies_df.iloc[i])
            for i in self.movies_df.sort_values("popularity", ascending=False).index[:n]
        ]

    # ---------------------------
    # ✅ NEW METHOD: Enrich Single Movie
    # ---------------------------
    def enrich_with_poster(self, movie_data: Dict) -> Dict:
        if movie_data.get('poster_path') and movie_data['poster_path'].startswith("http"):
            return movie_data

        title = movie_data.get('title')
        if not title:
            return movie_data

        api_data = self.search_movie_tmdb(title) or self.search_movie_omdb(title)

        if api_data:
            if api_data.get("poster_path"):
                movie_data["poster_path"] = api_data["poster_path"]

            if api_data.get("overview") and not movie_data.get("overview"):
                movie_data["overview"] = api_data["overview"]

            if api_data.get("vote_average") and not movie_data.get("vote_average"):
                movie_data["vote_average"] = api_data["vote_average"]

        return movie_data

    # ---------------------------
    # ✅ NEW METHOD: Batch Enrichment
    # ---------------------------
    def enrich_recommendations_batch(self, recommendations: List[Dict], max_api_calls: int = 10):
        enriched = []
        api_calls = 0

        for rec in recommendations:
            has_poster = rec.get("poster_path") and rec["poster_path"].startswith("http")

            if has_poster or api_calls >= max_api_calls:
                enriched.append(rec)
            else:
                new = self.enrich_with_poster(rec.copy())
                if new.get("poster_path"):
                    api_calls += 1
                enriched.append(new)

        self.logger.info(f"Poster API calls used: {api_calls}")
        return enriched

    # ---------------------------
    # ✅ UPDATED METHOD
    # ---------------------------
    def get_recommendations(self, movie_name: str, n_recommendations: int = 10,
                            preference_genres: Optional[List[str]] = None) -> Dict:

        preference_genres = preference_genres or []
        result = {'status': 'success', 'searched_movie': None, 'recommendations': [], 'message': ''}

        movie_idx = self.find_movie_in_dataset(movie_name)

        if movie_idx is not None:
            movie = self.movies_df.iloc[movie_idx]
            result['searched_movie'] = self.format_movie(movie)

            # ✅ enrich searched movie
            result['searched_movie'] = self.enrich_with_poster(result['searched_movie'])

            recs = self.recommend_for_existing_movie(movie_idx, n_recommendations * 2)
            result['message'] = "Movie found in dataset"

        else:
            api_data = self.search_movie_tmdb(movie_name) or self.search_movie_omdb(movie_name)

            if api_data:
                result['searched_movie'] = api_data
                recs = self.get_popular_movies(n_recommendations * 2)
                result['message'] = f"Movie found via {api_data.get('source','API')}"
            else:
                result['status'] = 'not_found'
                result['message'] = f'Movie "{movie_name}" not found'
                recs = self.get_popular_movies(n_recommendations)

        # ✅ Enrich recommendations posters
        enriched = self.enrich_recommendations_batch(recs, max_api_calls=15)

        if preference_genres:
            filtered = [
                r for r in enriched
                if any(g.lower() in (r.get("genres") or "").lower() for g in preference_genres)
            ]
            enriched = filtered or enriched

        result["recommendations"] = enriched[:n_recommendations]
        return result
