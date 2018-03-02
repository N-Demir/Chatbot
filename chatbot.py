#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
#
#TODOS: be snobby if they change
#####################################################################import csv
import math
import re
import csv
import copy

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
      self.NUMBER_TILL_REC = 5
      self.name = 'moviebot'

      #flags
      self.is_turbo = is_turbo
      self.is_repeat = False
      self.selection = False
      self.quotationFound = False
      self.unknown_movie = False

      # When a movie is talked about more than once
      self.repeatedMovie = False
      self.newSentiment = None
      self.repeatedIndx = -1

      # Flags for previous referencing
      self.no_sentiment = False
      self.previous_sentiment = None
      self.previous_movie = None
      self.spellChecking = False
      self.DONOTTOUCHME_TOY_STORY = False
      self.spellCheckPerformed1 = False # flag for confirmation of movie title
      self.spellCheckPerformed2 = False # flag for yes/no from user
      self.spell_check_sent = None
      self.spell_check_index = None
      self.spell_check_input = None

      # Flags for recommending movies
      self.get_recommend_date = False
      self.get_recommend_genre = False
      self.date_range = None
      self.give_rec = False
      self.use_date_range = False
      self.use_genre = False
      self.genre = None

      self.sentiment = {}
      self.usr_rating_vec = []
      self.numRatings = 5
      self.numRecs = 3
      self.movie_count = 0
      self.read_data()
      self.p = PorterStemmer()
      self.stemLexicon()
      self.binarize()

      self.negations = open("data/negations.txt", "r").read().splitlines()
      self.punctuations = open('data/punctuation.txt', "r").read().splitlines()
      self.strong_neg = open('data/strong_neg_words.txt', "r").read().splitlines()
      self.strong_pos = open('data/strong_pos_words.txt', "r").read().splitlines()
      self.intensifiers = open('data/intensifiers.txt', "r").read().splitlines()
      self.jokes = open('data/intensifiers.txt', "r").read().splitlines()
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

      goodbye_message = 'Have a nice day! It was great chatting!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      # For debug
      #print input
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
      if self.is_repeat: return self.getRepeatResponse(input)

      # Deal with repeated talking about movies
      if self.repeatedMovie: return self.updateResponse(input)

      # See if we are responding to spell check
      if self.spellCheckPerformed2: return self.spellCheckFeedback(input)

      # Get whether they want a date range for their rec
      #if self.get_recommend_date: response = self.recommend_date(input)
      if self.get_recommend_date: return self.recommend_date(input)

      if self.get_recommend_genre: response = self.recommend_genre(input)

      # Give the recommendation!
      if self.give_rec:
        continue_response = 'Hope these recommendations help! Please choose one of the options below by typing 1, 2, or 3.\n'
        continue_response += '1. Quit\n'
        continue_response += '2. Add additional movie ratings for more recommendations.\n'
        continue_response += '3. Restart with new ratings for new recommendations.'
        self.is_repeat = True
        self.give_rec = False
        return response + '\n' + 'Here\'s what I\'ve got for you:\n' + self.getRec() + '\n' + continue_response

      # Process movie title
      temp = self.processTitle(input)
      movie_tag = temp[0]
      old_input = input
      input = temp[1]
      # Get the flag indicating success of process Title
      movie_flag = movie_tag[1]
      if movie_flag == -1: # No movies found
          if self.no_sentiment and self.sentimentForPreviousMention(old_input): # Try to see if we can use previous info
            # Function to check for previous movie reference
            sentiment = self.sentimentClass(old_input) # We have to worry maybe if they still have no sentiment
            response = self.processMovieAndSentiment(sentiment, self.previous_movie, old_input)
            self.no_sentiment = False
          elif self.no_sentiment:
              return "Hm, unfortunately I still can't tell how you feel about \"" + self.titles[self.previous_movie][0] + "\". Could you fill me in?"
          elif self.unknown_movie:
            # Handle arbitrary input
            arbResp = self.getArbitraryResponse(input)
            if arbResp != None: return arbResp
            responses = []
            responses.append("Hey, let's chat about movies!")
            responses.append("Let's get back to talking about movies!")
            return responses[randint(1, len(responses)-1)]
          else:
            self.unknown_movie = True
            return self.noMovieResponse()
      elif movie_flag == 1: # Movie found
          movie_title = movie_tag[0]
          movie_indexes = self.isMovie(movie_title)
          # Added
          self.quotationFound = False

          if len(movie_indexes) != 0: # Good movie!
            # Undo ceratin flags!
            self.unknown_movie = False

            # Need to encorperate the sentiment
            #self.usr_rating_vec.append((movie_index, 1))
            #response = "Sentiment for " + movie + " is " + self.sentimentClass(input)

            # We have received a valid movie so we have to extract sentiment,
            # record the movie rating based on sentiment, and respond reflecting
            # the sentiment.
            response = ''
            sentiment = self.sentimentClass(input)
            movie_index = self.getMovieIndex(movie_indexes)

            # Check if movie index is already been seen
            location_already_discussed = -1
            for i in range(len(self.usr_rating_vec)):
              if self.usr_rating_vec[i][0] == movie_index:
                location_already_discussed = i
                break

            if (location_already_discussed != -1):
              # Compare the sentiment
              response = self.redundantInfo(sentiment, self.usr_rating_vec[i][2])
              self.newSentiment = sentiment
              self.repeatedIndx = location_already_discussed
            elif (movie_index != None):
              # Check if movies were spell checked
              if self.spellCheckPerformed1:
                title = self.titles[movie_index][0]
                self.spellCheckPerformed1 = False
                self.spellCheckPerformed2 = True
                self.spell_check_sent = sentiment
                self.spell_check_index = movie_index
                self.spell_check_input = old_input
                return "Did you mean the movie \"" + title + "\"?"

              response = self.processMovieAndSentiment(sentiment, movie_index, old_input)
            else:
              response = "Ok, tell me about another movie."

          else: # Unknown movie
            if self.no_sentiment and self.sentimentForPreviousMention(old_input): # Try to see if we can use previous info
              # Function to check for previous movie reference
              sentiment = self.sentimentClass(old_input) # We have to worry maybe if they still have no sentiment
              response = self.processMovieAndSentiment(sentiment, self.previous_movie, old_input)
              self.no_sentiment = False
            elif self.no_sentiment:
              return "Hm, unfortunately I still can't tell how you feel about \"" + self.titles[self.previous_movie][0] + "\". Could you fill me in?"
            else:
              if self.unknown_movie:
                # Handle arbitrary input
                arbResp = self.getArbitraryResponse(input)
                if arbResp != None: return arbResp
                return "Darn, I can't seem to remember that movie. Sorry about that! I promise I'll know the next one."
              self.unknown_movie = True
              return "Unfortunately I have never seen that movie, but I would love to hear about other movies that you have seen."
      else:
        return "Please tell me about one movie at a time. Go ahead."

      #print len(self.usr_rating_vec)
      if (len(self.usr_rating_vec) == self.numRatings):
        self.get_recommend_date = True

        responses = []
        responses.append('I think I am getting to know you a bit better, and I want to blow you away with some amazing movie recommendations. ')
        responses.append('Ok, I am ready to give you some movie recommendations! ')
        responses.append('Get ready for the big movie recommendations reveal! ')
        responses.append('Almost ready to give you your recommendations! ')
        responses.append('Now I think I have a good sense of some movies you would love. ')
        recommend_response = responses[randint(1, len(responses)-1)]
        recommend_response += 'First, though, would you like movies from a specific time period? e.g. ranges (2000-2005 or 2000+ or no).'

        # Return our response plus our recommendation
        return response + '\n' + recommend_response

      return response


    def getRec(self):
      recommendations = self.recommend(self.usr_rating_vec)
      movies_to_recommend = ''
      if self.use_genre and self.use_date_range:
        movie_count = 0
        while movie_count < self.numRecs and len(recommendations) > 0:
          movie_id = heapq.heappop(recommendations)[1]
          genres = self.titles[movie_id][1].lower()
          movie = self.titles[movie_id][0]
          date = re.findall(r'(\d\d\d\d)', movie)
          if len(date) > 0:
            date = int(date[0])
          else:
            date = 3001 # Out of max range
          if date >= int(self.date_range[0]) and date <= int(self.date_range[1]) and self.genre.lower() in genres:
            #print 'here'
            movie_count += 1
            movies_to_recommend += str(movie_count) + ') ' + movie + '\n'
      elif self.use_genre:
        movie_count = 0
        while movie_count < self.numRecs and len(recommendations) > 0:
          movie_id = heapq.heappop(recommendations)[1]
          genres = self.titles[movie_id][1].lower()
          movie = self.titles[movie_id][0]
          if self.genre.lower() in genres:
            movie_count += 1
            movies_to_recommend += str(movie_count) + ') ' + movie + '\n'
      elif self.use_date_range:
        movie_count = 0
        while movie_count < self.numRecs and len(recommendations) > 0:
          movie = self.titles[heapq.heappop(recommendations)[1]][0]
          date = re.findall(r'(\d\d\d\d)', movie)
          if len(date) > 0:
            date = int(date[0])
          else:
            date = 3001 # Out of max range
          if date >= int(self.date_range[0]) and date <= int(self.date_range[1]):
            #print 'here'
            movie_count += 1
            movies_to_recommend += str(movie_count) + ') ' + movie + '\n'
      else:
        for i in range(self.numRecs):
          movies_to_recommend += str(i + 1) + ') ' + self.titles[heapq.heappop(recommendations)[1]][0] + '\n'
      return movies_to_recommend


    def spellCheckFeedback(self, input):
      no_regex = r'(?:^[Nn]o|^[Nn]ope)'
      yes_regex = r'(?:^[Yy]es|^I did )'

      self.spellCheckPerformed2 = False
      if re.match(yes_regex, input):
        return "Sweet!\n" + self.processMovieAndSentiment(self.spell_check_sent, self.spell_check_index, self.spell_check_input)
      elif re.match(no_regex, input):
        return "Oops sorry. Hopefully I'll understand the next movie better"
      else:
        self.spellCheckPerformed2 = True
        return "Could you clarify with a yes or no?"


    def recommend_date(self, input):
      no_regex = r'(?:^[Nn]o|^[Nn]ope)'
      date_range_regex = r'(\d\d\d\d)-(\d\d\d\d)'
      one_date_regex = r'(\d\d\d\d)\+'
      self.get_recommend_date = False
      self.get_recommend_genre = True
      #self.give_rec = True
      if re.search(no_regex, input):
        responses = []
        responses.append("No problem!")
        responses.append("No worries!")
        responses.append("Ok, thanks!")
        return responses[randint(1, len(responses)-1)]
      elif re.search(date_range_regex, input):
        self.date_range = [re.findall(date_range_regex, input)[0][0], re.findall(date_range_regex, input)[0][1]]
        self.use_date_range = True
        return 'Awesome! We will take this into consideration.\nIs there a particular genre that you want e.g. (adventure) use \'no\' to quite'
      elif re.search(one_date_regex, input):
        self.date_range = [re.findall(one_date_regex, input)[0], 3000]
        self.use_date_range = True
        return 'Awesome! We will take this into consideration.\nIs there a particular genre that you want e.g. (adventure). Use \'no\' to quite'
      else:
        self.get_recommend_date = True
        self.get_recommend_genre = False
        #self.give_rec = False
        return "Sorry, I didn't quite get that. Please enter a response like one of the following formats: 2000-2003, 1995+, no"


    def recommend_genre(self, input):
      no_regex = r'(?:^[Nn]o|^[Nn]ope)'
      self.recommend_genre = False
      self.give_rec = True
      if re.search(no_regex, input):
        responses = []
        responses.append("No problem!")
        responses.append("No worries!")
        responses.append("Ok, thanks!")
        return responses[randint(1, len(responses)-1)]
      else: # Assume input is genre!
        self.genre = input
        self.use_genre = True
        return "Perfect! We can look for movies in this genre"


    def updateResponse(self, input):
      yes_regex = r'(?:^[Yy]es|^I do )'
      no_regex = r'(?:^[Nn]o|^[Nn]ope)'

      # Check if they respond yes and want to update
      if re.search(yes_regex, input):
        if self.newSentiment == 'pos':
          self.usr_rating_vec[self.repeatedIndx] = (self.usr_rating_vec[self.repeatedIndx][0], .5, self.newSentiment)
        elif self.newSentiment == 'neg':
          self.usr_rating_vec[self.repeatedIndx] = (self.usr_rating_vec[self.repeatedIndx][0], -.5, self.newSentiment)
        elif self.newSentiment == 'str_pos':
          self.usr_rating_vec[self.repeatedIndx] = (self.usr_rating_vec[self.repeatedIndx][0], 1, self.newSentiment)
        elif self.newSentiment == 'str_neg':
          self.usr_rating_vec[self.repeatedIndx] = (self.usr_rating_vec[self.repeatedIndx][0], -1, self.newSentiment)

        self.repeatedMovie = False

        return "Got it, thanks! I just updated your opinion. Let's hear about another movie."
      elif re.search(no_regex, input): # Check if they want to keep it as was
        self.repeatedMovie = False
        return "Sounds good, I agree with your first assessment! What's next?"
      else: # Unclear answer
        return "Sorry, I am not quite sure if you would like me to update your preference?"


    def redundantInfo(self, sentiment, old_sentiment):
      if sentiment == old_sentiment or sentiment == 'none' or sentiment == 'unclear':
        if old_sentiment == 'pos': return "Right, we talked about this movie earlier! You mentioned that you liked this movie."
        elif old_sentiment == 'neg': return "Right, we talked about this movie earlier! You mentioned that you didn't like this movie."
        elif old_sentiment == 'str_pos': return "Right, we talked about this movie earlier! You loved it!"
        else: return "Right, we talked about this movie earlier! You hated it!"
      else:
        self.repeatedMovie = True
        if old_sentiment == 'pos': return "Hm, earlier you mentioned that you liked this movie. Do you want to change your opinion?"
        elif old_sentiment == 'neg': return "Interesting, earlier you said that you disliked this movie. Do you want to change your opinion?"
        elif old_sentiment == 'str_pos': return "I though you loved this movie, do you want me to update how you feel about this movie?"
        else: return "I though you hated this movie, do you want me to update how you feel about this movie?"


    def sentimentForPreviousMention(self, input):
      it_regex = r'(?:^|[\W])[iI]t(?:$|[\W])'
      that_movie_regex = r'((?:^|[\W])[tT]hat movie(?:$|[\W]))'
      # Look for reference to previous said movie
      if re.search(it_regex, input) or re.search(that_movie_regex, input):
        return True
      return False


    def useSentimentFromPrevious(self, input):
      opposite_regex = r'(?:^But not )'
      same_begin_regex = r'(?:And | Also | Plus)'
      same_in_regex = r'(?: same (.*?) that(?:$|\W)| similar (.*?) that(?:$|\W))'

      if re.search(same_begin_regex, input) or re.search(same_in_regex, input):
        return 'same'
      elif re.search(opposite_regex, input):
        return 'op'
      else:
        return 'UNK'


    def getRepeatResponse(self, input):
      if input == '1':
          return "Please type \":quit\""
      elif input == '2':
          self.is_repeat = False
          self.numRatings += 3
          return "Ok, let's continue! Please tell me about another movie you've seen."
      elif input == '3':
          self.is_repeat = False
          self.usr_rating_vec = []
          self.numRatings = self.NUMBER_TILL_REC
          return "Great! Let's explore some new movies. Just like before, what are some movies I can base my recommendation off of?"
      else:
          return "I'm sorry, I don't understand your input. Please enter a number 1, 2, or 3."


    def getArbitraryResponse(self, input):
      input = input.lower()
      q0 = r'^hi|hello'
      q2 = r'what(?:\'s | is )your name'
      q7 = r'who are you'
      q4 = r'do you love me'
      q6 = r'tell me a joke'
      q1 = r'(?:how)?(\'s | is | are )(you|it)(?: doing| going)?(?: ok| well)?'
      q3 = r'how(?:\'s | is | has | was )your (?:day|night|evening|morning|afternoon)'
      q5 = r'^no\.?$'
      q10 = r'^can ([^?]*)(?:\?)?'
      basicQ1 = r'^(can|what|where|why|how|are|aren\'t) ([^?]*)(?:\?)?'
      basicQ2 = r'\?$'

      r0 = re.findall(q0, input)
      if len(r0) != 0:
        return "Hello! Tell me about a movie you've seen."
      r2 = re.findall(q2, input)
      r7 = re.findall(q7, input)
      if len(r2) != 0 or len(r7) != 0:
        return "My name is " + self.name + ". Now what is a movie you have an opinion about?"
      r4 = re.findall(q4, input)
      if len(r4) != 0:
        return "Yes, I love everyone. Now I know there are some movies you love - tell me about one."
      r1 = re.findall(q1, input)
      if len(r1) != 0:
        responses = []
        responses.append("I am well, but I would be even better if you told me about a movie.")
        responses.append("I'm fine. Is there a movie you can tell me about?")
        responses.append("I'm great! Can you tell me about a movie you have seen?")
        return responses[randint(1, len(responses)-1)]
      r3 = re.findall(q3, input)
      if len(r3) != 0:
        return "It has been good! Let's talk about some movies now."
      r5 = re.findall(q5, input)
      if len(r5) != 0:
        return "Yes, please."
      r6 = re.findall(q6, input)
      if len(r6) != 0:
        return self.jokes[randint(0, len(self.jokes))]
      # r10 = re.findall(q10, input)
      # if len(r10) != 0: return "I don't know, can " + r10[0] + "?"
      rbasic1 = re.findall(basicQ1, input)
      if len(rbasic1) != 0:
        responses = []
        responses.append("Hey, I'm the one asking the questions here! What is your opinion on a movie you have seen?")
        responses.append("Enough questions, let's get to the movies! Can you tell about one you have seen?")
        responses.append("I'll have to think about that. In the meantime, let's talk about some movies.")
        responses.append("I don't know, " + str(rbasic1[0][0]) + " " + str(rbasic1[0][1]) + "?")
        responses.append("I don't know, " + str(rbasic1[0][0]) + " " + str(rbasic1[0][1]) + "?")
        responses.append("I don't know, " + str(rbasic1[0][0]) + " " + str(rbasic1[0][1]) + "?")
        return responses[randint(1, len(responses)-1)]
      rbasic2 = re.findall(basicQ2, input)
      if len(rbasic2) != 0:
        responses = []
        responses.append("Hey, I'm the one asking the questions here! What is your opinion on a movie you have seen?")
        responses.append("Enough questions, let's get to the movies! Can you tell about one you have seen?")
        responses.append("I'll have to think about that. In the meantime, let's talk about some movies.")
        return responses[randint(1, len(responses)-1)]
      return None


    def processMovieAndSentiment(self, sentiment, movie_index, input):
      self.previous_movie = movie_index
      response = ''
      if sentiment == 'pos':
        self.no_sentiment = False
        self.usr_rating_vec.append((movie_index, .5, 'pos'))
        self.previous_sentiment = 'pos'
        response = self.getPosResponse(movie_index)
        if len(self.usr_rating_vec) < self.NUMBER_TILL_REC: response += self.getAddRequest()
        return response
      elif sentiment == 'str_pos':
        self.no_sentiment = False
        self.usr_rating_vec.append((movie_index, 1, 'str_pos'))
        self.previous_sentiment = 'str_pos'
        response = self.getStrPosResponse(movie_index)
        if len(self.usr_rating_vec) < self.numRecs: response += self.getAddRequest()
        return response
      elif sentiment == 'neg':
        self.no_sentiment = False
        self.usr_rating_vec.append((movie_index, -.5, 'neg'))
        self.previous_sentiment = 'neg'
        response = self.getNegResponse(movie_index)
        if len(self.usr_rating_vec) < self.numRecs: response += self.getAddRequest()
        return response
      elif sentiment == 'str_neg': # Don't yet deal with changing the rating
        self.no_sentiment = False
        self.usr_rating_vec.append((movie_index, -1, 'str_neg'))
        self.previous_sentiment = 'str_neg'
        response = self.getStrNegResponse(movie_index)
        if len(self.usr_rating_vec) < self.numRecs: response += self.getAddRequest()
        return response
      elif sentiment == 'none':
        #self.previous_movie = movie_index
        check_previous = self.useSentimentFromPrevious(input)
        if (check_previous == 'same') and self.previous_sentiment != None: # Test edge case
          return self.processMovieAndSentiment(self.previous_sentiment, movie_index, input)
        elif(check_previous == 'op'):
          negate = ''
          if self.previous_sentiment == 'pos': negate = 'neg'
          elif self.previous_sentiment == 'neg': negate = 'pos'
          elif self.previous_sentiment == 'str_pos': negate = 'neg' # Do we keep same
          elif self.previous_sentiment == 'str_neg': negate = 'pos'
          return self.processMovieAndSentiment(negate, movie_index, input)
        else:
          self.no_sentiment = True
          return self.getNoneResponse(movie_index)
      else: # Unclear sentiment
        # Try to see if they are referencing previous shit
        # Meaning that we have not been able to extract sentiment. They could
        # now reference previous info
        self.no_sentiment = True
        return self.getUnclearResponse(movie_index)


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

    def getAddRequest(self):
      addRequests = []
      addRequests.append(" What are some other movies you have seen?")
      addRequests.append(" What about another movie?")
      addRequests.append(" What's next?")
      addRequests.append(" Let's hear about another one.")
      addRequests.append(" Tell me about another one!")
      addRequests.append(" I'd love to here about other movies you have seen.")
      addRequests.append(" Any other movies you have an opinion about?")
      addRequests.append(" Can you tell me about another movie?")
      addRequests.append(" Tell me about another movie you have seen.")
      addRequests.append(" Is there another movie you can tell me about?")
      return addRequests[randint(1, len(addRequests)-1)]

    def noMovieResponse(self):
      responses = []
      responses.append("I'm sorry, I'm not sure what you mean. Tell me about a movie.")
      responses.append("Sorry, I don't quite understand. Tell me about a movie that you have seen.")
      responses.append("Let's get back to movies - I'd love to hear your opinion on one.")
      return responses[randint(1, len(responses)-1)]

    def getStrPosResponse(self, movie_index):
      responses = []
      responses.append("Awesome, you really liked \"" + self.titles[movie_index][0] + "\"!")
      responses.append("Great choice! That is an amazing movie. \"" + self.titles[movie_index][0] + "\".")
      responses.append("You loved \"" + self.titles[movie_index][0] + "\"!")
      responses.append("\"" + self.titles[movie_index][0] + "\" is a fantastic movie!!")
      responses.append("You were a huge fan of \"" + self.titles[movie_index][0] + "\"!")
      return responses[randint(1, len(responses)-1)]

    def getStrNegResponse(self, movie_index):
      responses = []
      responses.append("So you really disliked \"" + self.titles[movie_index][0] + "\".")
      responses.append("You hated \"" + self.titles[movie_index][0] + "\"! Thanks for the heads up.")
      responses.append("I see you really weren't a fan of \"" + self.titles[movie_index][0] + "\".")
      return responses[randint(1, len(responses)-1)]

    def getPosResponse(self, movie_index):
        responses = []
        responses.append("You liked \"" + self.titles[movie_index][0] + "\". Thank you!")
        responses.append("Ok, you enjoyed \"" + self.titles[movie_index][0] + "\".")
        responses.append("Great! I'm glad you liked \"" + self.titles[movie_index][0] + "\".")
        return responses[randint(1, len(responses)-1)]

    def getNegResponse(self, movie_index):
        responses = []
        responses.append("You did not like " + self.titles[movie_index][0] + ". Thank you!")
        responses.append("Ok, you disliked \"" + self.titles[movie_index][0] + "\".")
        responses.append("I'm sorry you did not enjoy \"" + self.titles[movie_index][0] + "\".")
        return responses[randint(1, len(responses)-1)]

    def getNoneResponse(self, movie_index):
        responses = []
        responses.append("Ok, thank you! Tell me your opinion on \"" + self.titles[movie_index][0] + "\".")
        responses.append("What did you think about \"" + self.titles[movie_index][0] + "\"?")
        responses.append("Did you like or dislike \"" + self.titles[movie_index][0] + "\"?")
        return responses[randint(1, len(responses)-1)]
        #TODO: REMEMBER PREVIOUS THING

    def getUnclearResponse(self, movie_index):
        responses = []
        responses.append("I'm sorry, I'm not quite sure if you liked \"" + self.titles[movie_index][0] + "\" Tell me more about \"" + self.titles[movie_index][0] + "\".")
        responses.append("I'm sorry, I can't quite tell what your opinion is on \"" + self.titles[movie_index][0] + "\". Can you tell me more?")
        responses.append("I'm not certain about your opinion on \"" + self.titles[movie_index][0] + "\". Could you tell me more about it?")
        return responses[randint(1, len(responses)-1)]

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
          # find movies not in quotation marks
          entity = self.findNonQuotationTitles(inpt)
          if len(entity) != 0:
              temp = entity
              #print "Movie: " + temp
              if re.search(r'\(.*\)', temp):
                  temp = re.sub(r'\(.*\)', "", temp)
              inpt = re.sub(temp, "", inpt)
              return ((entity, 1), inpt)
          # else we still found nothing
          return (("", -1), inpt)
        elif len(entities) == 1: # One movie found - flag 1
          self.quotationFound = False
          inpt = re.sub(movie_regex, "", inpt)
          return ((entities[0], 1), inpt)
        else: # Multiple movies found - flag 2
          #TODO: DO SOMETHING WITH THIS
          return ((entities, 2), inpt)


    def findNonQuotationTitles(self, inpt):
        # DOES NOT NEED FIRST LETTER CAPS, IS THAT OKAY?
        punctuations = '!.?'
        self.quotationFound = False

        inpt = re.sub(r'[!.?]', r'', inpt)
        temp2 = inpt.split()
        #print "INPUT: " + inpt
        inpt = inpt.lower()
        entities = []

        for entry in self.custom_titles:
            titles = re.findall("<>(.*?)</>", entry[0])
            for title in titles:
                movie_title = title
                movie_title = self.removeArticles(movie_title)

                movie_title = movie_title.split()
                #print "Movie title: " + str(movie_title)
                #TODO: Remove punctuations?

                for i, word in enumerate(inpt.split()):
                    if temp2[i][0].isupper() and movie_title[0] == word.lower():
                        #print "GOT HERE"
                        temp = ""
                        for j in range(0, min(len(movie_title), len(inpt.split()) - i)):
                            #print "INPUT" + str(inpt)
                            if inpt.split()[i] == movie_title[j]:
                                temp += " " + temp2[i]
                                i += 1
                            else:
                                break
                        temp = temp.strip()
                        entities.append(temp)

        if len(entities) == 0:
            return ""

        self.quotationFound = True
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

       #print str(sentences)
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
      query = self.removeArticles(query)
      query = self.removeDate(query)

      query_words = re.findall(r'\w+', query.lower())
      #query_words = query.lower().split()

      # Maximum edit distance stuff
      #max_edit = len(re.findall(r'\w+', query))
      max_edit = len(query_words)
      max_edit_word = 2
      # Try going word by word through a title and make sure at max one edit away!
      # Keep track of all possible titles substrings that are correct spellings
      correct_spellings = set()

      #for i, v in enumerate(self.titles):
      for i, entry in enumerate(self.custom_titles):
            titles = re.findall("<>(.*?)</>", entry[0])
            for title in titles:
              # Handle removing the final date plus any An|The|A that is at very end
              #test_title = re.sub(r'((, an \(\d\d\d\d\))|(, the \(\d\d\d\d\))|(, a \(\d\d\d\d\))|(\(\d\d\d\d\)))$', "", v[0].lower())
              #test_title = self.removeArticles(v[0].lower())
              test_title = self.removeArticles(title)
              test_title = self.removeDate(test_title)

              # Break the tital into individual words
              title_words = re.findall(r'\w+', test_title)
              #title_words = test_title.split()
              # Includes punction and stuff
              #title_actual = test_title.split()

              # Allow up to one error per word
              # Only consider words in length of query (i.e. allows for disambiguoizing)
              #if len(query_words) == len(title_words):
              title_substring = ''
              # Keep track of the last word seen
              last_word = ''
              if len(query_words) <= len(title_words):
                acceptable_error = True
                total_error = 0
                #for x in range(len(title_words)):
                for x in range(len(query_words)):
                  # Add the title word to our built up substring
                  title_substring += title_words[x] + ' '
                  last_word = title_words[x]
                  #print title_actual
                  #title_substring += title_actual[x] + ' '
                  distance = self.edit_distance(title_words[x], query_words[x], max_edit_word)
                  total_error += distance
                  if (distance > max_edit_word or (total_error > max_edit)):# and max_edit != 1)):
                    #f title_words[x] == 'Scream':#print 'here'
                    acceptable_error = False
                    break

                # Add the word if has one error per word
                if acceptable_error:
                  #title_substring = title_substring.strip()
                  # Get the location of the last word that matched as spelling error
                  # and generate the correclty spelled sequence
                  title_substring = test_title[0 : test_title.find(last_word) + len(last_word)]
                  #print title_substring
                  correct_spellings.add(title_substring)
                  indices.append(i)

      indices_2 = []
      for possible_title in correct_spellings:
        #self.quotationFound = True
        self.spellChecking = True
        indices_3 = self.isMovie(possible_title)
        #indices_3 = self.isTitleInLevel1(possible_title)
        #if len(indices_3) == 0:
            #indices_3 = self.isTitleInLevel4(possible_title)

        indices_2.extend(indices_3)

      #print "Spell check", time.time() - start_time, "to run"

      return list(set(indices_2))


    def isTitleInLevel1(self, inpt_title):
        self.DONOTTOUCHME_TOY_STORY = False
        # Check exact match
        #print "Level 1 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.custom_titles)
                    if self.isTitleInLevel1Helper(inpt_title, v[0])]
        return indices

    def isTitleInLevel1Helper(self, inpt_title, entry):
        titles = re.findall("<>(.*?)</>", entry)
        for title in titles:
            #print "Title: " + title
            if self.removeSequel(self.removeSubtitle(self.removeDate(self.removeArticles(inpt_title)))) == self.removeSequel(self.removeSubtitle(self.removeDate(self.removeArticles(title)))):
                self.DONOTTOUCHME_TOY_STORY = True
            if self.removeArticles(inpt_title) == self.removeArticles(title):
                return True
        return False

    def isTitleInLevel2(self, inpt_title):
        # Check but with dates irrelevent
        if self.DONOTTOUCHME_TOY_STORY == True:
            return []
       #print "Level 2 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.custom_titles)
                    if self.isTitleInLevel2Helper(inpt_title, v[0])]
        return indices

    def isTitleInLevel2Helper(self, inpt_title, entry):
        titles = re.findall("<>(.*?)</>", entry)
        for title in titles:
            #print "Title: " + title
            if self.removeDate(self.removeArticles(inpt_title)) == self.removeDate(self.removeArticles(title)):
                return True
        return False

    def isTitleInLevel3(self, inpt_title):
        # account for subtitles
        if self.DONOTTOUCHME_TOY_STORY == True:
            return []
       #print "Level 3 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.custom_titles)
                    if self.isTitleInLevel3Helper(inpt_title, v[0])]
        return indices

    def isTitleInLevel3Helper(self, inpt_title, entry):
        titles = re.findall("<>(.*?)</>", entry)
        for title in titles:
            #print "Title: " + title
            if self.removeSubtitle(self.removeDate(self.removeArticles(inpt_title))) == self.removeSubtitle(self.removeDate(self.removeArticles(title))):
                return True
        return False

    def isTitleInLevel4(self, inpt_title):
        # account for sequels as well
        #    return []
       #print "Level 4 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.custom_titles)
                    if self.isTitleInLevel4Helper(inpt_title, v[0])]
        return indices

    def isTitleInLevel4Helper(self, inpt_title, entry):
        titles = re.findall("<>(.*?)</>", entry)
        for title in titles:
            #print "Title: " + title
            if self.removeSequel(self.removeSubtitle(self.removeDate(self.removeArticles(inpt_title)))) == self.removeSequel(self.removeSubtitle(self.removeDate(self.removeArticles(title)))):
                return True
        return False

    def isTitleInLevel5(self, inpt_title):
        # All bets are off, just substring
        if self.quotationFound == True:
            return []
       #print "Level 5 titlesearch"
        indices = []
        indices = [i for i, v in enumerate(self.custom_titles)
                    if self.isTitleInLevel5Helper(inpt_title, v[0])]
        return indices

    def isTitleInLevel5Helper(self, inpt_title, entry):
        titles = re.findall("<>(.*?)</>", entry)
        for title in titles:
            #print "Title: " + title
            if self.removeArticles(title).startswith(self.removeArticles(inpt_title)):
                return True
        return False

    def removeArticles(self, movie_title):
        #Preprocess movie_titles: Lowercase; remove a, an, the at beg
        # MUST BE CALLED AFTER removeDate
        movie_title = movie_title.lower()
        title_regex1 = r'^((an )|(the )|(a ))'
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

    def removeSubtitle(self, movie_title):
        colon_regex = r'^(.*?)(?:(?::.*)|(?:and.*))'
        if re.search(colon_regex, movie_title):
            movie_title = re.findall(colon_regex, movie_title)[0]
            #print "Movie title after colon: " + movie_title
        movie_title = movie_title.strip()

        return movie_title

    def removeSequel(self, movie_title):
        # M?(CM|D?C?C?C? |CD)(XC |XL |L?X?X?X?)(V?I?I?I? |IV |IX)
        #TODO: FILL OUT SEQUELS
        sequel_regex = r'(.*) (?:\d|(?:m?(?:cm|d?c?c?c?|cd)(?:xc|xl|l?x?x?x?)(?:v?i?i?i?|iv|ix)))$'
        if re.search(sequel_regex, movie_title):
            movie_title = re.findall(sequel_regex, movie_title)[0]
            #print "Movie title after sequel: " + movie_title
        movie_title = movie_title.strip()

        return movie_title

    def isMovie(self, movie_title):
        # Search for query as substring of movie title
        # TODO: This does not quite work ex. search for "The Little Mermaid (1989)"
        #print "Movie: " + movie_title
        indices = self.isTitleInLevel1(movie_title)
        if len(indices) == 0:
            indices = self.isTitleInLevel2(movie_title)
            if len(indices) == 0:
                indices = self.isTitleInLevel3(movie_title)
                if len(indices) == 0:
                    indices = self.isTitleInLevel4(movie_title)
                    if len(indices) == 0:
                        indices = self.isTitleInLevel5(movie_title)

        # SPELLCHECK

        # If no substrings found try checking for miss-spelling
        # Try maybe to allow for different versions of the movie?
        if self.quotationFound == False and len(indices) == 0 and not self.spellChecking:
          self.spellCheckPerformed1 = True
          self.spellChecking = True
          indices = self.spellCheck(movie_title)

        self.spellChecking = False
        return indices

    def askForSelection(self, movie_indexes):
        bot_prompt = "\001\033[96m\002%s> \001\033[0m\002" % self.name
        print bot_prompt + "Sorry, which movie are you referring to?"
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
                return None
            elif len(inpt) != 0:
                # Check if this is a movie name
                temp = []
                for index in movie_indexes:
                   #print "title: " + self.titles[index][0]
                    if self.removeArticles(self.titles[index][0]).startswith(self.removeArticles(inpt)):
                        temp.append(index)

                if len(temp) > 1:
                   print bot_prompt + "Could you help me narrow it down more please?"
                    for i, movie_index in enumerate(temp):
                       print str(i + 1) + ") " + self.titles[movie_index][0]
                    movie_indexes = temp
                elif len(temp) == 0:
                   print bot_prompt + "Sorry, I don't know the movie \"" + inpt + "\""
                else:
                    return temp[0]
                # temp = self.isMovie(inpt)
                # if len(temp) == 1:
                #     return movie_indexes[0]
                # elif len(temp) == 0:
                #    #print bot_prompt + "Sorry, I don't know the movie \"" + inpt + "\""
            # elif inpt == "more":
            #    #print bot_prompt + "I know of more than one movie with the name \"" + inpt + "\". Which one were you referring to?"
            #     for i, movie_index in enumerate(temp):
            #        #print str(i + 1) + ") " + self.titles[movie_index][0]
            #    #print "Please tell me a number from 1 to " + str(len(temp)) + " or the movie name."
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
      #self.move_article_to_front(self.titles)
      for i,v in enumerate(self.titles):
          self.titles[i][0] = self.move_article_to_front(v[0])

      self.custom_titles = copy.deepcopy(self.titles)
      self.custom_titles = self.scope_movie_titles(self.custom_titles)
      #print self.titles

    def scope_movie_titles(self, titles):
        for i,v in enumerate(titles):
            date = re.findall(r'\(\d\d\d\d\)', v[0])
            #print str(v)
            alternate_titles = re.findall(r'\(([^\d]+?.*?)\)', v[0])
            #print str(alternate_titles)
            if len(alternate_titles) != 0:
                for j, title in enumerate(alternate_titles):
                    # Get rid of a.k.a
                    #if re.search(r'a\.k\.a\. ', alternate_titles[j]):
                        #print "FOUND SOMETHING: " + alternate_titles[j]
                    alternate_titles[j] = re.sub(r'a\.k\.a\. ', "", alternate_titles[j])
                    # Move article to the front
                    articles = re.findall(r', (\w{0,4})$', alternate_titles[j])
                    if len(articles) > 1:
                       #print "Problem, length not 1 of articles: " + str(articles)
                    elif len(articles) != 0:
                        #print "GOT HEREEE"
                        alternate_titles[j] = re.sub(r', (\w{0,4})$', "", alternate_titles[j])
                        alternate_titles[j] = articles[0] + " " + alternate_titles[j]
                        #print alternate_titles[j]

                    alternate_titles[j] = alternate_titles[j].strip()
                    #print str(alternate_titles)
                    if len(date) != 0:
                        #print str(alternate_titles)
                        alternate_titles[j] = alternate_titles[j] + " " + date[0]

            # fix original name
            #if len(alternate_titles) != 0:#print "Titles: " + str(titles)
            titles[i][0] = re.sub(r'\(.*?\)', '', titles[i][0])
            titles[i][0] = re.sub(r'\s+', ' ', titles[i][0])
            #titles[i][0] = titles[i][0].strip()


            #titles[i][0] = self.move_article_to_front(titles[i][0])
            titles[i][0] = titles[i][0].strip()
            if len(date) != 0:
                titles[i][0] = "<>" + titles[i][0] + " " + date[0] + "</>"
            else:
                #print "HIIIII"
                titles[i][0] = "<>" + titles[i][0] + "</>"

            for title in alternate_titles:
                titles[i][0] = titles[i][0] + "<>" + title + "</>"
            #print "TITLE:" + titles[i][0]
        return titles

    def move_article_to_front(self, v):
        movie_title = v
        date = re.findall(r'\(\d\d\d\d\)', movie_title)
        if len(date) != 0:
            date = date[0]
        else:
            date = ""

        if re.search(r'.*, The [)(]', movie_title):
            movie_title = re.sub(r', The ([)(])', r" \1", movie_title)
            movie_title = "The " + movie_title
        elif re.search(r'.*, An [)(]', movie_title):
            movie_title = re.sub(r', An ([)(])', r" \1", movie_title)
            movie_title = "An " + movie_title
        elif re.search(r'.*, A [)(]', movie_title):
            movie_title = re.sub(r', A ([)(])', r" \1", movie_title)
            movie_title = "A " + movie_title
        return movie_title

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      #TODO: This takes a whole, should we change it?
      #Threshold for binarizing movie rating matrix
      threshold = 3

      binarized_matrix = [[0 if i == 0 else -1 if i - threshold <= 0 else 1 for i in line] for line in self.ratings]
      self.ratings = binarized_matrix

    def stemLexicon(self):
      stemmedLex = {}
      for word in self.sentiment:
        stemmedLex[self.stem(word)] = self.sentiment[word]
      # Add awesome!
      stemmedLex[self.stem('awesome')] = 'pos'
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
      #nputString = inputString.split()
      inputString = re.findall(r"[\w']+|[.,!?;]+", inputString)

      # negate things first
      temp = []
      negate = False
      for word in inputString:
          #print word
          if word in self.negations:
              temp.append(word)
              if negate:
                  negate = False
              else:
                  negate = True
              continue
          elif word[len(word) - 1] in self.punctuations: # To catch case of repeated punction like !!!! or
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
            #print word

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
                #print "pos: %s" % (word)
                if word in self.strong_pos:
                  #added_sent += 2
                  strongPosCount += 1
                #added_sent *= 2 * intensifier_count if intensifier_count > 0 else 1
                posCount += added_sent
                strongPosCount += intensifier_count
              elif self.sentiment[word] == 'neg':
                #print "neg: %s" % (word)
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
      ##print "Count of word: " + word + " pos: " + str(posCount) + " neg: " + str(negCount)

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
      #movie_to_recomend = ''
      #for i in range(self.numRecs):
       # movie_to_recomend += str(i + 1) + ') ' + self.titles[heapq.heappop(est_ratings)[1]][0] + '\n'

      # Remove the last \n
      #movie_to_recomend = movie_to_recomend[:-1]

      print "Recommend took", time.time() - start_time, "to run"

      '''
      ##print top 50
      for i in range(50):
        #print '%s rated %f' % (self.titles[sorted_movies[i][0]][0], sorted_movies[i][1])
        movie_i = heapq.heappop(est_ratings)
       #print '%s rated %f' % (self.titles[movie_i[1]][0], movie_i[0] * -1)
      '''
      return est_ratings
      #return movie_to_recomend

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
      Welcome to our chatbot!
      We implemented the following creative features from the rubric:
        - Identifying movies without quotation marks or perfect capitalization
        - Fine-grained sentiment extraction
        - Spell-checking movie titles
        - Disambiguating movie titles for series and year ambiguities
        - Understanding references to things said previously
        - Responding to arbitrary input
        - Speaking very fluently
        - Alternate/foreign titles
      We also implemented some "other features," described below.
        - Give user the option to specify a range of dates for the recommendations.
        - Gives user the option to choose a specific genre for the recommendations.
        - Gives user a selection of movies to choose from if the input movie detected
          is part of a series.
        - Detect redundant input movies and update the user's rating if a different
          sentiment was detected than what is currently stored.
        - Explicitly confirm spell check with user to make sure it's what they intended.
        - Tell user jokes when prompted.
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
