import argparse
import json
import time
import string

import nltk
import pandas as pd
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import keys


# For storing data
STREAM_OUT = []

# Flags
STOP_STREAM = False


class Listener(StreamListener):
    """ Listener for Tweepy API """

    def on_data(self, data):
        STREAM_OUT.append(json.loads(data))
        return not STOP_STREAM
    
    def on_error(self, status):
        print(status)


def get_stream_data():
    """ Clean the data in STREAM_OUT """
    data = pd.DataFrame()

    # Username
    data['user'] = list(map(lambda x: x['user']['screen_name'], STREAM_OUT))

    # Text
    tweet = []
    for x in STREAM_OUT:
        if 'extended_tweet' in x:
            tweet.append(x['extended_tweet']['full_text'])
        else:
            tweet.append(x['text'])
    data['text'] = tweet

    return data


def get_user_report(data):
    """ Generate User Report """
    print('\n\nUser Report:\n')
    sep = 20
    u_report = data.groupby('user').count().text
    print('User'.ljust(sep) + '| ' + 'Tweet Count')
    print('-' * (sep + 10))
    for user, count in zip(u_report.index, u_report.values):
        print(user.ljust(sep) + '| ' + str(count))


def get_links_report():
    """ Generate Links Report """
    print('\n\nLinks Report:\n')
    links_count = 0
    domains = {}
    for x in STREAM_OUT:
        for url in x['entities']['urls']:
            links_count += 1
            domain = '.'.join(url['expanded_url'].split('/')[2].split('.')[-2:])
            if domain not in domains:
                domains[domain] = 1
            else:
                domains[domain] += 1
    sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)

    print('Total Number of links:', links_count)
    print('\nList of unique domains sorted by their count in decreasing order:')
    sep = 20
    print('-' * (sep + 10))
    print('Domain Name'.ljust(sep) + '| ' + 'Count')
    print('-' * (sep + 10))
    for d, c in sorted_domains:
        print(d.ljust(sep) + '| ' + str(c))


def get_content_report(data):
    """ Generate Content Report """
    print('\n\nContent Report:\n')
    freq_count = {}
    all_stops = set(nltk.corpus.stopwords.words('english')) | set(string.punctuation) | set('’')
    for text in data['text']:
        words = [word for word in nltk.tokenize.word_tokenize(str(text).lower()) if word not in all_stops and not word.isdigit()]
        for word in words:
            if len(word) > 1:
                if word[0] == "'":
                    word = word[1:]
                if word not in freq_count:
                    freq_count[word] = 1
                else:
                    freq_count[word] += 1
    sorted_freq_count = sorted(freq_count.items(), key=lambda x: x[1], reverse=True)

    print('Number of unique words:', len(freq_count))
    print('\nTop 10 most frequent words:')
    sep = 20
    print('-' * (sep + 10))
    print('Word'.ljust(sep) + '| ' + 'Count')
    print('-' * (sep + 10))
    for w, c in sorted_freq_count[:10]:
        print(w.ljust(sep) + '| ' + str(c))


def stream_tweets(auth, keyword):
    global STOP_STREAM

    max_minutes = 5

    t_start = time.time()
    stream = Stream(auth, Listener())
    stream.filter(track=[keyword], languages=['en'], is_async=True)
    
    print('Generating reports... (Please wait for 1 minute)')
    minutes_passed = 0
    while not STOP_STREAM:
        if (time.time() - t_start) % 60 == 0:
            minutes_passed += 1
            print('\n\nReports after %d minutes' % minutes_passed)
            stream_data = get_stream_data()
            get_user_report(stream_data)  # user report
            get_links_report()  # links report
            get_content_report(stream_data)  # content report

            if minutes_passed == max_minutes:
                STOP_STREAM = True
                print('\n\nFinished.')
            else:
                print('\n\n\nGenerating reports for the next minute...')


def main(keyword):
    # Authenticate with the Twitter Streaming API
    auth = OAuthHandler(keys.consumer_key, keys.consumer_key_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)

    # Stream tweets
    stream_tweets(auth, keyword)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate various reports of tweets on twitter')
    parser.add_argument('-k', '--keyword', help='Keyword by which to filter the tweets')
    args = parser.parse_args()

    main(args.keyword)
