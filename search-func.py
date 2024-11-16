async def search(update, context, page=None):
    if page is None:
        page = 1

    # Check if this is a callback or a fresh search
    if hasattr(update, 'message') and update.message:
        chat = update.message
        is_callback = False
    else:
        chat = update.callback_query.message
        is_callback = True

    # Get the search query (movie_title should be used)
    query = context.user_data.get('movie_title')
    if not query:
        await chat.reply_text("داداش کلیک نکن؛ دستور سرچُ نگهدار\nمثلا:\n*/search* `friends`", parse_mode="Markdown")
        return

    logger.info(f"User initiated search with query: {query} on page {page}")

    # Loading message for new searches
    if not is_callback:
        await chat.reply_text("در حال جستجو...")

    try:
        links = search_movies(query, page)
        if links:
            context.chat_data['search_results'] = links
            context.chat_data['page'] = page  # Save current page
            response = '\n'.join([f"{i + 1}. {name}" for i, (name, link) in enumerate(links)])
            keyboard = [[InlineKeyboardButton(f"{name}", callback_data=f"action:download:{i}")]
                        for i, (name, _) in enumerate(links)]

            navigation_buttons = []
            if page > 1:
                navigation_buttons.append(InlineKeyboardButton("Prev Page", callback_data="action:pagination:prev"))
            navigation_buttons.append(InlineKeyboardButton("Next Page", callback_data="action:pagination:next"))

            keyboard.append(navigation_buttons)
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Edit message if it's a callback, else reply
            if is_callback:
                await chat.edit_text(f"Results (Page {page}):", reply_markup=reply_markup, parse_mode="HTML")
            else:
                await chat.reply_text(f"Results (Page {page}):", reply_markup=reply_markup, parse_mode="HTML")
        else:
            await chat.reply_text("couldnt find anything")
    except Exception as e:
        logger.error(f"Error during search: {e}")
        await chat.reply_text("An error occurred during the search.")

# Function to scrape another website using the stored movie ID and full title
async def scrape_and_send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'movie_id' in context.user_data and 'movie_title' in context.user_data:
        movie_id = context.user_data['movie_id']
        movie_title = context.user_data['movie_title']
        result = scrape_movie_info(movie_title)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("No movie ID or title selected.")

# Function to search movies and handle pagination
def search_movies(query, page):
    # Implement the logic to search movies and handle pagination
    # This function should return a list of tuples (name, link)
    pass

# Function to scrape movie information
def scrape_movie_info(movie_title):
    # Implement the logic to scrape movie information using the movie title
    # This function should return the scraped information as a string
    pass
