# A simple and poorly optimised script that generates a related word for every unique pair of words
# Put words.csv in the root directory

import pandas as pd
import os
from itertools import combinations
import google.generativeai as genai

# Configure the API
genai.configure(api_key="PutAPIKeyHere") # PUT API KEY HERE

def read_words(file_path):
    """Read words from a file and return them as a list, maintaining order."""
    return pd.read_csv(file_path, header=None)[0].tolist() if os.path.exists(file_path) else []

def write_words(words, file_path):
    """Write words to a file."""
    pd.DataFrame(words).to_csv(file_path, index=False, header=False)

def generate_combinations(words):
    """Generate all unique 2-word combinations maintaining the list order."""
    return list(combinations(words, 2))

def generate_new_word(wordA, wordB):
    """Call the API to generate a new word from two words."""
    question = f"Combine the concepts of ({wordA}) and ({wordB}) to generate a simple, common noun, inspired by the game Little Alchemy. The new word should reflect a basic, everyday concept that a young child would understand and recognize. Avoid complex or scientific terms. Ensure the response is a real, existing noun that is easily recognizable and appropriate for all ages. For example, if the input words are 'water' and 'cold', a suitable response would be 'ice'. Keep the result straightforward and suitable for a general audience. Provide one word only."
    try:
        response = genai.GenerativeModel('gemini-1.0-pro').generate_content(question)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling API for {wordA}, {wordB}: {e}")
        return None

def add_word_to_file(new_word, words_file_path):
    """Immediately write the new word to the words file if it's unique."""
    existing_words = set(pd.read_csv(words_file_path, header=None)[0]) if os.path.exists(words_file_path) else set()
    if new_word not in existing_words:
        with open(words_file_path, 'a') as file:
            file.write(f"{new_word}\n")

def main(words_file_path, combinations_file_path, failed_combinations_path):
    global api_call_count
    words = read_words(words_file_path)  # Read words as a list

    try:
        processed_combinations = pd.read_csv(combinations_file_path)
        # Create a set of frozensets for quick bidirectional lookup
        processed_set = {frozenset([row['Word A'], row['Word B']]) for _, row in processed_combinations.iterrows()}
    except (FileNotFoundError, pd.errors.EmptyDataError):
        processed_combinations = pd.DataFrame(columns=['Word A', 'Word B', 'Generated Word'])
        processed_set = set()

    try:
        failed_combinations = pd.read_csv(failed_combinations_path)
        failed_set = {frozenset([row['Word A'], row['Word B']]) for _, row in failed_combinations.iterrows()}
    except (FileNotFoundError, pd.errors.EmptyDataError):
        failed_combinations = pd.DataFrame(columns=['Word A', 'Word B'])
        failed_set = set()

    # Process combinations in the order they are generated
    for wordA, wordB in generate_combinations(words):
        if api_call_count >= api_call_limit:
            print("API call limit reached.")
            break

        combination_set = frozenset([wordA, wordB])
        if combination_set not in processed_set and combination_set not in failed_set:
            new_word = generate_new_word(wordA, wordB)
            if new_word and new_word not in words:
                print(f"Generated new word: {new_word} = {wordA} + {wordB}")
                add_word_to_file(new_word, words_file_path)
                words.append(new_word)  # Optionally add the new word to the current session's list
                new_row = {'Word A': wordA, 'Word B': wordB, 'Generated Word': new_word}
                processed_combinations = processed_combinations._append(new_row, ignore_index=True)
                processed_set.add(combination_set)
                processed_combinations.to_csv(combinations_file_path, index=False)
                api_call_count += 1
            else:
               # if not new_word:
                print(f"Failed to generate a new word for: {wordA} + {wordB}")
                failed_combinations = failed_combinations._append({'Word A': wordA, 'Word B': wordB}, ignore_index=True)
                failed_combinations.to_csv(failed_combinations_path, index=False)  # Save immediately
                failed_set.add(combination_set)

    failed_combinations.to_csv(failed_combinations_path, index=False)

if __name__ == "__main__":
    words_file_path = 'words.csv'
    combinations_file_path = 'combinations.csv'
    failed_combinations_path = 'failed_combinations.csv'
    api_call_count = 0
    api_call_limit = 50
    main(words_file_path, combinations_file_path, failed_combinations_path)
