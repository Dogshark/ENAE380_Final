import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import math


def Generate_map():
    """Imports nodes and edges from .dat file to generate galaxy map"""
    data = nx.read_edgelist('Project-Galaxy.dat')
    return data


def encounter(input_ship):
    """ Determines whether any movement between different systems will result in a combat encounter, exploration event
    or nothing """
    # Generate random number to use for determining outcome
    roll = rand.randint(1, 20)
    if 1 <= roll <= 11:
        # Start combat encounter
        print("\n-----Enemy detected!-----")
        battle(input_ship)
    elif 12 <= roll <= 18:
        # Start exploration event
        print("\n-----Unknown signal detected!-----")
        examine = input("Would you like to investigate? [y/n]")
        examine = examine.upper().strip()
        if examine == 'Y':
            # Picks specific event depending on random number
            roll = rand.randint(1, 5)
            if roll == 1:
                asteroids(input_ship)
            elif roll == 2:
                distress(input_ship)
            elif roll == 3:
                facility(input_ship)
            elif roll == 4:
                cache(input_ship)
            else:
                storm(input_ship)
        elif examine == 'N':
            # Skips exploration event
            pass
    else:
        # No encounter happens
        pass


# --------Combat functions----------

def pick_enemy(x):
    """
    Selects an enemy stat set randomly based on player level

    :param x: player level
    :return: stat set for selected enemy
    """
    # t1: 25-40 (lvl 1-4), t2:40-55 (lvl 4-7), t3:55-70 (lvl 7-10), t4: 70-85 (lvl 10-13), t5: 85-100 (lvl 13-16)
    enemies_t1 = {1: [["Racer", 4, 3, 1, 7, 10], 5], 2: [["Strike Craft", 6, 6, 5, 6, 5], 10],
                  3: [["Bomber", 6, 6, 8, 8, 4], 15], 4: [["Interceptor", 8, 6, 6, 8, 8], 20],
                  5: [["Defense Drone", 12, 10, 8, 9, 1], 25]}

    enemies_t2 = {1: [["Blockade Runner", 7, 6, 4, 10, 14], 30], 2: [["Patrol Ship", 10, 9, 8, 9, 8], 35],
                  3: [["Gunship", 9, 9, 12, 11, 7], 40], 4: [["Scout Corvette", 11, 9, 9, 12, 11], 45],
                  5: [["Defense Platform", 16, 14, 12, 12, 1], 50]}

    enemies_t3 = {1: [["Assault Corvette", 10, 10, 7, 14, 14], 55], 2: [["Frigate", 13, 12, 11, 12, 11], 60],
                  3: [["Missile Frigate", 12, 12, 15, 14, 10], 65], 4: [["Armored Frigate", 14, 12, 12, 15, 14], 70],
                  5: [["Defense Outpost", 20, 18, 15, 16, 1], 75]}

    enemies_t4 = {1: [["Destroyer", 13, 13, 10, 17, 17], 80], 2: [["Cruiser", 16, 15, 14, 15, 14], 85],
                  3: [["Missile Cruiser", 15, 15, 18, 17, 13], 90], 4: [["Heavy Cruiser", 18, 15, 15, 18, 16], 95],
                  5: [["Defense Station", 24, 22, 18, 20, 1], 100]}

    enemies_t5 = {1: [["Assault Carrier", 16, 16, 13, 20, 20], 105], 2: [["Battleship", 19, 18, 17, 18, 16], 110],
                  3: [["Heavy Carrier", 18, 18, 21, 20, 16], 115], 4: [["Dreadnought", 21, 18, 18, 21, 19], 120],
                  5: [["Defense Fortress", 28, 26, 22, 24, 1], 125]}
    # Selects a random enemy from the appropriate list depending on player's level
    num = rand.randint(1, 5)
    if 1 <= x < 4:
        return enemies_t1[num]
    if 4 <= x < 7:
        return enemies_t2[num]
    if 7 <= x < 10:
        return enemies_t3[num]
    if 10 <= x < 13:
        return enemies_t4[num]
    if 13 <= x < 16:
        return enemies_t5[num]


def battle(ship1):
    """ Function controlling combat encounters

    :parameter ship1: player ship"""
    # Spawn enemy ship
    enemy_stats = pick_enemy(ship1.level)
    enemy = Ship(enemy_stats[0])
    retreat = 0
    # Run combat until either ship is destroyed or retreats
    while ship1.current_hull > 0 and enemy.current_hull > 0 and retreat != 1:
        # Display player's current status and combat option menu
        print("Current status:", "  Hull:", ship1.current_hull, "  Shields:", ship1.current_shields)
        print("Options: [a]-Attack  [d]-Defend  [s]-Scan  [r]-Retreat")
        # Get player's action choice, and generate action choice for enemy
        act = input("What do you want to do Captain? ")
        act = act.upper().strip()
        ai_act = ai_decide()
        if act == 'A':
            # Player attacks
            # If enemy chose to defend, determine modifiers to player hit chance and damage
            if ai_act == "D":
                ai_dodge_mod = round(.5 * (enemy.power + enemy.weapons))
                dmg_mod = round(.6 * enemy.power)
            else:
                ai_dodge_mod = 0
                dmg_mod = 0
            # Determine player hit chance and enemy dodge chance
            hit_die = rand.randint(20, 60)
            dodge_die = rand.randint(10, 40)
            hit_chance = hit_die + (2 * ship1.weapons + round(.5 * ship1.power))
            dodge_chance = dodge_die + (2 * enemy.speed + ai_dodge_mod)
            if hit_chance > dodge_chance:
                # Determine player damage if they successfully hit
                print("Enemy ship hit!\n")
                damage = max(0, math.ceil(.5 * ship1.weapons) + math.ceil(.2 * ship1.power) - dmg_mod)
                enemy.get_hit(damage)
            else:
                print("Attack missed!\n")
        elif act == 'S':
            # Display enemy stats
            enemy.get_stats()
        elif act == 'R':
            # Player attempts to retreat
            retreat_chance = rand.randint(1, 20) + ship1.speed + round(.2*ship1.power)
            if retreat_chance >= (enemy.speed + rand.randint(1, 20)):
                print("We successfully escaped!\n")
                retreat = 1
                break
            else:
                print("Retreat failed!\n")
        if ai_act == 'A':
            # Enemy attacks
            # Determine player dodge and damage modifiers if they chose to defend
            if act == "D":
                dodge_mod = round(.5 * (ship1.power + ship1.weapons))
                dmg_mod = round(.6 * ship1.power)
            else:
                dodge_mod = 0
                dmg_mod = 0
            # Determine enemy hit chance and player dodge chance
            hit_die = rand.randint(10, 50)
            dodge_die = rand.randint(10, 40)
            hit_chance = hit_die + (2 * enemy.weapons + round(.5 * enemy.power))
            dodge_chance = dodge_die + (2 * ship1.speed + dodge_mod)
            # If enemy hits, determine damage
            if hit_chance > dodge_chance:

                print("We've been hit!\n")
                damage = max(0, math.ceil(.5 * enemy.weapons) - dmg_mod)
                ship1.get_hit(damage)
            else:
                print("Enemy attack missed!\n")
        elif ai_act == 'S':
            # Enemy scans
            print("We've been scanned!\n")
        elif ai_act == 'R':
            # Enemy tries to retreat
            retreat_chance = rand.randint(1, 20) + enemy.speed + round(.2*enemy.power)
            if retreat_chance >= (ship1.speed + rand.randint(1, 20)):
                print("Enemy ship escaped!\n")
                retreat = 1
                break
            else:
                print("The enemy ship tried to get away!\n")
    # Determine outcome of encounter
    # Enemy destroyed
    if enemy.current_hull <= 0:
        print("Enemy ship destroyed!\n")
        ship1.current_shields = ship1.shields + round(.2*ship1.power)
        ship1.money = ship1.money + enemy_stats[1]
        if ship1.current_hull <= 0:
            player_death(ship1)
            ship1.money = ship1.money - enemy_stats[1]
    # Player destroyed
    elif ship1.current_hull <= 0:
        player_death(ship1)
    # Either ship retreats
    elif retreat == 1:
        ship1.current_shields = ship1.shields + round(.2*ship1.power)


def player_death(ship1):
    """Function that controls player death and respawning

    :parameter ship1: player ship"""
    print("Ship destroyed!\n")
    # Determine if player can afford to respawn
    if ship1.money >= ship1.hull:
        print("Would you like to respawn for", ship1.hull, "credits?\n")
        choice = input("[y/n]")
        choice = choice.upper().strip()
        if choice == 'Y':
            print("Respawning...")
            ship1.position = 'S1'
            ship1.current_hull = ship1.hull
            ship1.current_shields = ship1.shields + round(.2*ship1.power)
            ship1.money = ship1.money - ship1.hull
        elif choice == 'N':
            print("Oh no, better luck next time!")
            exit()
    else:
        print("Oh no, better luck next time!")
        exit()


def ai_decide():
    """Function driving AI decision-making during combat encounters

    :return AI action choice"""
    # Enemy decision based on random number, highest chance of attack, followed by defend, scan, and lastly retreat
    ai_act = rand.randint(1, 100)
    if 2 <= ai_act <= 51:
        return "A"
    elif 52 <= ai_act <= 81:
        return "D"
    elif 82 <= ai_act <= 99:
        return "S"
    elif ai_act == 1 or ai_act == 100:
        return "R"


# ------Event functions-------
def asteroids(ship1):
    """Simple text based event, outcomes are reward, damage, or nothing"""
    closer = input("There seems to be a large concentration of asteroids, should we investigate closer? [y/n]")
    closer = closer.strip().upper()
    # If player continues, determine outcome
    if closer == 'Y':
        roll2 = rand.randint(1, 10)
        # Reward outcome
        if 1 <= roll2 <= 5:
            print("We've discovered a cluster of valuable minerals!\n")
            ship1.money = ship1.money + (5 * ship1.level)
        # Damage outcome
        elif 7 <= roll2 <= 8:
            print("It seems to have been some kind of trap, we've taken a bit of damage.\n")
            ship1.current_hull = ship1.current_hull - (1 * (max(1, round(.5 * ship1.level))))
            if ship1.current_hull <= 0:
                player_death(ship1)
        # Nothing outcome
        else:
            print("Looks like its just a bunch of rocks.\n")
    else:
        pass


def facility(ship1):
    """ Binary conversion based event, outcomes are reward, damage, upgrade or nothing if fully upgraded"""
    def signal_add():
        # Binary conversion part separated to simplify determining outcome
        # Generate 2 numbers and sum, along with binary versions of each
        num1 = rand.randint(4, 32)
        num2 = rand.randint(4, 32)
        summ = num1 + num2
        num1_bin = "{0:b}".format(num1)
        num2_bin = "{0:b}".format(num2)
        sum_bin = list("{0:b}".format(summ))
        print("Captain, we're receiving a signal transmission, displaying it now:")
        print(num1_bin, "+", num2_bin)
        # Player has 3 tries to get it right
        attempts = 0
        while attempts < 3:
            sent = input("Captain, what signal should we send in response?")
            if list(sent.strip()) == sum_bin:
                print("Our transmission seems to have been accepted!")
                return 1
            else:
                print("That doesn't seem to be correct.")
                attempts += 1
        return 0
    choice = input("We seem to have found some abandoned facility, should we investigate more closely? [y/n]")
    choice = choice.upper().strip()
    # Ir player chooses to continue event, run binary conversion challenge and determine outcome
    if choice == 'Y':
        x = signal_add()
        if x == 1:
            # Player completes binary challenge, reward or upgrade outcome
            # (Nothing outcome if upgrade outcome is picked and player is max level)
            roll2 = rand.randint(1, 5)
            if 1 <= roll2 <= 4:
                print("There's a lot of valuable scrap in here we can salvage!\n")
                ship1.money = ship1.money + 15 * ship1.level
            elif roll2 == 5 and (ship1.hull + ship1.shields + ship1.weapons + ship1.power + ship1.speed) <= 100:
                print("We've managed to recover and install some of the advanced technology we found into our ship!\n")
                # Randomly choose stat to upgrade
                option = rand.randint(1, 5)
                if option == 1:
                    ship1.hull = ship1.hull + 1
                    ship1.current_hull = ship1.hull
                elif option == 2:
                    ship1.shields = ship1.shields + 1
                    ship1.current_shields = ship1.shields + round(.2 * ship1.power)
                elif option == 3:
                    ship1.weapons = ship1.weapons + 1
                elif option == 4:
                    ship1.power = ship1.power + 1
                elif option == 5:
                    ship1.speed = ship1.speed + 1
            else:
                print("Looks like there's nothing valuable here.\n")
        else:
            # Player fails binary challenge, damage outcome
            print("We appear to have activated some automated defenses, we've taken some damage.\n")
            ship1.current_hull = ship1.current_hull - 2 * (max(1, round(.5 * ship1.level)))
            if ship1.current_hull <= 0:
                player_death(ship1)
    else:
        # Player ski[s event
        print("Better to leave it be, who knows whats in there.\n")


def distress(ship1):
    """Simple text based event, outcomes are reward or battle"""
    choice = input("We seem to be picking up a distress call, should we investigate further? [y/n]")
    choice = choice.upper().strip()
    # If player continues event, determine outcome
    if choice == 'Y':
        roll2 = rand.randint(1, 10)
        if 1 <= roll2 <= 7:
            # Reward outcome
            print("We've successfully rescued the stranded crew, and they've given us some funds as a thanks!\n")
            ship1.money = ship1.money + 5 * ship1.level
        else:
            # Battle outcome
            print("The distress call was a trap, we're under attack!")
            battle(ship1)
    elif choice == 'N':
        print("Better not risk it, we'll let someone else take a look.\n")


def storm(ship1):
    """Stat based event, outcomes effect current shield levels"""
    choice = input("Captain, there seems to be some kind of radiation storm ahead, should we try to go through or head "
                   "around? [s]-Go through [a]-Go around")
    through = 0
    if choice.strip().upper() == 'S':
        # Player decides to go through
        through = 1
    elif choice.strip().upper() == 'A':
        # Player tries to go around, determine evade chance and difficulty
        evade_chance = rand.randint(1, 20) + ship1.speed
        evade_diff = 12 + ship1.level
        if evade_chance <= evade_diff:
            print("Captain, we weren't able to get around the storm, looks like we'll have to go through it.\n")
            through = 1
        else:
            through = 0
    if through == 1:
        # If player chose to go through or failed to go around, determine outcome
        roll = rand.randint(1, 100)
        if 1 <= roll <= 50:
            # Minor bad outcome
            print("Captain, the storm seems to have damaged our shields, it will take some time to get them fully "
                  "functional again.\n")
            ship1.current_shields = int(round(.5 * ship1.current_shields))
        elif 51 <= roll <= 80:
            # Good outcome
            print("Captain, the storm seems to have overcharged our shields, they seem to be well above their "
                  "normal capacity!\n")
            ship1.current_shields = int(round(1.5 * ship1.current_shields))
        else:
            # Major bad outcome
            print("Captain, the storm seems to have heavily damaged our shields, it will take some time to get "
                  "them operating again.\n")
            ship1.current_shields = 0
    else:
        print("We've successfully avoided the radiation storm.\n")


def cache(ship1):
    """Hexadecimal conversion based event, outcomes are reward, damage or minor upgrade"""
    # Conversion challenge separated to simplify outcome determination
    def signal_hex():
        print("Captain, the signal seems to be a heading transmitted in hexadecimal, we'll have to convert it.")
        attempts = 0
        success = 0
        # Player has 3 tries to convert 4 hex numbers
        while attempts < 3 and success != 4:
            course = rand.randint(0, 359)
            print("Course:", "{0:x}".format(course))
            path = input("Our heading:")
            if str(path) == str(course):
                print("Looks like we're being directed along a clear path.")
                success += 1
            else:
                print("Looks like we're going the wrong way, better try again.")
                attempts += 1
        if success == 4:
            return 1
        else:
            return 0
    choice = input("Captain, we're picking up a signal transmitting from a debris field, should we investigate?[y/n]")
    # If player decides to continue event, run hex challenge and determine outcome
    if choice.strip().upper() == 'Y':
        x = signal_hex()
        if x == 1:
            # Player completes hex challenge
            roll = rand.randint(1, 5)
            if 1 <= roll <= 4:
                # Reward outcome
                print("We've found a large cache of valuable materials!\n")
                ship1.money = ship1.money + 18*ship1.level
            elif roll == 5 and (ship1.hull + ship1.shields + ship1.weapons + ship1.power + ship1.speed) <= 100:
                # Upgrade outcome
                print("We've recovered some useful equipment for our ship!\n")
                roll2 = rand.randint(1, 2)
                if roll2 == 1:
                    ship1.hull = ship1.hull + 1
                    ship1.current_hull = ship1.current_hull + 1
                else:
                    ship1.weapons = ship1.weapons + 1
        else:
            # Player fails hex challenge
            print("Captain, we seem to have run into a mine, the ship has taken some damage.\n")
            ship1.current_hull = ship1.current_hull - 3*(round(max(1, .5*ship1.level)))
    elif choice.strip().upper() == 'N':
        print("Better to play it safe.\n")


class Ship:
    # Class used in player and enemy ships
    def __init__(self, stats):
        # stats: 6 item array, ['name', hull, shields, weapons, power, speed]
        # 5 "core" stats [Hull, Shields, Weapons, Power, Speed] and ship name
        self.name = stats[0]
        self.hull = stats[1]
        self.shields = stats[2]
        self.weapons = stats[3]
        self.power = stats[4]
        self.speed = stats[5]
        # Secondary stats based on "core" stats
        self.current_hull = self.hull
        self.current_shields = self.shields + round(.2*self.power)
        self.money = 0
        self.level = math.floor(((self.hull + self.shields + self.weapons + self.power + self.speed) / 5)) - 4
        self.position = 'S1'

    def get_stats(self):
        """Prints current stats of ship"""
        print('\n')
        print(self.name, '[lvl', self.level, ']', "Hull:", self.current_hull, "Shields:", self.current_shields)
        print("Max Hullpoints:", self.hull, "\nShields:", self.shields, '\nWeapons: ', self.weapons)
        print('Power:', self.power, '\nSpeed:', self.speed, "\n")

    def get_hit(self, dmg):
        """Deals damage to shields if the ship has them, and the hull if shields are down"""
        # Damage is dealt to shields first
        if self.current_shields >= dmg:
            self.current_shields = self.current_shields - dmg
        # Once shields are depleted, hull takes damage
        else:
            dmg -= self.current_shields
            self.current_shields = 0
            self.current_hull = self.current_hull - dmg

    def repair(self):
        """Replaces missing hull points if they ship has sufficient funds"""
        # Must be in s- or 0- system to repair
        if self.position in ["S1", "S2", "S3", "S4"]:
            # Check is player needs repairs
            if self.current_hull == self.hull:
                print("Ship doesn't need repairs!\n")
            else:
                cost = (self.hull - self.current_hull)
                if self.money >= cost:
                    print("Ship has been repaired.\n")
                    self.money = self.money - cost
                    self.current_hull = self.hull
                else:
                    print("Can't afford repairs!\n")
        elif self.position in ["O1", "O2", "O3", "O4"]:
            if self.current_hull == self.hull:
                print("Ship doesn't need repairs!\n")
            else:
                cost = round(1.5 * (self.hull - self.current_hull))
                if self.money >= cost:
                    print("Ship has been repaired.\n")
                    self.money = self.money - cost
                    self.current_hull = self.hull
                else:
                    print("Can't afford repairs!\n")
        else:
            print("Captain, we must be at a starbase or outpost to repair the ship!\n")

    def cash(self, amount):
        """Debug function used to provide funds to test other functions, not accessible in normal game"""
        self.money = self.money + amount

    def get_map(self, game_map):
        """Prints ships position and displays a galaxy map"""
        # Draw and show graph of nodes and edges
        # Setup each shell for shell layout
        s1 = ['S1', 'A1', 'A2', 'S2', 'A3', 'A4', 'S3', 'A5', 'A6', 'S4', 'A7', 'A8']
        s2 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12']
        s3 = ['O1', 'C1', 'C2', 'O2', 'C3', 'C4', 'O3', 'C5', 'C6', 'O4', 'C7', 'C8']
        print("You are currently at", self.position)
        print("Close the map window to continue")
        nx.draw(game_map, pos=nx.shell_layout(game_map, nlist=[s1, s2, s3], rotate=-.1), with_labels=True)
        v = nx.Graph()
        # Display player's current position
        v.add_node(self.position)
        nx.draw(v, pos=nx.shell_layout(game_map, nlist=[s1, s2, s3], rotate=-.1), node_color='r')
        plt.show()

    def move(self, data):
        """Moves ship from current system to an adjacent system of the player's choice"""
        near = []
        # Find and display connected systems
        for node in data.nodes:
            if len(nx.dijkstra_path(data, self.position, node)) <= 2 and node != self.position:
                near.append(node)
        print("Nearby systems are:", near)
        des = input("Which system do you want to go to? ")
        des = des.upper()
        # Wait until valid destination is picked
        while des not in near:
            print("Nearby systems are:", near)
            des = input("Which system do you want to go to? ")
            des = des.upper()
        self.position = des

    def upgrade(self):
        """
        Increases one stat of the player's choice, provided they can afford the upgrade and are in a starbase system
        """
        # Must be in S- system to upgrade
        if self.position in ["S1", "S2", "S3", "S4"]:
            # Check that player is not at max level
            if (self.hull + self.shields + self.weapons + self.power + self.speed) <= 100:
                print("Upgrade Options: [h]-Hull  [s]-Shields  [w]-Weapons  [p]-Power  [r]-Speed [c]-Cancel")
                stat = input("Select stat to upgrade:")
                stat = stat.strip().upper()
                # Dictionary with upgrade base costs
                up_stat = {"H": [self.hull, 5, 'Hull'], "S": [self.shields, 15, 'Shields'],
                           "W": [self.weapons, 10, 'Weapons'], "P": [self.power, 5, 'Power'],
                           "R": [self.speed, 10, 'Speed']}
                if stat == "C":
                    pass
                elif stat in ['H', 'S', 'W', 'P', 'R']:
                    # Calculate cost and confirm with player
                    cost = up_stat[stat][1] + up_stat[stat][1] * (up_stat[stat][0] - 5)
                    print("Upgrade", up_stat[stat][2], "from", up_stat[stat][0], "to", (up_stat[stat][0] + 1),
                          "for", cost, "?")
                    confirm = input("[y/n]")
                    confirm = confirm.strip().upper()
                    if confirm == 'Y' and self.money >= cost:
                        self.money = self.money - cost
                        if stat == 'H':
                            self.hull = self.hull + 1
                            self.current_hull = self.hull + 1
                        elif stat == 'S':
                            self.shields = self.shields + 1
                            self.current_shields = self.shields + round(.2*self.power)
                        elif stat == 'W':
                            self.weapons = self.weapons + 1
                        elif stat == 'P':
                            self.power = self.power + 1
                        elif stat == 'R':
                            self.speed = self.speed + 1
                    elif confirm == 'Y' and self.money < cost:
                        print("We can't afford that upgrade captain!\n")
                    elif confirm == 'N':
                        pass
                self.level = math.floor(((self.hull + self.shields + self.weapons + self.power + self.speed) / 5)) - 4
            else:
                print("Captain, our ship can't support anymore upgrades.\n")
        else:
            print("We must be at a starbase to perform upgrades!\n")

    def bank(self):
        """Prints the player's current balance"""
        print("Current balance is:", self.money, "credits.\n")


def main():
    """Main Code"""
    # Load map
    galaxy_map = Generate_map()
    # Creates player's ship, with custom name and base player stats
    name = input("What will you name your ship captain?")
    basestats = [name, 5, 5, 5, 5, 5]
    player = Ship(basestats)
    # Run until player decides to quit
    state = 0
    while state == 0:
        print("Options: [s]-stats  [u]-upgrade  [r]-repair  [m]-map  [g]-move  [b]-bank  [h]-help  [q]-quit")
        choice = input("What do you want to do? ")
        choice = choice.strip().upper()
        if choice == 'S':
            player.get_stats()
        elif choice == 'U':
            player.upgrade()
        elif choice == 'R':
            player.repair()
        elif choice == 'M':
            player.get_map(galaxy_map)
        elif choice == 'G':
            player.move(galaxy_map)
            encounter(player)
            print("Arrived!\n")
        elif choice == 'B':
            player.bank()
        elif choice == 'H':
            help_menu()
        elif choice == "Q":
            state = 1
    print("Goodbye!")


def help_menu():
    """Starts help menu"""
    # Load help info from separate text file
    with open("Help_Commands.txt") as file_obj:
        lines_help = file_obj.readlines()
    back = 0
    # Run until player chooses to return to main menu
    while back == 0:
        menu_choice = input("Type [p] for how to play, [c] for commands menu, [s] for details on ship stats, or [b] to "
                            "return to the main menu: \n")
        menu_choice = menu_choice.upper().strip()
        if menu_choice == "C":
            for x in range(0, 19):
                print(lines_help[x].rstrip())
            input("\nPress any key to continue")
            for x in range(20, 29):
                print(lines_help[x].rstrip())
            input("\nPress any key to return to the menu\n")
        elif menu_choice == "P":
            for x in range(31, 42):
                print(lines_help[x].rstrip())
            input("Press any key to return to the menu\n")
        elif menu_choice == 'S':
            for x in range(43, 61):
                print(lines_help[x].rstrip())
            input("Press any key to return to the menu\n")
        elif menu_choice == 'B':
            back = 1


# Startup and main menu code
menu = 0
# Run main menu until player decides to start a game
while menu == 0:
    print("Welcome to FTL Exploration!")
    print(" To start a new game, type: play", "\n", "For info on how to play, type: help", "\n", "To exit, type: quit")
    pick = input("Type here:")
    pick = pick.upper().strip()
    if pick == "PLAY":
        break
    elif pick == 'HELP':
        help_menu()
    elif pick == 'QUIT':
        print("Goodbye!")
        exit()

main()
