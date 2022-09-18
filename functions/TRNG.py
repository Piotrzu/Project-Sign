from cmath import log
import numpy as np
import math
import random
import pymp
def generateNumbers(valuesAmount = 1000):
        #random_chaotic = random.uniform(0.3521, 0.3527)
        random_chaotic = random.uniform(0.35221, 0.35235)
        chaotic_state = np.double(round(random_chaotic,4))
        control_parameter = np.double(4.0)
        number_of_networks = int(8)
        number_of_stages = int(6)
        number_of_interations = int(4)
        finalList = np.array([], dtype=np.uint8)
        testList = []

        # Output
        x_out: np.double
        r_out: np.double

        R: int

        # Variables
        r_prim = round(np.double(0.0),5)
        y_i = np.double(4 * [0.0])
        r_i = np.double(4 * [0.0])
        c = int(0)

        file = open('results.txt', 'ab')
        fileToStats = open('results_stats.txt', 'w')
        with pymp.Parallel(4) as p:
            #for i in range(valuesAmount):
            for index in p.range(0, valuesAmount):
                while (c != number_of_networks):
                    c = c + 1
                    r_prim = control_parameter
                    for a in range(4):
                        for j in range(number_of_interations):
                            chaotic_state = chaotic_state * r_prim * (1 - chaotic_state)
                            chaotic_state = (chaotic_state * 1000) - math.floor(chaotic_state * 1000)
                            chaotic_state = round(chaotic_state, 6)
                        y_i[a] = 3.86 + (chaotic_state * 0.14)
                for k in range(1, number_of_stages):
                    if (chaotic_state >= 0.5):
                        r_i[0] = (y_i[0] + y_i[2]) / 2
                        r_i[1] = (y_i[0] + y_i[2]) / 2

                        r_i[2] = (y_i[1] + y_i[3]) / 2
                        r_i[3] = (y_i[1] + y_i[3]) / 2
                    else:
                        r_i[0] = (y_i[0] + y_i[1] + y_i[2] + y_i[3]) / 4
                    for b in range(4):
                        for j in range(number_of_interations):
                            chaotic_state = chaotic_state * r_i[b] * (1 - chaotic_state)
                            chaotic_state = (1000 * chaotic_state) - math.floor(1000 * chaotic_state)
                        y_i[b] = 3.86 + (chaotic_state * 0.14)
                control_parameter = (y_i[0] + y_i[1] + y_i[2] + y_i[3]) / 4
                R = chaotic_state * 256
                fileToStats.write(str(int(R)))
                fileToStats.write('\n')
                finalList = np.append(finalList, int(R))
                testList.append(int(R))
            np.save(file, finalList)
            file.close()
            fileToStats.close()
            return testList

def getStatistics():
    valuesList = [0] * 255
    probList = [0] * 255
    entropy = 0
    open("results_stats.txt", "r")
    with open("results_stats.txt", 'r') as file:
        lines = file.readlines()
    
    allLinesInFile = len(lines)

    # Number of appearances
    for i in lines:
        for index in range(255):
            if(int(i) == index):
                valuesList[index] += 1

    # Probability of appearances
    for index, i in enumerate(valuesList):
        probList[index] = i / allLinesInFile

    # Entropy 
    for i in probList:
        if i != 0:
            entropy += i * log(i, 2)

    entropy = entropy.real * -1
    return valuesList, probList, entropy
    
