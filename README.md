**## About Agri Bot**

Howdy! Meet Agri Bot, your farming buddy with some pretty nifty features:

**### Multi-Language Magic**

Ever wanted to chat about farming in your language? Agri Bot is fluent in many, so ask away in your comfort zone, be it typing or talking.

**### Talk, Don't Type**

Feel like having a chat instead of typing? No problem! With Agri Bot's audio support, just talk, and the bot will respond with a friendly voice in your language. It's like having a conversation with a knowledgeable friend.

**### YouTube Answers**

Sometimes words aren't enough, right? Agri Bot gets it! Get personalized YouTube video recommendations, making learning about farming as easy as watching your favorite show.

**### Farmer-Focused Tech**

Agri Bot isn't just a tech gadget; it's your farming companion. We've made it simple, friendly, and loaded with features to make your agricultural journey smoother.

Ready to experience the farming magic? Agri Bot is here to help you grow, one friendly chat and clever feature at a time!


### Project Setup  


# Agri Bot

## Local Deployment
1. make virtual env   `mkvirtualenv`
2. Install required python packages
    `pip install -r requirements.txt`
   
3. Make a database in mongo
    `mongodb://user:password@server_name/?authSource=project_name` for server side
4. `cd agri-bot` 
5. `flask run --port=8001`
6. To run https server use `python manage.py runsslserver 0:8000`


## Pycharm
1. Make sure to update your virtual env in pycharm to the one you created
2. Add `app` folder to your project root



**Here is the Home Page of Agro Bot**

![Image Alt text](/static/images/agri-bot1.jpg "Home Page")

Now the farmer can ask his question or send an audio of his question

![Image Alt text](/static/images/agri-bot2.jpg "Farmer asking question")

as soon as he enters his question he gets the result in text audio with video recommendation 

![Image Alt text](/static/images/agri-bot3.jpg "Answer from the Agri Bot")
