import requests
import random

# Create an empty hashmap to store the rating IDs
rating_ids = {}

# Read the ratings.txt file and populate the hashmap
with open('ratings.txt', 'r') as file:
    for line in file:
        line = line.strip().split('\t')
        title = line[2]
        rating_id = line[0].split('.')[0]
        rating_ids[title] = rating_id

response = requests.get("https://leetcode.com/api/problems/all/", timeout=10)

# Check if the request was successful
if response.status_code == 200:
    # Load the response data as a JSON object
    data = response.json()

    # Get a list of all easy questions from the data
    easy_questions = [
        question for question in data['stat_status_pairs']
        if question['difficulty']['level'] == 1
    ]

    # Select a random easy question from the list
    question = random.choice(easy_questions)

    # Extract the question title and link from the data
    title = question['stat']['question__title']
    link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

    # Retrieve the rating ID from the hashmap based on the question title
    rating_id = rating_ids.get(title)

    print("LeetCode Question")
    print("ID:", question['stat']['frontend_question_id'])
    print("Easy")
    print("Title:", title)
    print("Rating ID:", rating_id)
    print("Link:", link)
else:
    # If the request was not successful, print an error message
    print("An error occurred while trying to get the question from LeetCode.")
