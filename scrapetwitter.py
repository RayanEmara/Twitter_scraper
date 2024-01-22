import requests
import bs4
from urllib.parse import parse_qs, urlparse
import lxml
import csv
import time


# CONSTS
SEARCH_QUERY    = "#gaza"
SINCE_PARAM     = '2023-12-24'
UNTIL_PARAM     = '2024-01-01'
CURL_BASE_URL = 'https://nitter.net/search'
CURL_HEADERS = {
    'authority': 'nitter.net',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en,it-IT;q=0.9,it;q=0.8,en-US;q=0.7',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
CSV_LOG_FILE_PATH = "C:\\Users\\emray\\Desktop\\Rayan\\Code\\Nitter scraper\\LOG.csv"
EMPTY_CURSOR = 'DAADDAABCgABGCtxNW5WUDMKAAIYKuXqmVeALwAIAAIAAAACCAADAAAAAAgABAAABA0KAAUYR0vLN4AnEAoABhhHS8s24Z0gAAA'

# Function to save tweets to a CSV file
def save_to_csv(data, file_path):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()

    with open(file_path, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys , delimiter= "|")

        # If the file is empty, write header
        if csv_file.tell() == 0:
            writer.writeheader()

        # Write data to CSV
        writer.writerows(data)

def get_stat(item, index):
    """
    Gets a timeline-item container and an index to return that index's stat

    Parameters:
    - item: The time-line container
    - index: 0 = comments , 1 = retweets , 2 = replies , 3 = likes
    
    Returns:
    Value of that specific stat.
    """
    try:
        stats_elements = item.select('span.tweet-stat')
        return stats_elements[index].text.strip() if stats_elements else 0
    except (IndexError, AttributeError):
        return None

def from_timelinehtml_to_tweets(html_content_of_page):
    """
    Extracts tweet information from the HTML content of a page.

    Parameters:
    - html_content_of_page (str): The HTML content of a file or page.

    Returns:
    Tuple: A tuple containing a list of dictionaries representing tweet data and the next page cursor parameter.

    The tweet data includes:
    - 'author' (str): The username of the tweet author.
    - 'date' (str): The date of the tweet.
    - 'num_likes' (str or None): The number of likes on the tweet.
    - 'num_retweets' (str or None): The number of retweets of the tweet.
    - 'num_comments' (str or None): The number of comments on the tweet.
    - 'num_replies' (str or None): The number of replies to the tweet.

    The next page cursor parameter is extracted from the 'show more' container and represents the cursor for the next timeline slice.
    """
    # Takes the html content of a file or page 
    soup = bs4.BeautifulSoup(html_content_of_page, 'lxml')
    # print(soup.contents)

    # Find the show more container and get the next page cursor
    show_more_container = soup.find_all('div', class_='show-more')[-1]
    next_page_cursor = show_more_container.find('a')['href'] if show_more_container and show_more_container.find('a') else None
    
    # Extract cursor parameter
    cursor_param = None
    if next_page_cursor:
        parsed_url = urlparse(next_page_cursor)
        query_params = parse_qs(parsed_url.query)
        cursor_param = query_params.get('cursor', [None])[0]


    # Get timeline items to iterate on, ONLY get timeline-item not show more, that is the cursor for the previous timeline-slice
    timeline_items = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['timeline-item'])
    
    # Manage the case where there's no tweets
    if not timeline_items:
        return []

    tweets = []
    # Extract relevant info for each tweet
    for item in timeline_items:
        
        tweet_data = {}

        # Tweet author
        username_element = item.select_one('a.username')
        tweet_data['author'] = username_element['title'] if username_element and 'title' in username_element.attrs else 'Unknown user'

        # Tweet author
        tweet_data['date'] = item.select_one('span.tweet-date a')['title'] if item.select_one('span.tweet-date a') else 'No date available'
        # tweet_data['body'] = item.select_one('div.tweet-content').get_text() if item.select_one('div.tweet-content').get_text() else None
        
        # Tweet stats
        # Num likes, retweets, comments, replies
        tweet_data['num_likes'] = get_stat(item, 3)
        tweet_data['num_retweets'] = get_stat(item, 1)
        tweet_data['num_comments'] = get_stat(item, 0)
        tweet_data['num_replies'] = get_stat(item, 2)

        tweets.append(tweet_data)
    

    return tweets, cursor_param


##############################
# Start with an empty cursor #
##############################

if __name__ == '__main__':
    # CURL STUFF
    # Headers is deined in CURL_HEADERS

    # Start with an empty cursor 
    cursor = EMPTY_CURSOR

    # Define the number of iterations
    iterations = 10000000

    for _ in range(iterations):
        # Update the cursor in the curl_params dictionary
        curl_params = {
            'f': 'tweets',
            'q': SEARCH_QUERY,
            'since': SINCE_PARAM,
            'until': UNTIL_PARAM,
            'near': '',
            'cursor': cursor
        }
        # Make the request
        response = requests.get(CURL_BASE_URL, params=curl_params, headers=CURL_HEADERS)

        # Check the response
        if response.status_code == 200:
            html_page_data = response.text
            tweets, cursor = from_timelinehtml_to_tweets(html_page_data)

            # Print and save tweets
            for tweet in tweets:
                print(tweet)

            # Save tweets to CSV file
            save_to_csv(tweets, CSV_LOG_FILE_PATH)

            print(f"Cursor: {cursor}")
        else:
            print(f"Error: {response.status_code}")

        # # Wait 
        # time.sleep(1)
