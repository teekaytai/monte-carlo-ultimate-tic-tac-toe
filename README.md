This repo features an AI written in Python 3 that plays ultimate tic tac toe. It uses a Monte Carlo Tree Search algorithm to choose what moves to play.

## What is Ultimate Tic Tac Toe?
Ultimate tic tac toe features a big tic tac toe board with 9 smaller tic tac toe boards arranged into the 3 by 3 grid. The first player can play anywhere on any of the smaller tic tac toe boards. After that, the position of the last move on the smaller tic tac toe board determines which smaller tic tac toe board the next player plays on. For example, playing in the top left cell of a smaller board forces the next player to play on the top left tic tac toe board. The only exception to this rule is when the board that would have been played on is already completed (contains a line of 3 or is completely filled), in which case the next player can play on any other incomplete board.

Forming a line of 3 on a smaller tic tac toe board earns the player that position on the big tic tac toe board. The object of the game is thus to win smaller boards to form a line of 3 on the big tic tac toe board. You can visit the [Wikipedia](https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe) page for a more detailed explanation of the game.

## How the AI Works
The AI employs Monte Carlo Tree Search, which roughly means it tries out random moves and tries to gauge which ones are more likely to lead to success. Each iteration, the AI selects a new move to try, then plays out the rest of the game to completion with random moves. The outcome of the game is then used to update the score of the move chosen. The cleverness of the AI comes from how it chooses moves each time. The AI balances between _exploration_ (trying out moves it has not played out much) and _exploitation_ (choosing moves with higher scores). Over time, the AI will traverse more and more of the game tree and zone in on the best moves.

## But Can it Beat a Human?
If you would like to experience the AI for yourself, run the python file in a terminal and play a round against the AI! I for one have yet to beat it at any difficulty higher than 2... (Note: In my version of the game, if no player forms a line of 3 on the global board, a player who has won more smaller boards wins the game.)

```
  0 1 2 3 4 5 6 7 8
0 O|O| | | |X| | |O
  -+-+-|-+-+-|-+-+-
1  | |X| |X| |O|O|O
  -+-+-|-+-+-|-+-+-
2  | |X|X| | | | |X
  -----+-----+-----
3  | |X|O| | | | |
  -+-+-|-+-+-|-+-+-
4 O| |X|X|X|X|O|O|O
  -+-+-|-+-+-|-+-+-
5 X|O|O|O| | | |X|X
  -----+-----+-----
6 X|O| | | |X|X|O|
  -+-+-|-+-+-|-+-+-
7 X| | |X| |X| |O|
  -+-+-|-+-+-|-+-+-
8  |O|O|O| | |X|O|

Maybe you'll fare better than me? (I was X)
```