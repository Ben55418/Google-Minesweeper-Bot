# (it's bad)

# Google-Minesweeper-Bot
A Python bot that can play Google Minesweeper


## Instructions
Have Google Minesweeper open on your main monitor for pyautogui to recognize. Upon opening the bot, provide the program with "easy", "medium" or "hard". The bot should automatically find the game and start playing (try to avoid similarly green colors in the background as it may confuse the bot)

## Additional instructions
```
typing the "exit" command will quit the program
typing the "delay" command will allow the user to set the start delay of the bot (in seconds), default 0. Useful for single-monitor setups
typing the "prints" command will toggle most prints. Win and error messages remain unaffected, default False
```

## Bot messages
### Rules
total_mines and total_open are for the surrounding tiles
```
basic mine rules - if total_mines + total_open == tile_value then mark all surrounding as mines
basic open rules - if total_mines == tile_value then mark all surround open tiles as open
1-2C+ mine rules - look it up
1-1+ open rules - look it up

all mines identified - all the mines have been found. Clear the board and win.
```
### Print board
the bot will print its vision of the board
```
"E" : value of -9 - error in identifying tile
"X" : value of -2 - identified as a mine
"?" : value of -1 - tile value unknown
" " : value of 0 - tile value of 0
"1"-"8" : value of 1-8 - tile value
```
### Other messages
```
game won - self explanatory
no progress can be made by this bot - the bot failed to clear any more squares for 3 moves in a row
quit due to error overload - either the software is crap or part of the board was obstructed
```

## Dependencies 
```
cv2
numpy
pyautogui
```



