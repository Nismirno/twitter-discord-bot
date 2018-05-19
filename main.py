from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
from tweepy.api import API
from discordWebhooks import Webhook, Embed, Field
import calendar, datetime, time, random, json
from time import gmtime, strftime
from datetime import datetime
import html


class StdOutListener(StreamListener):
    def __init__(self, api=None, dataD=None):
        self.api = api or API()

        if dataD is not None:
            with open('data.json') as data_file:
                datajson = json.load(data_file)
                self.dataD = datajson['Discord']
        else:
            self.dataD = dataD

    def on_status(self, status):
        colors = ['7f0000', '535900', '40d9ff', '8c7399', 'd97b6c',
                  'f2ff40', '8fb6bf', '502d59', '66504d', '89b359',
                  '00aaff', 'd600e6', '401100', '44ff00', '1a2b33',
                  'ff00aa', 'ff8c40', '17330d', '0066bf', '33001b',
                  'b39886', 'bfffd0', '163a59', '8c235b', '8c5e00',
                  '00733d', '000c59', 'ffbfd9', '4c3300', '36d98d',
                  '3d3df2', '590018', 'f2c200', '264d40', 'c8bfff',
                  'f23d6d', 'd9c36c', '2db3aa', 'b380ff', 'ff0022',
                  '333226', '005c73', '7c29a6']

        data = status._json

        for dataD in self.dataD:
            webhookURL = dataD['webhook-url']
            followedTwitterIDs = dataD['twitter-ids']
            content = ''
            if 'MentionEveryone' in dataD:
                if dataD['MentionEveryone'] == 'true':
                    content = 'New tweet @everyone'
            if (data['user']['id_str'] in dataD['twitter-ids'] and 'retweeted_status' not in data):
                username = data['user']['screen_name']
                icon_url = data['user']['profile_image_url']

                text = ''
                if 'extended_tweet' in data:
                    text = data['extended_tweet']['full_text']
                else:
                    text = data['text']

                for userMention in data['entities']['user_mentions']:
                    text = text.replace('@{0}'.format(userMention['screen_name']),
                                        '[@{0}](https://twitter.com/{0})'.format(userMention['screen_name']))
                media_url = ''
                media_type = ''

                if 'extended_tweet' in data:
                    if 'media' in data['extended_tweet']['entities']:
                        for media in data['extended_tweet']['entities']['media']:
                            if media['type'] == 'photo':
                                media_url = media['media_url']

                if 'media' in data['entities']:
                    for media in data['entities']['media']:
                        if media['type'] == 'photo' and not media_url:
                            media_url = media['media_url_https']
                            media_type = 'photo'
                        if media['type'] == 'video':
                            media_url = media['media_url_https']
                            media_type = 'video'
                        if media['type'] == 'animated_gif' and media_type != 'video':
                            media_url = media['media_url_https']
                            media_type = 'photo'

                videoAlert = False

                if 'extended_entities' in data and 'media' in data['extended_entities']:
                    for media in data['extended_entities']['media']:
                        if media['type'] == 'photo' and not media_url:
                            media_url = media['media_url_https']
                            media_type = media['type']
                        if media['type'] == 'video':
                            videoAlert = True
                            media_type = media['type']
                        if media['type'] == 'animated_gif' and media_type != "video":
                            videoAlert = True

                if videoAlert:
                    text += " *[tweet has video]*"

                text = html.unescape(text)
                color = random.choice(colors)
                color = int(color, 16)
                at = Embed(author_name=username,
                           author_url="https://twitter.com/" + data['user']['screen_name'],
                           author_icon=icon_url,
                           color=color,
                           description=text,
                           media_url=media_url,
                           media_type=media_type,
                           title=data['user']['name'],
                           url="https://twitter.com/" + data['user']['screen_name'] + "/status/" + str(data['id_str']),
                           footer="Tweet created on",
                           footer_icon="https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png",
                           timestamp=datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y').isoformat(' '))

                print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), data['user']['screen_name'], 'twittered.')

                wh = Webhook(url=webhookURL,
                             username="{0} Bot".format(username),
                             icon_url=icon_url,
                             content=content)
                wh.addAttachment(at)
                wh.post()

        return True

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        print('on_delete')
        print(status_id)
        print(user_id)
        return

    def on_event(self, status):
        """Called when a new event arrives"""
        print('on_event')
        print(status)
        return

    def on_direct_message(self, status):
        """Called when a new direct message arrives"""
        print('on_direct_message')
        print(status)
        return

    def on_friends(self, friends):
        """Called when a friends list arrives.
        friends is a list that contains user_id
        """
        print('on_friends')
        print(friends)
        return

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        print('on_limit')
        print(track)
        return

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        print('on_error')
        print(status_code)
        return False

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice
        Disconnect codes are listed here:
        https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
        """
        print('on_disconnect')
        print(notice)
        return

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        print('on_warning')
        print(notice)
        return


if __name__ == '__main__':
    with open('data.json') as d:
        authdata = json.load(d)

    CONSUMER_KEY = authdata['Twitter']['consumer-key']
    CONSUMER_SECRET = authdata['Twitter']['consumer-secret']
    ACCESS_TOKEN = authdata['Twitter']['access-token']
    ACCESS_TOKEN_SECRET = authdata['Twitter']['access-token-secret']
    followedTwitterIDs = []
    for element in authdata['Discord']:
        followedTwitterIDs.extend(x for x in element['twitter-ids'] if x not in followedTwitterIDs)

    l = StdOutListener(dataD=authdata)
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l)

    stream.filter(follow=followedTwitterIDs)
