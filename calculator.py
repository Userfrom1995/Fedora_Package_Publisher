#!/usr/bin/env python3
import sys

def main():
    print("Fedora Calculator. Enter mathematical expressions or press Ctrl+C to exit.")
    while True:
        try:
            expression = input(">>> ")
            result = eval(expression)
            print("= ", result)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
