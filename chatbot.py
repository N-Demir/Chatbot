#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
#
#TODOS: Remember what people said about previous movies, Fine grain sentiment?
# Add regex to negation file, if multiple choices pop up from isMovie ask user
#Dones:
######################################################################
import csv
import math
import re

# For time testing
import time

import numpy as np
import heapq

from movielens import ratings
from random import randint

from PorterStemmer import PorterStemmer


# IGNORE THIS STUFF
caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
# FOUND IT TO SPLIT SENTENCES

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.is_repeat = False
      self.skip_to_next = False
      self.sentiment = {}
      self.usr_rating_vec = []
      self.numRatings = 5
      self.numRecs = 3
      #self.prevInput = None
      self.read_data()
      self.p = PorterStemmer()
      self.stemLexicon()
      self.binarize()


      self.negations = open("data/negations.txt", "r").read().splitlines()
      self.punctuations = open('data/punctuation.txt', "r").read().splitlines()
      self.strong_neg = open('data/strong_neg_words.txt', "r").read().splitlines()
      self.strong_pos = open('data/strong_pos_words.txt', "r").read().splitlines()
      self.intensifiers = open('data/intensifiers.txt', "r").read().splitlines()
      self.stemPos_Neg_Words()


    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Change name of moviebot? keep plus?
      #############################################################################

      greeting_message = ("Hi! I'm " + self.name + "! I'm going to recommend a movie to you. \n"
      "First I will ask you about your taste in movies. Tell me about a movie that you have seen.")

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Have a nice day!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################

      # User decides how to continue or quit the chatbot after recommendations are given
      if self.is_repeat == True:
        if input == '1':
          return "Please type \":quit\""
        elif input == '2':
          self.is_repeat = False
          self.numRatings += 3
          return "Please tell me about another movie you've seen."
        elif input == '3':
          self.is_repeat = False
          self.usr_rating_vec = []
          return "Hello again! I'm going to give you some more movie recommendations. Please tell me about a movie you have seen."
        else:
          return "I'm sorry, I don't understand your input. Please enter a number 1, 2, or 3."


      if self.is_turbo == True:
        # CREATIVE SECTION

        # Allow for user to enter up to 2 movies
        movie_tag = self.processTitle(input)
        movie_flag = movie_tag[1]
        if movie_flag == -1: # No movies found
          return "Sorry, I don't understand. Tell me about a movie that you have seen."
          #emotion detection? means they are talking about something else other than movie
        elif movie_flag == 1: # 1 movie found
          movies = movie_tag[0]
          movie_index = self.isMovie(movie)
          sentiment = self.sentimentClass(input)
          if sentiment == 'pos':
            response = self.getPosResponse(movie_index)
            self.usr_rating_vec.append((movie_index, 1))
          elif sentiment == 'neg':
            response = self.getNegResponse(movie_index)
            self.usr_rating_vec.append((movie_index, -1))
          elif sentiment == 'none':
            response = self.getNoneResponse(movie)
          else: # Unclear sentiment
             response = self.getUnclearResponse(movie_index)
        elif movie_flag == 2: # multiple movies found
          movie1 = movies[0]
          movie2 = movies[1]
          movie_index1 = self.isMovie(movie1)
          movie_index2 = self.isMovie(movie2)

          #if len(movie_index1) != 0

          andRegex = r'(?:both )?"' + movie1 + '".{0,20}?and.{0,20}?"' + movie2 + '"' # same sentiment
          orRegex = r'(?:either |neither )?"' + movie1 + '".{0,20}?(?:or|nor).{0,20}?"' + movie2 + '"' # same sentiment?
          butRegex = r'"' + movie1 + '".{0,20}?but.{0,20}?"' + movie2 + '"' # different sentiment?

          andEntities = re.findall(andRegex, input)
          orEntities = re.findall(orRegex, input)
          butEntities = re.findall(butRegex, input)

          sentiment = self.sentimentClass(input)
          # if sentiment == 'pos':
          #   if len(andEntities) > 0:

          #   movie_index = self.getMovieIndex(movie_indexes)
          #   response = self.getPosResponse(movie_index)
          #   self.usr_rating_vec.append((movie_index, 1))
          # elif sentiment == 'neg':
          #   movie_index = self.getMovieIndex(movie_indexes)
          #   response = self.getNegResponse(movie_index)
          #   self.usr_rating_vec.append((movie_index, -1))
          # elif sentiment == 'none':
          #   response = self.getNoneResponse(movie_title)
          # else: # Unclear sentiment
          #   response = self.getUnclearResponse(movie_title)

          # if len(andEntities) > 0:

          # elif len(orEntities > 0):
          #   sentiment = self.sentimentClass
          # elif len(butEntities > 0):
          #   sentiment1 =
          #   sentiment2 =

        else: # more than 2 movies found
          return "I'm sorry, please tell me about either one or two movies at a time. Go ahead."

        response = 'processed %s in creative mode!!' % input


      else:
        # STARTER SECTION

        # Arbitrary input regexes

        q0 = r'hi|hello'
        q1 = r'[Hh]ow are you'
        q2 = r'[Ww]hat(?:\'s | is )your name'
        q3 = r'[Hh]ow(?:\'s | is | has | was )your (?:day|night|evening|morning|afternoon)'
        q4 = r'[Dd]o you love me'
        q5 = r'^[Nn]o\.?$'
        basicQ = r'\?$'

        r0 = re.findall(q0, input)
        if len(r0) != 0: return "Hello! Tell me about a movie you've seen."
        r1 = re.findall(q1, input)
        if len(r1) != 0: return "I am well, but tell me about some movies."
        r2 = re.findall(q2, input)
        if len(r2) != 0: return "My name is " + self.name + ". Now what is a movie you have an opinion about?"
        r3 = re.findall(q3, input)
        if len(r3) != 0: return "It has been good! Let's talk about some movies now."
        r4 = re.findall(q4, input)
        if len(r4) != 0: return "Yes, I love everyone. Now I know there are some movies you love - tell me about one."
        r5 = re.findall(q5, input)
        if len(r5) != 0: return "Yes, please."
        rbasic = re.findall(basicQ, input)
        if len(rbasic) != 0:
          numResponses = 2
          randInt = randint(1, numResponses)
          if randInt == 1:
            return "Hey, I'm the one asking the questions here! What is your opinion on a movie you have seen"
          elif randInt == 2:
            return "Enough with the questions, let's get to the movies! Can you tell about one you have seen?"
        # Process movie title
        temp = self.processTitle(input)
        movie_tag = temp[0]
        input = temp[1]
        # Get the flag indicating success of process Title
        movie_flag = movie_tag[1]
        if movie_flag == -1: # No movies found
            return "Sorry, I don't understand. Tell me about a movie that you have seen."
        elif movie_flag == 1: # Movie found
            movie_title = movie_tag[0]
            movie_indexes = self.isMovie(movie_title)

            if len(movie_indexes) != 0: # Good movie!
              # Need to encorperate the sentiment
              #self.usr_rating_vec.append((movie_index, 1))
              #response = "Sentiment for " + movie + " is " + self.sentimentClass(input)

              # We have received a valid movie so we have to extract sentiment,
              # record the movie rating based on sentiment, and respond reflecting
              # the sentiment.

              sentiment = self.sentimentClass(input)
              if sentiment == 'pos':
                movie_index = self.getMovieIndex(movie_indexes)
                if movie_index != None:
                  response = self.getPosResponse(movie_index)
                  self.usr_rating_vec.append((movie_index, 1))
                else: response = "Ok, tell me about about another movie."
              elif sentiment == 'str_pos':
                movie_index = self.getMovieIndex(movie_indexes)
                if movie_index != None:
                  response = self.getStrPosResponse(movie_index)
                  self.usr_rating_vec.append((movie_index, -1))
                else: response = "Ok, tell me about about another movie."
              elif sentiment == 'neg':
                movie_index = self.getMovieIndex(movie_indexes)
                if movie_index != None:
                  response = self.getNegResponse(movie_index)
                  self.usr_rating_vec.append((movie_index, -1))
                else: response = "Ok, tell me about about another movie."
              elif sentiment == 'str_neg': # Don't yet deal with changing the rating
                movie_index = self.getMovieIndex(movie_indexes)
                if movie_index != None:
                  response = self.getStrNegResponse(movie_index)
                  self.usr_rating_vec.append((movie_index, -1))
                else: response = "Ok, tell me about about another movie."
              elif sentiment == 'none':
                response = self.getNoneResponse(movie_title)
              else: # Unclear sentiment
                response = self.getUnclearResponse(movie_title)

              # Need to fix this, just for testing
              #if len(self.usr_rating_vec) == 5:
                #self.recommend(self.usr_rating_vec)
            else: # Unknown movie
              return "Unfortunately I have never seen that movie. I would love to hear about other movies that you have seen."
        else:
          return "Please tell me about one movie at a time. Go ahead."

      if (len(self.usr_rating_vec) == self.numRatings):
        movie_recommend = self.recommend(self.usr_rating_vec)
        # TODO: Make this a stand alone function
        recommend_response = 'I have learned a lot from your movie preferences. Here are a couple suggestions for movies you may like\n'
        recommend_response += movie_recommend
        recommend_response += '\n'
        recommend_response += 'Thank you for chatting with me today! Please choose one of the options below by typing 1, 2, or 3.\n'
        recommend_response += '1. Quit\n'
        recommend_response += '2. Add additional movie ratings for more recommendations.\n'
        recommend_response += '3. Restart with new ratings for new recommendations.'
        self.is_repeat = True

        # Return our response plus our recommendation
        return response + '\n' + recommend_response

      return response

    def getMovieIndex(self, movie_indexes):
      if len(movie_indexes) > 1:
          #TODO: GET STuck in while loop asking for choice
          movie = self.askForSelection(movie_indexes)
          if movie != None: return movie
          else: return None
      else:
          return movie_indexes[0]

    ###########################################################
    ######                   RESPONSES                   ######
    ###########################################################
    def getStrPosResponse(self, movie_index):
      NUM_POS_RESPONSES = 2
      randInt = randint(1, NUM_POS_RESPONSES)

      if randInt == 1:
          return "Awesome, you really liked \"" + self.titles[movie_index][0] + "\"! What are some other movies you have seen."
      elif randInt == 2:
          return "Great choice! That is an amazing movie. \"" + self.titles[movie_index][0] + "\". What about another movie?"

      return "ISSUE - posresponse" #TODO:REMOV

    def getStrNegResponse(self, movie_index):
      NUM_POS_RESPONSES = 2
      randInt = randint(1, NUM_POS_RESPONSES)

      if randInt == 1:
          return "So you really disliked \"" + self.titles[movie_index][0] + "\". I'd love to here about other movies you have seen."
      elif randInt == 2:
          return "You hated \"" + self.titles[movie_index][0] + "\"! Thanks for the heads up. Any other movies you have an opinion about?"

      return "ISSUE - posresponse" #TODO:REMOV

    def getPosResponse(self, movie_index):
        NUM_POS_RESPONSES = 2
        randInt = randint(1, NUM_POS_RESPONSES)

        if randInt == 1:
            return "You liked \"" + self.titles[movie_index][0] + "\". Thank you! Tell me about another movie you have seen."
        elif randInt == 2:
            return "Ok, you enjoyed \"" + self.titles[movie_index][0] + "\". What about another movie?"

        return "ISSUE - posresponse" #TODO:REMOVE

    def getNegResponse(self, movie_index):
        NUM_NEG_RESPONSES = 2
        randInt = randint(1, NUM_NEG_RESPONSES)

        if randInt == 1:
            return "You did not like " + self.titles[movie_index][0] + ". Thank you! Tell me about another movie you have seen."
        elif randInt == 2:
            return "Ok, you disliked \"" + self.titles[movie_index][0] + "\". What about another movie?" #TODO: fill out

        return "ISSUE - negresponse" #TODO:REMOVE

    def getNoneResponse(self, movie_title):
        NUM_NONE_RESPONSES = 2
        randInt = randint(1, NUM_NONE_RESPONSES)

        if randInt == 1:
            return "Ok, thank you! Tell me your opinion on \"" + movie_title + "\"."
        elif randInt == 2:
            return "What did you think about \"" + movie_title + "\"?" #TODO: fill out


        #TODO: REMEMBER PREVIOUS THING
        return "ISSUE - noneResponse"

    def getUnclearResponse(self, movie_title):
        NUM_UNCLEAR_RESPONSES = 2
        randInt = randint(1, NUM_UNCLEAR_RESPONSES)

        if randInt == 1:
            return "I'm sorry, I'm not quite sure if you liked \"" + movie_title + "\" Tell me more about \"" + movie + "\"."
        elif randInt == 2:
            return "I'm sorry, I can't quite tell what your opinion is on \"" + movie_title + "\". Can you tell me more?" #TODO: fill out

        return "ISSUE - unclearResponse" #TODO:REMOVE
    ###########################################################
    ######                 END RESPONSES                 ######
    ###########################################################


    def processTitle(self, inpt):
        # TODO: Expand to allow for no quotation marks
        # movies should be clearly in quotations and match our database
        movie_regex = r'"(.*?)"'

        # Find all the entities
        entities = re.findall(movie_regex, inpt)
        # No movies found - flag -1
        if len(entities) == 0:

          #CREATIVE
          # find movies not in quotation marks, assume first letter is capitalized
          entity = self.findNonQuotationTitles(inpt)
          if len(entity) != 0:
              inpt = re.sub(re.compile(entity), "", inpt)
              return ((entity, 1), inpt)
          # else we still found nothing
          return (("", -1), inpt)
        elif len(entities) == 1: # One movie found - flag 1
          inpt = re.sub(movie_regex, "", inpt)
          return ((entities[0], 1), inpt)
        else: # Multiple movies found - flag 2
          #TODO: DO SOMETHING WITH THIS
          return ((entities, 2), inpt)

    def findNonQuotationTitles(self, inpt):
        # check for every valid movie, stripped of date and article, if it is in
        # the input
        inpt = inpt.lower()
        entities = []

        for title in self.titles:
            movie_title = title[0]

            #strip and Lowercase
            movie_title = movie_title.lower()

            movie_title = re.sub(r' \(\d\d\d\d\)', "", movie_title)
            movie_title = re.sub(r'^(the |an |a )', "", movie_title)

            #print "Cur title after stripping: " + movie_title

            if movie_title in inpt:
                #TODO: " " + movie_title + " "
                #TODO: check if moving things around in beginning worked
                """
                print "Movie title: " + movie_title + " Input: " + inpt
                print "TITLE[0]: " + title[0
                """
                entities.append(movie_title)

        if len(entities) == 0:
            return ""
        return max(entities, key=len)


        """
        # TODO: REMOVE? Don't worry about multiple sentences?
        sentences = self.split_into_sentences(inpt)
        if len(sentences) == 0:
            sentences = [inpt]

        for sentence in sentences:
            words = sentence.split()

            for i in range(len(words), 0, -1):
                #TODO: FILL OUT

        print str(sentences)
        """


    def edit_distance(self, true_word, query, max_dist):
      # If length of titles differ more than max_dist than return max_dist + 1
      if abs(len(true_word) - len(query)) > max_dist:
        return max_dist + 1

      # Create matrix for DP algorithm
      # Initialize to all zeros and make dimension (m+1) x (n+1)
      # Initialize first row to be 0...M and first col to be 0...M
      edit_dist_M = [[(x + i) for i in range(len(query) + 1)] for x in range(len(true_word) + 1)]

      # Substitute cost
      sub_cost = 1

      for j in range(1, len(query) + 1):
        for i in range(1, len(true_word) + 1):
          cost_del = edit_dist_M[i - 1][j] + 1
          cost_ins = edit_dist_M[i][j-1] + 1
          # Compute cost of substitution. If letters we are comparing are
          # equal we encure no cost
          cost_sub = edit_dist_M[i-1][j-1] + (0 if query[j - 1].lower == true_word[i - 1].lower else sub_cost)

          edit_dist_M[i][j] = min(cost_del, cost_ins, cost_sub)

      return edit_dist_M[len(true_word)][len(query)]

    def spellCheck(self, query):
      # Indexes to suggest
      indices = []
      start_time = time.time()

      # Try removing the year from query and title!
      #query = re.sub(r'\(\d\d\d\d\)', "", movie_title)
      #query = self.

      # Maximum edit distance stuff
      max_edit = len(re.findall(r'\w+', movie_title))
      max_edit_word = 2
      # Try going word by word through a title and make sure at max one edit away!
      query_words = re.findall(r'\w+', movie_title.lower())
      # Keep track of all possible titles substrings that are correct spellings
      correct_spellings = set()

      for i, v in enumerate(self.titles):
        # Handle removing the final date plus any An|The|A that is at very end
        test_title = re.sub(r'((, an \(\d\d\d\d\))|(, the \(\d\d\d\d\))|(, a \(\d\d\d\d\))|(\(\d\d\d\d\)))$', "", v[0].lower())

        # Break the tital into individual words
        title_words = re.findall(r'\w+', test_title)

        # Allow up to one error per word
        # Only consider words in length of query (i.e. allows for disambiguoizing)
        #if len(query_words) == len(title_words):
        title_substring = ''
        if len(query_words) <= len(title_words):
          acceptable_error = True
          total_error = 0
          #for x in range(len(title_words)):
          for x in range(len(query_words)):
            # Add the title word to our built up substring
            title_substring += title_words[x] + ' '
            distance = self.edit_distance(title_words[x], query_words[x], max_edit_word)
            total_error += distance
            if (distance > max_edit_word or (total_error > max_edit)):# and max_edit != 1)):
              if title_words[x] == 'Scream': print 'here'
              acceptable_error = False
              break

          # Add the word if has one error per word
          if acceptable_error:
            title_substring = title_substring.strip()
            correct_spellings.add(title_substring)
            indices.append(i)

      indices_2 = []
      for possible_titles in correct_spellings:
        indices_3 = self.isTitleInLevel1(movie_title)
        if len(indices) == 0:
            indices_3 = self.isTitleInLevel4(movie_title)
        indices_2.extend(indices_3)

      print "Spell check", time.time() - start_time, "to run"

      return indices_2

    def isTitleInLevel1(self, inpt_title):
        # Check exact match
        print "Level 1 titlesearch"
        #TODO: ACCOUNT FOR AMERICAN IN PARIS, AN, HARRY POTTER AND
        indices = []
        indices = [i for i, v in enumerate(self.titles)
                    if self.removeArticles(inpt_title) == self.removeArticles(v[0])]
        return indices

    def isTitleInLevel2(self, inpt_title):
        # Check but with dates irrelevent
        print "Level 2 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.titles)
                    if self.removeDate(self.removeArticles(inpt_title)) ==
                       self.removeDate(self.removeArticles(v[0]))]
        return indices

    def isTitleInLevel3(self, inpt_title):
        # account for subtitles
        print "Level 3 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.titles)
                    if self.removeAfterColon(self.removeDate(self.removeArticles(inpt_title))) ==
                       self.removeAfterColon(self.removeDate(self.removeArticles(v[0])))]
        return indices

    def isTitleInLevel4(self, inpt_title):
        # account for sequels as well
        print "Level 4 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.titles)
                    if self.removeSequel(self.removeAfterColon(self.removeDate(self.removeArticles(inpt_title)))) ==
                       self.removeSequel(self.removeAfterColon(self.removeDate(self.removeArticles(v[0]))))]
        return indices

    def isTitleInLevel5(self, inpt_title):
        # All bets are off, just substring
        print "Level 5 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.titles)
                    if self.removeArticles(inpt_title) in self.removeArticles(v[0])]
        return indices

    def removeArticles(self, movie_title):
        #Preprocess movie_titles: Lowercase; remove a, an, the at beg
        # MUST BE CALLED AFTER removeDate
        movie_title = movie_title.lower()
        title_regex1 = r'^((an )|(the )|(a ))'
        #title_regex2 = r'(?:, an (\(\d\d\d\d\)))|(?:, the (\(\d\d\d\d\)))|(?:, a (\(\d\d\d\d\)))'
        title_regex_the = r', the (\(\d\d\d\d\))'
        title_regex_an = r', an (\(\d\d\d\d\))'
        title_regex_a = r', a (\(\d\d\d\d\))'
        if re.search(title_regex1, movie_title):
            movie_title = re.sub(title_regex1, r'', movie_title)
        elif re.search(title_regex_the, movie_title):
            movie_title = re.sub(title_regex_the, r' \1', movie_title)
        elif re.search(title_regex_an, movie_title):
            movie_title = re.sub(title_regex_an, r' \1', movie_title)
        elif re.search(title_regex_a, movie_title):
            movie_title = re.sub(title_regex_a, r' \1', movie_title)
        # Remove trailing whitespace
        movie_title = movie_title.strip()

        return movie_title

    def removeDate(self, movie_title):
        date_regex = r'\(\d\d\d\d\)'
        if re.search(date_regex, movie_title):
            movie_title = re.sub(date_regex, "", movie_title)
        movie_title = movie_title.strip()

        return movie_title

    def removeAfterColon(self, movie_title):
        colon_regex = r'^(.*?):.*'
        if re.search(colon_regex, movie_title):
            movie_title = re.findall(colon_regex, movie_title)[0]
            #print "Movie title after colon: " + movie_title
        movie_title = movie_title.strip()

        return movie_title

    def removeSequel(self, movie_title):
        #TODO: FILL OUT SEQUELS
        sequel_regex = r'(.*) (?:\d|i|ii|iii)$'
        if re.search(sequel_regex, movie_title):
            movie_title = re.findall(sequel_regex, movie_title)[0]
            #print "Movie title after sequel: " + movie_title
        movie_title = movie_title.strip()

        return movie_title

    def isMovie(self, movie_title):
        # Search for query as substring of movie title
        # TODO: This does not quite work ex. search for "The Little Mermaid (1989)"
        print "Movie: " + movie_title
        indices = self.isTitleInLevel1(movie_title)
        if len(indices) == 0:
            indices = self.isTitleInLevel4(movie_title)
            if len(indices) == 0:
                indices = self.isTitleInLevel5(movie_title)
            """
            if len(indices) == 0:
                indices = self.isTitleInLevel3(movie_title)
                if len(indices) == 0:
                    indices = self.isTitleInLevel4(movie_title)
            """

        # SPELLCHECK

        # If no substrings found try checking for miss-spelling
        # Try maybe to allow for different versions of the movie?
        if len(indices) == 0:
          '''
          # Set the max edit distance to be one edit per word
          # TODO: consider different strategies

          start_time = time.time()
          # Find movie titles that are max edit distance or less away
          #indices = [i for i, v in enumerate(self.titles) if self.edit_distance(v[0].lower(), movie_title, max_edit) <= max_edit]

          # Try removing the year from query and title!
          movie_title = re.sub(r'\(\d\d\d\d\)', "", movie_title)

          # Maximum edit distance stuff
          max_edit = len(re.findall(r'\w+', movie_title))
          max_edit_word = 2
          # Try going word by word through a title and make sure at max one edit away!
          query_words = re.findall(r'\w+', movie_title.lower())
          for i, v in enumerate(self.titles):
            # Handle removing the final date plus any An|The|A that is at very end
            test_title = re.sub(r'((, an \(\d\d\d\d\))|(, the \(\d\d\d\d\))|(, a \(\d\d\d\d\))|(\(\d\d\d\d\)))$', "", v[0].lower())

            # Try removing 'the', 'an', 'a'
            # Make this specific Be careful with an in the middle!
            #test_title = re.sub(r'(, an )|(, the )|(, a )', "", test_title)

            title_words = re.findall(r'\w+', test_title)

            # Allow up to one error per word
            # Only consider words in length of query (i.e. allows for disambiguoizing)
            #if len(query_words) == len(title_words):
            if len(query_words) <= len(title_words):
              acceptable_error = True
              total_error = 0
              #for x in range(len(title_words)):
              for x in range(len(query_words)):
                distance = self.edit_distance(title_words[x], query_words[x], max_edit_word)
                total_error += distance
                if (distance > max_edit_word or (total_error > max_edit)):# and max_edit != 1)):
                  if title_words[x] == 'Scream': print 'here'
                  acceptable_error = False
                  break

              # Add the word if has one error per word
              if acceptable_error:
                indices.append(i)

          print "Spell check", time.time() - start_time, "to run"
          '''
          indices = self.spellCheck(movie_title)

        return indices

    def askForSelection(self, movie_indexes):
        bot_prompt = "\001\033[96m\002%s> \001\033[0m\002" % self.name
        print bot_prompt + "I know of more than one movie with that name. Which one were you referring to?"
        for i, movie_index in enumerate(movie_indexes):
            print str(i + 1) + ") " + self.titles[movie_index][0]
        print "Please tell me a number from 1 to " + str(len(movie_indexes)) + " or the movie name."
        print "If the movie you are looking for is not listed above, please type \"next\"."

        while True:
            inpt = raw_input("> ")
            if inpt.isdigit():
                #TODO IS THIS BUG FREE??
                index = int(inpt)
                if index >= 1 and index <= len(movie_indexes):
                    print movie_indexes[index - 1]
                    return movie_indexes[index - 1]
                else:
                    print bot_prompt + "Please enter a valid input."
            elif inpt == "next":
                self.skip_to_next = True
                return None
            elif len(inpt) != 0:
                # Check if this is a movie name
                temp = self.isMovie(inpt)
                if len(temp) == 1:
                    return movie_indexes[0]
                elif len(temp) == 0:
                    print bot_prompt + "Sorry, I don't know the movie \"" + inpt + "\""
            # elif inpt == "more":
            #     print bot_prompt + "I know of more than one movie with the name \"" + inpt + "\". Which one were you referring to?"
            #     for i, movie_index in enumerate(temp):
            #         print str(i + 1) + ") " + self.titles[movie_index][0]
            #     print "Please tell me a number from 1 to " + str(len(temp)) + " or the movie name."
            #     movie_indexes = temp
            else:
                print bot_prompt + "Please enter a valid input."

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)

      self.move_article_to_front(self.titles)

      #Added for efficiency? -ND
      #self.titles = np.array(self.titles)

    def move_article_to_front(self, titles):
        for i,v in enumerate(titles):
            movie_title = v[0]
            date = re.findall(r'\(\d\d\d\d\)', movie_title)
            if len(date) != 0:
                date = date[0]
            else:
                date = ""


            if re.search(r'.*, The \(\d\d\d\d\)', movie_title):
                movie_title = re.sub(r', The \(\d\d\d\d\)', " " + date, movie_title)
                movie_title = "The " + movie_title
            elif re.search(r'.*, An \(\d\d\d\d\)', movie_title):
                movie_title = re.sub(r', An \(\d\d\d\d\)', " " + date, movie_title)
                movie_title = "An " + movie_title
            elif re.search(r'.*, A \(\d\d\d\d\)', movie_title):
                movie_title = re.sub(r', A \(\d\d\d\d\)', " " + date, movie_title)
                movie_title = "A " + movie_title

            titles[i][0] = movie_title

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      #TODO: This takes a whole, should we change it?
      #Threshold for binarizing movie rating matrix
      threshold = 3

      binarized_matrix = [[0 if i == 0 else -1 if i - threshold <= 0 else 1 for i in line] for line in self.ratings]
      self.ratings = binarized_matrix

      #TODO: test harness. REMOVE
      """
      for i in range(len(self.ratings)):
          for j in range(len(self.ratings[i])):
              original = self.ratings[i][j]
              binarized = binarized_matrix[i][j]
              #print "Original: " + str(original) + " Binarized: " + str(binarized)
              if original == 0:
                  if binarized != 0:
                      print "0 - MISTAKE"

              if original == 3:
                  if binarized != -1:
                      print "3 - MISTAKE"

              if original == 3.5:
                  if binarized != 1:
                      print "1 - MISTAKE"
      """

    def stemLexicon(self):
      stemmedLex = {}
      for word in self.sentiment:
        stemmedLex[self.stem(word)] = self.sentiment[word]
      self.sentiment = stemmedLex

    def stemPos_Neg_Words(self):
      stemmedPos = set()
      for word in self.strong_pos:
        stemmedPos.add(self.stem(word))
      self.strong_pos = stemmedPos

      stemmedNeg = set()
      for word in self.strong_neg:
        stemmedNeg.add(self.stem(word))
      self.strong_neg = stemmedNeg

    def stem(self, word):
      return self.p.stem(word)

    def sentimentClass(self, inputString):
      posCount = 0.0
      negCount = 0.0
      strongPosCount = 0.0
      strongNegCount = 0.0
      inputString.lower()
      inputString = re.sub(r'\".*\"', '', inputString)
      inputString = inputString.split()

      # negate things first
      temp = []
      negate = False
      for word in inputString:
          if word in self.negations:
              temp.append(word)
              if negate:
                  negate = False
              else:
                  negate = True
              continue
          elif word[0] in self.punctuations: # To catch case of repeated punction like !!!! or
              temp.append(word)
              negate = False
              continue

          # temp.add(word if !negate else "NOT_"+word)
          if negate:
              temp.append("NOT_" + word)
          else:
              temp.append(word)
      inputString = temp

      # Keep track of how many intensifiers appear in a row
      # e.g. really reaallly like
      intensifier_count = 0
      for word in inputString:
        # Should we include strong sentiment with not?
        if "NOT_" in word:
            print word

            word = word.replace("NOT_", "")
            word = self.stem(word)
            if word in self.sentiment:
              added_sent = 1
              #For each intensier we double added score
              #added_sent *= 2 * intensifier_count if intensifier_count > 0 else 1
              if self.sentiment[word] == 'pos':
                negCount += added_sent
                strongNegCount += intensifier_count
              elif self.sentiment[word] == 'neg':
                posCount += added_sent
                strongPosCount += intensifier_count

              # No longer intensifying
              intensifier_count = 0
        else:
            # See if our word is an intensifier
            for intens in self.intensifiers:
              # Match our word against intensifier regexes
              if re.compile(intens).match(word):
                intensifier_count += 1
                continue

            word = self.stem(word)
            if word in self.sentiment:
              # Fine-grained sentiment
              # normal pos/neg words have score 1
              # strong pos/neg have score of 3
              # intensifiers double word score
              added_sent = 1
              if self.sentiment[word] == 'pos':
                print "pos: %s" % (word)
                if word in self.strong_pos:
                  #added_sent += 2
                  strongPosCount += 1
                #added_sent *= 2 * intensifier_count if intensifier_count > 0 else 1
                posCount += added_sent
                strongPosCount += intensifier_count
              elif self.sentiment[word] == 'neg':
                print "neg: %s" % (word)
                if word in self.strong_neg:
                  #added_sent += 2
                  strongNegCount += 1
                #added_sent *= 2 * intensifier_count if intensifier_count > 0 else 1
                negCount += added_sent
                strongNegCount += intensifier_count

              # No longer intensifying
              intensifier_count = 0

      #TODO: Account for ! - multiply by 2 even for !+
      final_score = posCount - negCount
      #final_score *= 2 if intensifier_count > 0 else 1
      if final_score > 0 and strongNegCount <= strongPosCount: # Positive overall so make strong pos if '!' (But don't override strong neg)
        strongPosCount += intensifier_count
      elif final_score < 0 and strongPosCount <= strongNegCount: # Negative overall so make strong neg if '!' (But don't override strong pos)
        strongNegCount += intensifier_count

      # Just check if strong pos exist or strong neg exist and intensifier can boost the
      # non strong to a strong

      # DEBUGGING TODO:REMOVE
      # print "Count of word: " + word + " pos: " + str(posCount) + " neg: " + str(negCount)

      #TODO: Catch no sentiment or unclear sentiment!
      #TODO: Create stronger cutoffs for very strong / neg sentiment
      if posCount == 0.0 and negCount == 0.0: return 'none'
      elif strongPosCount > strongNegCount: return 'str_pos'
      elif strongPosCount < strongNegCount: return 'str_neg'
      elif final_score == 0: return 'unclear'
      #elif final_score >= 2: return 'str_pos' # Decide if 2 or 3???
      #elif final_score <= -2: return 'str_neg' # Decide if 2 or 3???
      elif final_score > 0: return 'pos'
      else: return 'neg'

    def distance(self, u, lenU, v, lenV):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      dotProd = np.dot(u, v)
      # TODO: Remove these as if we use this function we will likely
      # pre-process these
      #lenU = np.linalg.norm(u)
      #lenV = np.linalg.norm(v)
      if lenU != 0 and lenV != 0:
        return float(dotProd) / (lenU * lenV)
        #return dotProd
      else: return 0


    def recommend(self, u):
      # Probably want to add a parameter rec_num to allow for multiple
      # top recommendatoins
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot


      # TODO: Remove old implementation
      '''
      # Pre-calcute vector lengths for movies rated by user
      rated_vec_lengths = [np.linalg.norm(self.ratings[i]) for i in rated_movies]

      # Later to speed up we can pre load the movie rows of things we already rated

      # Time testing
      start_time = time.time()

      # Estimated user ratings
      est_ratings = []
      # Try with heap
      for i in range(len(self.titles)):
        # Only consider movies not already rated by u
        if not i in rated_movies:
          # Get the movie-vec from the matrix
          movie_vec = self.ratings[i]
          # Pre compute movie_vec length
          movie_vec_len = np.linalg.norm(movie_vec)

          est_rating = 0
          # Loop over the movies rated by u and use item-item collab filtering
          for inx, user_rating in enumerate(u):
            # Get the vector for the users movie
            usr_movie_vec = self.ratings[user_rating[0]]
            # Users rating
            rating = user_rating[1]

            # Estimate the rating of movie i
            est_rating += self.distance(movie_vec, movie_vec_len, usr_movie_vec, rated_vec_lengths[inx]) * rating

          # Add new estimated rating
          #est_ratings.append((i, est_rating))
          # Invert rating for putting into heap
          heapq.heappush(est_ratings, (est_rating * -1, i))
      '''

      # Sort the estimated rating in reverse order
      #sorted_movies = sorted(est_ratings, key=lambda movie_rating:movie_rating[1], reverse=True) # Sort by rating



      # Assume you is a sparse vector of the form
      # [(movie index, movie rating), ...]

      # Create list of indexes of movies that we have for simplicity
      rated_movies = [tup[0] for tup in u]

      # Create a matrix with the (normalized movie vectors rated by usr) as the rows
      norm_usr_movies = np.array([np.array(self.ratings[i]) / (float(np.linalg.norm(self.ratings[i])) \
                                          if float(np.linalg.norm(self.ratings[i])) != 0 else 1) for i in rated_movies])
      # Usr ratings array
      ratings_usr = np.array([tup[1] for tup in u])
      # Sum vector of all [1,...,1]
      ones = np.ones(len(rated_movies))

      # TODO: Remove test harness
      # Time testing
      start_time = time.time()

      est_ratings = []
      for i in range(len(self.titles)):
        if not i in rated_movies:
          # Get the normalized movie vec we want to generate a rating for
          movie_norm = float(np.linalg.norm(self.ratings[i]))
          movie_vec = np.array(self.ratings[i]) / (movie_norm if movie_norm != 0 else 1)

          # Cosine similarity
          cosine_sim = np.dot(norm_usr_movies, movie_vec)
          # Element wise multiply by rating
          rating_scaled = np.multiply(cosine_sim, ratings_usr)

          # Sum all the elements by taking dot with [1,...,1]
          est_rating = np.dot(rating_scaled, ones)

          # Invert rating for putting into min-heap
          # May want to consider using array rather than heap
          heapq.heappush(est_ratings, (est_rating * -1, i))

      # Return a string with the top three movies
      # Note: we pop from the heap, may want to add back to keep list of ratings
      movie_to_recomend = ''
      for i in range(self.numRecs):
        movie_to_recomend += str(i + 1) + ') ' + self.titles[heapq.heappop(est_ratings)[1]][0] + '\n'

      # Remove the last \n
      movie_to_recomend = movie_to_recomend[:-1]


      print "Recommend took", time.time() - start_time, "to run"

      '''
      # Print top 50
      for i in range(50):
        #print '%s rated %f' % (self.titles[sorted_movies[i][0]][0], sorted_movies[i][1])
        movie_i = heapq.heappop(est_ratings)
        print '%s rated %f' % (self.titles[movie_i[1]][0], movie_i[0] * -1)
      '''

      return movie_to_recomend



    def split_into_sentences(self, text):
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
        if "e.g." in text: text = text.replace("e.g.","e<prd>g<prd>")
        if "i.e." in text: text = text.replace("i.e.","i<prd>e<prd>")
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences
    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
