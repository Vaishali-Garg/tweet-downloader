import base64
import requests
import csv
import sys
import getopt

consumer_key = None
consumer_secret = None

def usage():
    msg = '''tweet-dl --key <twitter_app_key> --secret <twitter_app_secret> [--csv <output_file>] screen_name1 screen_name2 ...
    Arguments:
        --key <twitter app key>         Twitter Application Key
        --secret <twitter app secret>   Twitter Application Secret
        --csv <output_file> (Optional)  Filename where output records are written (default: tweets.csv)
'''
    print (msg)
    sys.exit()

def get_args():
    global consumer_key, consumer_secret

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ['key=', 'secret=','csv=', 'help'])
    except getopt.GetoptError as err:
        print(err)
        usage()

    output_file = 'tweets.csv'
    for opt, arg in opts:
        if opt in ('--key'):
            consumer_key = arg
        elif opt in ('--secret'):
            consumer_secret = arg
        elif opt in ('--csv'):
            output_file = arg
        elif opt == '--help':
            usage()
        else:
            usage()

    if (consumer_key is None) or (consumer_secret is None) or (len(args) < 1):
        usage()


    return output_file, args


def get_tweets(screen_name):
    # Use application auth with app level keys
    key_secret = '{}:{}'.format(consumer_key, consumer_secret).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')

    base_url = 'https://api.twitter.com/'
    auth_url = '{}oauth2/token'.format(base_url)
    auth_headers = {'Authorization': 'Basic {}'.format(b64_encoded_key),'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    auth_data = {'grant_type': 'client_credentials'}
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

    access_token = auth_resp.json()['access_token']
    search_headers = {'Authorization': 'Bearer {}'.format(access_token) }
    search_params = {'screen_name': screen_name,'count': 200}

    search_url = '{}1.1/statuses/user_timeline.json'.format(base_url)
    search_resp = requests.get(search_url, headers=search_headers, params=search_params)

    alltweets = []

    new_tweets = search_resp.json()
    alltweets.extend(new_tweets)
    oldest = alltweets[-1]['id'] - 1

    while len(new_tweets) > 0:
        search_params = {'screen_name': screen_name,'count': 200, 'max_id': oldest}
        search_resp = requests.get(search_url, headers=search_headers, params=search_params)
        new_tweets = search_resp.json()
        alltweets.extend(new_tweets)
        oldest = alltweets[-1]['id'] - 1
    
    outtweets = [[tweet['user']['name'],tweet['user']['description'], tweet['user']['location'],\

                  tweet['created_at'], tweet['id_str'], tweet['text'].encode("utf-8"),\
                  tweet['source'], tweet['in_reply_to_status_id_str'], tweet['in_reply_to_user_id_str'],\
                  tweet['in_reply_to_screen_name'], tweet.get('quote_count', 0),\
                  tweet.get('reply_count', 0), tweet.get('retweet_count', 0), tweet.get('favorite_count', 0),  tweet.get('retweeted',0),\

                  tweet['user']['id_str'], tweet['user']['followers_count'], tweet['user']['friends_count'],\
                  tweet['user']['favourites_count'], tweet['user']['statuses_count'],\
                  tweet['user']['time_zone'], tweet['user']['lang'], tweet['user']['created_at'],\

                  tweet.get('media', {}).get('display_url', None), tweet.get('media', {}).get('type', None)] \
                  for tweet in alltweets]
    return outtweets



def combine_tweets(screen_names):

    tweet_list = []

    for screen_name in screen_names:
        tweet_list.extend(get_tweets(screen_name))

    tweet_list.sort(key=lambda x: x[2], reverse=True)
    return tweet_list

def write_csv(tweet_list, output_file):

    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['user name' ,  'user description' ,   'user location' ,\
        'created_at' ,   'id_str' ,   'text', 'source' ,   'in_reply_to_status_id_str' ,\
        'in_reply_to_user_id_str' , 'in_reply_to_screen_name' ,  \
        'quote_count' , 'reply_count' ,   'retweet_count' ,   'favorite_count' ,\
        'retweeted' ,'user id' , 'followers_count' ,   'friends_count' ,'favourites_count',\
        'statuses_count' ,'user time_zone' ,   'user lang' ,   'user created_at' ,\
        'media display_url' ,   'media type' ])

        writer.writerows(tweet_list)


def main():

    output_file, screen_names = get_args()
    tweet_list = combine_tweets(screen_names)
    write_csv(tweet_list, output_file)

if __name__ == "__main__":
    main()
