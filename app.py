import tweepy
from textblob import TextBlob
from flask import Flask, render_template, request, redirect
import requests
import re, pandas as pd


app = Flask(__name__)

def cleaning(tweetx):
    tweet = tweetx.text
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_polarities(tweet):
    tb = TextBlob(tweet)
    p = tb.sentiment.polarity
    if p==0:
        return 0
    if p>0:
        return 1
    return -1

def get_sentiment(tweets):
    clean_tweets = list(map(cleaning,tweets))
    return list(map(get_polarities,clean_tweets))

def get_tweets(product_name):
    consumer_key = 'NpcPH02aXRHFB9aQqWJtLf39Q'
    consumer_secret = '7mvXjgh4NvwleQBArFvgGBnvgJbNcpZgahgl05DaQIeTNuZ8gl'

    access_token = '913817046659592192-ScOdsW9TXTXFt2oSeDkTOEqsqqje39u'
    access_token_secret = 'Oo0iez91r3JwzAejTtRXVBpldW71zNzHWpOOAenES181w'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    countries = pd.read_csv('required.csv')
    lat, longi, code = countries['latitude'], countries['longitude'], countries['CODE']
    actual = []
    for i in range(len(lat)):
        actual.append([lat[i], longi[i], code[i]])
    import random
    random.shuffle(actual)
    l = []
    for i in range(20):
        public_tweets = api.search(product_name, lang="en", count=100, geo=[actual[i][0],actual[i][1],"1000 km"])
        sentiments = get_sentiment(public_tweets)
        pos, neg = sentiments.count(1), sentiments.count(-1)
        l.append([actual[i][2], pos, neg])
    df = pd.DataFrame(data=l,columns=["code","positive","negative"])
    return df
    
def plotit2(df):
    import plotly
    import plotly.express as px
    from plotly.offline import plot
    tidy_df = df.melt(id_vars="code")
    print(tidy_df)
    fig = px.scatter_geo(tidy_df, locations="code",
        size="value", # size of markers, "pop" is one of the columns of gapminder
        color="variable"
    )
    # plot(fig,filname="a.html")
    # import plotly.io as pio
    fig.show()
    # New try
    import json
    return json.dumps([fig],cls=plotly.utils.PlotlyJSONEncoder)
    # return pio.to_image(fig, format='png')
     

@app.route("/",methods=['POST','GET'])
def index():
    if request.method=="POST":
        product_name = request.form['product']
        # tweets = get_tweets(product_name)
        df = get_tweets(product_name)
        fig = plotit2(df)
        return render_template("index.html", plot=fig)
        # return render_template("a.html")
         
    else:
        return render_template("index.html")
if __name__=="__main__":
    app.run(debug=True) 

