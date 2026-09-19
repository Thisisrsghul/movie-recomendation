import React, { useState } from "react";

// Fallback image
const fallbackPoster = "https://via.placeholder.com/300x450?text=No+Image";

function Spinner() {
  return (
    <div className="flex items-center justify-center mt-8">
      <svg className="animate-spin h-8 w-8 text-cyan-500" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <span className="ml-2 text-cyan-700 font-semibold text-lg">Loading…</span>
    </div>
  );
}

export default function MovieRecommender() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [movie, setMovie] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    if (e?.preventDefault) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setMovie(null);
    setRecommendations([]);

    try {
      const res = await fetch("http://127.0.0.1:5000/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_name: query }),
      });

      if (!res.ok) throw new Error("Movie not found or API error.");
      const data = await res.json();

      console.log("API Response:", data); // ✅ DEBUG: See what backend returns

      // ✅ FIX: Handle the backend response structure correctly
      const mainMovie = data.searched_movie || {};
      
      setMovie({
        title: mainMovie.title || "Unknown",
        poster: mainMovie.poster_path || fallbackPoster,
        year: mainMovie.release_date ? mainMovie.release_date.split('-')[0] : '',
        genres: mainMovie.genres || '',
        rating: mainMovie.vote_average || 0,
        overview: mainMovie.overview || '',
        runtime: mainMovie.runtime || null,
        language: mainMovie.original_language || mainMovie.language || null,
      });

      // ✅ FIX: Map recommendations properly
      const recs = (data.recommendations || []).map(r => ({
        title: r.title || "Unknown",
        poster: r.poster_path || fallbackPoster,
        year: r.release_date ? r.release_date.split('-')[0] : '',
        genres: r.genres || '',
        rating: r.vote_average || 0,
        overview: r.overview || '',
      }));

      console.log("Processed movie:", mainMovie); // ✅ DEBUG
      console.log("Processed recommendations:", recs); // ✅ DEBUG

      setRecommendations(recs);
    } catch (err) {
      console.error("Error:", err); // ✅ DEBUG
      setError(err.message || "Unknown error.");
    }

    setLoading(false);
  };

  // ✅ FIX: Pass the new query before searching
  const handleRecClick = (title) => {
    setQuery(title);
    // Use setTimeout to ensure state updates before search
    setTimeout(() => {
      const fakeEvent = { preventDefault: () => {} };
      handleSearch(fakeEvent);
    }, 0);
  };

  const splitGenres = (genres) => {
    if (!genres) return [];
    return typeof genres === "string" ? genres.split(" ").filter(Boolean) : genres;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col items-center py-8 px-2">
      <div className="w-full max-w-4xl bg-slate-800/90 shadow-2xl rounded-3xl p-8 backdrop-blur-2xl mt-4 text-white">

        <h1 className="text-4xl font-extrabold text-cyan-400 mb-8 text-center drop-shadow">
          🎬 Movie Recommender
        </h1>

        {/* Search Bar */}
        <form className="flex gap-3 justify-center mb-7" onSubmit={handleSearch}>
          <input
            type="text"
            value={query}
            placeholder="Enter a movie name…"
            className="flex-1 max-w-md px-5 py-3 rounded-xl border-2 border-cyan-400/30 bg-slate-700 text-white shadow focus:border-cyan-400 focus:ring focus:ring-cyan-800 text-lg placeholder:text-cyan-200/70"
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <button
            type="submit"
            className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-3 rounded-xl font-bold shadow-lg hover:from-cyan-600 hover:to-blue-700 transition-all duration-200"
            disabled={loading}
          >
            Search
          </button>
        </form>

        {loading && <Spinner />}
        {error && <div className="text-red-400 text-center font-semibold mb-4 animate-pulse">{error}</div>}

        {/* Main Movie Card */}
        {movie && (
          <div className="w-full flex flex-col md:flex-row gap-8 mb-12 items-center bg-slate-900/80 rounded-2xl shadow-lg border border-cyan-900 p-5">
            <img
              src={movie.poster}
              alt={movie.title}
              className="w-44 h-64 object-cover rounded-xl shadow-lg border-4 border-cyan-900"
              onError={(e) => {
                console.log("Image failed to load:", movie.poster); // ✅ DEBUG
                e.target.src = fallbackPoster;
              }}
            />
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
                {movie.title}
                {movie.year && <span className="text-cyan-300 text-lg font-light">({movie.year})</span>}
              </h2>

              <div className="flex flex-wrap items-center gap-3 mb-2">
                {splitGenres(movie.genres).map((g, i) => (
                  <span key={g + i} className="bg-cyan-700/70 rounded px-3 py-1 text-xs font-semibold uppercase tracking-wider">
                    {g}
                  </span>
                ))}
                {movie.rating > 0 && (
                  <span className="bg-yellow-500/80 text-slate-900 rounded px-2 py-1 text-xs font-bold ml-2">
                    ⭐ {movie.rating.toFixed(1)}
                  </span>
                )}
              </div>

              <div className="text-cyan-100 mb-3 line-clamp-5">{movie.overview}</div>

              {movie.runtime && <div className="text-cyan-200 text-sm">⏱ {movie.runtime} min</div>}
              {movie.language && <div className="text-cyan-200 text-sm">🌐 {movie.language.toUpperCase()}</div>}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="w-full">
            <h3 className="text-2xl font-bold mb-4 text-cyan-400 text-center tracking-wider">
              Recommended Movies
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-7">
              {recommendations.map((rec, idx) => (
                <div
                  key={rec.title + idx}
                  tabIndex={0}
                  className="bg-slate-900/90 rounded-2xl shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2 hover:scale-105 cursor-pointer flex flex-col items-center group border border-cyan-700/50 overflow-hidden"
                  onClick={() => handleRecClick(rec.title)}
                  onKeyDown={(e) => e.key === "Enter" && handleRecClick(rec.title)}
                >
                  <div className="relative w-full flex flex-col items-center">
                    <img
                      src={rec.poster}
                      alt={rec.title}
                      className="w-28 h-40 object-cover rounded-lg mt-2 group-hover:opacity-80 border-2 border-cyan-900"
                      onError={(e) => {
                        console.log("Rec image failed:", rec.poster); // ✅ DEBUG
                        e.target.src = fallbackPoster;
                      }}
                    />

                    <div className="absolute bottom-0 w-full bg-gradient-to-t from-slate-900/80 to-transparent opacity-0 group-hover:opacity-100 flex flex-col justify-end text-cyan-100 p-2 transition-all duration-200 text-xs">
                      {splitGenres(rec.genres).slice(0, 2).map((g, i) => (
                        <span key={g + i} className="bg-cyan-700/80 rounded px-1 mb-1">{g}</span>
                      ))}
                      {rec.rating > 0 && <div className="mb-1 text-yellow-400">⭐ {rec.rating.toFixed(1)}</div>}
                      <div className="line-clamp-3">{rec.overview}</div>
                    </div>
                  </div>
                  <div className="mt-2 text-center font-medium text-cyan-200 px-2 truncate w-28">{rec.title}</div>
                  {rec.year && <div className="text-cyan-400 text-xs mb-2">{rec.year}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 text-cyan-700 font-medium text-sm">
        Powered by TMDb/OMDb API • <span className="text-cyan-400">Content-based Recommender</span>
      </div>
    </div>
  );
}