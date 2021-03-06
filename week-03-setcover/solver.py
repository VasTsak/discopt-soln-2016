#!/usr/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Carleton Coffrin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from collections import namedtuple
import numpy as np
import cvxopt
import cvxopt.glpk
cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'

Set = namedtuple("Set", ['index', 'cost', 'items'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])
    
    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), map(int, parts[1:])))

    # build a trivial solution
    # pick add sets one-by-one until all the items are covered
    # ==========
    #solution = [0]*set_count
    #coverted = set()
    #
    #for s in sets:
    #    solution[s.index] = 1
    #    coverted |= set(s.items)
    #    if len(coverted) >= item_count:
    #        break

    # greedy solution
    # this is essentially the best-possible polynomial time approximation
    # algorithm for set cover
    # https://en.wikipedia.org/wiki/Set_cover_problem
    # ==========
    solution = greedy(item_count, sets)
        
    # MIP solution
    # slow but optimal
    # ==========
    #solution = mip(item_count, sets)

    # calculate the cost of the solution
    obj = sum([s.cost*solution[s.index] for s in sets])

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def mip(item_count, sets):
    set_count = len(sets)

    c = np.zeros(set_count)
    h = -1 * np.ones(item_count)
    xG = []
    yG = []
    valG = []
    for i, s in enumerate(sets):
        c[i] = s.cost
        for item in s.items:
            xG.append(item)
            yG.append(i)
            valG.append(-1)

    binVars=set()
    for var in range(set_count):
        binVars.add(var)
        
    status, isol = cvxopt.glpk.ilp(c = cvxopt.matrix(c),
                                   G = cvxopt.spmatrix(valG, xG, yG),
                                   h = cvxopt.matrix(h),
                                   I = binVars,
                                   B = binVars)

    return list(map(int, isol))

def greedy(item_count, sets):
    coveredItems = set()
    setDiffs = {}
    soln = [0] * len(sets)
    while len(coveredItems) < item_count:
        maxCoverDensity = 0
        maxCoverSet = set()
        maxCoverIndex = -1
        for i, s in enumerate(sets):
            setDiffs[i] = setDiffs.get(i, set(s.items)) - coveredItems
            newCoverDensity = len(setDiffs[i]) / s.cost
            if newCoverDensity > maxCoverDensity:
                maxCoverSet = setDiffs[i]
                maxCoverDensity = newCoverDensity
                maxCoverIndex = s.index
        coveredItems |= maxCoverSet
        soln[maxCoverIndex] = 1
        #print(coveredItems)
    return soln

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)')

