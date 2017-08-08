# Implementacja modelu Rabbits Grass Weeds w Python

import simpy
import random
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors

# Zarejestrowanie kolorow: bialy-krolik, zielony-trawa, fiolet-chwasty
map_colors = matplotlib.colors.ListedColormap(["black", "white", "green", "violet"])
plt.register_cmap(cmap=map_colors)

# Zdefiniowanie klasy krolika
class Agent_rabbit:
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

    # Krolik losuje miejsce dookola siebie, gdzie sprawdzi, czy jest jedzenie, jesli tak, to je
    def eating(self):    
        dx = random.sample([-1,0,1],1)[0]
        dy = random.sample([-1,0,1],1)[0]
        if dx != 0 and dy != 0:
            ref_loc = ((self.loc[0] + dx) % self.city.city_dim,
                       (self.loc[1] + dy) % self.city.city_dim) 
            if ref_loc in self.city.occupied:
                # Warunek jesli napotkanym miejscem jest trawa
                if self.city.occupied[ref_loc].color == 2: 
                    self.energy += self.grass_energy
                    self.city.occupied[ref_loc] = self
                    del self.city.occupied[self.loc]
                    self.loc = ref_loc
                # Warunek jesli napotkanym miejscem jest chwast
                if self.city.occupied[ref_loc].color == 3:
                    self.energy += self.weed_energy
                    self.city.occupied[ref_loc] = self
                    del self.city.occupied[self.loc]
                    self.loc = ref_loc
                    
                # Dodatkowo, gdy krolik zje dany fragment - przenosi sie na jego miejsce
        
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
            # Sprawdzam, czy krolik ma jeszcze jakakolwiek energie, jesli tak - ide dalej
            if self.energy>0:
                # Za kazdy ruch odejmuje jeden punkt energii krolika
                self.energy -= 1
                # Krolik probuje cos zjesc, tj. zyskac energii
                self.eating()
                jedzenie = self.eating()
                if jedzenie: 
                    # Jesli krolik ma energie i los mu sprzyja (dla przyjetego prawdopodobienstwa),
                    # reprodukuje sie :)
                    if self.energy>self.born_energy and self.born_p>random.uniform(0,1):
                        Agent_rabbit(self.color, self.first_energy, self.born_energy, self.born_p, 
                                     self.grass_energy, self.weed_energy, self.city)
                        # Za reprodukcje odejmujemy dodatkowa energie
                        self.energy = self.energy-self.born_energy
                        # Dodajemy nowego krolika do zliczonej populacji
                        self.city.rabbit_final += 1
                    # Jesli krolik ma jeszcze sile, idzie dalej
                    if self.energy >= 1:
                        self.move()
            # Jesli krolik nie ma energii - umiera
            else:
                self.die()
           
           
# Zdefiniowanie klasy dla rosnacej trawy i chwastow 
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

    # Trawa lub chwast rosna w losowym miejscu z okreslonym prawdopodobienstwem
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
            Agent_rabbit(1, self.rabbit_energy, self.rabbit_born_energy, self.rabbit_born_p, self.grass_energy, self.weed_energy, self)
        for i in range(grass_count):
            Agent(2, self.grass_energy, self.grass_prob, self)
        for i in range(weed_count):
            Agent(3, self.weed_energy, self.weed_prob, self)
        if plotting:
            plt.figure(1)
            self.plot(True)
        self.env.run(until=self.max_iter)
        if plotting:
            self.plot(False)
            plt.show()
        # Zwraca informacje o liczbie krolikow w populacji
        return(self.rabbit_final)

## Ustawienie parametrow 

DIM = 50 # Wymiar mapy
GRASS_DENSITY_FROM = 0.02 # Minimalna procentowa zajetosc mapy przez trawe
GRASS_DENSITY_TO = 0.13 # Maksymalna procentowa zajetosc mapy przez trawe
WEED_DENSITY_FROM = 0.02 # Minimalna procentowa zajetosc mapy przez chwasty
WEED_DENSITY_TO = 0.13 # Maksymalna procentowa zajetosc mapy przez chwasty
RAB_EN_FROM = 5 # Minimalna poczatkowa energia, jaka ma krolik
RAB_EN_TO = 11 # Maksymalna poczatkowa energia, jaka ma krolik
RAB_NUM = 150 # Liczba krolikow w poczatkowej populacji
MAX_ITER = 500 # Maksymalna liczba iteracji
GRASS_P = 0.3 # Prawdopodobienstwo pojawienia sie nowej trawy
WEED_P = 0.5 # Prawdopodobienstwo pojawienia sie nowego chwasta
GRASS_EN = 3 # Energia, jaka daje jedzenie trawy
WEED_EN = 1 # Energia, jak daje jedzenie chwasta
RAB_BORN_EN = 7 # Energia, potrzebna krolikowi do reprodukcji
RAB_P = 0.4 # Prawdopodobienstwo reprodukcji krolika

## Budowanie kombinacji

grass_dt = pd.DataFrame({'grass_dt': np.arange(GRASS_DENSITY_FROM, GRASS_DENSITY_TO, 0.01)})
weed_dt = pd.DataFrame({'weed_dt': np.arange(WEED_DENSITY_FROM, WEED_DENSITY_TO, 0.01)})
rab_energy = pd.DataFrame({'rab_energy': np.arange(RAB_EN_FROM, RAB_EN_TO, 1)})

wyniki = pd.DataFrame(columns=['grass_dt', 'weed_dt', 'rab_energy', 'rab_number'])

## Uruchomienie eksperymentu dla kazdej kombinacji

# Liczba wierszy, ktora bedzie sie zwiekszac z kazda iteracja
l_w=0
for idx_gr, row_gr in grass_dt.iterrows():
    for idx_wd, row_wd in weed_dt.iterrows():
        for idx_rab, row_rab in rab_energy.iterrows():
            l_w += 1
            city = City(DIM, row_gr.grass_dt, row_wd.weed_dt, MAX_ITER, RAB_NUM, row_rab.rab_energy, 
                        RAB_BORN_EN, RAB_P, GRASS_EN, WEED_EN, GRASS_P, WEED_P)
            ps = city.run(False)
            wyniki.at[l_w,'grass_dt'] = row_gr.grass_dt
            wyniki.at[l_w,'weed_dt'] = row_wd.weed_dt
            wyniki.at[l_w,'rab_energy'] = row_rab.rab_energy
            wyniki.at[l_w,'rab_number'] = ps
            print("Liczba krolikow: "+str(ps)+", grass_dt="+str(row_gr.grass_dt)+", weed_dt="+
                    str(row_wd.weed_dt)+", rabbit_energy="+str(row_rab.rab_energy))

# Dodanie zmiennej z przyrostem krolikow w populacji dla danych warunkow
wyniki['przyrost']=wyniki['rab_number']-RAB_NUM

# Zapisanie wynikow do csv, w celu analizy w R
wyniki.to_csv('rabbit_wyniki.csv', index=False)
