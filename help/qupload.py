import pickle

# List of questions, options, and answers
data = [
    {
        "question": "What is the 'rule of thirds' in video creation?",
        "options": [
            "A) A law about video duration",
            "B) A guideline for framing shots",
            "C) A rule about video editing",
            "D) A guideline for video lighting"
        ],
        "answer": "B) A guideline for framing shots"
    },
    {
        "question": "Which thumbnail type tends to get the most clicks on YouTube?",
        "options": [
            "A) Text-only",
            "B) Clickbait",
            "C) Faces with emotions",
            "D) Logo-based"
        ],
        "answer": "C) Faces with emotions"
    },
    {
        "question": "What is 'YouTube SEO'?",
        "options": [
            "A) Software for editing videos",
            "B) Optimizing video titles, descriptions, and tags for search",
            "C) A marketing strategy to increase subscribers",
            "D) A tool for ranking on Google"
        ],
        "answer": "B) Optimizing video titles, descriptions, and tags for search"
    },
    {
        "question": "Why are custom thumbnails important?",
        "options": [
            "A) They improve video quality",
            "B) They make videos load faster",
            "C) They increase click-through rates",
            "D) They allow longer videos"
        ],
        "answer": "C) They increase click-through rates"
    },
    {
        "question": "Which of the following helps improve audience retention?",
        "options": [
            "A) High video resolution",
            "B) Engaging content in the first 30 seconds",
            "C) Using many transitions",
            "D) Longer video length"
        ],
        "answer": "B) Engaging content in the first 30 seconds"
    },
    {
        "question": "What is YouTube's 'Watch Time'?",
        "options": [
            "A) The time spent editing videos",
            "B) The amount of time viewers spend watching videos",
            "C) The time videos take to upload",
            "D) The time viewers spend on YouTube daily"
        ],
        "answer": "B) The amount of time viewers spend watching videos"
    },
    {
        "question": "Which of these increases YouTube engagement?",
        "options": [
            "A) Posting without comments enabled",
            "B) Using calls to action (CTAs) in videos",
            "C) Uploading short videos only",
            "D) Avoiding social media promotion"
        ],
        "answer": "B) Using calls to action (CTAs) in videos"
    },
    {
        "question": "What is a 'YouTube card'?",
        "options": [
            "A) A reward for YouTube creators",
            "B) A clickable element that links to other videos",
            "C) A credit card associated with YouTube",
            "D) A guide for YouTube policies"
        ],
        "answer": "B) A clickable element that links to other videos"
    },
    {
        "question": "What does 'CTR' stand for in YouTube analytics?",
        "options": [
            "A) Click-through rate",
            "B) Content-time ratio",
            "C) Channel title ranking",
            "D) Comment-to-review"
        ],
        "answer": "A) Click-through rate"
    },
    {
        "question": "How can you encourage viewers to subscribe?",
        "options": [
            "A) By using a paid service",
            "B) By directly asking in videos and descriptions",
            "C) By not uploading too often",
            "D) By removing ads"
        ],
        "answer": "B) By directly asking in videos and descriptions"
    },
    {
        "question": "What’s the ideal video length for maximum engagement?",
        "options": [
            "A) Under 1 minute",
            "B) 10–15 minutes",
            "C) Over 30 minutes",
            "D) 1–2 hours"
        ],
        "answer": "B) 10–15 minutes"
    },
    {
        "question": "Which metric is most critical for ranking in YouTube's algorithm?",
        "options": [
            "A) Likes",
            "B) Watch time",
            "C) Video file size",
            "D) Number of shares"
        ],
        "answer": "B) Watch time"
    },
    {
        "question": "Why are YouTube playlists useful?",
        "options": [
            "A) They allow you to upload more videos at once",
            "B) They keep viewers engaged for longer",
            "C) They reduce watch time",
            "D) They decrease video loading time"
        ],
        "answer": "B) They keep viewers engaged for longer"
    },
    {
        "question": "What should a YouTube description contain for SEO?",
        "options": [
            "A) A video link only",
            "B) Random keywords",
            "C) Relevant keywords, links, and a call to action",
            "D) Just the title"
        ],
        "answer": "C) Relevant keywords, links, and a call to action"
    },
    {
        "question": "What’s the benefit of using end screens?",
        "options": [
            "A) It improves video quality",
            "B) It keeps viewers on your channel longer",
            "C) It shortens video duration",
            "D) It improves audio clarity"
        ],
        "answer": "B) It keeps viewers on your channel longer"
    },
    {
        "question": "What is 'YouTube Shorts'?",
        "options": [
            "A) A YouTube feature for live streaming",
            "B) A type of ad",
            "C) Short-form videos under 60 seconds",
            "D) A premium YouTube membership"
        ],
        "answer": "C) Short-form videos under 60 seconds"
    },
    {
        "question": "Which of these is NOT a good strategy to grow a YouTube channel?",
        "options": [
            "A) Posting consistently",
            "B) Ignoring analytics",
            "C) Engaging with viewers in comments",
            "D) Collaborating with other creators"
        ],
        "answer": "B) Ignoring analytics"
    },
    {
        "question": "What is the primary purpose of a YouTube channel trailer?",
        "options": [
            "A) To summarize your content for new visitors",
            "B) To showcase advertisements",
            "C) To promote YouTube ads",
            "D) To block comments"
        ],
        "answer": "A) To summarize your content for new visitors"
    },
    {
        "question": "How does closed captioning help a YouTube channel?",
        "options": [
            "A) It improves audio quality",
            "B) It enhances accessibility and SEO",
            "C) It reduces video length",
            "D) It prevents video monetization"
        ],
        "answer": "B) It enhances accessibility and SEO"
    },
    {
        "question": "What does 'monetization' mean on YouTube?",
        "options": [
            "A) Earning money from ads on your videos",
            "B) Paying to promote your videos",
            "C) Reducing video length",
            "D) Making private videos"
        ],
        "answer": "A) Earning money from ads on your videos"
    },
    {
        "question": "How can you use YouTube Analytics to improve content?",
        "options": [
            "A) Ignore analytics for consistent uploading",
            "B) Use data to adjust content based on viewer behavior",
            "C) Only focus on subscriber count",
            "D) Pay for analytics tools"
        ],
        "answer": "B) Use data to adjust content based on viewer behavior"
    },
    {
        "question": "What is a 'YouTube strike'?",
        "options": [
            "A) A penalty for violating community guidelines",
            "B) A reward for getting 1,000 views",
            "C) A tool for uploading longer videos",
            "D) A special badge for YouTube partners"
        ],
        "answer": "A) A penalty for violating community guidelines"
    },
    {
        "question": "What is an advantage of using chapters in YouTube videos?",
        "options": [
            "A) It reduces video engagement",
            "B) It helps viewers navigate content easily",
            "C) It adds more ads to the video",
            "D) It hides comments"
        ],
        "answer": "B) It helps viewers navigate content easily"
    },
    {
        "question": "Which of these is an example of 'evergreen content'?",
        "options": [
            "A) Trending news updates",
            "B) A tutorial that remains useful for years",
            "C) A reaction to a viral meme",
            "D) A live event"
        ],
        "answer": "B) A tutorial that remains useful for years"
    }
]

for entry in data:
    question = Question(
        question=entry['question'],
        options=pickle.dumps(entry['options']),
        answer=entry['answer']
    )
    db.session.add(question)

db.session.commit()
db.session.close()