import os
import pandas as pd


def main():
    print("Insert the relative path to the file containing data you want to analyze")
    filepath = input("filepath: ")
    print(f"Reading into {filepath}...")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error in reading the file: {e}")

if __name__ == "__main__":
    main()
