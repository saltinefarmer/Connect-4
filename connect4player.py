"""
ComputerPlayer is an algorithm that assesses a board of connect four and selects
the best move. It works in tandem with connect4.py. It requires an ID (1 or 2) to tell it 
which player it is, and a difficulty level telling it how many plies of a
decision tree to look ahead.
"""
__author__ = "Silver Lippert"
__date__ = "2/25/24"

import random
import time
import heapq

class ComputerPlayer:
    id = 0 # globals
    difficulty = 0
    def __init__(self, id, difficulty_level):
        self.id = id
        self.difficulty = difficulty_level
        """
        Constructor, takes a difficulty level (the # of plies to look
        ahead), and a player ID that's either 1 or 2 that tells the player which turn 
        to play on.

        """

    def pick_move(self, rack):
        """
        Pick the move to make. It will be passed a rack with the current board
        layout, column-major. A 0 indicates no token is there, and 1 or 2
        indicate discs from the two players. Column 0 is on the left, and row 0 
        is on the bottom. It must return an int indicating in which column to 
        drop a disc.

        """

        while True:
            best = self.__make_choice(rack, 0, self.id)
            if rack[best[2]][-1] == 0: return best[2]



    def __make_choice(self, rack: tuple, ply: int, id: int)-> tuple:
        moves = []
        i = 0
        while i < len(rack): # current board's potential moves
            # each potential move should make more potential moves
            test = self.__create_board(rack, i, id)
            if test != None: # will return none if there are no moves in that column

                score = self.__eval_board(test, id)
                ret_ply = ply
                
                if ply != self.difficulty - 1 and score != float('inf'):
                    if id == 1:
                        ret_val = self.__make_choice(test, ply+1, 2) # will return best move for next player
                    if id == 2:
                        ret_val = self.__make_choice(test, ply+1, 1) # should return best score of the child here
                    
                    score = ret_val[0]
                    ret_ply = ret_val[1]
                    
                elif score == float('inf'):
                    return (float('-inf'), ply, i)

                # return scored, negated
                if(score == float('inf')):
                    score = float('-inf')
                    heapq.heappush(moves, (score, ret_ply,  i))
                elif(score == float('-inf')):
                    score = float('inf')
                    heapq.heappush(moves, (score, ret_ply, i))
                else:
                # making score negative so it will choose the largest number bc heapq sorts by smallest
                    heapq.heappush(moves, (-score, ret_ply, i))
                

            i+=1
        
        if(len(moves)>0):
            best = heapq.heappop(moves)
        else:
            best = ()
        return best # (score, move)


    def __create_board(self, rack: tuple, play: int, id: int): # create a board that doesnt affect final choice
        
        rack_list = [list(x) for x in rack]
        i = 0
        while i < len(rack_list[play]):
            if rack_list[play][i] == 0:
                rack_list[play][i] = id
                rack_list = tuple([tuple(x) for x in rack_list])
                return rack_list
            i += 1
        return None
        

    def __eval_board(self, rack, id: int):
        score = 0
    
        # to evaluate score:
        # check each quartet

        # check for transposed horizontal
        column = 0
        row = 0
        while row < len(rack):

            while column < len(rack[row]) - 3: # dont explore final 3, as there will not be 4 tokens to evaluate
                score = self.__count_score(score, rack[row][column: column+4].count(1), rack[row][column: column+4].count(2), id)
                column += 1

            row += 1
            column = 0

        # check for transposed vertical
        row = 0
        while column < len(rack[0]):

            while row < len(rack) -3: # dont explore final 3, as there will not be 4 tokens to evaluate

                temp = []
                i = row
                while i < row + 4:
                    temp.append(rack[i][column])
                    i += 1
                temp = tuple(temp)

                score = self.__count_score(score, temp.count(1), temp.count(2), id)

                row += 1

            column += 1
            row = 0
        

        # check for -> diagonal 
        column = 0
        while column < len(rack[row])-3:

            while row < len(rack) -3:
                temp = []
                diagonal = 0

                while diagonal < 4:
                    # check
                    temp.append(rack[row + diagonal][column + diagonal])

                    diagonal += 1

                score = self.__count_score(score, temp.count(1), temp.count(2), id)

                row += 1

            column += 1
            row = 0

        # check for <- diagonal 
        column = 0
        row = len(rack) -1
        diagonal = 0
        while column < len(rack[row])-3: # 

            while row > 2:
                diagonal = 0
                temp = []

                while diagonal < 4:
                    # check
                    temp.append(rack[row - diagonal][column + diagonal])
                    diagonal += 1

                score = self.__count_score(score, temp.count(1), temp.count(2), id)
                row -= 1

            column += 1
            row = len(rack) - 1
        
        return score
    

    def __count_score(self, score: int, p1_score: int, p2_score: int, id: int):
        # accepts the number of player 1 tokens and player 2 tokens in a quadrent
        # assesses them, and decides how much weight the quartet has
        # p1 score is not necessarily the score of the player with ID 1
        # it is the score of the player that we are actively assessing in the current ply

        if(p1_score > 0 and p2_score > 0): # if theres both p1 and p2 in a quartet, no points are added
            return score
        elif(p1_score > 0 and p1_score < 4): # 1 token is 1 point, 2 is 10 points, and 3 is 100
            p1_score = 10**(p1_score -1)
        elif(p1_score == 4): # infinite score for a win
            p1_score = float('inf')

        elif(p2_score > 0 and p2_score < 4): # repeat above for p2
            p2_score = 10**(p2_score -1)
        elif(p2_score == 4):
            p2_score = float('inf')
        
        if(id == 1): # change score depending on which player we are currently
            # the current player will get positive vals, the opponent will get negative vals
            score += p1_score
            score -= p2_score
        else:
            score -= p1_score
            score += p2_score
        return score