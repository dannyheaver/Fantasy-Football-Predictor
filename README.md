# **Succeeding in Fantasy Football**

## **Predicting how many points a Premier League player will get in the upcoming gameweek**


## Executive Summary

This project was started during my time on the General Assembly Data Science Immersive course. I have subsequently worked further to reformat this tool for easier download and general use.

By using [Vaastav's Github recourse](https://github.com/vaastav/Fantasy-Premier-League), I have access to the Premier League players most recent Fantasty Premier League (FPL) statistics hours after the final match in each gameweek is completed, as well as 4 previous seasons worth of data. The entries to the CSVs contain important information and key statistics that contribute to the points a player earned.

Using classification machine learning algorithms I was able to model the relationship between various statistics and match information that are available pre-game and make predictions. The best model I trained performed with 72% accuracy, better than the baseline of 66.7%. Of course there are many unpredictable factors in sport putting a glass ceilig on the acturacy that can be achived.

I then created a couple of tools for FPL managers to use to help improve their squad, including a function that returns the best predicted squad given a certain constraint and a transfer recommendation notebook.

**To easily get predictions, run the get_predictions_and_best_squads.py in python. This will return the most recent predictions for the upcoming gameweek, as well as all the best squads for each constraint.**


## Objective

Using a players statistics from their most recent appearance, to predict how many points they can be expected to get against their upcoming opponent.



## Methodology

Using self-defined functions, I started the project by cleaning the previous 4 completed seasons CSVs. This was a one-time process in which I could clean the CSVs and save them to a folder to concatenate later. Of course, the 2020-21 Premier League season is still occuring, as of writing this we are on gameweek 21. Therefore, whenever new information is added, I pull the latest CSV from the Github resource and reclean. 

After some initial data cleaning, including aligning player names and team names across the available seasons, I realised a key predictor would come in the form of opponent difficulty, i.e. a player will be more likely to score points against Fulham than Manchester City. Having read many articles across medium and other blogging sites, a common difficulty attribute was the teams position in the table. As I did not have this information readily available to me in the dataset, I opted for a different approach.

Instead I used the website [Football Data](http://www.football-data.co.uk/) to get various bookies odds from before each fixture. I created a "win expectation" column, which is the ratio of the probability of the players team winning over the probability of the opponents team winning. As the odds of a team are equal to 1/probability of said team winning, the win expectation is equal to the odds of the opponent team winning over the odds of the players team winning. I did various analysis on the different bookies and found that they all had extremely similar accuracies and the differences between the magnitude in odds was negligible, so I ended up using the BET365 odds as they were easily scrapale from the website [SportRadar](https://s5.sir.sportradar.com/bet365/en/1/season/77179/fixtures/round/).

The final step in my data cleaning, was the rolling means. A players form is a key indicating factor in how they are expected to perform. To capture that I took mean statistics from each players last 3 matches to be used as a predictor. Similarly, some players are known to perform better against specific opponents, with a common example in recent times being Jamie Vardy against Arsenal (with 11 goals in 12 matches against the Gunners). I therefore also calculated the rolling mean statistics of a player against their specific upcoming opponent.

The aim of this project was to predict how many points a player will earn in their upcoming match, using the statistics from their most recent performance. In order to do this, I shifted the points earned, as well as all match information that is available pre-game.


## Exploratory Data Analysis

The [player statisitcs visualisation notebook] contains plots and tables showcasing the players statistics from the 4 previous seasons and how the current season compares. The EDA is within this notebook.

An example is this plot which shows the variance in various statistics between different positions in football.

<a href="https://github.com/dannyheaver/FPL_prediction_analysis/blob/main/VISUALISATION/IMAGES/mean_stats_per_position.png"><img src="https://github.com/dannyheaver/FPL_prediction_analysis/blob/main/VISUALISATION/IMAGES/mean_stats_per_position.png" title="source: snipboard.io" style="width: 500px"/></a>

## Modeling

Attempting to model a players upcoming points return as a regression problem proved unsuccessful. The exact performance of a player in a future game was affected by simply too many factors, many of which are random. In an attempt to resolve this, I turned it into a classification problem, where the label classes are point ranges. This proved successful and with the neural network model MLPClassifier, with the adam solver, returning an accuracy of 72%, 5.3% better than the baseline of 66.7%.


## Prediction Tools

To make use of the predictions for general use, I constructed 2 tools to help better shape an FPL managers squad. The first one being a squad creator of the best players, given a certain constraint. The 4 constraints available are 'teams', in which a max of 3 players from one Premier League team are allowed in the squad, 'budget' in which the squad value must be below or equal to 1000, a combination of the two, or none. If you would like to apply the tool to the FPL app, you must choose to have both constaints on, however, there is not always a team that fits these constraints (unless you increase the number of combinations to check, which in turn exponentially increases the time to run). 

The second tool available is a transfer recommendation system in a Jupyter notebook. To operate this you will need to go into the notebook and run all of the cells. You can then use the green button to add every player in your squad (note if a player does not have a prediction, i.e. played in the last 5 rounds for more than 45 minutes, than they will not be available, in which case you would be recommended to swap this player out). If you make a mistake you can re-run the cell with the yellow button and remove specific players from your squad, or use the red button to reset it entirely. Once your squad is complete, you can view the predictions in a dataframe format using the first blue button. If happy with everything, you are ready to make your recommendation. Click the second blue button and you the player you should swap, and the corresponding recommendation will be shown. The system works by taking the player with the highest probability of a high points return, thats not in your current squad, and trying to fit them in by replacing the worst player in that position, given their probability is lower than the new recommendation.


## Conclusion

This project has been a success, with accurate predictions being made in a way that is easy to run (once set up) and even easier to view. I am extremely pleased with the tools I have made and will be making use of them in my squad, as I recommend you do. The main thing I am happy about is the ability for me to adapt this to a new season. With the functions made, and relying on the format not being too different next season, it should take minimal adjustment to get the new season set up. This project is more aimed a football enthusiasts who can take the predictions as suggestions to help them with their final decision as the tools still need some initiative to be utilized to their full potential.
