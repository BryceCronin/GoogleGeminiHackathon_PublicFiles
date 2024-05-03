# A simple and poorly optimised script for generating corresponding emoji for a given list of words
# Put words.csv in the root directory

import csv
import google.generativeai as genai

# Configure API
genai.configure(api_key="PutAPIKeyHere") # PUT API KEY HERE

def generate_emoji(word):
    """Call the AI API to generate an emoji based on the word."""
    question = f"Generate an emoji that best represents the word '{word}'."
    try:
        # Ask gemini
        response = genai.GenerativeModel('gemini-1.0-pro').generate_content(question)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling API: {e}")
        return "❓"

def add_emoji_to_csv(input_file):
    # Read existing data
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]

    # Generate emoji for each word and append to the row
    with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            word = ' '.join(row).strip()  # Combine all columns into a single word
            emoji = generate_emoji(word)
            row.append(emoji)  # Append emoji to the row
            writer.writerow(row)
            print(f"Added emoji {emoji} for word '{word}'.")

# Replace 'words.csv' with your file path!
add_emoji_to_csv('words.csv')

