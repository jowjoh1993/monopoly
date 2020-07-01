# -*- coding: utf-8 -*-
"""
AUTHOR:   Joshua W. Johnstone
NAME:     example.py
PURPOSE:  Test / show an example of Monopoly simulator

"""

import monopoly

#%% Define players
player1 = monopoly.Player(name='Josh', cash_threshold=50)
player2 = monopoly.Player(name='Austin')
player3 = monopoly.Player(name='Zander')
player4 = monopoly.Player(name='Scott', cash_threshold=500)


#%% Configure game
game = monopoly.Game(players=[player1, player2, player3, player4], debug=True)

for player in game.players:
    print(player.name)


#%% Play one round
game.reset()
game.play_round()


#%% Play a whole game
game.debug = True
game.play()


#%% Print the board
print(game.board)
print(f'Winner is {game.winner.name}!')


#%% Simulate many games

N = 20
winners = []
game_lengths = []

for n in range(N):
    game.play()
    winners.append(game.winner.name)
    game_lengths.append(game.rounds)

for player in game.players:
    print(f'{player.name} won {winners.count(player.name)} out of {len(winners)} games.')

print(f'Average length of game is {round(sum(game_lengths)/len(game_lengths))} rounds.')
    
