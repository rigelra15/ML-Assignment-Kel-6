import os
import nltk
from nltk.corpus import cmudict
from pydub import AudioSegment
import speech_recognition as sr

# Download necessary NLTK data
nltk.download('cmudict')
nltk.download('punkt')

# Initialize CMU Pronouncing Dictionary
pronouncing_dict = cmudict.dict()

# Function to count syllables in a word using CMU Pronouncing Dictionary
def count_syllables(word):
    if word.lower() in pronouncing_dict:
        # Get the pronunciation list for the word
        pronunciation_list = pronouncing_dict[word.lower()]
        # Count the number of vowels in the pronunciation list
        syllable_counts = [len(list(y for y in x if y[-1].isdigit())) for x in pronunciation_list]
        # Return the maximum count as the number of syllables
        return max(syllable_counts)
    else:
        # If word not found in dictionary, use a simple heuristic
        return len([char for char in word if char in 'aeiouAEIOU'])

# Function to calculate difficulty score
def difficulty_score(word):
    # Length of the word
    length_score = len(word)
    # Number of syllables
    syllable_score = count_syllables(word)
    # Total difficulty score (could be weighted differently)
    total_score = length_score + syllable_score
    return total_score

# Function to sort words based on difficulty
def sort_words_by_difficulty(words):
    return sorted(words, key=difficulty_score, reverse=True)

# Function to process a paragraph of text
def process_paragraph(paragraph):
    # Tokenize the paragraph into words
    words = nltk.word_tokenize(paragraph)
    # Remove punctuation and convert to lowercase
    words = [word.lower() for word in words if word.isalpha()]
    # Remove duplicates by converting to a set and back to a list
    unique_words = list(set(words))
    # Sort words based on difficulty
    sorted_words = sort_words_by_difficulty(unique_words)
    return sorted_words

# Function to cut audio file based on words
def cut_audio_file(input_file, words, output_folder):
    audio = AudioSegment.from_file(input_file, format="wav")
    start_time = 0
    recognizer = sr.Recognizer()
    with sr.AudioFile(input_file) as source:
        audio_data = recognizer.record(source)

    for i, word in enumerate(words, start=1):
        # Search for the current word in the recognized text
        word_index = audio_data.frame_data.find(word.encode())
        if word_index == -1:
            continue

        # Get the frame rate
        frame_rate = audio.frame_rate

        # Calculate start and end time for the segment
        start_time = word_index / frame_rate * 1000  # convert frame index to milliseconds
        end_time = (word_index + len(word.encode())) / frame_rate * 1000  # convert frame index to milliseconds

        # Cut the audio segment
        segment = audio[start_time:end_time]
        # Export the segment to a WAV file
        output_file = os.path.join(output_folder, f"{i}_{word}.wav")
        segment.export(output_file, format="wav")
        print(f"Cut '{word}' from {start_time} ms to {end_time} ms, saved as {output_file}")
        start_time = end_time

# Example paragraph
paragraph = """
London, the capital city of the United Kingdom, is a vibrant metropolis rich in history and culture. Known as the 'Square Mile', the City of London is the historic core where the Romans first established Londinium. Today, it's a major business and financial center, housing the Bank of England, the Royal Exchange, and the London Stock Exchange. Despite its modern skyscrapers like the Gherkin and the Walkie Talkie, London retains its historical charm with landmarks such as Tower of London. The city's boundaries have remained nearly unchanged since medieval times, making it a unique blend of ancient and contemporary. With a small resident population but a bustling daytime workforce, the City is always alive with activity, reflecting its status as one of the world's leading financial hubs.
"""

# Process the paragraph
sorted_words = process_paragraph(paragraph)

# Input audio file
input_file = "voiceData/Data-1.wav"

# Output folder
output_folder = "output_folder"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Cut audio file based on words
cut_audio_file(input_file, sorted_words, output_folder)




