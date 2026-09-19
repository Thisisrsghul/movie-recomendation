# movie_apis.py
import requests
import os
from typing import Dict, Optional

class TMDBApi:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/"

    def search_movie(self, query: str, year: Optional[int] = None) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': query,
                'language': 'en-US',
                'page': 1,
                'include_adult': False
            }
            if year:
                params['year'] = year
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return data['results'][0]
            return None
        except Exception as e:
            print(f"Error searching movie: {e}")
            return None

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'append_to_response': 'keywords,credits,videos,similar'
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting movie details: {e}")
            return None

    def format_movie_data(self, movie_data: Dict) -> Dict:
        formatted_data = {
            'tmdb_id': movie_data.get('id'),
            'title': movie_data.get('title', ''),
            'overview': movie_data.get('overview', ''),
            'release_date': movie_data.get('release_date', ''),
            'year': None,
            'runtime': movie_data.get('runtime', 0),
            'vote_average': movie_data.get('vote_average', 0),
            'vote_count': movie_data.get('vote_count', 0),
            'popularity': movie_data.get('popularity', 0),
            'poster_path': '',
            'backdrop_path': '',
            'genres': [],
            'keywords': [],
            'cast': [],
            'directors': [],
            'production_companies': [],
            'production_countries': [],
            'spoken_languages': []
        }

        if formatted_data['release_date']:
            try:
                formatted_data['year'] = int(formatted_data['release_date'][:4])
            except:
                pass

        # poster_path from TMDB is usually a partial path like "/abc.jpg"
        if movie_data.get('poster_path'):
            p = movie_data['poster_path']
            # Ensure we produce a full URL
            if p.startswith('http'):
                formatted_data['poster_path'] = p
            else:
                formatted_data['poster_path'] = f"{self.image_base_url}w500{p}"

        if movie_data.get('backdrop_path'):
            b = movie_data['backdrop_path']
            if b.startswith('http'):
                formatted_data['backdrop_path'] = b
            else:
                formatted_data['backdrop_path'] = f"{self.image_base_url}original{b}"

        if movie_data.get('genres'):
            formatted_data['genres'] = [g['name'] for g in movie_data['genres']]

        if movie_data.get('credits'):
            credits = movie_data['credits']
            if credits.get('cast'):
                formatted_data['cast'] = [
                    {'name': c['name'], 'character': c.get('character', '')}
                    for c in credits['cast'][:5]
                ]
            if credits.get('crew'):
                directors = [p['name'] for p in credits['crew'] if p.get('job') == 'Director']
                formatted_data['directors'] = directors

        if movie_data.get('production_companies'):
            formatted_data['production_companies'] = [c['name'] for c in movie_data['production_companies']]

        if movie_data.get('production_countries'):
            formatted_data['production_countries'] = [c['name'] for c in movie_data['production_countries']]

        if movie_data.get('spoken_languages'):
            formatted_data['spoken_languages'] = [l.get('english_name', l.get('name', '')) for l in movie_data['spoken_languages']]

        return formatted_data


class OMDBApi:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OMDB_API_KEY')
        self.base_url = "http://www.omdbapi.com/"

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        try:
            params = {'apikey': self.api_key, 't': title, 'plot': 'full'}
            if year:
                params['y'] = year
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    return data
            return None
        except Exception as e:
            print(f"Error searching movie in OMDB: {e}")
            return None

    def search_by_imdb_id(self, imdb_id: str) -> Optional[Dict]:
        try:
            params = {'apikey': self.api_key, 'i': imdb_id, 'plot': 'full'}
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    return data
            return None
        except Exception as e:
            print(f"Error getting movie by IMDB ID: {e}")
            return None

    def format_movie_data(self, omdb_data: Dict) -> Dict:
        formatted_data = {
            'imdb_id': omdb_data.get('imdbID', ''),
            'title': omdb_data.get('Title', ''),
            'overview': omdb_data.get('Plot', ''),
            'release_date': omdb_data.get('Released', ''),
            'year': None,
            'runtime': 0,
            'vote_average': 0,
            'vote_count': 0,
            'poster_path': '',
            'genres': [],
            'cast': [],
            'directors': [],
            'writers': [],
            'awards': omdb_data.get('Awards', ''),
            'box_office': omdb_data.get('BoxOffice', ''),
            'production': omdb_data.get('Production', ''),
            'rated': omdb_data.get('Rated', ''),
            'language': omdb_data.get('Language', ''),
            'country': omdb_data.get('Country', ''),
            'source': 'OMDB'
        }

        try:
            formatted_data['year'] = int(omdb_data.get('Year', '').split('–')[0])
        except:
            pass

        try:
            runtime_str = omdb_data.get('Runtime', '0 min')
            formatted_data['runtime'] = int(runtime_str.split(' ')[0])
        except:
            pass

        try:
            imdb_rating = omdb_data.get('imdbRating', '0')
            if imdb_rating != 'N/A':
                formatted_data['vote_average'] = float(imdb_rating)
        except:
            pass

        try:
            imdb_votes = omdb_data.get('imdbVotes', '0').replace(',', '')
            if imdb_votes != 'N/A':
                formatted_data['vote_count'] = int(imdb_votes)
        except:
            pass

        poster = omdb_data.get('Poster', '')
        formatted_data['poster_path'] = poster if poster and poster != 'N/A' else ''

        if omdb_data.get('Genre'):
            formatted_data['genres'] = [g.strip() for g in omdb_data['Genre'].split(',')]
        if omdb_data.get('Actors'):
            formatted_data['cast'] = [a.strip() for a in omdb_data['Actors'].split(',')]
        if omdb_data.get('Director'):
            formatted_data['directors'] = [d.strip() for d in omdb_data['Director'].split(',')]
        if omdb_data.get('Writer'):
            formatted_data['writers'] = [w.strip() for w in omdb_data['Writer'].split(',')]

        return formatted_data


class MovieAPIService:
    def __init__(self):
        self.tmdb = TMDBApi(os.getenv("TMDB_API_KEY"))
        self.omdb = OMDBApi(os.getenv("OMDB_API_KEY"))

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        tmdb_movie = self.tmdb.get_movie_details(movie_id)
        if tmdb_movie:
            # ensure partial poster path is converted to full URL
            if tmdb_movie.get('poster_path') and not tmdb_movie['poster_path'].startswith('http'):
                tmdb_movie['poster_path'] = f"{self.tmdb.image_base_url}w500{tmdb_movie['poster_path']}"
            return self.tmdb.format_movie_data(tmdb_movie)

        # fallback via imdb id if available
        if tmdb_movie and 'imdb_id' in tmdb_movie:
            imdb_id = tmdb_movie['imdb_id']
            omdb_data = self.omdb.search_by_imdb_id(imdb_id)
            if omdb_data:
                return self.omdb.format_movie_data(omdb_data)
        return None
