#! /usr/bin/env python3
""" This is my first Python project.
    It is a simple number guessing game.
    The computer randomly selects a number between 1 and 100,
    and the user has to guess it.
    The user has 3 attempts to guess the number.
    The program gives feedback on whether the guess is too high or too low.
    The program also keeps track of the number of attempts and the time taken to guess the number.
    The program ends when the user guesses the number or runs out of attempts.
"""
import random

number_to_guess = random.randint(1, 100)

attempts = 7

def get_user_guess():
    while True:
        try:
            guess = int(input("Guess a number between 1 and 100: "))
            if 1 <= guess <= 100:
                return guess
            else:
                print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    print("Welcome to the Number Guessing Game!")
    print("You have 3 attempts to guess the number between 1 and 100.")
    print("Let's start!")

    for attempt in range(attempts):
        guess = get_user_guess()
        if guess == number_to_guess:
            print(f"Congratulations! You guessed the number {number_to_guess} in {attempt + 1} attempts.")
            break
        elif guess < number_to_guess:
            print("Too low!")
        else:
            print("Too high!")
    else:
        print(f"Sorry! You've used all your attempts. The number was {number_to_guess}.")

if __name__ == "__main__":
    main()