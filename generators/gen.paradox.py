import random
from deap import creator, base, tools, algorithms

import numpy as np

#problem parameters
membersize = 100 #length for each indivudual
poplen = 500 #population dimension
min_val = -5 #minimum value used when generating random individuals
max_val = 5 #maximum value used when generating random individuals

NRUN = 10 #number of parallel indipendent runs
NGEN = 20 #number of generations for each separate run

verbose = True #debug messages

filename = "paradox.dataset"
testfilename = "paradox.testset"

#multi objective problem
creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, min_val, max_val)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=membersize)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#fitness functions
##for testing purposes this is a combination of different known functions
def evaluate(individual):
    return sum(individual), sum(individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

#population size
population = toolbox.population(n=poplen)

if(verbose):
    print("Starting algorithm runs")

#training generations
training = []
for n in range(NRUN):
    if(verbose):
        print("Run", n, "out of", NRUN)
    for gen in range(NGEN):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
    training.append(population)

#building training dataset
if(verbose):
    print("Building training dataset...")
clfin = []
tops = []
for population in training:
    pareto = tools.sortNondominated(population, len(population))
    top = pareto[0] #the actual pareto front
    #using best and worst elements to build training data
    for member in top:
        #careful avoiding duplicates
        if member not in tops:
            tops.append(member)
        if member not in clfin:
            clfin.append(member)
    for member in tools.selBest(population, k=len(population))[:-len(top)]:
        if member not in clfin:
            clfin.append(member)
        
labels = []
ones = 0
zeros = 0

if(verbose):
    print("Shuffling dataset and setting labels")

np.random.shuffle(clfin)

for member in clfin:
    if member in tops:
        labels.append(1)
        ones += 1
    else:
        labels.append(0)
        zeros += 1

samples = len(clfin)

if(verbose):
    print("0:", zeros, "1:", ones)

filename += "." + str(samples) + "." + str(zeros) + "." + str(ones) + ".csv"

if(verbose):
    print("Writing dataset to", filename) 

with open(filename, 'w') as f:
    for index, individual in enumerate(clfin):
        for feature in individual:
            f.write(str(feature) + ", ")
        f.write(str(labels[index]) + "\n")

testfilename += "." + str(samples) + "." + str(zeros) + "." + str(ones) + ".csv"

if(verbose):
    print("Writing test dataset to", testfilename) 

with open(testfilename, 'w') as f:
    for index, individual in enumerate(clfin[:int(len(clfin)/2)]):
        for feature in individual:
            f.write(str(feature) + ", ")
        f.write(str(labels[index]) + "\n")