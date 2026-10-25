# Movie Recommendation System

A full-stack movie recommendation application with a React frontend and a Flask REST API backend. The backend exposes an endpoint for searching for a movie and returning recommendations. Movie metadata and recommendation artifacts are required for recommendation results.

**Repository:** https://github.com/Alexbenva/movierecomendationsystem

## Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Important Dataset Note](#important-dataset-note)
- [Run Locally on Windows](#run-locally-on-windows)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Features

- React-based web interface.
- Flask REST API.
- Movie search and recommendation endpoint.
- Optional genre preferences and configurable recommendation count.
- Health endpoint to check backend status.
- TMDB and OMDb API-key configuration for movie information, if enabled in the application.

## Technology Stack

- **Frontend:** React, Create React App (`react-scripts`), Tailwind CSS
- **Backend:** Python, Flask, Flask-CORS
- **Configuration:** environment variables loaded from a `.env` file
- **Movie data/model:** dataset and model artifacts included or referenced by the repository

## Project Structure

```text
movierecomendationsystem/
├── movie_recommender_backend/
│   ├── app.py
│   ├── config.py
│   ├── .env
│   ├── requirements.txt
│   ├── ml_model/
│   ├── services/
│   └── tests/
└── movie_recommender_frontend/
    ├── package.json
    ├── package-lock.json
    ├── public/
    └── src/
```

The backend `requirements.txt` in the repository may be empty. The large `TMDB_all_movies.csv` file is managed with Git LFS; if Git LFS reports a missing object (HTTP 404), the dataset cannot be restored from that repository version and recommendation functionality may not work until the file/artifacts are supplied.

## Prerequisites

Install the following before starting:

- Git
- Python 3
- Node.js and npm

Check that Python and Node.js are available:

```powershell
py --version
node --version
npm --version
```

## Important Dataset Note

During cloning, Git LFS may fail to download `TMDB_all_movies.csv` with an error similar to `Object does not exist on the server: [404]`. This is a repository-side missing LFS object, not a command-line mistake. The repository may still contain source files, but the recommender needs the correct dataset/model artifacts. Obtain the missing CSV from the project owner or a valid source and place it where the code expects it. Do not rename an unrelated dataset to pretend it is the missing file.

## Run Locally on Windows

Open **two separate PowerShell windows**: one for the backend and one for the frontend. The commands below assume you cloned the repository into `D:\movie recomendation\movierecomendationsystem`. Adjust the path if your folder is elsewhere.

### 1. Start the backend

In the first PowerShell window:

```powershell
cd "D:\movie recomendation\movierecomendationsystem\movie_recommender_backend"
```

Create and activate a virtual environment (skip creation if `.venv` already exists at this location):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the packages used by the Flask API and common data/recommendation components:

```powershell
python -m pip install --upgrade pip
python -m pip install flask flask-cors python-dotenv requests pandas numpy scikit-learn
```

Start the backend:

```powershell
python app.py
```

The Flask app is configured to listen on `http://127.0.0.1:5000`. Keep this terminal open.

**Note:** The repository's `requirements.txt` is currently empty, and `app.py` imports `MovieRecommender`. If startup reports a missing module such as `recommend`, or a missing model artifact, the repository checkout is incomplete or needs additional files/dependencies. Installing packages alone cannot fix a missing source file or model artifact.

### 2. Start the frontend

In the second PowerShell window:

```powershell
cd "D:\movie recomendation\movierecomendationsystem\movie_recommender_frontend"
npm install
npm start
```

The frontend uses Create React App, so `npm start` should open the app at:

```text
http://localhost:3000
```

Keep this terminal open while using the frontend.

### 3. Test the backend

With the backend running, open:

- API status: http://127.0.0.1:5000/
- Health check: http://127.0.0.1:5000/api/health

The health response reports whether the recommendation model loaded and whether TMDB/OMDb API keys are configured.

## API Endpoints

### `GET /`

Returns basic API information and the current recommender initialization status.

### `GET /api/health`

Returns health status and indicates whether the recommender and optional API keys are configured.

### `POST /api/search`

Search for a movie and request recommendations.

Example JSON request:

```json
{
  "movie_name": "Inception",
  "n_recommendations": 10,
  "preference_genres": []
}
```

`n_recommendations` is optional; the API defaults to 10 and accepts values from 1 to 50. `preference_genres` is optional.

## Troubleshooting

### `cd /d` fails in PowerShell

`cd /d` is a Command Prompt syntax. In PowerShell use:

```powershell
cd "D:\movie recomendation\movierecomendationsystem\movie_recommender_backend"
```

### `requirements.txt` is empty

Install the listed packages from the backend setup section. If Python then reports another missing import, check the exact module named in the error and whether the repository includes it.

### `ModuleNotFoundError: No module named 'recommend'`

The backend entry point imports `MovieRecommender` from `recommend`. Check whether the expected Python file/module is present in the backend folder or its package structure. This is a source-code issue, not something `pip install` can necessarily resolve.

### Git LFS fails to download `TMDB_all_movies.csv` with HTTP 404

The LFS object is missing from the remote repository. Ask the repository owner for a working dataset or repaired LFS upload. Retrying `git clone` repeatedly will not restore an object that is absent on the server.

### Frontend cannot connect to the backend

Make sure the backend is running at `http://127.0.0.1:5000` and that the frontend's API base URL matches it. Check the browser console and both terminal windows for errors.

### `npm` says `package.json` is missing

Run `npm install` and `npm start` inside `movie_recommender_frontend`, not the repository's parent folder.


