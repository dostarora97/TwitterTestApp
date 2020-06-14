import json, base64, requests
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import webbrowser
import tweepy
import sys

class Twitter:
    def __init__(self, auth, Bearer_Token=None):
        self.auth = auth
        self.Bearer_Token = Bearer_Token
        if self.auth is None:
            raise ValueError("API Authorisation keys needed.")
        if (self.auth.get("API_key", None) == None) or (self.auth.get("API_secret_key", None) == None):
            raise ValueError("'API_key' and 'API_scret_key' not specified")

        Path().absolute().joinpath("data").mkdir(parents=True, exist_ok=True)

    def GET_BearerToken(self):
        credentials = self.auth["API_key"] + ":" + self.auth["API_secret_key"]
        b64_creds = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization" : "Basic " + b64_creds,
            "Content-Type" : "application/x-www-form-urlencoded",
            "charset" : "UTF-8"
        }
        payload = {
            "grant_type" : "client_credentials"
        }

        r = requests.post(
            "https://api.twitter.com/oauth2/token",
            headers=headers,
            data=payload
         )
        self.Bearer_Token = r.json()
        
        later_use = input("Save Bearer Token for later use? [y/n] : ")
        if (later_use.lower() == "y"):
            with open("Bearer_Token.json", "w", encoding="UTF-8") as bt_file:
                json.dump(self.Bearer_Token, bt_file)
            print("Saved to Bearer_Token.json")

        return self.Bearer_Token

    def GET_Favourites(self, screen_name, count, Bearer_Token=None):
        if Bearer_Token == None:
            print("Bearer Token not specified.\n Using from Class Instance.")
            Bearer_Token = self.Bearer_Token
        if Bearer_Token == None:
            raise ValueError("Class instance not initialized Bearer_Token")
        
        headers = {
            "Authorization" :   Bearer_Token["token_type"] + 
            " " +
            Bearer_Token["access_token"]
        }

        payload = {
            "screen_name" : screen_name,
            "count" : count,
            "tweet_mode" : "extended"
        }

        r = requests.get(
            "https://api.twitter.com/1.1/favorites/list.json",
            headers=headers,
            params=payload
        )
        favs = r.json()

        with open("data/favs.json", "w", encoding='UTF-8') as favs_file:
            json.dump(favs, favs_file, indent=4, ensure_ascii=False)

        print("{} Favourite Tweets Captured".format(len(favs)))
        return favs


    def GET_MediaTweets(self, favs=None):
        if favs == None :
            with open("data/favs.json", "r", encoding="UTF-8") as fav_file:

                favs = json.load(fav_file)

        media_tweets = []
        for tweet in favs:
            extended_entity = tweet.get("extended_entities", None)
            if extended_entity != None:
                media_tweet = {}
                media_tweet["created_at"] = tweet["created_at"]
                media_tweet["media"] = tweet["extended_entities"]["media"]
                media_tweets.append(media_tweet)

        with open("data/media_tweets.json", "w", encoding="UTF-8") as media_tweets_file:
            json.dump(media_tweets, media_tweets_file, indent=4, ensure_ascii=False)

        print("{} Tweets with Media".format(len(media_tweets)))
        return media_tweets

    def GET_Media(self, media_tweets=None):
        if media_tweets == None:
            with open("data/media_tweets.json", "r", encoding="UTF-8") as media_tweets_file:
                media_tweets = json.load(media_tweets_file)

        custom_media_list = []

        for tweet in media_tweets:
            media_ele_list = tweet["media"]
            for media_ele in media_ele_list:
                custom_media_ele = {}
                custom_media_ele["created_at"] = tweet["created_at"]
                custom_media_ele["type"] = media_ele["type"]
                custom_media_ele["id"] = media_ele["id_str"]
                if custom_media_ele["type"] == "video" or custom_media_ele["type"] == "animated_gif":
                    variants = {}
                    for video_variants in media_ele["video_info"]["variants"]:
                        if video_variants["content_type"] == "video/mp4":
                            variants[video_variants["bitrate"]] = video_variants["url"]
                    max_bitrate = max(variants.keys())
                    custom_media_ele["url"] = variants[max_bitrate]
                else:
                    custom_media_ele["url"] = media_ele["media_url"]
                custom_media_list.append(custom_media_ele)

        with open("data/media.json", "w", encoding="UTF-8") as media_file:
            json.dump(custom_media_list, media_file, indent=4, ensure_ascii=False)
        
        print("{} Media".format(len(custom_media_list)))
        return custom_media_list

    def visualize(self, media=None):
        if media == None:
            with open("data/media.json", "r", encoding="UTF-8") as media_file:
                media_list = json.load(media_file)
        else:
            media_list = media

        file_loader = FileSystemLoader('Templates')
        env = Environment(loader=file_loader)

        template = env.get_template('media.html')
        output = template.render(media_list=media_list)

        with open("./data/media.html", "w") as index_file:
            index_file.write(output)

        webbrowser.open("data\\media.html")

with open("auth.json", "r") as auth_file:
    auth = json.load(auth_file)

twpy = Twitter(auth)

twpy.visualize(
    twpy.GET_Media(
        twpy.GET_MediaTweets(
            twpy.GET_Favourites(
                "Twitter", 200, twpy.GET_BearerToken()
            )
        )
    )
)
