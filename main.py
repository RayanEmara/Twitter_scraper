import config
from funcs import save_to_csv, from_timelinehtml_to_tweets
from requests import get
from datetime import date, timedelta 
import requests
import os
import time

if __name__ == '__main__':
    
    # Set time constraints 
    START_DATE  = date(2024, 1 , 24) # I want tp scrape from this
    FINISH_DATE = date(2024, 1 ,  2) # To this


    START_UNTIL = START_DATE + timedelta(days = 1) # Just the day after that st dt

    # Set variables for dates so that we can later change them
    var_since_param     = START_DATE
    var_until_param     = START_UNTIL
    
    while var_until_param != FINISH_DATE:
        # This is my condition for stopping the whole script
        # For everyday:
            # Until i'm out of tweets:
                # Do
        # Initalize cursor as empty
        cursor = ''
        
        finished_items = False
        while not finished_items:
      
            curl_params = {
            'f': 'tweets',
            'q': config.SEARCH_QUERY,
            'since': var_since_param.strftime('%Y-%m-%d'),
            'until': var_until_param.strftime('%Y-%m-%d'),
            'near': '',
            'cursor': cursor,
            'e-nativeretweets': 'on',
            'e-replies': 'on'
            }
            response = requests.get(config.CURL_BASE_URL, params=curl_params, headers=config.CURL_HEADERS)

            if response.status_code == 200:
                try:

                    html_page_data = response.text
                    tweets, cursor = from_timelinehtml_to_tweets(html_page_data)
                    print('Updated cursor')

                    for tweet in tweets:
                        print(tweet)


                    save_to_csv(tweets, config.CSV_LOG_FILE_PATH)

                    print(f"Cursor: {cursor}")
                except ValueError:
                    finished_items = True
                except IndexError:
                    finished_items = True
                
        # Once day scraping is finished update date variables and
        # update config params 
        var_since_param = var_since_param - timedelta(days = 1)
        var_until_param = var_until_param - timedelta(days = 1)
        # Now i'm done with that particlar 
        cursor = config.EMPTY_CURSOR
        
