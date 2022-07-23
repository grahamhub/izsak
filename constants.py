import os

MESSAGES = {
    "wtf": [
        "I'm sorry not sorry but......What The Fuck Did you Just Say?",
        "https://cdn.discordapp.com/attachments/403414926183366672/999776569893584946/wolf.gif",
        ("You've got about 5 Damn Seconds to retract that awful statement before I destroy your ass "
         "{replace_with} before I update the Harry Potter fandom of this situation. Our community is "
         "highly active so I suggest you do at least something before you get smoked by a lot of people....")
    ],
    "love": [
        "i wuv you too owo",
        "Sorry my heart belongs to Nico",
        ":fuckboy:",
        ":kittyblush:",
        "I love you too!",
        ":02heart:",
        "I would die for you",
        "I would kill for you",
        "Nico and I saw you from across the bar and we really liked your vibe...",
        "What is love?",
        "Love is the ultimate expression of the will to live.",
        "ok",
    ],
}

NOT_FOUND_MAX_RETRIES = 5
NOT_FOUND_MSG = "Sorry, I couldn't find a media item for that category."

AUTO_SEND_CHANNEL = int(os.environ.get("IZSAK_AUTO_SEND_CHANNEL", "-1"))
