#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re

import numpy as np

from movielens import ratings
from random import randint

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.sentiment = {}
      self.read_data()
      self.binarize()

      self.negations = set(self.readFile("data/negations.txt"))
      self.punctuations = set(self.readFile("data/punctuation.txt"))

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
      if self.is_turbo == True:
        #CREATIVE SECTION
        response = 'processed %s in creative mode!!' % input
      else:
        #STARTER SECTION
        # Process Movie title
        movie_tag = self.processTitle(input)
        # Get the flag indicating success of process Title
        movie_flag = movie_tag[1]
        # Movie found
        movie = movie_tag[0]
        if movie_flag == -1: # No movies found
            return "Sorry, I don't understand. Tell me about a movie that you have seen."
        elif movie_flag == 1:
            movie_index = self.isMovie(movie)
            if movie_index != -1: # Good movie!!
              #response = "I love " + movie + "!"
              response = "I love " + self.titles[movie_index][0][0] + "!"
            else: # Unknown movie
              return "Unfortunately I have never seen that movie. I would love to hear about other movies that you have seen"
        else:
          return "Please tell me about one movie at a time. Go ahead."
      return response

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
        indices = np.where(self.titles == movie_title)
        if len(indices[0]) != 0:
            return indices[0]
        else:
            return -1

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
      self.titles = np.array(self.titles)

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

    def sentimentClass(self, inputString):
      posCount = 0.0
      negCount = 0.0
      inputString.lower()
      inputString = re.sub(r'\".*\"', '', inputString)
      #inputString = re.sub(r' +', ' ', inputString)
      inputWords = inputString.split()

      #TODO:REMOVE
      print "INPUTWORDS: " + str(inputWords)

      #negate things first
      temp = []
      negate = False
      for word in inputString:
          if word in self.negations:
              temp.append(word)
              negate = True
              continue
          elif word in self.punctuations:
              temp.append(word)
              negate = False
              continue

          #temp.add(word if !negate else "NOT_"+word)
          if negate:
              temp.append("NOT_" + word)
          else:
              temp.append(word)
      inputWords = temp

      for word in inputWords:
        if "NOT_" in word:
            word.replace("NOT_", "")
        if word in self.sentiment:
          if self.sentiment[word] == 'pos': posCount += 1
          elif self.sentiment[word] == 'neg': negCount += 1
      if posCount >= negCount: return 'pos'
      else: return 'neg'

    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      dotProd = np.dot(u, v)
      lenU = np.linalg.norm(u)
      lenV = np.linalg.norm(v)
      if lenU != 0 and lenV != 0:
        return float(dotProd) / (lenU * lenV)
      else: return 0


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      pass


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
