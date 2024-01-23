import csv
import bs4
from urllib.parse import parse_qs, urlparse
import lxml

# Function to loop between two dates iteratively

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
