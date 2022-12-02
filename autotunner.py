from drone import Drone



class AutoTunner ():
    POPULATION = 100
    GENERATION = 80

    k = 100                   # roulette wheel parameter


    def __init__ (self):
        self.happy_birthday()
        self.reporter = Report()

    def happy_birthday (self):
        self.drones = []
        for i in range(AutoTunner.POPULATION):
            self.drones.append(Drone(model_visible=False, graph_visible=False))
        
        # set K
    
    def ga



    def simulate (self, n):
        for i in range(n):
            self.generation()



    def generation (self):
        for adult in self.adult:
            adult.simulate()
        
        self.adjust_fitness(self.k)

        offspring = []
        for i in range(self.POPULATION):
            chromosome = self.mutation(self.crossover(self.selection()))
            offspring.append(Man(chromosome))
        
        self.reporter.report(self.adult)
        self.you_are_not_baby(offspring)



    def adjust_fitness (self, k):
        self.fitness = np.array([adult.fitness for adult in self.adult])

        # k min max scaler
        # _min = min(self.fitness)
        # _max = max(self.fitness)

        # self.fitness = [(_max-_min)/(k-1) + (fi - _min) for fi in self.fitness]


        self.fitness = 2 ** (self.fitness)
    


    def roulette_wheel (self):
        wheel = np.cumsum(self.fitness)
        dart = sum(self.fitness) * random()
        
        # scaled_fitness = 2 ** (self.fitness/10)
        # wheel = np.cumsum(scaled_fitness)
        # dart = sum(scaled_fitness) * random()

        idx = np.argwhere(dart <= wheel)
        return idx[0][0]
    


    def selection (self):
        parent = [self.roulette_wheel(), self.roulette_wheel()]
        return parent



    def crossover (self, parent):
        point = randrange(0, self.CHROMOSOME_LEN+1)
        return self.adult[parent[0]].chromosome[:point] + self.adult[parent[1]].chromosome[-point:]
    

        
    def mutation (self, chromosome):
        for i in range(len(chromosome)):
            if random() < 0.0015:
                chromosome[i] = randint(0, 2)
        
        return chromosome



    def you_are_not_baby (self, offspring):
        for adult in self.adult:
            adult.body.visible = False

        self.adult = offspring







                
class Report ():
    TARGET = 36



    def __init__(self):
        self.n = 0
        self.tile = []

        scene.append_to_caption('population = ' + str(RootFinder.POPULATION) + '\n')

        self.f1 = graph(width=600, height=200, title='each man fitness', ymin=0, ymax=self.TARGET * 1.3, align='left')
        self.g1 = gvbars(graph=self.f1, color=color.blue)

        self.f2 = graph(width=600, height=200, title='fitness', ymin=0, ymax=self.TARGET * 1.3, align='left')
        self.g2 = gcurve(graph=self.f2, color=color.red)
        self.g3 = gcurve(graph=self.f2, color=color.black)
    


    def report (self, adult):
        self.render_arrival(adult)
        self.each_fitness_graph(adult)
        self.total_fitness_graph(adult)
    


    def render_arrival(self, adult):
        for t in self.tile:
            t.visible = False

        pos = [(a.x, a.y) for a in adult]
        pos = pd.Series(pos)

        count = pos.value_counts()
        idx   = count.index
        ratio = count.values / count.values.sum()

        self.tile = []
        for i in range(len(count)):
            self.tile.append(box(pos=self.wall_vec(idx[i]), size=vector(1, 0.05, 1) , opacity=ratio[i]))



    def wall_vec (self, pos):
        return vec(pos[0], 0, -(pos[1]-25))



    def each_fitness_graph(self, adult):
        self.g1.delete()
        self.g1.plot([[i, a.fitness] for i, a in enumerate(adult)])



    def total_fitness_graph(self, adult):
        fitness = [a.fitness for a in adult]

        self.n += 1
        self.g2.plot(self.n, np.array(fitness).mean())
        self.g3.plot(self.n, self.TARGET)                # adjoint line
