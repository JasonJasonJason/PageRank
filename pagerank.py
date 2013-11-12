#import numpy as np
#from scipy import sparse
import os
import json
from collections import OrderedDict


PAGE_RANK_ALPHA = .1
REAL_ALPHA = 0.9


def read_data(filename):
    """
    purpose: read all tweets from the json file.
    parameter: 
        filename - the path of json file in your local computer 
    return: a list containing all raw tweets each of which has the data structure of dictionary
    """
    data = []
    try:
        with open(filename) as f:
            for line in f:
                data.append(json.loads(line.strip()))
    except:
        print "Failed to read data!"
        return []
    print "The json file has been successfully read!"
    return data


class PageRanker(object):
    def __init__(self):
        """
        purpose: Create an object to calculate page rank
        """
        self.in_edges = {}
        self.out_edges = {}
        self.rank = {}
        self.corpus = []
        self.corpus_count = 0

    def calc_pagerank(self, tweets):
        """
        purpose: read the tweet dicts and calculate page rank for each user
        preconditions: None
        parameters:
          tweets - an iterator of tweet dictionaries (just like index_tweets)
        returns: none
        """

        for tweet in tweets:
            user_screen_name = tweet["user"]["screen_name"]
            if user_screen_name not in self.out_edges:
                self.out_edges[user_screen_name] = []
            if user_screen_name not in self.in_edges:
                self.in_edges[user_screen_name] = []

            for mention in tweet["entities"]["user_mentions"]:
                screen_name = mention["screen_name"]
                if screen_name != user_screen_name:
                    if screen_name not in self.in_edges:
                        self.in_edges[screen_name] = []
                    if screen_name not in self.out_edges:
                        self.out_edges[screen_name] = []

                    if screen_name not in self.out_edges[user_screen_name]:
                        self.out_edges[user_screen_name].append(screen_name)

                    if user_screen_name not in self.in_edges[screen_name]:
                        self.in_edges[screen_name].append(user_screen_name)

        self.corpus = set (self.in_edges.keys()).union (set (self.out_edges.keys()))
        self.corpus_count = len(self.corpus)

        for user in self.corpus:
            self.rank[user] = 1.0

        precision = 0.00001
        iterations = self.corpus_pagerank(precision)
        print "Performed " + str(iterations) + " pagerank iterations before getting the desired average difference of " + str(precision)


        self.rank = OrderedDict(sorted(self.rank.items(), key=lambda x: 1-x[1]))


        print ""
        print "Top 20 twitter users:"
        for index, user in enumerate(self.rank):
            print user + ": " + str(self.rank[user])
            if index > 20:
                break


    def corpus_pagerank(self, precision):
        """
        purpose: perform pagerank calclations until the desired prevision is met
        preconditions: None
        parameters:
          precision - the desired precision to iterate until
        returns:
            iteration - the number of iterations performed
        """
        nextPageRankScore = {}
        iteration = 0
        repeat = True

        while repeat:
            iteration += 1
            repeat = False

            for user in self.corpus:
                new_rank = self.user_pagerank(user)
                nextPageRankScore[user] = new_rank
                rank_difference = self.rank[user] - new_rank
                if rank_difference > precision:
                    repeat = True

            for user in self.corpus:
                self.rank[user] = nextPageRankScore[user]

        return iteration
            

    def user_pagerank(self, screen_name):
        """
        purpose: perform a pagerank iteration calculation
        preconditions: None
        parameters:
            screen_name - the name of the twitter user
        returns:
            the pagerank of the given user using the current ranking
        """
        incoming_score = 0.0
        if screen_name in self.in_edges:
            for user in self.in_edges[screen_name]:
                if len(self.out_edges[user]) > 0:
                    incoming_score += self.rank[user] / len(self.out_edges[user])

        return REAL_ALPHA * incoming_score + (1-REAL_ALPHA)/self.corpus_count


            


    
if __name__=="__main__":
    # this is just here for you to test running page rank
    ranker = PageRanker()
    tweets = read_data(os.path.join(os.getcwd(),'pagerank.json'))
    ranker.calc_pagerank(tweets)






