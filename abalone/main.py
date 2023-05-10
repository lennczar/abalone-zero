import numpy as np
import ast
from enum import IntEnum

class Marble(IntEnum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2

gutter = {
    Marble.WHITE: 0,
    Marble.BLACK: 0
}

board_state = np.transpose([
    [0, 0, 0, 0, 2, 2, 2, 2, 2],
    [0, 0, 0, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 0],
])

current_player = 0

def get_board_state():
    return board_state

def main():        
    global current_player

    # example moves: black pushes white marble off board

    # move_marbles([(-1,2)],[(-1,1)])
    # current_player = 1 - current_player
    # move_marbles([(1,-4),(1,-3),(1,-2)],[(1,-3),(1,-2),(1,-1)])
    # current_player = 1 - current_player
    # move_marbles([(-1,1)],[(-1,0)])
    # current_player = 1 - current_player
    # move_marbles([(1,-3),(1,-2),(1,-1)],[(1,-2),(1,-1),(1,-0)])
    # current_player = 1 - current_player
    # move_marbles([(-1,0)],[(-1,1)])
    # current_player = 1 - current_player
    # move_marbles([(1,-2),(1,-1),(1,-0)],[(1,-1),(1,0),(1,1)])
    # current_player = 1 - current_player
    # move_marbles([(-1,1)],[(-1,0)])
    # current_player = 1 - current_player
    # move_marbles([(1,-1),(1,0),(1,1)],[(1,0),(1,1),(1,2)])
    # current_player = 1 - current_player
    # move_marbles([(-1,0)],[(-1,1)])
    # current_player = 1 - current_player
    # move_marbles([(1,0),(1,1),(1,2)],[(1,1),(1,2),(1,3)])
    # current_player = 1 - current_player
    # move_marbles([(-1,1)],[(-1,0)])
    # current_player = 1 - current_player
    # move_marbles([(1,1),(1,2),(1,3)],[(1,2),(1,3),(1,4)])
    # current_player = 1 - current_player

    while gutter[Marble.BLACK] < 6 and gutter[Marble.WHITE] < 6:

        # get move from user input
        print(board_state)
        print(("WHITE" if current_player == 0 else "BLACK") + " players move!")
        move_str = input("make a move (sources, targets): ")
        (ss, ts) = ast.literal_eval(move_str)

        # ignore illegal moves, just try again
        while (move_marbles(ss, ts) == False):
            move_str = input("make a move (sources, targets): ")
            (ss, ts) = ast.literal_eval(move_str)

        # alernate between players
        current_player = 1 - current_player

    if gutter[Marble.BLACK] >= 6:
        print("White wins!")
    elif gutter[Marble.WHITE] >= 6:
        print("Black wins!")

def move_marbles(ss, ts, pushing=False):
    global board_state

    print(("WHITE" if current_player == 0 else ("BLACK" if not pushing else "PUSHED")) + " " + str(ss) + " to " + str(ts))

    # moving information
    moving_forward = any( (t in ss) for t in ts )
    moving_direction = delta(ss[0], ts[0])
    own_marble = board_state_at(ss[0])

    # sources and targets have same amount of marbles
    same_size = len(ss) == len(ts)
    if not same_size: 
        print("illegal move: not same size")
        return False
    
    # attempting to move a marble that is not owned by current player
    if not pushing:
        for s in ss:
            marble = board_state_at(s)
            if ((current_player == 0 and marble != Marble.WHITE) 
                or (current_player == 1 and marble != Marble.BLACK)):
                print("illegal move: not your marble (" + str(marble) + ")")
                return False

    # sources and targets are in a line
    same_shape = is_on_line(ss) and is_on_line(ts)
    if not same_shape: 
        print("illegal move: not same shape")
        return False

    # source and target lines are parllel
    parallel = len(ss) == 1 or delta(ss[0], ss[1]) == delta(ts[0], ts[1])
    if not parallel: 
        print("illegal move: not parallel")
        return False

    # we're only moving one space
    moving_one_space = all( is_neighbor(s, t) for (s, t) in zip(ss, ts) )
    if not moving_one_space: 
        print("illegal move: not moving one space")
        return False

    # target location is occupied
    target_occupied = any( is_on_board(t) and board_state_at(t) != Marble.EMPTY for t in ts )
    if target_occupied and not moving_forward: 
        print("illegal move: target occupied")
        return False

    # print("target occupied? " + str(target_occupied))
    # print("moving forward? " + str(moving_forward))

    # pushing opponents marble(s)
    if (moving_forward and target_occupied):
        p = ss[0]
        (mq, mr) = moving_direction 

        # move to space in front of line
        while (p in ss):
            (pq, pr) = p
            p = (pq + mq, pr + mr)

        # scan next 1/2/3 spaces
        pushing = []
        for i in range(len(ss)):
            
            if not is_on_board(p) or board_state_at(p) == Marble.EMPTY:
                # print("pushing? " + str(len(pushing)))
                if len(pushing) > 0:
                    # print("pushing " + str(pushing))
                    move_marbles(pushing, [ (q + mq, r + mr) for (q, r) in pushing ], pushing=True)
                break

            elif board_state_at(p) == own_marble:
                print("illegal move: pushing own marble")
                return False

            else:
                if (i < len(ss) - 1):
                    # not last move
                    pushing.append(p)
                else:
                    # last move (& there was no empty space)
                    print("illegal move: insufficient pushing strength")
                    return False 

            # print(pushing)
            # print(p)

            (pq, pr) = p
            p = (pq + mq, pr + mr)

    # keep copy of relevent states to prevent self overriding
    marbles = [ board_state_at(s) for s in ss ]
    # print("moving " + str(marbles))

    # remove marbles from current position
    for s in ss:
        set_board_state_at(s, Marble.EMPTY)

    # add marbles to new position
    for s, t, m in zip(ss, ts, marbles):

        # remove marble if pushed off the board
        if not is_on_board(t):
            print(("WHITE" if own_marble == Marble.BLACK else "BLACK") + " scored a point! (" + str(gutter) + ")")
            gutter[own_marble] += 1
        else:
            set_board_state_at(t, m)

    return True

## Auxiliaries ##

# conforming to conventions in
# https://www.redblobgames.com/grids/hexagons/#coordinates
def axial_to_cartesian(p, radius = 4):
    (q, r) = p
    return (radius + q, radius + r)

def cartesian_to_axial(p, radius = 4):
    (x, y) = p
    return (x - radius, y - radius)

def delta(p0, p1):
    (q0, r0) = p0
    (q1, r1) = p1
    return (q1 - q0, r1 - r0)

def get_neighbors(p):
    (q, r) = p
    return [
        (q,     r - 1),
        (q + 1, r - 1),
        (q - 1, r    ),
        (q + 1, r    ),
        (q - 1, r + 1),
        (q,     r + 1),
    ]

def board_state_at(p):
    (x, y) = axial_to_cartesian(p)
    return board_state[x][y]

def set_board_state_at(p, val):
    global board_state
    (x, y) = axial_to_cartesian(p)
    board_state[x][y] = val
    
def is_on_board(p, radius = 4):
    (q, r) = p
    return q <= radius and q >= -radius and r <= radius and r >= -radius

def is_on_line(ps):

    if len(ps) == 1:
        return True
    
    elif len(ps) == 2:
        p0, p1 = ps
        is_neighbor(p0, p1)
    
    elif len(ps) == 3:
        (q0, r0), (q1, r1), (q2, r2) = ps
        (dq, dr) = (q1 - q0, r1 - r0)
        return abs(dq + dr) <= 1 and q1 + dq == q2 and r1 + dr == r2
    
    else:
        return False

def is_neighbor(p0, p1):
    (dq, dr) = delta(p0, p1)
    return abs(dq + dr) <= 1

main()


# example initial moves
# ([(-1,2)],[(-1,1)]) - move a single white marble 
# ([(1,-4),(1,-3),(1,-2)],[(1,-3),(1,-2),(1,-1)]) - move three black marbles

# illegal initial moves
# ([(-2,2),(-3,2)],[(-3,1),(-2,1)]) - attempt to move a white and "empty" marble

