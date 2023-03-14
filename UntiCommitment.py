# 230227 - ENEL 693 Assignment 2 - Security Constrained Optimal Power Flow.py - Austyn Nagribianko

import numpy as np
import pyomo
from pyomo.environ import*
from pyomo.opt import SolverFactory
import pandas as pd
import math

def main():

    # STATIC VARIABLES
    # Active Power Min and Max and Ramping Limits
    power = {"min": [0.15, 0.2], "max": [1.5, 1.5], "rampDown": [0.2, 0.3], "rampUp": [0.2, 0.3], "shutDown": [0.2, 0.3], "startUp": [0.2, 0.3]}
    # Unit Costs
    cost = {"fixed": [3, 1], "variable": [10, 20], "startUp": [5, 2], "shutDown": [1, 1]}
    # Line Power Flow Limitations
    line = {"maxApPow": [1, 1], "susceptance": [1, 1]}
    # Hour Zero Power Output and Generating Status
    p1_0 = 0.7
    p2_0 = 0.6
    u1_0 = 1
    u2_0 = 0
    # Hourly Demand for Hours [1, 2, 3, 4]
    demand = {"demand": [1, 0.9, 1.3, 1.5]}
    # Reserve Demand

    # MODEL
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    model.dual.pprint()

    # VARIABLES
    # Active Power Hourly Output
    model.p1_1 = Var(within=NonNegativeReals) # Unit 1 Active Power Output - Hour 1
    model.p1_2 = Var(within=NonNegativeReals) # Unit 1 Active Power Output - Hour 2
    model.p1_3 = Var(within=NonNegativeReals) # Unit 1 Active Power Output - Hour 3
    model.p1_4 = Var(within=NonNegativeReals) # Unit 1 Active Power Output - Hour 4
    model.p2_1 = Var(within=NonNegativeReals) # Unit 2 Active Power Output - Hour 1
    model.p2_2 = Var(within=NonNegativeReals) # Unit 2 Active Power Output - Hour 2
    model.p2_3 = Var(within=NonNegativeReals) # Unit 2 Active Power Output - Hour 3
    model.p2_4 = Var(within=NonNegativeReals) # Unit 2 Active Power Output - Hour 4

    # Unit Generating Status Binary Variables
    model.u1_1 = Var(domain=Binary) # Unit 1 Generating Status - Hour 1
    model.u1_2 = Var(domain=Binary) # Unit 1 Generating Status - Hour 2
    model.u1_3 = Var(domain=Binary) # Unit 1 Generating Status - Hour 3
    model.u1_4 = Var(domain=Binary) # Unit 1 Generating Status - Hour 4
    model.u2_1 = Var(domain=Binary) # Unit 2 Generating Status - Hour 1
    model.u2_2 = Var(domain=Binary) # Unit 2 Generating Status - Hour 2
    model.u2_3 = Var(domain=Binary) # Unit 2 Generating Status - Hour 3
    model.u2_4 = Var(domain=Binary) # Unit 2 Generating Status - Hour 4

    # Unit Start-Up Status Binary Variables
    model.y1_1 = Var(domain=Binary) # Unit 1 Start-Up Status - Hour 1
    model.y1_2 = Var(domain=Binary) # Unit 1 Start-Up Status - Hour 2
    model.y1_3 = Var(domain=Binary) # Unit 1 Start-Up Status - Hour 3
    model.y1_4 = Var(domain=Binary) # Unit 1 Start-Up Status - Hour 4
    model.y2_1 = Var(domain=Binary) # Unit 2 Start-Up Status - Hour 1
    model.y2_2 = Var(domain=Binary) # Unit 2 Start-Up Status - Hour 2
    model.y2_3 = Var(domain=Binary) # Unit 2 Start-Up Status - Hour 3
    model.y2_4 = Var(domain=Binary) # Unit 2 Start-Up Status - Hour 4

    # Unit Shut-Down Status Binary Variables
    model.z1_1 = Var(domain=Binary) # Unit 1 Shut-Down Status - Hour 1
    model.z1_2 = Var(domain=Binary) # Unit 1 Shut-Down Status - Hour 2
    model.z1_3 = Var(domain=Binary) # Unit 1 Shut-Down Status - Hour 3
    model.z1_4 = Var(domain=Binary) # Unit 1 Shut-Down Status - Hour 4
    model.z2_1 = Var(domain=Binary) # Unit 2 Shut-Down Status - Hour 1
    model.z2_2 = Var(domain=Binary) # Unit 2 Shut-Down Status - Hour 2
    model.z2_3 = Var(domain=Binary) # Unit 2 Shut-Down Status - Hour 3
    model.z2_4 = Var(domain=Binary) # Unit 2 Shut-Down Status - Hour 4

    # OPF CONSTRAINTS
    # Start-Up Shut-Down Equality
    model.c1a = Constraint(expr=model.y1_1 - model.z1_1 == model.u1_1 - u1_0)       # Unit 1 Start-Up Shut-Down - Hour 1
    model.c1b = Constraint(expr=model.y1_2 - model.z1_2 == model.u1_2 - model.u1_1) # Unit 1 Start-Up Shut-Down - Hour 2
    model.c1c = Constraint(expr=model.y1_3 - model.z1_3 == model.u1_3 - model.u1_2) # Unit 1 Start-Up Shut-Down - Hour 3
    model.c1d = Constraint(expr=model.y1_4 - model.z1_4 == model.u1_4 - model.u1_3) # Unit 1 Start-Up Shut-Down - Hour 4
    
    model.c2a = Constraint(expr=model.y2_1 - model.z2_1 == model.u2_1 - u2_0)       # Unit 2 Start-Up Shut-Down - Hour 1
    model.c2b = Constraint(expr=model.y2_2 - model.z2_2 == model.u2_2 - model.u2_1) # Unit 2 Start-Up Shut-Down - Hour 2
    model.c2c = Constraint(expr=model.y2_3 - model.z2_3 == model.u2_3 - model.u2_2) # Unit 2 Start-Up Shut-Down - Hour 3
    model.c2d = Constraint(expr=model.y2_4 - model.z2_4 == model.u2_4 - model.u2_3) # Unit 2 Start-Up Shut-Down - Hour 4

    model.c3a = Constraint(expr=model.y1_1 + model.z1_1 <= 1)   # Unit 1 Start-Up Shut-Down Limit - Hour 1
    model.c3b = Constraint(expr=model.y1_2 + model.z1_2 <= 1)   # Unit 1 Start-Up Shut-Down Limit - Hour 2
    model.c3c = Constraint(expr=model.y1_3 + model.z1_3 <= 1)   # Unit 1 Start-Up Shut-Down Limit - Hour 3
    model.c3d = Constraint(expr=model.y1_4 + model.z1_4 <= 1)   # Unit 1 Start-Up Shut-Down Limit - Hour 4
    
    model.c4a = Constraint(expr=model.y2_1 + model.z2_1 <= 1)   # Unit 2 Start-Up Shut-Down Limit - Hour 1
    model.c4b = Constraint(expr=model.y2_2 + model.z2_2 <= 1)   # Unit 2 Start-Up Shut-Down Limit - Hour 2
    model.c4c = Constraint(expr=model.y2_3 + model.z2_3 <= 1)   # Unit 2 Start-Up Shut-Down Limit - Hour 3
    model.c4d = Constraint(expr=model.y2_4 + model.z2_4 <= 1)   # Unit 2 Start-Up Shut-Down Limit - Hour 4

    # Active Power Limits
    model.c5a = Constraint(expr=model.p1_1 <= power["max"][0]*model.u1_1)   # Unit 1 Active Power Upper Limit - Hour 1
    model.c5b = Constraint(expr=model.p1_2 <= power["max"][0]*model.u1_2)   # Unit 1 Active Power Upper Limit - Hour 2
    model.c5c = Constraint(expr=model.p1_3 <= power["max"][0]*model.u1_3)   # Unit 1 Active Power Upper Limit - Hour 3
    model.c5d = Constraint(expr=model.p1_4 <= power["max"][0]*model.u1_4)   # Unit 1 Active Power Upper Limit - Hour 4

    model.c6a = Constraint(expr=model.p1_1 >= power["min"][0]*model.u1_1)   # Unit 1 Active Power Lower Limit - Hour 1
    model.c6b = Constraint(expr=model.p1_3 >= power["min"][0]*model.u1_3)   # Unit 1 Active Power Lower Limit - Hour 3
    model.c6c = Constraint(expr=model.p1_2 >= power["min"][0]*model.u1_2)   # Unit 1 Active Power Lower Limit - Hour 2
    model.c6d = Constraint(expr=model.p1_4 >= power["min"][0]*model.u1_4)   # Unit 1 Active Power Lower Limit - Hour 4
    
    model.c7a = Constraint(expr=model.p2_1 <= power["max"][0]*model.u2_1)   # Unit 2 Active Power Upper Limit - Hour 1
    model.c7b = Constraint(expr=model.p2_2 <= power["max"][0]*model.u2_2)   # Unit 2 Active Power Upper Limit - Hour 2
    model.c7c = Constraint(expr=model.p2_3 <= power["max"][0]*model.u2_3)   # Unit 2 Active Power Upper Limit - Hour 3
    model.c7d = Constraint(expr=model.p2_4 <= power["max"][0]*model.u2_4)   # Unit 2 Active Power Upper Limit - Hour 4

    model.c8a = Constraint(expr=model.p2_1 >= power["min"][0]*model.u2_1)   # Unit 2 Active Power Lower Limit - Hour 1
    model.c8b = Constraint(expr=model.p2_3 >= power["min"][0]*model.u2_3)   # Unit 2 Active Power Lower Limit - Hour 3
    model.c8c = Constraint(expr=model.p2_2 >= power["min"][0]*model.u2_2)   # Unit 2 Active Power Lower Limit - Hour 2
    model.c8d = Constraint(expr=model.p2_4 >= power["min"][0]*model.u2_4)   # Unit 2 Active Power Lower Limit - Hour 4

    # Ramping Limits
    model.c9a = Constraint(expr=model.p1_1 - p1_0 <= power["rampUp"][0]*u1_0 +
                                power["startUp"][0]*model.y1_1)  # Unit 1 Ramp-Up Limits - Hour 1
    model.c9b = Constraint(expr=model.p1_2 - model.p1_1 <= power["rampUp"][0]*model.u1_1 +
                                power["startUp"][0]*model.y1_2)  # Unit 1 Ramp-Up Limits - Hour 2
    model.c9c = Constraint(expr=model.p1_3 - model.p1_2 <= power["rampUp"][0]*model.u1_2 +
                                power["startUp"][0]*model.y1_3)  # Unit 1 Ramp-Up Limits - Hour 3
    model.c9d = Constraint(expr=model.p1_4 - model.p1_3 <= power["rampUp"][0]*model.u1_3 +
                                power["startUp"][0]*model.y1_4)  # Unit 1 Ramp-Up Limits - Hour 4
    
    model.c10a = Constraint(expr=model.p2_1 - p2_0 <= power["rampUp"][1]*u2_0 +
                                power["startUp"][1]*model.y2_1)  # Unit 2 Ramp-Up Limits - Hour 1
    model.c10b = Constraint(expr=model.p2_2 - model.p2_1 <= power["rampUp"][1]*model.u2_1 +
                                power["startUp"][1]*model.y2_2)  # Unit 2 Ramp-Up Limits - Hour 2
    model.c10c = Constraint(expr=model.p2_3 - model.p2_2 <= power["rampUp"][1]*model.u2_2 +
                                power["startUp"][1]*model.y2_3)  # Unit 2 Ramp-Up Limits - Hour 3
    model.c10d = Constraint(expr=model.p2_4 - model.p2_3 <= power["rampUp"][1]*model.u2_3 +
                                power["startUp"][1]*model.y2_4)  # Unit 2 Ramp-Up Limits - Hour 4

    model.c11a = Constraint(expr=p1_0 - model.p1_1 <= power["rampDown"][0] * model.u1_1 +
                                power["shutDown"][0] * model.z1_1)  # Unit 1 Ramp-Down Limits - Hour 1
    model.c11b = Constraint(expr=model.p1_1 - model.p1_2 <= power["rampDown"][0] * model.u1_2 +
                                power["shutDown"][0] * model.z1_2)  # Unit 1 Ramp-Down Limits - Hour 2
    model.c11c = Constraint(expr=model.p1_2 - model.p1_3 <= power["rampDown"][0] * model.u1_3 +
                                power["shutDown"][0] * model.z1_3)  # Unit 1 Ramp-Down Limits - Hour 3
    model.c11d = Constraint(expr=model.p1_3 - model.p1_4 <= power["rampDown"][0] * model.u1_4 +
                                power["shutDown"][0] * model.z1_4)  # Unit 1 Ramp-Down Limits - Hour 4

    model.c12a = Constraint(expr=p2_0 - model.p2_1 <= power["rampDown"][1] * model.u2_1 +
                                power["shutDown"][1] * model.z2_1)  # Unit 2 Ramp-Down Limits - Hour 1
    model.c12b = Constraint(expr=model.p2_1 - model.p2_2 <= power["rampDown"][1] * model.u2_2 +
                                power["shutDown"][1] * model.z2_2)  # Unit 2 Ramp-Down Limits - Hour 2
    model.c12c = Constraint(expr=model.p2_2 - model.p2_3 <= power["rampDown"][1] * model.u2_3 +
                                power["shutDown"][1] * model.z2_3)  # Unit 2 Ramp-Down Limits - Hour 3
    model.c12d = Constraint(expr=model.p2_3 - model.p2_4 <= power["rampDown"][1] * model.u2_4 +
                                power["shutDown"][1] * model.z2_4)  # Unit 2 Ramp-Down Limits - Hour 4
    
    # Hourly Power Balance
    model.c13a = Constraint(expr=model.p1_1 + model.p2_1 == demand["demand"][0])  # Active Power Balance - Hour 1
    model.c13b = Constraint(expr=model.p1_2 + model.p2_2 == demand["demand"][1])  # Active Power Balance - Hour 2
    model.c13c = Constraint(expr=model.p1_3 + model.p2_3 == demand["demand"][2])  # Active Power Balance - Hour 3
    model.c13d = Constraint(expr=model.p1_4 + model.p2_4 == demand["demand"][3])  # Active Power Balance - Hour 4    

    # Line Limits
    # model.c14a = Constraint(expr=model.p1_1 + demand["demand"][0] - model.p2_1 <= line["maxApPow"]) # Line 1-3 Flow Limits - Hour 1
    # model.c14b = Constraint(expr=model.p1_1 + demand["demand"][0] - model.p2_1 >= -line["maxApPow"]) # Line 3-1 Flow Limits - Hour 1
    # model.c14c = Constraint(expr=model.p2_1 + demand["demand"][0] - model.p1_1 <= line["maxApPow"]) # Line 1-2 Flow Limits - Hour 1
    # model.c14d = Constraint(expr=model.p2_1 + demand["demand"][0] - model.p1_1 >= -line["maxApPow"]) # Line 2-1 Flow Limits - Hour 1
    #
    # model.c15a = Constraint(expr=model.p1_2 + demand["demand"][1] - model.p2_2 <= line["maxApPow"]) # Line 1-3 Flow Limits - Hour 2
    # model.c15b = Constraint(expr=model.p1_2 + demand["demand"][1] - model.p2_2 >= -line["maxApPow"]) # Line 3-1 Flow Limits - Hour 2
    # model.c15c = Constraint(expr=model.p2_2 + demand["demand"][1] - model.p1_2 <= line["maxApPow"]) # Line 1-2 Flow Limits - Hour 2
    # model.c15d = Constraint(expr=model.p2_2 + demand["demand"][1] - model.p1_2 >= -line["maxApPow"]) # Line 2-1 Flow Limits - Hour 2
    #
    # model.c16a = Constraint(expr=model.p1_3 + demand["demand"][2] - model.p2_3 <= line["maxApPow"]) # Line 1-3 Flow Limits - Hour 3
    # model.c16b = Constraint(expr=model.p1_3 + demand["demand"][2] - model.p2_3 >= -line["maxApPow"]) # Line 3-1 Flow Limits - Hour 3
    # model.c16c = Constraint(expr=model.p2_3 + demand["demand"][2] - model.p1_3 <= line["maxApPow"]) # Line 1-2 Flow Limits - Hour 3
    # model.c16d = Constraint(expr=model.p2_3 + demand["demand"][2] - model.p1_3 >= -line["maxApPow"]) # Line 2-1 Flow Limits - Hour 3
    #
    # model.c17a = Constraint(expr=model.p1_4 + demand["demand"][3] - model.p2_4 <= line["maxApPow"]) # Line 1-3 Flow Limits - Hour 4
    # model.c17b = Constraint(expr=model.p1_4 + demand["demand"][3] - model.p2_4 >= -line["maxApPow"]) # Line 3-1 Flow Limits - Hour 4
    # model.c17c = Constraint(expr=model.p2_4 + demand["demand"][3] - model.p1_4 <= line["maxApPow"]) # Line 1-2 Flow Limits - Hour 4
    # model.c17d = Constraint(expr=model.p2_4 + demand["demand"][3] - model.p1_4 >= -line["maxApPow"]) # Line 2-1 Flow Limits - Hour 4

    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=
                          cost["fixed"][0]*model.u1_1 + cost["variable"][0]*model.p1_1 + cost["startUp"][0]*model.y1_1 + cost["shutDown"][0]*model.z1_1 +
                          cost["fixed"][0]*model.u1_2 + cost["variable"][0]*model.p1_2 + cost["startUp"][0]*model.y1_2 + cost["shutDown"][0]*model.z1_2 +
                          cost["fixed"][0]*model.u1_3 + cost["variable"][0]*model.p1_3 + cost["startUp"][0]*model.y1_3 + cost["shutDown"][0]*model.z1_3 +
                          cost["fixed"][0]*model.u1_4 + cost["variable"][0]*model.p1_4 + cost["startUp"][0]*model.y1_4 + cost["shutDown"][0]*model.z1_4 +
                          cost["fixed"][1]*model.u2_1 + cost["variable"][1]*model.p2_1 + cost["startUp"][1]*model.y2_1 + cost["shutDown"][1]*model.z2_1 +
                          cost["fixed"][1]*model.u2_2 + cost["variable"][1]*model.p2_2 + cost["startUp"][1]*model.y2_2 + cost["shutDown"][1]*model.z2_2 +
                          cost["fixed"][1]*model.u2_3 + cost["variable"][1]*model.p2_3 + cost["startUp"][1]*model.y2_3 + cost["shutDown"][1]*model.z2_3 +
                          cost["fixed"][1]*model.u2_4 + cost["variable"][1]*model.p2_4 + cost["startUp"][1]*model.y2_4 + cost["shutDown"][1]*model.z2_4)

    # SOLVING
    model.pprint() # Printing Variable, Objective, and Constraint Declarations
    opt = SolverFactory("gurobi") # Declaring Solver
    results = opt.solve(model) # Calling Optimizer to Solve Model

    # PRINTING RESULTS
    # Headers
    print("\n\n{}".format("Objective Optimized".center(50, "-"))) # Printing Header

    # Printing Control Variables
    print("\nControl Variable Solutions:")
    print("\np1_1:\t\t%5.3f" % model.p1_1())
    print("p1_2:\t\t%5.3f" % model.p1_2())
    print("p1_3:\t\t%5.3f" % model.p1_3())
    print("p1_4:\t\t%5.3f" % model.p1_4())
    print("p2_1:\t\t%5.3f" % model.p2_1())
    print("p2_2:\t\t%5.3f" % model.p2_2())
    print("p2_3:\t\t%5.3f" % model.p2_3())
    print("p2_4:\t\t%5.3f" % model.p2_4())
    
    print("\nu1_1:\t\t%5.3f" % model.u1_1())
    print("u1_2:\t\t%5.3f" % model.u1_2())
    print("u1_3:\t\t%5.3f" % model.u1_3())
    print("u1_4:\t\t%5.3f" % model.u1_4())
    print("u2_1:\t\t%5.3f" % model.u2_1())
    print("u2_2:\t\t%5.3f" % model.u2_2())
    print("u2_3:\t\t%5.3f" % model.u2_3())
    print("u2_4:\t\t%5.3f" % model.u2_4())
    
    print("\ny1_1:\t\t%5.3f" % model.y1_1())
    print("y1_2:\t\t%5.3f" % model.y1_2())
    print("y1_3:\t\t%5.3f" % model.y1_3())
    print("y1_4:\t\t%5.3f" % model.y1_4())
    print("y2_1:\t\t%5.3f" % model.y2_1())
    print("y2_2:\t\t%5.3f" % model.y2_2())
    print("y2_3:\t\t%5.3f" % model.y2_3())
    print("y2_4:\t\t%5.3f" % model.y2_4())
    
    print("\nz1_1:\t\t%5.3f" % model.z1_1())
    print("z1_2:\t\t%5.3f" % model.z1_2())
    print("z1_3:\t\t%5.3f" % model.z1_3())
    print("z1_4:\t\t%5.3f" % model.z1_4())
    print("z2_1:\t\t%5.3f" % model.z2_1())
    print("z2_2:\t\t%5.3f" % model.z2_2())
    print("z2_3:\t\t%5.3f" % model.z2_3())
    print("z2_4:\t\t%5.3f" % model.z2_4())

    # Printing Costs
    solutionCost = cost["fixed"][0]*model.u1_1() + cost["variable"][0]*model.p1_1() + cost["startUp"][0]*model.y1_1() +\
                   cost["shutDown"][0]*model.z1_1() + cost["fixed"][0]*model.u1_2() + cost["variable"][0]*model.p1_2() +\
                   cost["startUp"][0]*model.y1_2() + cost["shutDown"][0]*model.z1_2() + cost["fixed"][0]*model.u1_3() +\
                   cost["variable"][0]*model.p1_3() + cost["startUp"][0]*model.y1_3() + cost["shutDown"][0]*model.z1_3() +\
                   cost["fixed"][0]*model.u1_4() + cost["variable"][0]*model.p1_4() + cost["startUp"][0]*model.y1_4() +\
                   cost["shutDown"][0]*model.z1_4() + cost["fixed"][1]*model.u2_1() + cost["variable"][1]*model.p2_1() +\
                   cost["startUp"][1]*model.y2_1() + cost["shutDown"][1]*model.z2_1() + cost["fixed"][1]*model.u2_2() +\
                   cost["variable"][1]*model.p2_2() + cost["startUp"][1]*model.y2_2() + cost["shutDown"][1]*model.z2_2() +\
                   cost["fixed"][1]*model.u2_3() + cost["variable"][1]*model.p2_3() + cost["startUp"][1]*model.y2_3() + \
                   cost["shutDown"][1]*model.z2_3() + cost["fixed"][1]*model.u2_4() + cost["variable"][1]*model.p2_4() +\
                   cost["startUp"][1]*model.y2_4() + cost["shutDown"][1]*model.z2_4()
    print("\nSolution Cost:", solutionCost)

if __name__ == "__main__":
    main()