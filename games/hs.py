from common.constants import PLAY1, PLAY2, PLAY3, ATTACK, PASS, DECKS, STARTING_HANDS, HEROES, A, CHANCE
import random
import itertools


class GameStateBase:

    def __init__(self, parent, to_move, decks, n):
        self.parent = parent
        self.to_move = to_move
        self.decks = decks
        self.n = n

    def play(self, action):
        # print('play this action', action)
        # print('children[action]', self.children[action])
        return self.children[action]

    def is_chance(self):
        return self.to_move == CHANCE

    def inf_set(self):
        raise NotImplementedError("Please implement information_set method")


class RootChanceGameState(GameStateBase):
    def __init__(self, starting_hands):
        super().__init__(parent = None, to_move = CHANCE, decks = DECKS, n = 0)
        self.starting_hands = starting_hands

        self.children = {
            starting_cards: PlayerMoveGameState(
                self, A, self.__get_deck_next_round(self.decks, starting_cards), starting_cards, [[HEROES[0]], [HEROES[1]]], [], self.n+1
            ) for starting_cards in self.starting_hands
        }
        # print(self.children)
        self._chance_prob = 1. / len(self.children)

    def __get_deck_next_round(self, decks, starting_cards):
        for i in range(len(decks[0])):
            if decks[0][i] in starting_cards[0]:
                del decks[0][i]
            if decks[1][i] in starting_cards[1]:
                del decks[1][i]
        return decks

    def is_terminal(self):
        return False

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))


class PlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, decks, hands, battle_fields, actions_history, n):
        super().__init__(parent = parent, to_move = to_move, decks = decks, n = n)
        # print(parent)
        # self.n += 1

        self.hands = hands
        self.battle_fields = battle_fields
        self.actions_history = actions_history

        self.actions_sequences = self.__get_action_sequence()
        self.children = {
            a_s:  LeafOrChanceGameState(
                self,
                -to_move,
                self.decks,
                self.hands,
                self.battle_fields,
                self.actions_history + [a_s],
                self.n+1
            ) for a_s in self.actions_sequences
        }
        # print(self.children)

        public_card = self.cards[0] if self.to_move == A else self.cards[1]
        self._information_set = ".{0}.{1}".format(public_card, ".".join(self.actions_history))
        # print('level', self.n)
        # print('cards', self.cards, 'public_card', public_card)
        # print('inf_set', self._information_set)

    def __action_available(self, hand, battle_field, opbattlefield):
        action_available = []
        if len(battle_field) == 1:
            action_available += []
        if len(battle_field) == 2:
            for i in range(len(opbattlefield)):
                action_available += [[ATTACK[0][i]]]
        elif len(battle_field) == 3:
            for i in range(len(opbattlefield)):
                for j in range(len(opbattlefield)):
                    action_available += [[ATTACK[0][i], ATTACK[1][j]]]
        elif len(battle_field) == 4:
            for i in range(len(opbattlefield)):
                for j in range(len(opbattlefield)):
                    for k in range(len(opbattlefield)):
                        action_available += [[ATTACK[0][i], ATTACK[1][j], ATTACK[2][k]]]

        if len(hand) == 1 & hand[0].cost <= self.n:
            for i in range(len(action_available)):
                action_available[i] += [PLAY1]
        elif len(hand) == 2:
            if hand[0].cost + hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1, PLAY2]
                return action_available
            elif hand[0].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1]
                return action_available
            elif hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY2]
                return action_available
        elif len(hand) == 3:
            if hand[0].cost + hand[1].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1, PLAY2, PLAY3]
                return action_available
            elif hand[0].cost + hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1, PLAY2]
                return action_available
            elif hand[0].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1, PLAY3]
                return action_available
            elif hand[1].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY2, PLAY3]
                return action_available
            elif hand[0].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY1]
                return action_available
            elif hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY2]
                return action_available
            elif hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available += [PLAY3]
                return action_available
        return action_available

    def __get_action_sequence(self):
        def mid(a,b,c):
            if c<a and c<b:return b if b<a else a
            r=a if a>b else b
            return r if r<c else c

        if self.to_move == A:
            deck = self.decks[0]
            hand = self.hands[0]
            battlefield = self.battle_fields[0]
            opdeck = self.decks[1]
            ophand = self.hands[1]
            opbattlefield = self.battle_fields[1]
        else:
            deck = self.decks[1]
            hand = self.hands[1]
            battlefield = self.battle_fields[1]
            opdeck = self.decks[0]
            ophand = self.hands[0]
            opbattlefield = self.battle_fields[0]

        ac_ava = self.__action_available(hand, battlefield, opbattlefield)
        n = self.n

        ac_seq = []
        for i in range(len(ac_ava)):
            t = []
            for j in range(len(ac_ava[i])):
                t.append(list(itertools.permutations(ac_ava, j+1)))
                for k in range(len(t[j])):
                    a_s = list(t[j][k])
                    if a_s in ac_seq:
                        continue
                    else:
                        if "ATTACK10" in a_s and "ATTACK20" in a_s and "ATTACK30" in a_s:
                            first = min(a_s.index("ATTACK10"), a_s.index("ATTACK20"), a_s.index("ATTACK30"))
                            second = mid(a_s.index("ATTACK10"), a_s.index("ATTACK20"), a_s.index("ATTACK30"))
                            first_attack = int(a_s[first][6])
                            second_attack = int(a_s[second][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                            elif battlefield[first_attack].at + battlefield[second_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK10" in a_s and "ATTACK20" in a_s:
                            first = min(a_s.index("ATTACK10"), a_s.index("ATTACK20"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK10" in a_s and "ATTACK30" in a_s:
                            first = min(a_s.index("ATTACK10"), a_s.index("ATTACK30"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK20" in a_s and "ATTACK30" in a_s:
                            first = min(a_s.index("ATTACK20"), a_s.index("ATTACK30"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK11" in a_s and "ATTACK21" in a_s and "ATTACK31" in a_s:
                            first = min(a_s.index("ATTACK11"), a_s.index("ATTACK21"), a_s.index("ATTACK31"))
                            second = mid(a_s.index("ATTACK11"), a_s.index("ATTACK21"), a_s.index("ATTACK31"))
                            first_attack = int(a_s[first][6])
                            second_attack = int(a_s[second][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                            elif battlefield[first_attack].at + battlefield[second_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK11" in a_s and "ATTACK21" in a_s:
                            first = min(a_s.index("ATTACK11"), a_s.index("ATTACK21"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK11" in a_s and "ATTACK31" in a_s:
                            first = min(a_s.index("ATTACK11"), a_s.index("ATTACK31"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK21" in a_s and "ATTACK31" in a_s:
                            first = min(a_s.index("ATTACK21"), a_s.index("ATTACK31"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK22" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            second = mid(a_s.index("ATTACK12"), a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            second_attack = int(a_s[second][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                            elif battlefield[first_attack].at + battlefield[second_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK22" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK22"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue
                        elif "ATTACK22" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[0].hp:
                                continue





                    ac_seq.append(list(t[j][k]))
        for i in range(len(ac_seq)):
            ac_seq += [PASS]
        ac_seq.insert(0, [PASS])
        return ac_seq

    def inf_set(self):
        return self._information_set



class LeafOrChanceGameState(GameStateBase):

    def __init__(self, parent, to_move, heroes, decks, hands, battle_fields, actions_history, n):
        super().__init__(parent = parent, to_move = to_move, decks = decks, n = n)

        self.heroes = heroes
        self.hands = hands
        self.battle_fields = battle_fields
        self.actions_history = actions_history

        self.children = {
            starting_cards: PlayerMoveGameState(
                self, A, self.__get_deck_next_round(self.decks, starting_cards), starting_cards, [], [], self.__action_available(starting_cards, self.n+1), self.n+1
            ) for starting_cards in self.starting_hands
        }
        # print(self.children)
        self._chance_prob = 1. / len(self.children)

    def __action_available(self, st_ca, n):
        action_available = [PASS]
        if st_ca[0][0].cost > n & st_ca[0][1].cost > n:
            return action_available
        elif st_ca[0][0].cost < n:
            action_available += [PLAY1]
        elif st_ca[0][1].cost < n:
            action_available += [PLAY2]
        return  action_available

    def __get_deck_next_round(self, decks, starting_cards):
        for i in range(len(decks[0])):
            if decks[0][i] in starting_cards[0]:
                del decks[0][i]
            if decks[1][i] in starting_cards[1]:
                del decks[1][i]
        return decks

    def __update_hero_deck_hand_battlefield(self):
        if self.to_move == A:
            hero = self.heroes[0]
            deck = self.decks[0]
            hand = self.hands[0]
            battlefield = self.battle_fields[0]
            ophero = self.heroes[1]
            opdeck = self.decks[1]
            ophand = self.hands[1]
            opbattlefield = self.battle_fields[1]
        else:
            hero = self.heroes[1]
            deck = self.decks[1]
            hand = self.hands[1]
            battlefield = self.battle_fields[1]
            ophero = self.heroes[0]
            opdeck = self.decks[0]
            ophand = self.hands[0]
            opbattlefield = self.battle_fields[0]

        a_s = self.actions_history[-1]

        if



    def is_terminal(self):


    def evaluation(self):
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")

        if self.actions_history[-1] == CHECK and self.actions_history[-2] == CHECK:
            return RESULTS_MAP[self.cards] * 1

        if self.actions_history[-2] == BET and self.actions_history[-1] == CALL:
            return RESULTS_MAP[self.cards] * 2

        if self.actions_history[-2] == BET and self.actions_history[-1] == FOLD:
            return self.to_move * 1

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))