# Implementation of the Rabbits Grass Weeds model in Python

import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors

# Register colors: white-rabbit, green-grass, purple-weeds
map_colors = matplotlib.colors.ListedColormap(["black", "white", "green", "violet"])
plt.register_cmap(cmap=map_colors)

# Define the rabbit class
class Rabbit:
    def __init__(self, color, energy, born_energy, born_p, grass_energy, weed_energy, city):
        self.city = city
        self.color = color
        self.first_energy = energy
        self.energy = energy
        self.born_energy = born_energy
        self.born_p = born_p
        self.grass_energy = grass_energy
        self.weed_energy = weed_energy
        self.loc = self.gen_loc()
        self.city.env.process(self.iteration())

    def gen_loc(self):
        while True:
            loc = (random.randrange(self.city.city_dim),
                   random.randrange(self.city.city_dim))
            if loc not in self.city.occupied:
                self.city.occupied[loc] = self
                return(loc)

    # Rabbit randomly chooses a place around itself to check for food, if there is food, it eats
    def eating(self):
        dx = random.sample([-1,0,1],1)[0]
        dy = random.sample([-1,0,1],1)[0]
        if dx != 0 and dy != 0:
            ref_loc = ((self.loc[0] + dx) % self.city.city_dim,
                       (self.loc[1] + dy) % self.city.city_dim)
            if ref_loc in self.city.occupied:
                # Condition if the encountered place is grass
                if self.city.occupied[ref_loc].color == 2:
                    self.energy += self.grass_energy
                    self.city.occupied[ref_loc] = self
                    del self.city.occupied[self.loc]
                    self.loc = ref_loc
                # Condition if the encountered place is a weed
                if self.city.occupied[ref_loc].color == 3:
                    self.energy += self.weed_energy
                    self.city.occupied[ref_loc] = self
                    del self.city.occupied[self.loc]
                    self.loc = ref_loc

                # Additionally, when the rabbit eats a given fragment - it moves to its place

        return(self.energy > 0)

    def move(self):
        yield self.city.env.timeout(random.random())
        new_loc = self.gen_loc()
        del self.city.occupied[self.loc]
        self.loc = new_loc

    def die(self):
        yield self.city.env.timeout(random.random())
        del self.city.occupied[self.loc]

    def iteration(self):
        yield self.city.env.timeout(random.random())
        while True:
            yield self.city.env.timeout(1)
            # Check if the rabbit still has any energy, if so - continue
            if self.energy>0:
                # For each move, subtract one energy point from the rabbit
                self.energy -= 1
                # The rabbit tries to eat something, i.e., gain energy
                self.eating()
                jedzenie = self.eating()
                if jedzenie:
                    # If the rabbit has energy and luck is on its side (for the accepted probability),
                    # it reproduces :)
                    if self.energy>self.born_energy and self.born_p>random.uniform(0,1):
                        Rabbit(self.color, self.first_energy, self.born_energy, self.born_p,
                                     self.grass_energy, self.weed_energy, self.city)
                        # We subtract additional energy for reproduction
                        self.energy = self.energy-self.born_energy
                        # We add a new rabbit to the counted population
                        self.city.rabbit_final += 1
                    # If the rabbit still has strength, it moves on
                    if self.energy >= 1:
                        self.move()
            # If the rabbit has no energy - it dies
            else:
                self.die()


# Define a class for growing grass and weeds
class Agent:
    def __init__(self, color, energy, prob, city):
        self.city = city
        self.color = color
        self.energy = energy
        self.prob = prob
        self.loc = self.gen_loc()
        self.city.env.process(self.born())

    def gen_loc(self):
        while True:
            loc = (random.randrange(self.city.city_dim),
                   random.randrange(self.city.city_dim))
            if loc not in self.city.occupied:
                self.city.occupied[loc] = self
                return(loc)

    # Grass or weed grows in a random place with a specified probability
    def born(self):
        yield self.city.env.timeout(random.random())
        if random.uniform(0, 1) < self.prob:
            Agent(self.color, self.energy, self.prob, self.city)


class City:
    def __init__(self, city_dim, grass_density, weed_density, max_iter, rabbit_num, rabbit_energy,
                 rabbit_born_energy, rabbit_born_p, grass_energy, weed_energy, grass_prob, weed_prob):
        self.city_dim = city_dim
        self.grass_density = grass_density
        self.weed_density = weed_density
        self.max_iter = max_iter
        self.rabbit_num = rabbit_num
        self.rabbit_energy = rabbit_energy
        self.rabbit_born_energy = rabbit_born_energy
        self.rabbit_born_p = rabbit_born_p
        self.grass_energy = grass_energy
        self.weed_energy = weed_energy
        self.grass_prob = grass_prob
        self.weed_prob = weed_prob
        self.rabbit_final = rabbit_num

    def plot(self, start):
        if start:
            plt.subplot(1, 2, 1)
            plt.title("Start")
        else:
            plt.subplot(1, 2, 2)
            plt.title("Stop")
        data = np.zeros((self.city_dim, self.city_dim))
        for agent in self.occupied:
            data[agent[0], agent[1]] = self.occupied[agent].color
        plt.imshow(data, cmap=map_colors, interpolation="none")

    def run(self, plotting=True):
        self.occupied = dict()
        self.env = simpy.Environment()
        grass_count = int(self.city_dim * self.city_dim * self.grass_density)
        weed_count = int(self.city_dim * self.city_dim * self.weed_density)
        for i in range(self.rabbit_num):
            Rabbit(1, self.rabbit_energy, self.rabbit_born_energy, self.rabbit_born_p, self.grass_energy, self.weed_energy, self)
        for i in range(int(grass_count+1)):
            Agent(2, self.grass_energy, self.grass_prob, self)
        for i in range(int(weed_count+1)):
            Agent(3, self.weed_energy, self.weed_prob, self)
        if plotting:
            plt.figure(1)
            self.plot(True)
        self.env.run(until=self.max_iter)
        if plotting:
            self.plot(False)
            plt.show()
        # Returns information about the number of rabbits in the population
        return(self.rabbit_final)

## Setting parameters

DIM = 50 # Map dimension
GRASS_DENSITY_FROM = 0.02 # Minimum percentage of map occupied by grass
GRASS_DENSITY_TO = 0.13 # Maximum percentage of map occupied by grass
WEED_DENSITY_FROM = 0.02 # Minimum percentage of map occupied by weeds
WEED_DENSITY_TO = 0.13 # Maximum percentage of map occupied by weeds
RAB_EN_FROM = 5 # Minimum initial energy a rabbit has
RAB_EN_TO = 11 # Maximum initial energy a rabbit has
RAB_NUM = 150 # Number of rabbits in the initial population
MAX_ITER = 500 # Maximum number of iterations
GRASS_P = 0.3 # Probability of new grass appearing
WEED_P = 0.5 # Probability of new weed appearing
GRASS_EN = 3 # Energy given by eating grass
WEED_EN = 1 # Energy given by eating weed
RAB_BORN_EN = 7 # Energy needed for rabbit reproduction
RAB_P = 0.4 # Probability of rabbit reproduction

## Building combinations

grass_dt = pd.DataFrame({'grass_dt': np.arange(GRASS_DENSITY_FROM, GRASS_DENSITY_TO, 0.01)})
weed_dt = pd.DataFrame({'weed_dt': np.arange(WEED_DENSITY_FROM, WEED_DENSITY_TO, 0.01)})
rab_energy = pd.DataFrame({'rab_energy': np.arange(RAB_EN_FROM, RAB_EN_TO, 1)})

results = pd.DataFrame(columns=['grass_dt', 'weed_dt', 'rab_energy', 'rab_number'])

## Running the experiment for each combination

# Number of rows that will increase with each iteration
l_w=0
for idx_gr, row_gr in grass_dt.iterrows():
    for idx_wd, row_wd in weed_dt.iterrows():
        for idx_rab, row_rab in rab_energy.iterrows():
            l_w += 1
            city = City(DIM, row_gr.grass_dt, row_wd.weed_dt, MAX_ITER, RAB_NUM, row_rab.rab_energy,
                        RAB_BORN_EN, RAB_P, GRASS_EN, WEED_EN, GRASS_P, WEED_P)
            ps = city.run(False)
            results.at[l_w,'grass_dt'] = row_gr.grass_dt
            results.at[l_w,'weed_dt'] = row_wd.weed_dt
            results.at[l_w,'rab_energy'] = row_rab.rab_energy
            results.at[l_w,'rab_number'] = ps
            print(f"Number of rabbits: {str(ps)}, grass_dt={str(row_gr.grass_dt)}, weed_dt={str(row_wd.weed_dt)}, rabbit_energy={str(row_rab.rab_energy)}")

# Adding a variable with the increase in rabbits in the population for given conditions
results['increase']=results['rab_number']-RAB_NUM

# Saving results to csv for analysis in R
results.to_csv('output/rabbit_results.csv', index=False)
