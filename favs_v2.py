import json, base64, requests
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import webbrowser
import tweepy
import sys

class Twitter:
    def __init__(self, API_Key, API_secret_key, access_token=None, access_token_secret=None):
        self.API_key = API_Key
        self.API_secret_key = API_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        Path().absolute().joinpath("data").mkdir(parents=True, exist_ok=True)

    def GET_Favourites(self, screen_name):
        auth = tweepy.OAuthHandler(self.API_key, self.API_secret_key)
        if self.access_token == None or self.access_token_secret == None:
            print("access_token or access_token_secret not intiliazed. Redirecting to Authorization Page")
            redirect_url = auth.get_authorization_url()
            print("Get Verifier token from : {}".format(redirect_url))
            webbrowser.open(redirect_url)
            auth.get_access_token(input("Verifier Token: "))

            later_use = input("Save access credentials for later use? [y/n] : ")
            if (later_use.lower() == "y"):
                with open("access.json", "w", encoding="UTF-8") as access_file:
                    access = {"access_token" : auth.access_token, "access_token_secret" : auth.access_token_secret}
                    json.dump(access, access_file)
                print("Saved to 'access.json'. This will be later used to fetch. To revoke access, delete the file 'access.json'")
        else:
            auth.set_access_token(self.access_token, self.access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        favs = []
        for status in tweepy.Cursor(api.favorites, id=screen_name, tweet_mode="extended").items():
            favs.append(status._json)
            print("Tweets Captured: {}".format(len(favs)), end='\r')
            sys.stdout.flush()

        with open("data/favs.json", "w", encoding="UTF-8") as file:
            json.dump(favs, file, indent=4)
        
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

        print("Media Count : {}".format(len(media_list)))

        file_loader = FileSystemLoader('Templates')
        env = Environment(loader=file_loader)

        template = env.get_template('media.html')
        output = template.render(media_list=media_list)

        with open("./data/media.html", "w") as index_file:
            index_file.write(output)

        webbrowser.open("data\\media.html")

if Path().joinpath("auth.json").exists() :
    with open("auth.json", "r") as auth_file:
        auth = json.load(auth_file)
        api_key = auth["API_key"]
        api_secret_key = auth["API_secret_key"]
else:
    api_key = input("API_key : ")
    api_secret_key = input("API_secret_key : ")
    
    later_use = input("Save access credentials later use? [y/n] : ")
    if (later_use.lower() == "y"):
        with open("auth.json", "w", encoding="UTF-8") as auth_file:
            auth = {"API_key" : api_key, "API_secret_key" : api_secret_key}
            json.dump(auth, auth_file)
        print("Saved to 'auth.json'. This will be later used to fetch. To revoke access, delete the file 'auth.json'")

if Path().joinpath("access.json").exists() :
    with open("access.json", "r") as access_file:
        access = json.load(access_file)
        access_token = access["API_key"]
        access_token_secret = access["API_secret_key"]
else:
    access_token = None
    access_token_secret = None

twpy = Twitter(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret)

screen_name = input("Enter Screen Name of the user : ")

twpy.visualize(
    twpy.GET_Media(
        twpy.GET_MediaTweets(
            twpy.GET_Favourites(
                screen_name
            )
        )
    )
)

print("All the data is saved in Directory: './data")