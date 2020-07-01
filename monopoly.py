# -*- coding: utf-8 -*-

"""
AUTHOR:   Joshua W. Johnstone
NAME:     monopoly.py
PURPOSE:  Simulate a game of Monopoly

Objects:
    Space
    Property (Space)
    Utility (Space)
    Railroad (Space)
    Board (dict)
    Player
    Game
    ChanceDeck (TODO)
    CommunityChest (TODO)
"""

import pandas as pd
import random
from collections import defaultdict

class Space():
    '''
    Object representing a generic space on the game board.
    '''
    KINDS = ('go',
             'property',
             'chance',
             'community_chest',
             'income_tax',
             'luxury_tax',
             'jail',
             'go_to_jail',
             'free_parking')
    
    def __init__(self,
                 kind='go',
                 owner=None,
                 color=None):
        self.kind = kind
        self.color = color
        
    def __str__(self):
        return f'{self.kind}'     
    
    def __repr__(self):
        return (f'Space(kind={self.kind}, color={self.color})')
    
    def reset(self):
        self.owner = None

class Property(Space):
    '''
    Subclass of Space. Represents a colored property on the board.
    '''
    COLORS = ['brown','light_blue','pink','orange','red','yellow','green','blue']
    
    def __init__(self,
                 name=None,
                 color=None,
                 price=None,
                 owner=None,
                 rent_data=None,
                 houses=0,
                 house_price=0,
                 mortgaged=False):
        self.name = name
        self.color = color
        self.price = price
        self.owner = owner
        self.rent_data = rent_data
        self.houses = houses
        self.house_price = house_price
        self.mortgaged = mortgaged
        
        super().__init__(kind='property', color=color)
        
    def __str__(self):
        owner = 'None' if self.owner is None else self.owner.name
        mort = '(mortgaged)' if self.mortgaged else ''
        return f'{self.name} ({self.color}) {mort} (Owner: {owner}, Houses: {self.houses})'
      
    
    def __repr__(self):
        return (f'Property(name={self.name},'+
                f'color={self.color},'+
                f'price={self.price},'+
                f'owner={self.owner},'+
                f'rent_data={self.rent_data},'+
                f'houses={self.houses},'+
                f'house_price={self.house_price},'+
                f'mortgaged={self.mortgaged})')              
      
    @property
    def rent(self):
        return self.rent_data[self.houses]
    
    @property
    def houses(self):
        return self._houses
    @houses.setter
    def houses(self, value):
        self._houses = value
        
    def reset(self):
        self.owner = None
        self.houses = 0
        self.mortgaged = False
        
class ChanceDeck():
    def __init__(self):
        pass #TODO
    
class CommunityChest():
    def __init__(self):
        pass #TODO
    
class Utility(Space):
    '''
    Subclass of Space. Represents Electric Company and Water Works
    '''
    def __init__(self, name=None, price=150, owner=None, mortgaged=False):
        self.name = name
        self.price = price
        self.owner = owner
        self.mortgaged = mortgaged
        super().__init__(kind='utility')        
    def __str__(self):
        owner = 'None' if self.owner is None else self.owner.name
        mort = '(mortgaged)' if self.mortgaged else ''
        return f'{self.name} {mort} (Owner: {owner})'         
    def __repr__(self):
        return (f'Utility(name={self.name}, owner={self.owner})')
    def reset(self):
        self.owner = None
        self.mortgaged = False
    
class Railroad(Space):
    '''
    Subclass of Space. Represents the four railroads on the board
    '''
    def __init__(self, name=None, price=200, owner=None, mortgaged=False):
        self.name = name
        self.price = price
        self.owner = owner
        self.mortgaged = mortgaged
        super().__init__(kind='railroad')
    def __str__(self):
        owner = 'None' if self.owner is None else self.owner.name
        mort = '(mortgaged)' if self.mortgaged else ''
        return f'{self.name} {mort} (Owner: {owner})'        
    def __repr__(self):
        return (f'Railroad(name={self.name}, owner={self.owner})')
    def reset(self):
        self.owner = None
        self.mortgaged = False
        
class Board(dict):
    '''
    Subclass of dict. Maps an index 0,1,...,39 to Space objects. Keeps track
    of color groups and available houses.
    '''
    def __init__(self, houses=44, **kwargs):
        self.houses = houses
        super().__init__(kwargs)
        
    def __str__(self):
        out = ''
        for index, space in self.items():
            out += f'{index} -- {str(space)}\n'
        return out
    
    def reset(self):
        self.houses = 44
        for index, space in self.items():
            space.reset()
            
    @property
    def color_groups(self):
        groups = defaultdict(list)
        for p in list(self.values()):
            groups[p.color].append(p)
        return groups
        
def build_board():
    '''
    Builds a game board using data in an Excel sheet.

    Returns
    -------
    board : Board

    '''
    board = Board()
    board_data = pd.read_excel('property_data.xlsx')
    for index, row in board_data.iterrows():
        if row['kind'] == 'property':
            board[index] = Property(
                        name = row['name'],
                        color = row['color'],
                        price = row['price'],
                        rent_data = {0:row['rent0'],
                                     1:row['rent1'],
                                     2:row['rent2'],
                                     3:row['rent3'],
                                     4:row['rent4'],
                                     5:row['rent5']},
                        house_price = row['house_price'])
        elif row['kind'] == 'railroad':
            board[index] = Railroad(name=row['name'])
        elif row['kind'] == 'utility':
            board[index] = Utility(name=row['name'])
        else:
            board[index] = Space(kind=row['kind'])
    return board

class Player():
    '''
    Each instance represents one of the players in a game. Handles all actions
    and behaviors a typical player would have. Tracks properties owned, jail
    status, cash amount, bankruptcy status, and monopolies.
    '''
    def __init__(self,
                 name=None,
                 cash=1500,
                 bankrupt=False,
                 cash_threshold=200,
                 in_jail=False,
                 turns_in_jail=0,
                 board = None,
                 space = 0,
                 debug = False):
        self.name = name
        self.cash = cash
        self.bankrupt = bankrupt
        self.cash_threshold = cash_threshold
        self.in_jail = in_jail
        self.turns_in_jail = turns_in_jail
        self.board = board
        self.space = space
        self.debug = debug
        
    def __str__(self):
        b = '(bankrupt)' if self.bankrupt else ''
        j = '(in jail)' if self.in_jail else ''
        return f'{self.name} {b}{j}-- Cash: ${self.cash}'
    
    def __repr__(self):
        return (f'Player('+
                f'name={self.name},'+
                f'cash={self.cash},'+
                f'bankrupt={self.bankrupt},'+
                f'cash_threshold={self.cash_threshold},'+
                f'in_jail={self.in_jail},'+
                f'turns_in_jail={self.turns_in_jail},'+
                f'board={self.board},'+
                f'space={self.space},'+
                f'debug={self.debug})')
        
    def reset(self):
        '''
        Resets player to beginning-of-game status.
        '''
        self.cash = 1500
        self.bankrupt = False
        self.in_jail = False
        self.turns_in_jail = 0
        self.space = 0

    def has_monopoly(self, color):
        '''
        Given a color, returns True if player has a monopoly in that color, and
        False otherwise.
        '''
        count = 0
        for prop in self.owned:
            if not isinstance(prop, Property):
                continue
            if prop.color == color:
                count += 1
        if color in ['blue', 'brown']:
            need = 2
        else:
            need = 3
        if count < need:
            return False
        else:
            return True
        
    def printd(self, msg):
        '''
        Given a string, prints only if self.debug = True.
        '''
        if self.debug:
            print(msg)
        
    @property
    def owned(self):
        '''
        Returns a list of properties that this player owns.
        '''
        owned = []
        for index, space in self.board.items():
            if isinstance(space, (Property, Utility, Railroad)):
                if space.owner == self:
                    owned.append(space)
        return owned
                    
    @property
    def monopolies(self):
        '''
        Returns a list of monopolies that this player has.
        '''
        m = []
        for color in Property.COLORS:
            if self.has_monopoly(color):
                m.append(color)
        return m

    @property
    def railroads_owned(self):
        '''
        Returns a list of Railroads that the player owns.
        '''
        count = 0
        for prop in self.owned:
            if isinstance(prop, Railroad):
                count +=1
        return count
    
    @property
    def houses_owned(self):
        '''
        Returns a count of the total number of houses this player owns.
        '''
        count = 0
        for prop in self.owned:
            if isinstance(prop, Property):
                count += prop.houses
        return count
    
    @property
    def utilities_owned(self):
        '''
        Returns a list of Utilities that the player owns.
        '''
        count = 0
        for prop in self.owned:
            if isinstance(prop, Utility):
                count +=1
        return count   

    @property
    def almost_monopolies(self):
        '''
        Returns a list of "almost monopolies": colors for which the player is
        missing just a single property to have a monopoly. For example, if 
        player owns 2 out of the 3 'red' properties, or 1 out of the 2 'blue'
        properties. This information is used to find trade opportunities between
        players.
        '''
        colors = []
        for color in Property.COLORS:
            count = 0
            for prop in self.owned:
                if isinstance(prop, Property):
                    if prop.color == color:
                        count += 1
            if (color in ['brown','blue'] and count==1) or count==2:
                colors.append(color)
        return colors
    
    @property
    def wants(self):
        '''
        Returns a list of properties that the player "wants." A player is said
        to "want" a property if that property is the last one needed to 
        complete a monopoly. 
        '''
        wants = []
        for color in self.almost_monopolies:
            props = self.board.color_groups[color]
            for p in props:
                if p.owner != self:
                    wants.append(p)
        return wants
    
    def trade(self, player, buy=None, sell=None):
        '''
        Trades 'sell' (a property owned by self) to 'player' in exchange for
        'buy' (a property owned by the 'player').
        '''
        sell.owner = player
        buy.owner = self
        
    def mortgage(self, prop):
        '''
        Changes the 'mortgaged' status of an owned, unmortgaged property to 
        True, and adds the mortgage value of the property to self.cash.
        '''
        if prop not in self.owned:
            raise ValueError("Can't mortgage an unowned property!")
        if prop.mortgaged is True:
            raise ValueError("Property is already mortgaged!")
        self.printd(f'{self.name} mortgages {prop.name}')
        prop.mortgaged = True
        self.cash += round(0.5*prop.price)
        
    def un_mortgage(self, prop):
        '''
        Changes the 'mortgaged' status of an owned, mortgaged property to
        False, and subtracts the mortgage value of the property plus 10% from
        self.cash.
        '''
        if prop not in self.owned:
            raise ValueError("Can't un-mortgage an unowned property!")
        if prop.mortgaged is False:
            raise ValueError("Property is not mortgaged!")
        self.printd(f'{self.name} un-mortgages {prop.name}.')
        prop.mortgaged = False
        self.cash -= round(1.1 * (0.5*prop.price))
    
    def buy(self, prop):
        '''
        Given an unonwed property, changes the owner to self and subtracts
        the purchase price of the property from self.cash.
        '''
        if prop.owner is not None:
            raise ValueError("Property is already owned!")
        self.printd(f'{self.name} buys {prop.name}.')
        self.cash -= prop.price
        prop.owner = self
        
    def buy_house(self, prop):
        '''
        Given a property owned by self, adds one house to the property and
        subtracts one house from the board's available houses. Subtracts the 
        house price of the property from self.cash. If the available houses is
        zero, this action fails.
        '''
        if self.board.houses == 0:
            self.printd(f'{self.name} tried to buy a house, but there are none left.')
        else:
            self.printd(f'{self.name} buys a house for {prop.name}.')
            self.cash -= prop.house_price
            prop.houses += 1
            self.board.houses -= 1
        
    def sell_house(self, prop):
        '''
        Given a property owned by self, subtracts one house from the property
        and adds one house to the board's available houses. Adds one-half of
        house price of the property to self.cash.
        '''
        self.printd(f'{self.name} sells a house from {prop.name}.')
        self.cash += round(0.5*prop.house_price)
        prop.houses -= 1
        self.board.houses += 1
    
    def pay_rent(self, prop):
        '''
        Pays rent to the owner of a property. If self.cash is lower than the
        rent amount, calls self.cover_debt() to attempt to raise the cash. 
        '''
        if prop.mortgaged:
            rent = 0
        else:
            if isinstance(prop, Property):
                rent = prop.rent
                if prop.owner.has_monopoly(prop.color) and prop.houses == 0:
                    rent = rent * 2
            elif isinstance(prop, Railroad):
                rent = 50 * prop.owner.railroads_owned
            elif isinstance(prop, Utility):
                if prop.owner.utilities_owned == 1:
                    mult = 4
                else:
                    mult = 10
                dice_roll = random.randint(1,6) + random.randint(1,6)
                rent = mult * dice_roll
            
        if self.cash - rent < 0:
            self.cover_debt(rent - self.cash, prop.owner)
        if not self.bankrupt:
            self.printd(f'{self.name} pays ${rent} to {prop.owner.name}.')
            self.cash -= rent
            prop.owner.cash += rent
        
    def pay_bank(self, amount):
        '''
        Pays an amount of money to the bank. If self.cash is lower than the 
        amount owed, calls self.cover_debt() to attempt to raise the cash.
        '''
        if self.cash - amount < 0:
            self.cover_debt(amount, 'bank')
        if not self.bankrupt:
            self.printd(f'{self.name} pays ${amount} to the bank.')
            self.cash -= amount
    
    def cover_debt(self, debt, player):
        '''
        Attempts to make up the difference if self.cash can't cover a debt to 
        the bank or to another player. Starts by mortgaging railroads and 
        utilities, then sells houses, and finally mortgages colored properties.
        If all of these alternatives are exhausted, then self declares 
        bankruptcy. 
        '''
        raised = 0
        
        # First, mortgage railroads and utilities
        for prop in self.owned:
            if isinstance(prop, (Railroad, Utility)):
                if prop.mortgaged is False:
                    self.mortgage(prop)
                    raised += 0.5*prop.price
                    if raised > debt:
                        return
        
        # Next, sell houses
        for prop in self.owned:
            if isinstance(prop, Property):
                if prop.houses > 0:
                    self.sell_house(prop)
                    raised += 0.5*prop.house_price
                    if raised > debt:
                        return
                    
        # Finally, mortgage properties
        for prop in self.owned:
            if isinstance(prop, Property):
                if prop.mortgaged is False:
                    self.mortgage(prop)
                    raised += 0.5*prop.price
                    if raised > debt:
                        return
        
        # If we got this far and haven't covered debt, declare bankruptcy
        self.declare_bankruptcy(player)                      
        
    def declare_bankruptcy(self, player):
        '''
        Declares bankruptcy to the given player. If player is 'bank', then
        the owner of all self's properties is set to None. If player is another
        player in the game, then all of self's properties go to that player, as
        well as any remaining amount in self.cash.
        '''
        self.printd(f'{self.name} declares bankruptcy!')
        self.bankrupt = True
        for prop in self.owned:
            if player == 'bank':
                prop.owner = None
            else:
                prop.owner = player
        if player != 'bank':
            player.cash += self.cash
            
    def draw_card(self, kind):
        #TODO: Draw community chest and chance cards
        pass
    
    def roll(self):
        '''
        Rolls the dice! Returns both the total result of the roll, and a boolean
        which is True if the roll was a double, and False otherwise.
        '''
        dice1 = random.randint(1,6)
        dice2 = random.randint(1,6)
        roll = dice1 + dice2
        if dice1 == dice2: 
            double = True
            d = ', a double!'
        else:
            double = False
            d = ''
        self.printd(f'{self.name} rolls {roll} ({dice1}+{dice2}){d}')
        return (roll, double)
    
    def move(self, spaces):
        '''
        Moves self along the game board the given number of spaces. If self 
        passes go, add 200 to self.cash.
        '''
        old_space = self.space
        self.space = (old_space + spaces) % 40
        if spaces > 0 and self.space < old_space:
            self.printd(f'{self.name} passes go and collects $200.')
            self.cash += 200
        
    def resolve_space(self, space):
        '''
        Resolves the outcome of landing on a space, depending on the kind of
        space. 
        '''
        self.printd(f'{self.name} lands on space {self.space} ({space.kind}).')
        if space.kind in ['property','utility','railroad']:
            if space.owner == self:
                self.printd(f'{self.name} owns {space.name}.')
                return
            elif space.owner is None:
                if self.cash-space.price > self.cash_threshold:
                    self.buy(space)
                else:
                    self.printd(f'{self.name} chooses not to buy {space.name}.')
            else:
                self.pay_rent(space)
        elif space.kind == 'luxury_tax':
            self.pay_bank(75)
        elif space.kind == 'income_tax':
            amount = 200 if self.cash >= 2000 else round(0.1*self.cash)
            self.pay_bank(amount)
        elif space.kind == 'go_to_jail':
            self.go_to_jail()
        elif space.kind == 'community_chest':
            self.draw_card('community')
        elif space.kind == 'chance':
            self.draw_card('chance')
            
    def go_to_jail(self):
        '''
        Puts self in jail. 
        '''
        self.printd(f'{self.name} goes to jail.')
        self.space = 10
        self.in_jail = True
        
    def leave_jail(self, spaces):
        '''
        Leaves jail and moves the given number of spaces.
        '''
        self.in_jail = False
        self.move(spaces)
        self.resolve_space(self.board[self.space])
        self.turns_in_jail = 0       
            
    def take_turn(self):
        '''
        Takes a turn in the game. If self is in jail, rolls to try to get out. 
        Upon the third failed attempt, pays $50 to the bank and leaves jail. 
        
        If not in jail: rolls the dice, moves to a new space, and resolves the
        space. If the roll was a double, roll again. Upon the third double roll,
        sends self to jail. 
        
        At the end of the turn, attempts to unmortgage any mortgage properties
        and buy houses for properties in monopolies.
        '''
        self.printd(f"{self.name}'s turn. (Cash={self.cash})")
        if self.in_jail:
            self.turns_in_jail += 1
            self.printd(f'{self.name} has been in jail for {self.turns_in_jail} turns.')
            roll, double = self.roll()
            if double:
                self.printd(f'{self.name} escapes from jail.')
                self.leave_jail(roll)                
            else:                            
                if self.turns_in_jail == 3:
                    self.printd(f'{self.name} posts bail.')
                    self.pay_bank(50)
                    self.leave_jail(roll)
        else:
            double_count = 0
            roll_again = True
            
            while roll_again and not self.in_jail and not self.bankrupt:
                roll, roll_again = self.roll()
                if roll_again:
                    double_count += 1
                if double_count == 3:
                    self.go_to_jail()
                    break
                self.move(roll)
                self.resolve_space(self.board[self.space])
        
        if self.cash > self.cash_threshold:
            for prop in self.owned:
                if prop.mortgaged and (self.cash-1.1*0.5*prop.price)>=self.cash_threshold:
                    self.un_mortgage(prop)
            for color in self.monopolies:
                props = []
                for prop in self.owned:
                    if isinstance(prop, Property):
                        if prop.color == color:
                            props.append(prop)                       
                house_price = props[0].house_price
                while self.cash - house_price >= self.cash_threshold and self.board.houses > 0:
                    h = [p.houses for p in props]
                    if all(x==h[0] for x in h):
                        if h[0] == 5:
                            break
                        limit = h[0]+1
                    else:
                        limit = max(h)
                    
                    for prop in props:
                        if prop.houses < limit and self.cash-prop.house_price >= self.cash_threshold and not prop.mortgaged:
                            self.buy_house(prop)
                    
        
class Game():
    '''
    Represents a game of monopoly, including a game board and players.
    '''
    def __init__(self,
                 board=None,
                 players=None,
                 debug=False):

        if board is None:
            board = build_board()
        self.board = board
        self.players = players
        self.rounds = 0
        self.debug = debug
        self.rounds_no_monopolies = 0

    def printd(self, msg):
        if self.debug:
            print(msg)
        
    @property
    def player_count(self):
        count = 0
        for player in self.players:
            if not player.bankrupt:
                count += 1
        return count
    
    @property
    def game_over(self):
        if self.player_count == 1:
            return True
        else:
            return False
        
    @property
    def active_players(self):
        active_players = []
        for p in self.players:
            if not p.bankrupt:
                active_players.append(p)
        return active_players
        
    @property
    def winner(self):
        if not self.game_over:
            return None
        else:
            for player in self.players:
                if not player.bankrupt:
                    return player
                
    @property
    def has_monopolies(self):
        has_monopolies = False
        for player in self.players:
            if player.monopolies:
                has_monopolies = True
                break
        return has_monopolies
                
    def find_trades(self, buyer):
        '''
        Attempts to find trades between players. A trade occurs if and only if
        the following conditions are satisfied:
            1. A player ('buyer') has at least one "almost monopoly" (see 
               Player.wants).
            2. Another player ('seller') owns one of the properties that
               'buyer' wants
            3. 'Buyer' also has a property that 'seller' wants
            
        If all three conditions are satisfied, then we are guaranteed the
        following situation:
            * 'Buyer' wants property 'X', which 'seller' owns
            * 'Seller' wants property 'Y', which 'buyer' owns
            
        Now, we can swap the owership of properties 'X' and 'Y' to execute the
        trade.
        
        This algorithm is not ideal. It is possible and somewhat likely that
        the trade conditions will never occur, and thus a game will continue
        forever. For now, this is worked around by Game.random_trade, which
        will randomly swap the ownership of two owned properties. Game.play()
        will execute the random trade at regular intervals, unless at least
        one player has a monopoly.
        '''
        for seller in self.players:
            if seller is buyer:
                continue
            buyer_wants  = [p for p in buyer.wants if p in seller.owned]
            seller_wants = [p for p in seller.wants if p in buyer.owned]
            if buyer_wants and seller_wants:
                buy = None
                sell = None
                for b in buyer_wants:
                    for s in seller_wants:
                        if b.color != s.color:
                            buy = b
                            sell = s
                            break
                    if buy and sell:
                        break
                if buy and sell:
                    self.printd(f"{buyer.name} trades {sell.name} to {seller.name} for {buy.name}.")
                    buyer.trade(seller, buy=buy, sell=sell)
                    break
    
    def reset(self):
        self.board.reset()
        for player in self.players:
            player.reset()
            player.board = self.board
            player.debug = self.debug
        self.rounds = 0
        
    def play_round(self):
        self.rounds += 1
        for player in self.players:
            if player.bankrupt:
                continue
            player.take_turn()
            self.find_trades(player)
            if self.game_over:
                break
            
    def random_trade(self):
        p1, p2 = random.sample(self.active_players, k=2)
        if p1.owned and p2.owned:        
            prop_p1 = random.choice(p1.owned)
            prop_p2 = random.choice(p2.owned)
            p1.trade(p2, buy=prop_p2, sell=prop_p1)
               
    def play(self):
        self.reset()        
        while not self.game_over:
            
            # Random trades to prevent infinite games
            if self.rounds_no_monopolies%10==0 and self.rounds_no_monopolies>0:
                self.random_trade()
            if self.rounds > 0 and self.rounds % 50 == 0:
                self.random_trade()
                
            self.play_round()
            if not self.has_monopolies:
                self.rounds_no_monopolies += 1
            else:
                self.rounds_no_monopolies = 0

        self.printd(f'Winner is {self.winner.name}!')
        
