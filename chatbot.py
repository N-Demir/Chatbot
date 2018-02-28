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

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.is_repeat = False
      self.sentiment = {}
      self.usr_rating_vec = []
      self.numRatings = 5
      self.numRecs = 3
      self.read_data()
      self.p = PorterStemmer()
      self.stemLexicon()
      self.binarize()


      self.negations = open("data/negations.txt", "r").read().splitlines()
      self.punctuations = open('data/punctuation.txt', "r").read().splitlines()

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
          return "I'm sorry, we don't understand your input. Please enter a number 1, 2, or 3."
      if self.is_turbo == True:
        #CREATIVE SECTION
        response = 'processed %s in creative mode!!' % input
      else:
        #STARTER SECTION
        # Process Movie title
        movie_tag = self.processTitle(input)
        # Get the flag indicating success of process Title
        movie_flag = movie_tag[1]
        if movie_flag == -1: # No movies found
            return "Sorry, I don't understand. Tell me about a movie that you have seen."
        elif movie_flag == 1:
            # Movie found
            movie_title = movie_tag[0]
            movie_indexes = self.isMovie(movie_title)

            if len(movie_indexes) != 0: # Good movie!!
              # Need to encorperate the sentiment
              #self.usr_rating_vec.append((movie_index, 1))
              #response = "Sentiment for " + movie + " is " + self.sentimentClass(input)

              #TODO: fill out
              # We have recieved a valid movie so we have to extract sentiment,
              # record the movie rating based on sentiment, and respond reflecting
              # the sentiment.

              sentiment = self.sentimentClass(input)
              if sentiment == 'pos':
                movie_index = self.getMovieIndex(movie_indexes)
                response = self.getPosResponse(movie_index)
                self.usr_rating_vec.append((movie_index, 1))
              elif sentiment == 'neg':
                movie_index = self.getMovieIndex(movie_indexes)
                response = self.getNegResponse(movie_index)
                self.usr_rating_vec.append((movie_index, -1))
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
      if len(movie_indexes) != 1:
          #TODO: GET STuck in while loop asking for choice
          return self.askForSelection(movie_indexes)
      else:
          return movie_indexes[0]

    ###########################################################
    ######                   RESPONSES                   ######
    ###########################################################
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


    def processTitle(self, input):
        #TODO: fill out
        # movies should be clearly in quotations and match our database
        movie_regex = r'"(.*?)"'

        # Find all the entities
        entities = re.findall(movie_regex, input)

        # No movies found - flag -1
        if len(entities) == 0:
          return ("", -1)
        elif len(entities) == 1: # One movie found - flag 1
          return (entities[0], 1)
        else: # Multiple movies found - flag 2
          return ("", 2)

    def isMovie(self, movie_title):
        #indices = np.where(self.titles == movie_title)

        #Preprocess movie_titles: Lowercase; remove a, an, the at beg
        movie_title = movie_title.lower()
        title_regex = r'^((an )|(the )|(a ))'
        if re.search(title_regex, movie_title):
            movie_title = re.sub(title_regex, "", movie_title)

        indices = [i for i, v in enumerate(self.titles) if movie_title in v[0].lower()]
        return indices

    def askForSelection(self, movie_indexes):
        bot_prompt = "\001\033[96m\002%s> \001\033[0m\002" % self.name
        print bot_prompt + "I know of more than one movie with that name. Which one were you referring to?"
        for i, movie_index in enumerate(movie_indexes):
            print str(i + 1) + ") " + self.titles[movie_index][0]
        print "Please tell me a number from 1 to " + str(len(movie_indexes)) + " or the movie name."

        while True:
            inpt = raw_input("> ")
            if inpt.isdigit():
                #TODO IS THIS Enough
                index = int(inpt)
                if 1 <= index and index <= len(movie_indexes):
                    return movie_indexes[index - 1]
                else:
                    print bot_prompt + "Sorry, that's not a valid number."
            elif len(inpt) != 0:
                #Check if this is a movie name
                movie_indexes = self.isMovie(inpt)
                if len(movie_indexes) == 1:
                    return movie_indexes[0]
                elif len(movie_indexes) == 0:
                    print bot_prompt + "Sorry I don't know the movie \"" + inpt + "\""
                else:
                    print bot_prompt + "I know of more than one movie with the name \"" + inpt + "\". Which one were you referring to?"
                    for i, movie_index in enumerate(movie_indexes):
                        print str(i + 1) + ") " + self.titles[movie_index][0]
                    print "Please tell me a number from 1 to " + str(len(movie_indexes)) + " or the movie name."
            else:
                print bot_prompt + "Please enter something."


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

      #Added for efficiency? -ND
      #self.titles = np.array(self.titles)

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

    def stem(self, word):
      return self.p.stem(word)

    def sentimentClass(self, inputString):
      posCount = 0.0
      negCount = 0.0
      inputString.lower()
      inputString = re.sub(r'\".*\"', '', inputString)
      inputString = inputString.split()

      # negate things first
      temp = []
      negate = False
      for word in inputString:
          # print "Word: " + word
          if word in self.negations:
              temp.append(word)
              if negate:
                  negate = False
              else:
                  negate = True
              continue
          elif word in self.punctuations:
              temp.append(word)
              negate = False
              continue

          # temp.add(word if !negate else "NOT_"+word)
          if negate:
              temp.append("NOT_" + word)
          else:
              temp.append(word)
      inputString = temp

      for word in inputString:
        # print "Word: " + word
        if "NOT_" in word:
            word = word.replace("NOT_", "")
            word = self.stem(word)
            if word in self.sentiment:
              if self.sentiment[word] == 'pos': negCount += 1
              elif self.sentiment[word] == 'neg': posCount += 1
        else:
            word = self.stem(word)
            if word in self.sentiment:
              if self.sentiment[word] == 'pos': posCount += 1
              elif self.sentiment[word] == 'neg': negCount += 1
        # DEBUGGING TODO:REMOVE
        # print "Count of word: " + word + " pos: " + str(posCount) + " neg: " + str(negCount)

      #TODO: Catch no sentiment or unclear sentiment!
      if posCount == 0.0 and negCount == 0.0: return 'none'
      elif posCount >= negCount: return 'pos'
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
