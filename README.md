# aspen-war
Take home assignment for Aspen Capital SWE Intern

[Slide Deck with Summary](https://docs.google.com/presentation/d/11Y5qw-r474YOa8p7ATsy-tiG8JjTFZDsxNpDX-a5sbQ/edit?usp=sharing)


Hello! Thank you for reviewing my submission for the take-home assignment for the SWE internship position at Aspen Capital. I have implemented the game of War in Python, using Flask as a web server for hosting the API endpoints and a MySQL database for persisting the results of the games. I have also deployed this on an AWS EC2 instance, which can be accessed at http://ec2-34-227-58-248.compute-1.amazonaws.com:5000

The two requested endpoints are avaible at the following routes:

- GET /run-game (EC2 Link: http://ec2-34-227-58-248.compute-1.amazonaws.com:5000/run-game)

  response pattern:
  
  {"turns":<no_of_turns_played>,"winner":<winning_player>}
  
  Here, the "winner" corresponds to whether player 1 or player 2 won and "turns" is the number of turns played by the deciding game.
  
  
- GET /game-history (EC2 Link: http://ec2-34-227-58-248.compute-1.amazonaws.com:5000/game-history)

  response pattern:
  
  {"player1":<no_wins_p1>,"player2":<no_wins_p2>}

  Here, the number of wins by player 1 is indicated by "player1" and the number of wins by player 2 is indicated by "player2".
  

### Local Run Instructions
To run locally, please set up a local MySQL installation. Export the MYSQL_USER and MYSQL_PWD variables as per your local installation. Then, log into the mysql installation (using ``` mysql -u <MYSQL_USER> -p ```), and run ``` source init_db.sql ``` to initialize the required database tables.

Also, install [flask](https://flask.palletsprojects.com/en/2.2.x/installation/) and the [MySQL connector](https://www.w3schools.com/python/python_mysql_getstarted.asp).

Then, run ``` flask --app war run ```, which will bring up a local server on port 5000. You can send requests to http://localhost:5000


### Reflection on Assignment
I had quite an interesting experience with the implementation of the game. In particular, I spent quite some time analyzing the results of the game before realizing that War is not guaranteed to have an end. The game can theoretically proceed forever given the right distribution of cards. Hence, based on [this](https://boardgames.stackexchange.com/questions/44275/what-is-the-expected-duration-of-a-game-of-war), I have limited the upper number of turns to 5000. In case we cross this threshold, we deem a tie and restart the game until we have a result.

I have included a test set that sends a 100 run-game requests, and then verifies the game-history at the end (can be run by running the program as ``` python war.py ```. To see the turn-by-turn hands (which might be impossible to follow with hundreds of turns), use the ``` -v ``` verbose flag.


Given more time, I would have tried to implement a more generalized solution that makes it easy to add more players to the game without much modification to the code. I would have also created a Docker image that couples the MySQL and Flask dependencies into one image, and deployed the image using a more elaborate container orchestration method, such as using Kubernetes. I would have also used a more reliable, production-grade web-server (such as Apache/Nginx), rather than the dev server that Flask brings up.



