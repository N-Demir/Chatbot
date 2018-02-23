#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math

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
      self.read_data()

      #Globals TODO:Is this where they go in python? -ND


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
        response = 'processed %s in starter mode' % input

      return response


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

      self.binarize()

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      #TODO: This takes a whole, should we change it?
      #print self.threshold

      #Threshold for binarizing movie rating matrix
      threshold = 3
      maxRating = 5

      #binarized_matrix = [[np.sign(i - threshold) for i in line] for line in self.ratings]
      #binarized_matrix = [[int(i - threshold)/maxRating for i in line] for line in self.ratings]
      #binarized_matrix = [[-1 if i - threshold < 0 else 0 if i == 0.0 else 1 for i in line] for line in self.ratings]
      binarized_matrix = [[0 if i == 0 else -1 if i - threshold <= 0 else 1 for i in line] for line in self.ratings]
      self.ratings = binarized_matrix
      #check it works, TODO: remove:
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

    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      pass


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
