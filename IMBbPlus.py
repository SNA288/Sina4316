
import requests
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes
import hashlib

# Inline query handler for searching movies using OMDb API
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query

    if not query:
        return

    # Search OMDb for the query
    search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
    search_response = requests.get(search_url)
    
    if search_response.status_code != 200:
        logger.error(f"OMDb API search request failed with status code {search_response.status_code}")
        return

    search_data = search_response.json()
    if search_data.get("Response") == "False":
        logger.warning(f"No results found for query: {query}")
        return

    search_results = search_data.get("Search", [])
    results = []

    for movie in search_results[:5]:  # Limit to top 5 results
        imdb_id = movie.get('imdbID', 'N/A')
        title = movie.get('Title', 'N/A')
        year = movie.get('Year', 'N/A')
        poster = movie.get('Poster', "https://via.placeholder.com/300x450?text=No+Image")  # Placeholder if no image
        
        # Fetch detailed movie information for rating and genres
        details_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
        details_response = requests.get(details_url)
        
        if details_response.status_code == 200:
            details_data = details_response.json()
            rating = details_data.get('imdbRating', 'N/A')
            genres = details_data.get('Genre', 'N/A')
        else:
            rating = 'N/A'
            genres = 'N/A'
            logger.error(f"Failed to retrieve details for IMDb ID {imdb_id}")

        # Create a unique result ID using hashlib
        result_id = hashlib.md5(imdb_id.encode()).hexdigest()

        # Use InlineQueryResultArticle for results with thumbnails
        result = InlineQueryResultArticle(
            id=result_id,
            title=f"{title} ({year})",
            description=f"⭐: {rating}/10 \n🎭: {genres}",
            input_message_content=InputTextMessageContent(
                message_text=f"🎬 *{title}* ({year})\n⭐: {rating}/10\n🎭: {genres}\nhttps://www.imdb.com/title/{imdb_id}/",
                parse_mode="Markdown"
            ),
            thumbnail_url=poster  # Use thumb_url for the thumbnail image
        )
        results.append(result)

    # Send the results back to the user
    await update.inline_query.answer(results, cache_time=1)
