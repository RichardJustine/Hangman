import os
import requests
from random import randrange
import math
from replit import db


def itemgetter(*items):
  if len(items) == 1:
    item = items[0]

    def g(obj):
      return obj[item]
  else:

    def g(obj):
      return tuple(obj[item] for item in items)

  return g


def view_high_scores():
  if len(db["high_scores"]) > 0:
    print("\tHIGH SCORES")
    print("RANK\tNAME\tSCORE")
    rank = 1
    for high_score in sorted(db["high_scores"],
                             key=itemgetter("score"),
                             reverse=True):
      if high_score['score'] > 0 and rank <= 5:
        print(
          f"{rank}\t\t{high_score['player'].upper()}\t{high_score['score']}")
        rank += 1
  else:
    print("No scores recorded yet!")
  print()


class Hangman:

  def __init__(self, current_player, current_score):
    self.current_player = current_player
    self.current_score = current_score
    self.random_word = requests.get(
      "https://random-word-form.herokuapp.com/random/noun").json()[0]
    self.word_len = len(self.random_word)
    self.divisor = 3 if self.word_len <= 3 else 2
    self.letter_count_to_pop = math.ceil(self.word_len / self.divisor)
    self.letter_index_to_pop = []
    self.popped_word = ""
    self.word_to_pop = self.random_word
    self.correct_word = ""
    self.score_card = 0
    self.lives = 3
    self.guessed_letter_count = 0

  def start(self):
    print("*" * 30)
    print("Let's play Hangman")
    print("*" * 30)
    print("[1] Start")
    print("[2] High Scores")
    start_option = input("Which one? ")
    print("*" * 30)
    print()
    while not start_option.isdigit() or int(start_option) > 2 or int(
        start_option) < 1:
      start_option = input("\nNo option selected. Choose again: ")
      print()
    start_option = int(start_option)

    if start_option == 1:
      if (self.current_player == ""):
        self.current_player = input("Enter name (up to 4 characters only): ")
        while len(self.current_player) < 1 or len(
            self.current_player) > 4 or self.current_player.find(" ") > -1:
          self.current_player = input("Incorrect input! Try again: ")
      self.generate_popped_word()
    else:
      view_high_scores()
      self.start()

  def generate_popped_word(self):
    for ltp_item in range(self.letter_count_to_pop):
      pop_index = randrange(0, self.word_len - 1)
      while pop_index in self.letter_index_to_pop:
        pop_index = randrange(0, self.word_len - 1)
      self.letter_index_to_pop.append(pop_index)
    self.letter_index_to_pop.sort()

    for rw_index, rw_item in enumerate(self.random_word):
      for litp_item in self.letter_index_to_pop:
        if rw_index == litp_item:
          self.popped_word = self.word_to_pop[:
                                              rw_index] + "_" + self.word_to_pop[
                                                rw_index + 1:]
          self.word_to_pop = self.popped_word
    print("\nWord: " + self.popped_word)
    self.guess_letter()

  def guess_letter(self):
    while self.popped_word.find("_") >= 0 and self.lives > 0:
      letter_guessed = input("Guess a letter: ")
      while len(letter_guessed) > 1 or not letter_guessed.isalpha():
        letter_guessed = input("Invalid letter. Guess a letter again: ")

      for litp_index, litp_item in enumerate(self.letter_index_to_pop):
        if self.random_word[litp_item].lower() == letter_guessed.lower():
          self.score_card += 1
          self.correct_word = self.popped_word[:
                                               litp_item] + letter_guessed + self.popped_word[
                                                 litp_item + 1:]
          self.popped_word = self.correct_word
          self.letter_index_to_pop.pop(litp_index)
          self.guessed_letter_count += 1
        else:
          self.correct_word = self.popped_word

      if self.score_card >= 1:
        if len(self.letter_index_to_pop) >= 1:
          print(
            f"\nNice! You guessed {self.score_card if self.score_card > 1 else 'a'} correct letter{'s' if self.guessed_letter_count > 1 else ''}."
          )
          print(
            f"Keep it going! {len(self.letter_index_to_pop)} letter{'s' if len(self.letter_index_to_pop) > 1 else ''} remaining."
          )
      else:
        self.lives -= 1
        print("\nIncorrect! You guessed a wrong letter.")
        print("The rope has been slightly cut.")

      self.score_card = 0
      self.guessed_letter_count = 0
      print(f"\nWord: {self.correct_word}")

    if self.lives > 0:
      print("Congrats! You guessed the word.")
      self.current_score += 1
    else:
      print("Boo! You have been hanged.")
    self.ask_player()

  def ask_player(self):
    print()
    print("*" * 30)
    print("Do you want to play again? ")
    print("[1] Yes")
    print("[2] No")
    player_choice = input("Which one? ")
    print("*" * 30)
    while not player_choice.isdigit() or int(player_choice) > 2 or int(
        player_choice) < 1:
      player_choice = input("\nNo option selected. Choose again: ")
    player_choice = int(player_choice)
    if player_choice == 1:
      clear = lambda: os.system("clear")
      clear()
      new_game = Hangman(self.current_player, self.current_score)
      new_game.start()
    else:
      if self.current_score > 0:
        db["high_scores"].append({
          "player": self.current_player,
          "score": self.current_score
        })
      print("Goodbye! Thanks for playing.")


game = Hangman("", 0)
game.start()
