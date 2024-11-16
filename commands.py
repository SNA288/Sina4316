# commands.py v11

import os
import re
from urllib.parse import urlparse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from collections import defaultdict
from scraper import search_movies, scrape_download_links


# Function to save links to a text file
def save_links_to_file(filename, links):
    try:
        with open(filename, 'w') as f:
            for link in links:
                f.write(link + '\n')
        logger.info(f"Links successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving links to {filename}: {e}")

# Search command
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

    # Get the search query # movie_title should or shouldnt
    query = ' '.join(context.args) if context.args else context.chat_data.get('query')
    if not query:
        await chat.reply_text("داداش کلیک نکن؛ دستور سرچُ نگهدار\nمثلا:\n*/search* `friends`", parse_mode="Markdown")
        return

    # Save the query to chat data
    context.chat_data['query'] = query

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
                navigation_buttons.append(InlineKeyboardButton("صفحه قبلی", callback_data="action:pagination:prev"))
            navigation_buttons.append(InlineKeyboardButton("صفحه بعدی", callback_data="action:pagination:next"))

            keyboard.append(navigation_buttons)
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Edit message if it's a callback, else reply
            if is_callback:
                await chat.edit_text(f"نتایج جستجو (صفحه {page}):", reply_markup=reply_markup, parse_mode="HTML")
            else:
                await chat.reply_text(f"نتایج جستجو (صفحه {page}):", reply_markup=reply_markup, parse_mode="HTML")
        else:
            await chat.reply_text("گشتم نبود!")
    except Exception as e:
        await chat.reply_text("خطا در جستجو؛ لطفا دوباره یا بعدا امتحان کنید")


# Button handler for inline keyboard
async def buttons(update, context):
    """Handle button clicks."""
    query = update.callback_query
    data = query.data
    logger.info(f"Button pressed with data: {data}")

    parts = data.split(":")
    action = parts[1]
    item_id = parts[2]
    
    # Track the current page number in context
    page = context.chat_data.get('page', 1)

    # Handle pagination buttons
    if action == "pagination":
        direction = parts[2]  # "next" or "prev"
        page = page + 1 if direction == "next" else max(page - 1, 1)
        await search(update, context, page)
        logger.info(f"Pagination triggered: {direction}, moving to page {page}")

    elif action == "download":
        index = int(parts[2])
        links = context.chat_data.get('search_results', [])

        if index < len(links):
            movie_link = links[index][1]
            logger.info(f"Initiating download for movie at index {index}: {movie_link}")

            try:
                download_links = scrape_download_links(movie_link)
                if download_links:
                    dubbed_resolutions = [res for res in download_links if 'Dubbed' in res]
                    non_dubbed_resolutions = [res for res in download_links if 'Dubbed' not in res]

                    # Add buttons for "Dubbed" and "Non-Dubbed"
                    keyboard = []
                    if dubbed_resolutions:
                        keyboard.append([InlineKeyboardButton("نسخه دوبله", callback_data=f"action:dubbed:{index}")])
                    if non_dubbed_resolutions:
                        keyboard.append([InlineKeyboardButton("نسخه اصلی", callback_data=f"action:non_dubbed:{index}")])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.reply_text("انتخاب نسخه:", reply_markup=reply_markup)
                    logger.info("Download options sent to user")
                else:
                    await query.message.reply_text("نیاز به خرید اشتراک؛ لینک‌های دانلود در دسترس نیست")
                    logger.warning(f"No download links available for {movie_link}")
            except Exception as e:
                logger.error(f"Error fetching download links for {movie_link}: {e}")
                await query.message.reply_text("خطا در دریافت لینک‌های دانلود؛ لطفا دوباره یا بعدا امتحان کنید")

        await query.answer()



    elif action in ["dubbed", "non_dubbed"]:
        index = int(item_id)
        links = context.chat_data.get('search_results', [])

        if index < len(links):
            movie_link = links[index][1]
            logger.info(f"User selected {action} version for movie at index {index}: {movie_link}")

            try:
                download_links = scrape_download_links(movie_link)
                if download_links:
                    # Filter based on dubbed or non-dubbed
                    if action == "dubbed":
                        resolutions = [res for res in download_links if 'Dubbed' in res]
                    else:
                        resolutions = [res for res in download_links if 'Dubbed' not in res]

                    # Create resolution buttons
                    keyboard = [
                        [InlineKeyboardButton(res, callback_data=f"action:resolution:{index}:{res}")]
                        for res in resolutions
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.reply_text("انتخاب رزولوشن:", reply_markup=reply_markup)
                    logger.info(f"Resolution options for {action} version sent to user")
                else:
                    await query.message.reply_text("لینک‌های دانلود در دسترس نیست")
                    logger.warning(f"No download links available for {movie_link}")
            except Exception as e:
                logger.error(f"Error fetching {action} links for {movie_link}: {e}")
                await query.message.reply_text("خطا در پردازش درخواست")

        await query.answer()

    elif action == "resolution":
        resolution = parts[3]
        index = int(item_id)
        links = context.chat_data.get('search_results', [])

        if index < len(links):
            movie_link = links[index][1]
            logger.info(f"User selected resolution {resolution} for movie at index {index}: {movie_link}")

            try:
                download_links = scrape_download_links(movie_link)
                if download_links:
                    links_for_resolution = list(set(download_links.get(resolution, [])))

                    has_season_episode = any(re.search(r'[sS](\d{2})[eE](\d{2})', os.path.basename(urlparse(link).path)) for link in links_for_resolution)

                    if has_season_episode:
                        season_links = defaultdict(list)
                        for link in sorted(links_for_resolution):
                            parsed_url = urlparse(link)
                            file_name = os.path.basename(parsed_url.path)
                            match = re.search(r'[sS](\d{2})[eE](\d{2})', file_name)
                            if match:
                                season = match.group(1)
                                episode = match.group(2)
                                season_links[season].append((episode, link))

                        keyboard = [
                            [InlineKeyboardButton(f"فصل {season}", callback_data=f"action:season:{index}:{resolution}:S{season}")]
                            for season in sorted(season_links.keys())
                        ]
                        keyboard.append([InlineKeyboardButton("همه فصلها", callback_data=f"action:all_seasons:{index}:{resolution}")])
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.message.reply_text("انتخاب فصل:", reply_markup=reply_markup)
                        logger.info(f"Season selection sent to user for movie at index {index}, resolution {resolution}")
                    else:
                        formatted_links = "\n".join([f"<pre>{link}</pre>" for link in links_for_resolution])
                        await query.message.reply_text(f"لینک‌های دانلود فیلم:\n{formatted_links}", parse_mode="HTML", disable_web_page_preview=True)
                        logger.info(f"Formatted movie links sent for resolution {resolution}")
                else:
                    await query.message.reply_text("خطا در بارگیری لینک‌های دانلود")
                    logger.warning(f"No links available for resolution {resolution} at index {index}")
            except Exception as e:
                logger.error(f"Error processing resolution {resolution} for movie at index {index}: {e}")
                await query.message.reply_text("خطا در پردازش درخواست")
        await query.answer()

    elif action == "season":
        season = parts[4][1:]  # Extract season number
        resolution = parts[3]
        index = int(item_id)
        links = context.chat_data.get('search_results', [])

        if index < len(links):
            movie_link = links[index][1]

            try:
                download_links = scrape_download_links(movie_link)
                if download_links:
                    links_for_resolution = download_links.get(resolution, [])
                    season_links = defaultdict(list)

                    for link in links_for_resolution:
                        parsed_url = urlparse(link)
                        file_name = os.path.basename(parsed_url.path)
                        match = re.search(r'[sS](\d{2})[eE](\d{2})', file_name)
                        if match and match.group(1) == season:
                            season_links[season].append(link)

                    text_links = [link for link in season_links.get(season, [])]
                    save_links_to_file(f'Season_{season}_Download_Links.txt', text_links)

                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=open(f'Season_{season}_Download_Links.txt', 'rb'),
                        filename=f'Season_{season}_Download_Links.txt'
                    )
                else:
                    await query.message.reply_text(f"هیچ لینکی برای فصل {season} یافت نشد.")
            except Exception as e:
                await query.message.reply_text(f"خطا در پردازش درخواست: {e}")

        await query.answer()
        

    elif action == "all_seasons":
        resolution = parts[3]
        index = int(item_id)
        links = context.chat_data.get('search_results', [])

        if index < len(links):
            movie_link = links[index][1]

            try:
                download_links = scrape_download_links(movie_link)
                if download_links:
                    links_for_resolution = download_links.get(resolution, [])
                    text_links = [link for link in links_for_resolution]
                    save_links_to_file('All_Download_Links.txt', text_links)

                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=open('All_Download_Links.txt', 'rb'),
                        filename='All_Download_Links.txt'
                    )
                else:
                    await query.message.reply_text("هیچ لینکی پیدا نشد.")
            except Exception as e:
                await query.message.reply_text(f"خطا در پردازش درخواست: {e}")

        await query.answer()
