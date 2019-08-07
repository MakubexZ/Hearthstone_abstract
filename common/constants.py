class Cards:

    def __init__(self, cost, attack, health_point, characteristic, battle_field):
        self.cost = cost
        self.at = attack
        self.hp = health_point
        self.charac = characteristic
        self.battle_field = battle_field

    def play(self):
        self.battle_field = True

    def is_dead(self):
        return self.hp <= 0


class Hero(Cards):

    def __init__(self, attack, health_point):
        super().__init__(cost=0, attack=attack, health_point=health_point, characteristic=None, battle_field=False)
        self.at = attack
        self.hp = health_point

        self.armed = False

    def get_attacked(self, op_at):
        self.hp = self.hp - op_at
        return self.is_dead()

    def armed(self):
        self.armed = True

    def is_dead(self):
        return self.hp <= 0


class Minion(Cards):

    def __init__(self, cost, attack, health_point, characteristic, battle_field):
        super().__init__(cost=cost, attack=attack, health_point=health_point, characteristic=characteristic, battle_field=battle_field)
        self.cost = cost
        self.at = attack
        self.hp = health_point
        self.charac = characteristic
        self.battle_field = battle_field

    def play(self):
        self.battle_field = True

    def get_attacked(self, op_at):
        self.hp = self.hp - op_at
        return self.is_dead()

    def is_dead(self):
        return self.hp <= 0


minion1 = Minion(cost=1, attack=1, health_point=1, characteristic=None, battle_field=False)
minion2 = Minion(cost=2, attack=1, health_point=2, characteristic=None, battle_field=False)
minion3 = Minion(cost=2, attack=2, health_point=1, characteristic=None, battle_field=False)
# minion4 = Minion(cost=3, attack=2, health_point=2, characteristic=None, battle_field=False)
# minion5 = Minion(cost=4, attack=3, health_point=3, characteristic=None, battle_field=False)

hero1 = Hero(attack=0, health_point=5)
hero2 = Hero(attack=0, health_point=5)

DECKS = [[minion1, minion2, minion3], [minion1, minion2, minion3]]
# HANDS = [[minion1, minion2], [minion1, minion3], [minion1, minion4], [minion2, minion3], [minion2, minion4], [minion3, minion4]]
STARTING_HANDS = [[[minion1, minion2], [minion1]], [[minion1, minion2], [minion2]],
                  [[minion1, minion2], [minion3]], [[minion1, minion3], [minion1]],
                  [[minion1, minion3], [minion2]], [[minion1, minion3], [minion3]],
                  [[minion2, minion3], [minion1]], [[minion2, minion3], [minion2]],
                  [[minion2, minion3], [minion3]]]
HEROES = [hero1, hero2]


CHANCE = "CHANCE"

PLAY1 = "PLAY1"
PLAY2 = "PLAY2"
PLAY3 = "PLAY3"

ATTACK = [["ATTACK10", "ATTACK11", "ATTACK12", "ATTACK13"], ["ATTACK20", "ATTACK21", "ATTACK22", "ATTACK23"],
          ["ATTACK30", "ATTACK31", "ATTACK32", "ATTACK33"]]

PASS = "PASS"

A = 1
B = -A

