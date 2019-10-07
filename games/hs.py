from common.constants import PLAY1, PLAY2, PLAY3, ATTACK, PASS, DECKS, STARTING_HANDS, HEROES, A, CHANCE, minion_null
import random
import itertools


class GameStateBase:

    def __init__(self, parent, to_move, actions, decks, n):
        self.parent = parent
        self.to_move = to_move
        self.actions = actions
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
    def __init__(self, actions):
        super().__init__(parent = None, to_move = CHANCE, actions = actions, decks = DECKS, n = 0)

        self.children = {
            key: PlayerMoveGameState(
                self, A, [], self.__get_deck_next_round(self.decks, value), value, [[HEROES[0]], [HEROES[1]]], [], self.n+1
            ) for key, value in self.actions.items()
        }
        # print(self.children)
        self._chance_prob = 1. / len(self.children)

    def __get_deck_next_round(self, decks, starting_cards):
        newdeck = [[], []]
        for i in range(len(decks[0])):
            if decks[0][i] not in starting_cards[0]:
                newdeck[0].append(decks[0][i])
            if decks[1][i] not in starting_cards[1]:
                newdeck[1].append(decks[1][i])
        return newdeck

    def is_terminal(self):
        return False

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))


class PlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, actions, decks, hands, battle_fields, actions_history, n):
        super().__init__(parent = parent, to_move = to_move, actions = actions, decks = list(decks), n = n)
        # print(parent)
        # self.n += 1
        # print("\nplayer in level", self.n)

        self.hands = list(hands)
        self.battle_fields = list(battle_fields)
        self.actions_history = list(actions_history)

        '''
        if self.n == 2:
            print("now in level ", self.n)
        '''
        actions_se = self.__get_action_sequence(self.hands, self.battle_fields)
        #print("has actions sequences", actions_se)
        for i in range(len(actions_se)):
            # print(actions_se[i])
            str_temp = ".".join(actions_se[i])
            self.actions.append(str_temp)
        # print(self.actions)

        self.children = {
            a_s:  LeafOrChanceGameState(
                self,
                CHANCE,
                [],
                to_move,
                self.decks,
                self.hands,
                self.battle_fields,
                self.actions_history + [a_s],
                self.n
            ) for a_s in self.actions
        }
        # print(self.children)

        private_card = self.hands[0] if self.to_move == A else self.hands[1]
        self._information_set = ".{0}.{1}".format(private_card, ".".join(self.actions_history))
        # print('level', self.n)
        # print('cards', self.cards)
        # print('inf_set', self._information_set)

    def __action_available(self, hand, battle_field, opbattlefield):
        action_available = []
        if len(battle_field) == 1:
            action_available += [[]]
        elif len(battle_field) == 2:
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
        #print('card1 cost', hand[0].cost, '  card2 cost', hand[1].cost)
        #print('now have crystal', self.n)

        if len(hand) == 1 and hand[0].cost <= self.n:
            # print('player can use card1')
            for i in range(len(action_available)):
                action_available[i] += [PLAY1]
        elif len(hand) == 2:
            if hand[0].cost + hand[1].cost <= self.n:
                # print('player can use card1 and card2')
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1, PLAY2]
                return action_available
            elif hand[0].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1]
                return action_available
            elif hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY2]
                return action_available
        elif len(hand) == 3:
            if hand[0].cost + hand[1].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1, PLAY2, PLAY3]
                return action_available
            elif hand[0].cost + hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1, PLAY2]
                return action_available
            elif hand[0].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1, PLAY3]
                return action_available
            elif hand[1].cost + hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY2, PLAY3]
                return action_available
            elif hand[0].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY1]
                return action_available
            elif hand[1].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY2]
                return action_available
            elif hand[2].cost <= self.n:
                for i in range(len(action_available)):
                    action_available[i] += [PLAY3]
                return action_available
        return action_available

    def __get_action_sequence(self, hands, battle_fields):
        def mid(a, b, c):
            if c < a and c < b: return b if b < a else a
            r = a if a > b else b
            return r if r < c else c

        if self.to_move == A:
            hand = hands[0]
            battlefield = battle_fields[0]
            opbattlefield = battle_fields[1]
        else:
            hand = hands[1]
            battlefield = battle_fields[1]
            opbattlefield = battle_fields[0]
        # print("hand for this player is", hand)

        ac_ava = self.__action_available(hand, battlefield, opbattlefield)
        # print("ac_ava",ac_ava)

        ac_seq = []
        for i in range(len(ac_ava)):
            t = []
            for j in range(len(ac_ava[i])):
                t.append(list(itertools.permutations(ac_ava[i], j+1)))
                # print(t)
                for k in range(len(t[j])):
                    a_s = list(t[j][k])
                    # print("a_s", a_s)
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
                            if battlefield[first_attack].at > opbattlefield[1].hp:
                                continue
                            elif battlefield[first_attack].at + battlefield[second_attack].at > opbattlefield[1].hp:
                                continue
                        elif "ATTACK11" in a_s and "ATTACK21" in a_s:
                            first = min(a_s.index("ATTACK11"), a_s.index("ATTACK21"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[1].hp:
                                continue
                        elif "ATTACK11" in a_s and "ATTACK31" in a_s:
                            first = min(a_s.index("ATTACK11"), a_s.index("ATTACK31"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[1].hp:
                                continue
                        elif "ATTACK21" in a_s and "ATTACK31" in a_s:
                            first = min(a_s.index("ATTACK21"), a_s.index("ATTACK31"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[1].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK22" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            second = mid(a_s.index("ATTACK12"), a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            second_attack = int(a_s[second][6])
                            if battlefield[first_attack].at > opbattlefield[2].hp:
                                continue
                            elif battlefield[first_attack].at + battlefield[second_attack].at > opbattlefield[2].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK22" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK22"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[2].hp:
                                continue
                        elif "ATTACK12" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK12"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[2].hp:
                                continue
                        elif "ATTACK22" in a_s and "ATTACK32" in a_s:
                            first = min(a_s.index("ATTACK22"), a_s.index("ATTACK32"))
                            first_attack = int(a_s[first][6])
                            if battlefield[first_attack].at > opbattlefield[2].hp:
                                continue
                    # print(list(t[j][k]))
                    ac_seq.append(list(t[j][k]))
                    # print(ac_seq)
        for i in range(len(ac_seq)):
            ac_seq[i] += [PASS]
        ac_seq.insert(len(ac_seq), [PASS])
        return ac_seq

    def is_terminal(self):
        return False

    def inf_set(self):
        return self._information_set


class LeafOrChanceGameState(GameStateBase):

    def __init__(self, parent, to_move, actions, to_move1, decks, hands, battle_fields, actions_history, n):
        super().__init__(parent = parent, to_move = to_move, actions = actions, decks = decks, n = n)
        self.to_move1 = to_move1
        self.hands = list(hands)
        self.battle_fields = list(battle_fields)
        # print(battle_fields[1][0].hp)
        self.actions_history = list(actions_history)
        # print("\nchance in level", self.n)
        # print("player's hands are", self.hands, "\nbattle fields are", self.battle_fields)

        damage_de, damage_of, minion_d, minion_f = self.__update_hero_hand_battlefield(self.hands, self.battle_fields)

        self.actions = self.__get_actions()
        # print("cards for next player", self.actions)
        self.children = {
            card.name: PlayerMoveGameState(
                self, -to_move1, [], self.__draw_card_from_deck(card), self.__draw_card_to_hand(card), self.battle_fields, self.actions_history, self.n+1
            ) for card in self.actions
        }
        # print(self.children)

        minion_d_key = list(minion_d.keys())
        minion_f_key = list(minion_f.keys())
        minion_d_key.sort()
        minion_f_key.sort()

        if self.to_move1 == A:
            # print(minion_d)
            for position_d in minion_d_key:
                self.battle_fields[1].insert(position_d, minion_d[position_d])
            # print('now op battle field backs to ', self.battle_fields[1])
            # print(damage_de)
            for posi_d in damage_de:
                self.battle_fields[1][posi_d].hp += damage_de[posi_d]
                # print('op enemy hp backs to', self.battle_fields[1][posi_d].hp)

            for position_f in minion_f_key:
                self.battle_fields[0].insert(position_f, minion_f[position_f])
            # print('now battle field backs to ', self.battle_fields[0])
            for posi_f in damage_of:
                self.battle_fields[0][posi_f].hp += damage_of[posi_f]
                # print('own hp backs to', self.battle_fields[0][posi_f].hp)
        else:
            for position_d in minion_d_key:
                self.battle_fields[0].insert(position_d, minion_d[position_d])
            # print('now op battle field backs to ', self.battle_fields[0])
            # print(damage_de)
            for posi_d in damage_de:
                self.battle_fields[0][posi_d].hp += damage_de[posi_d]
                # print('op enemy hp backs to', self.battle_fields[0][posi_d].hp)

            for position_f in minion_f_key:
                self.battle_fields[1].insert(position_f, minion_f[position_f])
            # print('now battle field backs to ', self.battle_fields[1])
            for posi_f in damage_of:
                self.battle_fields[1][posi_f].hp += damage_of[posi_f]
                # print('own hp backs to', self.battle_fields[1][posi_f].hp)

        if len(self.children) != 0:
            self._chance_prob = 1. / len(self.children)

    def __get_actions(self):
        '''
        if self.n == 6:
            return []
        '''
        for _ in HEROES:
            if _ not in self.battle_fields[0] and _ not in self.battle_fields[1]:
                '''
                if HEROES.index(_) == 0:
                    self.battle_fields[0].insert(0, _)
                elif HEROES.index(_) == 1:
                    self.battle_fields[1].insert(0, _)
                '''
                return []
        if self.to_move1 == A:
            opdeck = self.decks[1]
        else:
            opdeck = self.decks[0]
        if len(opdeck) == 0:
            if len(self.actions_history) == 20:
                return []
            else:
                return [minion_null]
        return opdeck

    def __draw_card_from_deck(self, card):
        if card == minion_null:
            return self.decks

        if self.to_move1 == A:
            opdeck = self.decks[1]
        else:
            opdeck = self.decks[0]

        opdeck.remove(card)

        if self.to_move1 == A:
            self.decks[1] = opdeck
        else:
            self.decks[0] = opdeck

        return self.decks

    def __draw_card_to_hand(self, card):
        if card == minion_null:
            return self.hands

        if self.to_move1 == A:
            ophand = self.hands[1]
        else:
            ophand = self.hands[0]

        ophand.append(card)

        if self.to_move1 == A:
            self.hands[1] = ophand
        else:
            self.hands[0] = ophand

        return self.hands

    def __update_hero_hand_battlefield(self, hands, battle_fields):
        if self.to_move1 == A:
            hand = hands[0]
            battlefield = battle_fields[0]
            opbattlefield = battle_fields[1]
        else:
            hand = hands[1]
            battlefield = battle_fields[1]
            opbattlefield = battle_fields[0]

        a_s1 = self.actions_history[-1]
        a_s = a_s1.split('.')
        # print("choose actions ", a_s)
        damaged_of = {}
        damaged_de = {}
        minion_of = {}
        minion_de = {}
        hand_of = []

        hand_temp = list(hand)
        battlefield_temp = list(battlefield)
        opbattlefield_temp = list(opbattlefield)
        for i in range(len(a_s)):
            if "ATT" in a_s[i]:
                offense = int(a_s[i][6])
                defense = int(a_s[i][7])
                # print("minion", offense, "attacked minion", defense)

                tf1 = opbattlefield[defense].get_attacked(battlefield[offense].at)
                if defense in damaged_de:
                    damaged_de[defense] += battlefield[offense].at
                else:
                    damaged_de[defense] = battlefield[offense].at
                # print('op get damaged ', damaged_de)
                # print("after attack hp =", opbattlefield[defense].hp)
                if tf1:
                    minion_de[defense] = opbattlefield[defense]

                tf2 = battlefield[offense].get_attacked(opbattlefield[defense].at)
                if offense in damaged_of:
                    damaged_of[offense] += opbattlefield[defense].at
                else:
                    damaged_of[offense] = opbattlefield[defense].at
                # print('player of this round get damaged ', damaged_of)
                # print(opbattlefield[defense].at)
                # print(battle_fields)
                if tf2:
                    minion_of[offense] = battlefield[offense]
                    # print('own hp = ', battlefield[offense].hp)

            elif "PLA" in a_s[i]:
                # print("player used card", a_s[i])
                pla = int(a_s[i][4]) - 1
                # print("hand is", hand_temp)
                if not hand[pla].battle_field:
                    hand_temp[pla].play()
                    battlefield_temp.append(hand[pla])
                    # print("battle field changed into", battlefield_temp)
                    hand_of.append(pla)

        delete_po_de = []
        delete_po_of = []
        for positions_de in minion_de:
            delete_po_de.append(positions_de)
            delete_po_de.sort(reverse=True)
        for po_de in delete_po_de:
            del opbattlefield_temp[po_de]
            # print('op battle field changed into', opbattlefield_temp)
        for positions_of in minion_of:
            delete_po_of.append(positions_of)
            delete_po_of.sort(reverse=True)
        for po_of in delete_po_of:
            del battlefield_temp[po_of]
            # print('battle field changed into', battlefield_temp)
        hand_of.sort()
        for h_d in hand_of:
            del hand_temp[h_d]
            # print("after that hand changed into", hand_temp)

        if self.to_move1 == A:
            self.hands[0] = list(hand_temp)
            self.battle_fields[0] = list(battlefield_temp)
            self.battle_fields[1] = list(opbattlefield_temp)
            # print("after this round player1's hands is", self.hands[0], "\nbattle field is", self.battle_fields)
        else:
            self.hands[1] = list(hand_temp)
            self.battle_fields[1] = list(battlefield_temp)
            self.battle_fields[0] = list(opbattlefield_temp)
            # print("after this round player2's hands is", self.hands[1], "\nbattle field is", self.battle_fields)

        return damaged_de, damaged_of, minion_de, minion_of

    def is_terminal(self):
        self.__update_hero_hand_battlefield(self.hands, self.battle_fields)
        for _ in HEROES:
            if _ not in self.battle_fields[0] and _ not in self.battle_fields[1]:
                return True
        return False

    def evaluation(self):
        '''
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")
        '''
        return 1

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))


root = RootChanceGameState(STARTING_HANDS)