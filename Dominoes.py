# Dominoes
# 12/9/18
# Erik Edwards

# TODO - Bugs
#  - proto-chain: moves to n and s get lost instead of rejected?
#  - check for game points and end game.
# TODO - Features
#  - Intro screen to choose players, computer algorithm, score goal, etc
#  - Add comp player algorithms
#  - Add "auto-play n games" feature to find best comp algorithm
#  - App UI. Use Kivy?

# import headers
from random import shuffle
import pygame
from pygame.locals import *
import os

# CONSTANTS
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
PBOX_WIDTH = SCREEN_WIDTH / 2
PBOX_HEIGHT = 110
BOARD_WIDTH = SCREEN_WIDTH
BOARD_HEIGHT = SCREEN_HEIGHT - PBOX_HEIGHT
DOMINO_WIDTH = 40
DOMINO_HEIGHT = 80
DOMINO_GAP = 2
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SCORE_FONT_SZ = 20
SCORE_FONT_RGB = RED
USE_DELAYS = True
DELAY = 500

# init pygame
pygame.init()
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Domino - a rad skillz joint")
SCORE_FONT = pygame.font.SysFont('Courier New', SCORE_FONT_SZ)

p1_box = pygame.Surface((PBOX_WIDTH, PBOX_HEIGHT))
p2_box = pygame.Surface((PBOX_WIDTH, PBOX_HEIGHT))
board_box = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
board_center = board_box.get_rect().center
end_of_round_screen = pygame.Surface((200, 200))

# img_bg = pygame.image.load("img\img_bg.bmp").convert()


class BoneImg(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super(BoneImg, self).__init__()
        self.image = []
        if img_path != "none":
            # orientations = heavy side DOWN [0], hs UP [1], hs LEFT [2], hs RIGHT [3]
            raw_img = pygame.image.load(img_path).convert()
            t_img = pygame.transform.scale(raw_img, (DOMINO_WIDTH, DOMINO_HEIGHT))
            # add index [0]
            self.image.append(t_img)
            t_img = pygame.transform.flip(self.image[0], False, True)
            # add index [1]
            self.image.append(t_img)
            t_img = pygame.transform.rotate(self.image[0], -90)
            # add index [2]
            self.image.append(t_img)
            t_img = pygame.transform.rotate(self.image[0], 90)
            # add index [3]
            self.image.append(t_img)
            self.rect = self.image[0].get_rect()


class CursorImg(pygame.sprite.Sprite):
    def __init__(self):
        super(CursorImg, self).__init__()
        img_path = os.path.normpath("img/cursor.bmp")
        self.image = []
        raw_img = pygame.image.load(img_path).convert()
        tmp_img = pygame.transform.scale(raw_img, (DOMINO_WIDTH, DOMINO_HEIGHT))
        tmp_img.set_colorkey(WHITE, RLEACCEL)
        self.image.append(tmp_img)
        self.rect = self.image[0].get_rect()
        self.rect.center = (50, 100)
        tmp_img = pygame.transform.rotate(self.image[0], 90)
        self.image.append(tmp_img)
        # for selection of bone to play.
        # cursor val of -1 means draw, val = 0 thru n means position of bone in hand
        self.val = 0
        # for selection of bone placement on board
        # better data structure? "N" or "S" or "E" or "W"
        self.placement = "N"


# Define the domino class
class Domino:

    def __init__(self, side_A, side_B, img_path):
        self.side_A = side_A
        self.side_B = side_B
        # orientations = heavy side DOWN [0], hs UP [1], hs LEFT [2], hs RIGHT [3]
        self.orientation = 0
        self.bone_img = BoneImg(img_path)

    def print_domino(self):
        return str(self.side_A) + ":" + str(self.side_B)

    def is_double(self):
        if self.side_A == self.side_B:
            return True
        else:
            return False

    def swap(self):
        # TODO - swap img too?
        i = self.side_A
        self.side_A = self.side_B
        self.side_B = i

    def locate_img(self, x_pos, y_pos):
        # locate x, y position of img_rect.center
        self.bone_img.rect.centerx = x_pos
        self.bone_img.rect.centery = y_pos

    def display_bone(self, surf):
        surf.blit(self.bone_img.image[self.orientation], self.bone_img.rect)


# Define bone yard class
class BoneYard:

    def __init__(self):
        self.yard = []

        # fill yard with all double 6 dominoes, in order
        for A in range(0, 7):
            for B in range(A, 7):
                img_path = os.path.normpath("img/img_" + str(A) + "-" + str(B) + ".bmp")
                self.yard.append(Domino(A, B, img_path))

        # show ordered yard
        # print("init: add all bones in order.")
        # self.print_yard()

        # shuffle into a random order
        self.shuffle()

        # show shuffled yard
        # print("init: shuffle bone yard.")
        # self.print_yard()

    def print_yard(self):
        for d in self.yard:
            d.print_domino()

    def shuffle(self):
        shuffle(self.yard)

    def deal_one(self):
        if self.yard.__len__() > 0:
            return self.yard.pop()
        else:

            return False


# Define player
class Player:
    def __init__(self, p_num):
        self.hand = []
        self.hand.clear()
        self.score = 0
        self.p_num = p_num
        self.max_double = -1
        self.max_non_double = -1

    def draw(self, domino):
        # set heaviest bones to see who plays first during round 1
        if domino.is_double():
            if self.max_double < domino.side_A*2:
                self.max_double = domino.side_A*2
        # else not a double:
        elif self.max_non_double < domino.side_A + domino.side_B:
            self.max_non_double = domino.side_A + domino.side_B
        # add bone to hand
        self.hand.append(domino)

    def in_hand(self, val):
        # does player hold a bone that matches val?
        for d in self.hand:
            if d.side_A == val:
                return True
            elif d.side_B == val:
                return True
        # if you made it through the loop without returning a val, there wasn't a match
        return False


class CompFirstLegalMoveAlgorithm(Player):
    def __init__(self, player_num):
        super(CompFirstLegalMoveAlgorithm, self).__init__(player_num)

    def make_move(self, board):
        # game.play_bone(bone, pos)
        positions = ["N", "S", "E", "W"]
        # check each bone in hand at each position on board and play first available legal move
        for d in self.hand:
            for move_pos in positions:
                if game.play_bone(self.hand.index(d), move_pos):
                    return True
        # if you went through the loop without finding a legal move, return false
        return False


# define the board object
class Board:
    def __init__(self):
        self.spinner = Domino(-1, -1, "img\img_0-0.bmp")
        self.n_chain = [Domino(-1, -1, "img\img_0-0.bmp")]
        self.s_chain = [Domino(-1, -1, "img\img_0-0.bmp")]
        self.e_chain = [Domino(-1, -1, "img\img_0-0.bmp")]
        self.w_chain = [Domino(-1, -1, "img\img_0-0.bmp")]
        self.proto_chain = [Domino(-1, -1, "img\img_0-0.bmp")]
        self.n_chain.clear()
        self.s_chain.clear()
        self.e_chain.clear()
        self.w_chain.clear()
        self.proto_chain.clear()
        self.spinner_played = False

    def reset_board(self):
        self.spinner = Domino(-1, -1, "img\img_0-0.bmp")
        self.n_chain.clear()
        self.s_chain.clear()
        self.e_chain.clear()
        self.w_chain.clear()
        self.proto_chain.clear()
        self.spinner_played = False

    def curr_board_val(self):
        score = 0
        # if no spinner, score is side b of west (left) end + side a of east (right) end from proto_chain
        if not self.spinner_played:
            if self.proto_chain.__len__() > 1:
                score = self.proto_chain[0].side_B + self.proto_chain[-1].side_A
            elif self.proto_chain.__len__() == 1:
                score = self.proto_chain[0].side_B + self.proto_chain[0].side_A
        # else we do have a spinner, and it's more complicated
        # spinner counts double until both east and west sides are played
        # could be 1) just a spinner, 2) spinner + east, or 3) spinner + west
        else:
            # spinner has been played
            # if north and south are empty, spinner score may be in effect
            if self.n_chain.__len__() + self.s_chain.__len__() == 0:
                # if all four arms are empty, check spinner score
                if self.e_chain.__len__() + self.w_chain.__len__() == 0:
                    score = self.spinner.side_B*2
                # else, east and/or west must be filled, count spinner as double
                else:
                    if self.e_chain.__len__() > 0:
                        # if E chain filled, check west chain
                        if self.w_chain.__len__() > 0:
                            # both east and west are filled. north and south are empty.
                            # check ends of chain for doubles and add up score
                            if self.e_chain[-1].is_double():
                                e_val = self.e_chain[-1].side_B*2
                            else:
                                e_val = self.e_chain[-1].side_B
                            if self.w_chain[-1].is_double():
                                w_val = self.w_chain[-1].side_B*2
                            else:
                                w_val = self.w_chain[-1].side_B
                            score = e_val + w_val
                        else:
                            # east is filled, west is empty. N & S also empty.
                            if self.e_chain[-1].is_double():
                                e_val = self.e_chain[-1].side_B*2
                            else:
                                e_val = self.e_chain[-1].side_B
                            score = e_val + self.spinner.side_B*2
                    else:
                        # E chain is empty. N & S are also empty. check W chain
                        if self.w_chain.__len__() > 0:
                            if self.w_chain[-1].is_double():
                                w_val = self.w_chain[-1].side_B*2
                            else:
                                w_val = self.w_chain[-1].side_B
                            score = w_val + self.spinner.side_B*2
            else:
                # either north or south (or both) are filled. no spinner scoring
                if self.n_chain.__len__() > 0:
                    if self.n_chain[-1].is_double():
                        score += self.n_chain[-1].side_B*2
                    else:
                        score += self.n_chain[-1].side_B
                if self.s_chain.__len__() > 0:
                    if self.s_chain[-1].is_double():
                        score += self.s_chain[-1].side_B*2
                    else:
                        score += self.s_chain[-1].side_B
                if self.e_chain.__len__() > 0:
                    if self.e_chain[-1].is_double():
                        score += self.e_chain[-1].side_B*2
                    else:
                        score += self.e_chain[-1].side_B
                if self.w_chain.__len__() > 0:
                    if self.w_chain[-1].is_double():
                        score += self.w_chain[-1].side_B*2
                    else:
                        score += self.w_chain[-1].side_B
        return score

    def check_points(self):
        score = self.curr_board_val()
        if score % 5 == 0:
            return score
        else:
            return 0

    def play(self, domino, position):
        # add the domino in the position
        # if no spinner on the board, use the proto-chain to hold bones until spinner shows up
        if not self.spinner_played:
            # check if this play is the spinner
            if domino.is_double():
                self.spinner_played = True
                self.spinner = domino
                # move proto-chain to either east or west chain now that spinner is on the board.
                # if first bone is the spinner, don't stress about proto-chain
                if self.proto_chain.__len__() > 0:
                    # does proto-chain belong on east or west side of spinner?
                    # if spinner was played on east, proto becomes west leg, and vice versa
                    if position == "E":
                        for i in range(0, self.proto_chain.__len__()):
                            d = self.proto_chain.pop()
                            self.w_chain.append(d)
                    if position == "W":
                        for i in range(0, self.proto_chain.__len__()):
                            d = self.proto_chain[i]
                            d.swap()
                            self.e_chain.append(d)
                # else proto-chain length == 0 and it can be ignored
            # if proto chain is empty (and no spinner) this is first domino played.
            elif self.proto_chain.__len__() == 0:
                # don't worry about position for first bone
                self.proto_chain.append(domino)
            # if no spinner yet, add to proto-chain
            # proto-chain assumes a points to east and b to west. East (right) towards (meta-spinner)
            # assume requested moves are legal. swap a and b sides if first check doesn't match
            elif position == "W":
                if self.proto_chain[0].side_B != domino.side_A:
                    if self.proto_chain[0].side_B == domino.side_B:
                        domino.swap()
                    else:
                        # neither side is a match. Invalid play
                        return False
                self.proto_chain.insert(0, domino)
            elif position == "E":
                if self.proto_chain[-1].side_A != domino.side_B:
                    if self.proto_chain[-1].side_A == domino.side_A:
                        domino.swap()
                    else:
                        # neither side is a match. Invalid play
                        return False
                self.proto_chain.append(domino)
        else:
            # spinner on the board
            if position == "N":
                # fail unless both e and w chains are started
                if self.e_chain.__len__() == 0 or self.w_chain.__len__() == 0:
                    return False
                # E & W are populated. Add if a match
                if self.n_chain.__len__() > 0:
                    if domino.side_A != self.n_chain[-1].side_B:
                        if domino.side_B == self.n_chain[-1].side_B:
                            domino.swap()
                        else:
                            # neither side matches. throw a fit
                            return False
                # this is first bone in the n chain
                elif domino.side_A != self.spinner.side_A:
                    if domino.side_B == self.spinner.side_A:
                        domino.swap()
                    else:
                        # neither side matches.
                        return False
                self.n_chain.append(domino)
            if position == "S":
                # fail unless both e and w are started
                if self.e_chain.__len__() == 0 or self.w_chain.__len__() == 0:
                    return False
                # E & W are populated. Add if a match
                if self.s_chain.__len__() > 0:
                    if domino.side_A != self.s_chain[-1].side_B:
                        if domino.side_B == self.s_chain[-1].side_B:
                            domino.swap()
                        else:
                            # neither side matches. Bail out
                            return False
                # this is first bone in S chain
                elif domino.side_A != self.spinner.side_A:
                    if domino.side_B == self.spinner.side_A:
                        domino.swap()
                    else:
                        # neither side matches.
                        return False
                self.s_chain.append(domino)
            if position == "E":
                if self.e_chain.__len__() > 0:
                    # chain already populated. check for match with end of chain
                    if domino.side_A != self.e_chain[-1].side_B:
                        if domino.side_B == self.e_chain[-1].side_B:
                            domino.swap()
                        else:
                            # neither side matches
                            return False
                # this is first bone in S chain
                elif domino.side_A != self.spinner.side_A:
                    if domino.side_B == self.spinner.side_A:
                        domino.swap()
                    else:
                        # neither side matches
                        return False
                self.e_chain.append(domino)
            if position == "W":
                if self.w_chain.__len__() > 0:
                    # chain already populated. check for match
                    if domino.side_A != self.w_chain[-1].side_B:
                        if domino.side_B == self.w_chain[-1].side_B:
                            domino.swap()
                        else:
                            # neither side matches
                            return False
                # this is first bone in w chain
                elif domino.side_A != self.spinner.side_A:
                    if domino.side_B == self.spinner.side_A:
                        domino.swap()
                    else:
                        # neither side matches
                        return False
                self.w_chain.append(domino)
        return True

    def print_board(self):
        if self.spinner_played:
            n_str = " "
            # add offset (8 chars * (num bones west of spinner - num bones in north chain) )
            r = self.w_chain.__len__() - self.n_chain.__len__() + 1
            if r < 0:
                r = 0
            for j in range(0, r):
                n_str += "        "
            for i in range(1, self.n_chain.__len__()+1):
                p = self.n_chain[-i]
                n_str += " |" + str(p.side_B) + "||" + str(p.side_A) + "| "
            print(n_str)
            # if n_str longer than w_str + 1, add offset to w_str and s_str to keep spinner aligned
            w_str = ""
            s_str = " "
            if self.w_chain.__len__() + 1 < self.n_chain.__len__():
                n = self.n_chain.__len__() - self.w_chain.__len__() - 1
                for i in range(0, n):
                    w_str += "        "
                    s_str += "        "
            # fill w_str
            for i in range(1, self.w_chain.__len__()+1):
                p = self.w_chain[-i]
                w_str += " |" + str(p.side_B) + "||" + str(p.side_A) + "| "
            e_str = ""
            for i in range(0, self.e_chain.__len__()):
                p = self.e_chain[i]
                e_str += " |" + str(p.side_A) + "||" + str(p.side_B) + "| "
            print(w_str + " |[" + str(self.spinner.side_A) + "||" + str(self.spinner.side_B) + "]| " + e_str)
            # fill s_str
            # add offset (8 chars * num bones west of spinner)
            for j in range(0, self.w_chain.__len__()):
                s_str += "        "
            for i in range(0, self.s_chain.__len__()):
                p = self.s_chain[i]
                s_str += " |" + str(p.side_A) + "||" + str(p.side_B) + "| "

            print(s_str)
        else:
            # no spinner so print proto-chain
            p_str = ""
            for i in range(0, self.proto_chain.__len__()):
                p = self.proto_chain[i]
                p_str += " |" + str(p.side_B) + "||" + str(p.side_A) + "| "
            print(p_str)


# define the game class
class Game:
    def __init__(self, num_players):
        self.game_over = False
        self.num_players = num_players
        self.turn = 0
        # selection starts off as false. Once bone selected, toggle to true to move cursor for placement
        self.selected = False
        self.players = [Player(0)]
        self.players.clear()

        # init players
        '''
        for i in range (0, num_players):
            p = Player(i + 1)
            self.players.append(p)
        '''
        p1 = Player(1)
        p2 = CompFirstLegalMoveAlgorithm(2)
        self.players.append(p1)
        self.players.append(p2)

        self.yard = BoneYard()
        self.board = Board()
        self.cursor = CursorImg()

    def deal_new_game(self):
        if self.num_players == 1 or self.num_players == 2:
            num_bones = 7
        else:
            num_bones = 5

        # give each player a bone, repeat num_bone times
        for i in range(0, num_bones):
            for p in self.players:
                print("player: ", p.p_num, "bone: ", i + 1)
                d = self.yard.deal_one()
                # self.turn = self.players.index(p) + 1
                # d.locate_img()
                p.draw(d)

    def find_starting_player(self):

        high_val = -1
        starting_player = -1
        
        for p in self.players:
            # find best non-double score
            if p.max_non_double > high_val:
                high_val = p.max_non_double
                starting_player = self.players.index(p) + 1

        for p in self.players:
            if p.max_double > high_val:
                high_val = p.max_double
                starting_player = self.players.index(p) + 1

        return starting_player

    def print_all_hands(self):
        for p in self.players:
            print(f'player {p.p_num}, Score: {p.score}, Bones Left: {p.hand.__len__()} ')
            for i in range(0, p.hand.__len__()):
                print(f'{i} : {p.hand[i].print_domino()}')

    def draw_bone(self, p_num):
        b = self.yard.deal_one()
        if not b == False:
            self.players[p_num-1].draw(b)

        # self.players[p_num-1].draw(self.yard.deal_one())

    # TODO - use check for moves to force draw
    # TODO - break check_for_moves into discrete functions for each chain
    # TODO - use to change placement cursor color depending on validity of move
    def check_for_moves(self, p_num):
        # Does player p-num have a legal move?

        # if no spinner, check proto-chain:
        if not self.board.spinner_played:
            # check proto-chain for moves
            if self.board.proto_chain.__len__() == 0:
                # if empty, this is first move so it is legal
                return True
            else:
                # available ends to play are first spot's b-side or last spot's a-side
                if self.players[p_num-1].in_hand(self.board.proto_chain[0].side_B):
                    return True
                elif self.players[p_num-1].in_hand(self.board.proto_chain[-1].side_A):
                    return True

        # otherwise, spinner on the board so check each chain for matches

        # check west chain, if empty check spinner:
        if self.board.w_chain.__len__() > 0:
            w_val = self.board.w_chain[-1].side_B
            if self.players[p_num-1].in_hand(w_val):
                return True
        elif self.players[p_num-1].in_hand(self.board.spinner.side_B):
            return True

        # check east chain, if empty check spinner:
        if self.board.e_chain.__len__() > 0:
            e_val = self.board.e_chain[-1].side_B
            if self.players[p_num - 1].in_hand(e_val):
                return True
        elif self.players[p_num - 1].in_hand(self.board.spinner.side_B):
            return True

        # check north chain, if empty check spinner:
        if self.board.n_chain.__len__() > 0:
            n_val = self.board.n_chain[-1].side_B
            if self.players[p_num - 1].in_hand(n_val):
                return True
        elif self.players[p_num - 1].in_hand(self.board.spinner.side_B):
            return True

        # check south chain, if empty check spinner:
        if self.board.s_chain.__len__() > 0:
            s_val = self.board.s_chain[-1].side_B
            if self.players[p_num - 1].in_hand(s_val):
                return True
        elif self.players[p_num - 1].in_hand(self.board.spinner.side_B):
            return True

        return False

    def check_move(self, bone_to_check, pos):
        # Is bone_to_check at pos a legal move?

        # if no spinner, check proto-chain:
        if not self.board.spinner_played:
            # check proto-chain for moves
            if self.board.proto_chain.__len__() == 0:
                # if empty, this is first move so it is legal
                return True
            else:
                # available ends to play are first spot's b-side or last spot's a-side
                if bone_to_check.sideA == self.board.proto_chain[0].side_B or \
                        bone_to_check.sideB == self.board.proto_chain[0].side_B:
                    return True
                elif bone_to_check.sideA == self.board.proto_chain[-1].side_A or \
                        bone_to_check.sideB == self.board.proto_chain[-1].side_A:
                    return True

        # otherwise, spinner on the board so check each chain for matches

        # check west chain, if empty check spinner:
        if self.board.w_chain.__len__() > 0:
            w_val = self.board.w_chain[-1].side_B
            if bone_to_check.sideA == w_val or bone_to_check.sideB == w_val:
                return True
        elif bone_to_check.side_A == self.board.spinner.side_B or bone_to_check.side_B == self.board.spinner.side_B:
            return True

        # check east chain, if empty check spinner:
        if self.board.e_chain.__len__() > 0:
            e_val = self.board.e_chain[-1].side_B
            if bone_to_check.sideA == e_val or bone_to_check.sideB == e_val:
                return True
        elif bone_to_check.side_A == self.board.spinner.side_B or bone_to_check.side_B == self.board.spinner.side_B:
            return True

        # check north chain, if empty check spinner:
        if self.board.n_chain.__len__() > 0:
            n_val = self.board.n_chain[-1].side_B
            if bone_to_check.sideA == n_val or bone_to_check.sideB == n_val:
                return True
        elif bone_to_check.side_A == self.board.spinner.side_B or bone_to_check.side_B == self.board.spinner.side_B:
            return True

        # check south chain, if empty check spinner:
        if self.board.s_chain.__len__() > 0:
            s_val = self.board.s_chain[-1].side_B
            if bone_to_check.sideA == s_val or bone_to_check.sideB == s_val:
                return True
        elif bone_to_check.side_A == self.board.spinner.side_B or bone_to_check.side_B == self.board.spinner.side_B:
            return True

        return False

    def play_bone(self, bone_num, board_pos):
        d = self.players[self.turn - 1].hand.pop(bone_num)
        # board.play function returns bool to indicate if move is valid
        if self.board.play(d, board_pos):
            # if valid, check points
            score = self.board.check_points()
            self.players[self.turn - 1].score += score
            # and increment turn counter
            self.turn += 1
            if self.turn > self.num_players:
                self.turn = 1
            self.cursor.val = 0
            return True
        else:
            # if not valid move, return bone to player's hand
            self.players[self.turn - 1].hand.append(d)
            print("Invalid Move")
            return False

    def win_round(self, player_num):

        # player "player_num" wins this round. they play first next round and score opponents leftovers
        # score points from opponents' hands
        round_bonus = 0
        for loser in self.players:
            loser_bonus = 0
            for b in loser.hand:
                loser_bonus += b.side_A + b.side_B
            # round this loser's points to the nearest multiple of 5
            div = loser_bonus // 5
            mod = loser_bonus % 5
            rounded_mod = round(mod / 5)
            round_bonus += 5 * div + rounded_mod * 5
        self.players[player_num - 1].score += round_bonus

        # show (splash screen?) round winner and bonus amount
        end_of_round_screen.fill(GREY)
        text = "Player " + str(player_num) + " wins the round"
        text_surf = SCORE_FONT.render(text, True, SCORE_FONT_RGB)
        x = SCREEN_WIDTH / 2
        y = 0
        end_of_round_screen.blit(text_surf, (x, y))
        text = "Bonus Score: " + str(round_bonus)
        text_surf = SCORE_FONT.render(text, True, SCORE_FONT_RGB)
        x = SCREEN_WIDTH / 2
        y = 0
        end_of_round_screen.blit(text_surf, (x, y))
        # REDRAW SCREEN
        self.redraw_screen()
        pygame.display.update()

        # wait a tick so humans can see what's happening
        if USE_DELAYS:
            pygame.time.delay(DELAY)

        # make sure we didn't increment to next player
        self.turn = player_num

        # clear all player' hands
        for p in self.players:
            p.hand.clear()

        # clear dmoinoes from board (spinner, proto, and NSEW chains)
        self.board.reset_board()

        # get a new, freshly shuffled bone yard
        self.yard = BoneYard()

        # re-deal
        self.deal_new_game()

    def redraw_screen(self):
        # clear screen and redraw blank background
        screen.fill(BLACK)
        # screen.blit(img_bg, (0, 0))
        board_box.fill(BLACK)

        # DRAW P1 BOX

        # indicate turn with background color
        if self.turn == 1:
            p1_box.fill(GREY)
        else:
            p1_box.fill(BLACK)

        # show bones in hand
        for d in self.players[0].hand:
            d.display_bone(p1_box)

        # show score
        curr_score = "P1 SCORE: " + str(self.players[0].score)
        score_surf = SCORE_FONT.render(curr_score, True, SCORE_FONT_RGB)
        x = 0
        y = 0   # SCORE_FONT_SZ/2
        p1_box.blit(score_surf, (x, y))

        # DRAW P2 BOX

        # indicate turn
        if self.turn == 2:
            p2_box.fill(GREY)
        else:
            p2_box.fill(BLACK)

        # show bones in hand
        for d in self.players[1].hand:
            d.display_bone(p2_box)

        # show score
        curr_score = "P2 SCORE: " + str(self.players[1].score)
        score_surf = SCORE_FONT.render(curr_score, True, SCORE_FONT_RGB)
        x = 0
        y = 0   # SCORE_FONT_SZ/2
        p2_box.blit(score_surf, (x, y))

        # DRAW BOARD

        # show current board value
        curr_val = "BOARD VALUE: " + str(self.board.curr_board_val())
        val_surf = SCORE_FONT.render(curr_val, True, SCORE_FONT_RGB)
        x = 0
        y = 0   # SCORE_FONT_SZ/2
        board_box.blit(val_surf, (x, y))

        # if there's a spinner, start there then add any side that have non-zero length
        if self.board.spinner_played:
            # offset spinner to center whole chain (positive right and up)
            spinner_x_offset = (self.board.w_chain.__len__() - self.board.e_chain.__len__())/2 * DOMINO_HEIGHT
            spinner_y_offset = (self.board.n_chain.__len__() - self.board.s_chain.__len__())/2 * DOMINO_HEIGHT
           #  self.board.spinner.bone_img.rect.move_ip(-1*spinner_x_offset, -1*spinner_y_offset)
            # draw spinner (vert orientation)
            board_box.blit(self.board.spinner.bone_img.image[0], self.board.spinner.bone_img.rect)
            # draw E
            for d in self.board.e_chain:
                if d.is_double():
                    # show vertical
                    board_box.blit(d.bone_img.image[0], d.bone_img.rect)
                else:
                    # show horizontal
                    # for e_chain, a-side should point left (west)
                    # if a-side is the heavy side:
                    if d.side_A > d.side_B:
                        board_box.blit(d.bone_img.image[2], d.bone_img.rect)
                    # else b-side is heavy side:
                    else:
                        board_box.blit(d.bone_img.image[3], d.bone_img.rect)
            # draw W
            for d in self.board.w_chain:
                if d. is_double():
                    # show vertical
                    board_box.blit(d.bone_img.image[0], d.bone_img.rect)
                else:
                    # show horizontal
                    # for w-Chain, a-side should point right (east)
                    # if side A is heavy:
                    if d.side_A > d.side_B:
                        board_box.blit(d.bone_img.image[3], d.bone_img.rect)
                    # else side B is heavy:
                    else:
                        board_box.blit(d.bone_img.image[2], d.bone_img.rect)
            # draw N
            for d in self.board.n_chain:
                if d.is_double():
                    # show horizontal
                    board_box.blit(d.bone_img.image[2], d.bone_img.rect)
                else:
                    # show vertical
                    # for n_chain, a side points down
                    # if a side is heavy
                    if d.side_A > d.side_B:
                        board_box.blit(d.bone_img.image[0], d.bone_img.rect)
                    # else b side is heavy
                    else:
                        board_box.blit(d.bone_img.image[1], d.bone_img.rect)
            # draw S
            for d in self.board.s_chain:
                if d.is_double():
                    # show horizontal
                    board_box.blit(d.bone_img.image[2], d.bone_img.rect)
                else:
                    # show vertical
                    # for s_chain, a side points up
                    # if a side heavy:
                    if d.side_A > d.side_B:
                        board_box.blit(d.bone_img.image[1], d.bone_img.rect)
                    # else b side heavy:
                    else:
                        board_box.blit(d.bone_img.image[0], d.bone_img.rect)
        # otherwise, spinner hasn't been played. draw proto-chain
        else:
            for d in self.board.proto_chain:
                if d.side_A > d.side_B:
                    # side a is heavy
                    board_box.blit(d.bone_img.image[3], d.bone_img.rect)
                elif d.side_B > d.side_A:
                    # side b is heavy
                    board_box.blit(d.bone_img.image[2], d.bone_img.rect)
                elif d.side_A == d.side_B:
                    # double. show vertically
                    board_box.blit(d.bone_img.image[0], d.bone_img.rect)
        screen.blit(board_box, (0, 0))

        # draw cursor
        # if bone not selected yet, draw selection cursor
        if not self.selected:
            # if p1 turn, draw p1 selection cursor
            if self.turn == 1:
                p1_box.blit(self.cursor.image[0], self.cursor.rect)
            elif self.turn == 2:
                p2_box.blit(self.cursor.image[0], self.cursor.rect)
        else:
            # bone has been selected, draw placement cursor
            if self.cursor.placement == "N" or self.cursor.placement == "S":
                if self.players[self.turn-1].hand[self.cursor.val].is_double():
                    # draw horizontal
                    board_box.blit(self.cursor.image[1], self.cursor.rect)
                else:
                    # draw vert cursor
                    board_box.blit(self.cursor.image[0], self.cursor.rect)
            else:
                if self.players[self.turn-1].hand[self.cursor.val].is_double():
                    # draw vertical
                    board_box.blit(self.cursor.image[0], self.cursor.rect)
                else:
                    # draw horiz cursor
                    board_box.blit(self.cursor.image[1], self.cursor.rect)

        # screen.blit(p1_box, (0, 600))
        screen.blit(p1_box, (0, SCREEN_HEIGHT - PBOX_HEIGHT))
        screen.blit(p2_box, (PBOX_WIDTH, SCREEN_HEIGHT - PBOX_HEIGHT))
        screen.blit(board_box, (0, 0))

    def update_cursor_position(self):
        # selection mode, moves rect depending on val
        if not self.selected:
            self.cursor.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
            if -1 < self.cursor.val < self.players[self.turn-1].hand.__len__():
                # cursor is on a bone so use it's location
                self.cursor.rect.center = self.players[self.turn-1].hand[self.cursor.val].bone_img.rect.center
            elif self.cursor.val == -1:
                # cursor is on "draw a bone"
                self.cursor.rect.center = (0, PBOX_HEIGHT/2)
        # else placement mode, move rect to end of appropriate chain
        else:
            if self.cursor.placement == "N":
                self.cursor.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                if self.board.n_chain.__len__() > 0:
                    # offset from last in chain
                    self.cursor.rect.center = self.board.n_chain[-1].bone_img.rect.center
                    self.cursor.rect.centery -= DOMINO_HEIGHT
                else:
                    # offset from spinner
                    self.cursor.rect.center = (board_center[0], board_center[1] - DOMINO_HEIGHT - DOMINO_GAP)
            elif self.cursor.placement == "S":
                self.cursor.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                if self.board.s_chain.__len__() > 0:
                    self.cursor.rect.center = self.board.s_chain[-1].bone_img.rect.center
                    self.cursor.rect.centery += DOMINO_HEIGHT
                else:
                    self.cursor.rect.center = (board_center[0], board_center[1] + DOMINO_HEIGHT + DOMINO_GAP)
            elif self.cursor.placement == "E":
                self.cursor.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                if self.board.e_chain.__len__() > 0:
                    self.cursor.rect.center = self.board.e_chain[-1].bone_img.rect.center
                    self.cursor.rect.centerx += DOMINO_HEIGHT
                else:
                    self.cursor.rect.center = (board_center[0] + (DOMINO_WIDTH/2) + (DOMINO_HEIGHT/2), board_center[1])
            elif self.cursor.placement == "W":
                self.cursor.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                if self.board.w_chain.__len__() > 0:
                    self.cursor.rect.center = self.board.w_chain[-1].bone_img.rect.center
                    self.cursor.rect.centerx -= DOMINO_HEIGHT
                else:
                    self.cursor.rect.center = (board_center[0] - (DOMINO_WIDTH/2) - (DOMINO_HEIGHT/2), board_center[1])

    def update_hand_rects(self):

        x_offset = 10
        y_offset = 5

        # draw player 1 box
        for d in self.players[0].hand:
            # locate upper left corner of img_rect relative to player window
            x_pos = x_offset + DOMINO_WIDTH/2 + (self.players[0].hand.index(d) * (DOMINO_WIDTH + DOMINO_GAP))
            y_pos = PBOX_HEIGHT - DOMINO_HEIGHT/2 - y_offset
            d.locate_img(x_pos, y_pos)
            d.display_bone(p1_box)

        # draw player 2 box
        for d in self.players[1].hand:
            # locate upper left corner of img_rect relative to player window
            x_pos = x_offset + DOMINO_WIDTH/2 + (self.players[1].hand.index(d) * (DOMINO_WIDTH + DOMINO_GAP))
            y_pos = PBOX_HEIGHT - DOMINO_HEIGHT/2 - y_offset
            d.locate_img(x_pos, y_pos)
            d.display_bone(p2_box)

    def update_board_rects(self):
        if self.board.spinner_played:
            # draw spinner board
            # assume board is legal. don't check rules

            # start with spinner
            self.board.spinner.bone_img.rect.center = board_box.get_rect().center

            # draw e_chain
            for d in self.board.e_chain:
                i = self.board.e_chain.index(d)
                x = y = 0
                if d.is_double():
                    # draw vertical
                    d.bone_img.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                    offset = DOMINO_HEIGHT/2 + DOMINO_GAP + DOMINO_WIDTH/2
                    # is_double = True so there must be a previous bone in chain
                    # offset from prev bone in chain
                    x = self.board.e_chain[i-1].bone_img.rect.centerx + offset
                    y = self.board.e_chain[i-1].bone_img.rect.centery
                    d.bone_img.rect.center = (x, y)
                else:
                    # draw horizontal
                    d.bone_img.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                    if i > 0:
                        # if previous bone in chain was a double:
                        if self.board.e_chain[i-1].is_double():
                            offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        # if previous bone wasn't a double:
                        else:
                            offset = DOMINO_HEIGHT + DOMINO_GAP
                        x = self.board.e_chain[i-1].bone_img.rect.centerx + offset
                        y = self.board.e_chain[i-1].bone_img.rect.centery
                    elif i == 0:
                        # first bone in chain so offset from spinner
                        offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        x = self.board.spinner.bone_img.rect.centerx + offset
                        y = self.board.spinner.bone_img.rect.centery
                    d.bone_img.rect.center = (x, y)

            # draw w_chain
            for d in self.board.w_chain:
                i = self.board.w_chain.index(d)
                x = y = 0
                if d.is_double():
                    # draw vertical
                    d.bone_img.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                    offset = DOMINO_HEIGHT/2 + DOMINO_GAP + DOMINO_WIDTH/2
                    # offset from prev bone in chain
                    x = self.board.w_chain[i-1].bone_img.rect.centerx - offset
                    y = self.board.w_chain[i-1].bone_img.rect.centery
                    d.bone_img.rect.center = (x, y)
                else:
                    # draw horizontal
                    d.bone_img.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                    if i > 0:
                        # if previous bone was a double:
                        if self.board.w_chain[i-1].is_double():
                            offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        # if previous bone wasn't a double:
                        else:
                            offset = DOMINO_HEIGHT + DOMINO_GAP
                        x = self.board.w_chain[i-1].bone_img.rect.centerx - offset
                        y = self.board.w_chain[i-1].bone_img.rect.centery
                    elif i == 0:
                        # first bone in chain so offset from spinner
                        offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        x = self.board.spinner.bone_img.rect.centerx - offset
                        y = self.board.spinner.bone_img.rect.centery
                    d.bone_img.rect.center = (x, y)

            # draw n_chain
            for d in self.board.n_chain:
                i = self.board.n_chain.index(d)
                x = y = 0
                if d.is_double():
                    # draw horizontal
                    d.bone_img.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                    offset = DOMINO_HEIGHT/2 + DOMINO_GAP + DOMINO_WIDTH/2
                    # offset from prev bone in chain
                    x = self.board.n_chain[i-1].bone_img.rect.centerx
                    y = self.board.n_chain[i-1].bone_img.rect.centery - offset
                    d.bone_img.rect.center = (x, y)
                else:
                    # draw vertical
                    d.bone_img.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                    if i > 0:
                        # if previous bone was a double:
                        if self.board.n_chain[i-1].is_double():
                            offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        # if previous bone wasn't a double:
                        else:
                            offset = DOMINO_HEIGHT + DOMINO_GAP
                        x = self.board.n_chain[i-1].bone_img.rect.centerx
                        y = self.board.n_chain[i-1].bone_img.rect.centery - offset
                    elif i == 0:
                        # first bone in chain so offset from spinner
                        offset = DOMINO_GAP + DOMINO_HEIGHT
                        x = self.board.spinner.bone_img.rect.centerx
                        y = self.board.spinner.bone_img.rect.centery - offset
                    d.bone_img.rect.center = (x, y)

            # draw s_chain
            for d in self.board.s_chain:
                i = self.board.s_chain.index(d)
                x = y = 0
                if d.is_double():
                    # draw horizontal
                    d.bone_img.rect.size = (DOMINO_HEIGHT, DOMINO_WIDTH)
                    offset = DOMINO_HEIGHT/2 + DOMINO_GAP + DOMINO_WIDTH/2
                    # offset from prev bone in chain
                    x = self.board.s_chain[i-1].bone_img.rect.centerx
                    y = self.board.s_chain[i-1].bone_img.rect.centery + offset
                    d.bone_img.rect.center = (x, y)
                else:
                    # draw vertical
                    d.bone_img.rect.size = (DOMINO_WIDTH, DOMINO_HEIGHT)
                    if i > 0:
                        # if previous bone was a double:
                        if self.board.s_chain[i-1].is_double():
                            offset = DOMINO_WIDTH/2 + DOMINO_GAP + DOMINO_HEIGHT/2
                        # if previous bone wasn't a double:
                        else:
                            offset = DOMINO_HEIGHT + DOMINO_GAP
                        x = self.board.s_chain[i-1].bone_img.rect.centerx
                        y = self.board.s_chain[i-1].bone_img.rect.centery + offset
                    elif i == 0:
                        # first bone in chain so offset from spinner
                        offset = DOMINO_GAP + DOMINO_HEIGHT
                        x = self.board.spinner.bone_img.rect.centerx
                        y = self.board.spinner.bone_img.rect.centery + offset
                    d.bone_img.rect.center = (x, y)

        else:
            # draw proto-chain
            n = self.board.proto_chain.__len__()
            if n > 0:
                offset = self.board.proto_chain.__len__() / 2 * (DOMINO_HEIGHT + DOMINO_GAP)
                for d in self.board.proto_chain:
                    x = board_center[0] - offset + (self.board.proto_chain.index(d) * (DOMINO_HEIGHT + DOMINO_GAP))
                    y = board_center[1]
                    d.bone_img.rect.center = (x, y)


def test_print():
    print("keydown_count: " + str(keydown_count))
    print("turn: " + str(game.turn))
    print("cursor val: " + str(game.cursor.val))
    print("cursor placement: " + str(game.cursor.placement))
    print("selection made?: " + str(game.selected))
    game.print_all_hands()
    game.board.print_board()


# TODO: add intro screen to select game or choose auto match
np = 2

# initialize game
game = Game(np)
game.deal_new_game()
game.turn = game.find_starting_player()

# print to terminal
game.print_all_hands()
game.board.print_board()

# TODO - Test
keydown_count = 0

# TODO - check gameover vs roundover. add opponents' hands to score after round. allow for re-deal after round.
# Main program loop
while not game.game_over:

    # if any player is out of bones: round over, man
    for p in game.players:
        if p.hand.__len__() == 0:
            game.win_round(p.p_num)

    # If P1 turn, run event loop to choose move. If P2 turn, send game state to some P2.move() function
    if game.turn == 1:

        # Run Event loop for P1 turn
        for event in pygame.event.get():
            # check for quitters
            if event.type == pygame.QUIT:
                game.game_over = True
            # check for keydown events
            elif event.type == pygame.KEYDOWN:
                # if we're waiting to pick a bone, check for arrows or return key
                if not game.selected:
                    if event.key == pygame.K_LEFT:
                        if game.cursor.val > -1:
                            game.cursor.val -= 1
                    elif event.key == pygame.K_RIGHT:
                        if game.cursor.val < game.players[game.turn - 1].hand.__len__() - 1:
                            game.cursor.val += 1
                    elif event.key == K_RETURN:
                        # selection has been made.
                        # cursor.val will either be index of bone to play or -1 (draw from yard)
                        if game.cursor.val == -1:
                            # draw pile was selected
                            game.draw_bone(game.turn)
                        else:
                            # bone to play was selected
                            game.selected = True
                # else we have a bone selected and we're placing it,
                # so check for cursor movements on board to select placement
                else:
                    if event.key == K_LEFT:
                        game.cursor.placement = "W"
                    elif event.key == K_RIGHT:
                        game.cursor.placement = "E"
                    elif event.key == K_UP:
                        game.cursor.placement = "N"
                    elif event.key == K_DOWN:
                        game.cursor.placement = "S"
                    elif event.key == K_RETURN:
                        # placement has been selected
                        bone = game.cursor.val
                        pos = game.cursor.placement
                        if bone > -1:
                            # a bone was selected to play
                            game.play_bone(bone, pos)
                            game.selected = False
                # TODO - TEST: check cursor position, hands, and board on console after every key press
                keydown_count += 1
                test_print()

    # if P2 turn, get move from algorithm
    elif game.turn == 2:
        # slow 'er down there
        if USE_DELAYS:
            pygame.time.delay(DELAY)
        # try making a move from hand, draw if no legal moves are available
        if not game.players[1].make_move(game.board):
            if game.yard.yard.__len__() > 0:
                game.players[1].draw(game.yard.yard.pop())
            else:
                # no more bones to draw = blocked --> end round
                game.win_round(2)



    # update cursor rect position if needed
    game.update_cursor_position()
    # update domino positions in hands and on board
    game.update_hand_rects()
    game.update_board_rects()

    # GAME LOGIC

    # REDRAW SCREEN
    game.redraw_screen()
    pygame.display.update()

pygame.quit()
