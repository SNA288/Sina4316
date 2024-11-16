from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Function to scrape another website using the stored movie ID and full title
async def scrape_and_send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'movie_id' in context.user_data and 'movie_title' in context.user_data:
        movie_id = context.user_data['movie_id']
        movie_title = context.user_data['movie_title']
        result = scrape_movie_info(movie_title)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("No movie ID or title selected.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if this is a callback or a fresh search
    if hasattr(update, 'message') and update.message:
        chat = update.message
        is_callback = False
    else:
        chat = update.callback_query.message
        is_callback = True

    # Get the search query (movie_title should be used)
    query = context.user_data.get('movie_title', ' '.join(context.args)) if context.args else context.chat_data.get('query')
    if not query:
        await chat.reply_text("Please use the search command with a query.\nExample:\n*/search* `friends`", parse_mode="Markdown")
        return

    # Save the query to chat data
    context.chat_data['query'] = query

    # Loading message for new searches
    if not is_callback:
        await chat.reply_text("Searching...")

    try:
        all_links = []
        page = 1
        while True:
            links = search_movies(query, page)
            if not links:
                break
            all_links.extend(links)
            page += 1

        if all_links:
            context.chat_data['search_results'] = all_links
            response = '\n'.join([f"{i + 1}. {name}" for i, (name, link) in enumerate(all_links)])
            keyboard = [[InlineKeyboardButton(f"{name}", callback_data=f"action:download:{i}")]
                        for i, (name, _) in enumerate(all_links)]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Edit message if it's a callback, else reply
            if is_callback:
                await chat.edit_text(f"Results:", reply_markup=reply_markup, parse_mode="HTML")
            else:
                await chat.reply_text(f"Results:", reply_markup=reply_markup, parse_mode="HTML")
        else:
            await chat.reply_text("Couldn't find anything.")
    except Exception:
        await chat.reply_text("An error occurred during the search.")

# Function to handle download action
async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    index = int(query.data.split(':')[-1])
    links = context.chat_data.get('search_results', [])

    if 0 <= index < len(links):
        name, link = links[index]
        # Extract movie_id from the link or any other method
        movie_id = extract_movie_id_from_link(link)
        context.user_data['movie_id'] = movie_id
        context.user_data['movie_title'] = name

        # Automatically trigger the scraping process
        await scrape_and_send_results(update, context)
    else:
        await query.message.reply_text("Invalid selection.")

# Dummy function to simulate movie ID extraction
def extract_movie_id_from_link(link: str) -> str:
    # Implement the logic to extract movie_id from the link
    return "dummy_movie_id"

# Dummy function to simulate movie search
def search_movies(query: str, page: int) -> list:
    # Implement the logic to search movies and return a list of (name, link) tuples
    # This is a placeholder and should be replaced with actual search logic
    return [("Movie 1", "link1"), ("Movie 2", "link2")] if page == 1 else []

# Dummy function to simulate movie info scraping
def scrape_movie_info(movie_title: str) -> str:
    # Implement the logic to scrape movie info
    return f"Scraped info for {movie_title}"
