# 230227 - ENEL 693 Assignment 2 - Security Constrained Optimal Power Flow.py - Austyn Nagribianko

import numpy as np
import pyomo
from pyomo.environ import*
from pyomo.opt import SolverFactory
import pandas as pd
import math
import gnuplotpy as gp
import itertools

def main():

    # SYSTEM SETTINGS
    printSummary = True

    # STATIC VARIABLES
    # Active Power Min and Max and Ramping Limits
    power = {"min": [0.15, 0.2], "max": [1.5, 1.5], "rampDown": [0.2, 0.3], "rampUp": [0.2, 0.3], "shutDown": [0.2, 0.3], "startUp": [0.2, 0.3]}
    # Unit Costs
    cost = {"fixed": [3, 1], "variable": [10, 20], "startUp": [5, 2], "shutDown": [1, 1]}
    # Line Power Flow Limitations
    line = {"maxApPow": [1, 1], "admMag": [1, 1]}
    # Hourly Load and Reserve for Hours [1, 2, 3, 4]
    demand = {"load": [1, 0.9, 1.3, 1.5], "reserve": [0.1, 0.09, 0.13, 0.15]}
    # Bus Voltage and Angle Limits
    busVoltage = {"angMin": [-math.pi], "angMax": [math.pi]}
    # Hour Zero Power Output and Generating Status
    p1_0 = 0.7
    p2_0 = 0.6
    u1_0 = 1
    u2_0 = 1
    hours = len(demand["load"])

    # MODEL
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    model.dual.pprint()

    # INDICES
    model.I = Set(initialize=range(hours))   # initializing model with indices

    # VARIABLES
    # Active Power Hourly Output
    model.p1 = Var(model.I, domain=NonNegativeReals) # Unit 1 Active Power Output
    model.p2 = Var(model.I, domain=NonNegativeReals) # Unit 2 Active Power Output

    # Unit Generating Status Binary Variables
    model.u1 = Var(model.I, domain=Binary) # Unit 1 Generating Status
    model.u2 = Var(model.I, domain=Binary) # Unit 2 Generating Status

    # Unit Start-Up Status Binary Variables
    model.y1 = Var(model.I, domain=Binary) # Unit 1 Start-Up Status
    model.y2 = Var(model.I, domain=Binary) # Unit 2 Start-Up Status

    # Unit Shut-Down Status Binary Variables
    model.z1 = Var(model.I, domain=Binary) # Unit 1 Shut-Down Status
    model.z2 = Var(model.I, domain=Binary) # Unit 2 Shut-Down Status
    
    # Bus Voltage Angles
    model.d1 = Var(model.I, domain=Reals) # Bus 1 Voltage Angle
    model.d2 = Var(model.I, domain=Reals) # Bus 2 Voltage Angle
    model.d3 = Var(model.I, domain=Reals) # Bus 3 Voltage Angle
    
    # Line Flows
    model.p13 = Var(model.I, domain=Reals) # Line 13 Line Flow
    model.p31 = Var(model.I, domain=Reals) # Line 31 Line Flow
    model.p23 = Var(model.I, domain=Reals) # Line 23 Line Flow
    model.p32 = Var(model.I, domain=Reals) # Line 32 Line Flow

    # UNIT COMMITMENT CONSTRAINTS
    model.cons = ConstraintList()

    # Start-Up Shut-Down Equality
    model.cons.add(expr=model.y1[0] - model.z1[0] == model.u1[0] - u1_0) # Unit 1 Start-Up Shut-Down Equality
    model.cons.add(expr=model.y2[0] - model.z2[0] == model.u2[0] - u2_0) # Unit 2 Start-Up Shut-Down Equality
    for i in range(1, hours):
        model.cons.add(expr=model.y1[i] - model.z1[i] == model.u1[i] - model.u1[i-1]) # Unit 1 Start-Up Shut-Down Equality
        model.cons.add(expr=model.y2[i] - model.z2[i] == model.u2[i] - model.u2[i-1]) # Unit 2 Start-Up Shut-Down Equality

    # Start-Up Shut-Down Limit
    for i in range(hours):
        model.cons.add(expr=model.y1[i] + model.z1[i] <= 1) # Unit 1 Start-Up Shut-Down Limit
        model.cons.add(expr=model.y2[i] + model.z2[i] <= 1) # Unit 2 Start-Up Shut-Down Limit

    # Active Power Limits
    for i in range(hours):
        model.cons.add(expr=model.p1[i] <= power["max"][0] * model.u1[i]) # Unit 1 Active Power Upper Limit
        model.cons.add(expr=model.p1[i] >= power["min"][0] * model.u1[i]) # Unit 1 Active Power Lower Limit
        model.cons.add(expr=model.p2[i] <= power["max"][1] * model.u2[i]) # Unit 2 Active Power Upper Limit
        model.cons.add(expr=model.p2[i] >= power["min"][1] * model.u2[i]) # Unit 2 Active Power Lower Limit

    # Ramp Up Limits
    model.cons.add(expr=model.p1[0] - p1_0 <= power["rampUp"][0] * u1_0 + power["startUp"][0] * model.y1[0]) # Unit 1 Ramp-Up Limits
    model.cons.add(expr=model.p2[0] - p2_0 <= power["rampUp"][1] * u2_0 + power["startUp"][1] * model.y2[0]) # Unit 2 Ramp-Up Limits
    for i in range(1, hours):
        model.cons.add(expr=model.p1[i] - model.p1[i-1] <= power["rampUp"][0] * model.u1[i-1] + power["startUp"][0] * model.y1[i]) # Unit 1 Ramp-Up Limits
        model.cons.add(expr=model.p2[i] - model.p2[i-1] <= power["rampUp"][1] * model.u2[i-1] + power["startUp"][1] * model.y2[i]) # Unit 2 Ramp-Up Limits

    # Ramp Down Limits
    model.cons.add(expr=p1_0 - model.p1[0] <= power["rampDown"][0] * model.u1[0] + power["shutDown"][0] * model.z1[0]) # Unit 1 Ramp-Down Limits
    model.cons.add(expr=p2_0 - model.p2[0] <= power["rampDown"][1] * model.u2[0] + power["shutDown"][1] * model.z2[0]) # Unit 2 Ramp-Down Limits
    for i in range(1, hours):
        model.cons.add(expr=model.p1[i-1] - model.p1[i] <= power["rampDown"][0] * model.u1[i] + power["shutDown"][0] * model.z1[i]) # Unit 1 Ramp-Down Limits
        model.cons.add(expr=model.p2[i-1] - model.p2[i] <= power["rampDown"][1] * model.u2[i] + power["shutDown"][1] * model.z2[i]) # Unit 2 Ramp-Down Limits

    # Hourly Reserve Requirements
    for i in range(hours):
        model.cons.add(expr=demand["load"][i] + demand["reserve"][i] <= model.u1[i] * power["max"][0] + model.u2[i] * power["max"][1]) # Hourly Reserve Requirement

    # Line Flows
    for i in range(hours):
        model.cons.add(expr=model.p13[i] == (model.d1[i] - model.d3[i]) * line["admMag"][0]) # Line 13 Active Power
        model.cons.add(expr=model.p31[i] == (model.d3[i] - model.d1[i]) * line["admMag"][0]) # Line 31 Active Power
        model.cons.add(expr=model.p23[i] == (model.d2[i] - model.d3[i]) * line["admMag"][1]) # Line 23 Active Power
        model.cons.add(expr=model.p32[i] == (model.d3[i] - model.d2[i]) * line["admMag"][1]) # Line 32 Active Power

    # Voltage Angle Limits
    for i in range(hours):
        model.cons.add(expr=model.d1[i] <= busVoltage["angMax"][0]) # Bus 1 Voltage Angle Upper Limit
        model.cons.add(expr=model.d1[i] >= busVoltage["angMin"][0]) # Bus 1 Voltage Angle Lower Limit
        model.cons.add(expr=model.d2[i] <= busVoltage["angMax"][0]) # Bus 2 Voltage Angle Upper Limit
        model.cons.add(expr=model.d2[i] >= busVoltage["angMin"][0]) # Bus 2 Voltage Angle Lower Limit
        model.cons.add(expr=model.d3[i] == 0) # Bus 3 Voltage Angle Equality

    # Line Flow Power Balance
    for i in range(hours):
        model.cons.add(expr=model.p1[i] == model.p13[i]) # Bus 1 Flow Balance
        model.cons.add(expr=model.p2[i] == model.p23[i]) # Bus 2 Flow Balance
        model.cons.add(expr=-demand["load"][i] == model.p32[i] + model.p31[i]) # Bus 3 Flow Balance

    # Line Flow Limits
    for i in range(hours):
        model.cons.add(expr=model.p13[i] <= line["maxApPow"][0]) # Line 13 Line Limits
        model.cons.add(expr=model.p31[i] <= line["maxApPow"][0]) # Line 31 Line Limits
        model.cons.add(expr=model.p23[i] <= line["maxApPow"][1]) # Line 23 Line Limits
        model.cons.add(expr=model.p32[i] <= line["maxApPow"][1]) # Line 32 Line Limits
    
    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=
                          sum(cost["fixed"][0]*model.u1[i] + cost["variable"][0]*model.p1[i] + cost["startUp"][0]*model.y1[i] + cost["shutDown"][0]*model.z1[i] +
                          cost["fixed"][1]*model.u2[i] + cost["variable"][1]*model.p2[i] + cost["startUp"][1]*model.y2[i] + cost["shutDown"][1]*model.z2[i] for i in range(hours)))

    # SOLVING
    model.pprint() # Printing Variable, Objective, and Constraint Declarations
    opt = SolverFactory("gurobi") # Declaring Solver
    results = opt.solve(model) # Calling Optimizer to Solve Model

    # PRINTING RESULTS
    # Headers
    print("\n\n{}".format("Objective Optimized".center(50, "-"))) # Printing Header

    # Printing Control Variables
    print("\nControl Variable Solutions:")
    for i in range(hours):
        print("\nLoad\t\t\t\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, demand["load"][i]))
        print("Unit 1 Power (p1)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p1[i]()))
        print("Unit 2 Power (p2)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p2[i]()))
        if not printSummary:
            print("Line 13 Flow (p13)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p13[i]()))
            print("Line 31 Flow (p31)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p31[i]()))
            print("Line 23 Flow (p23)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p23[i]()))
            print("Line 32 Flow (p32)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p32[i]()))
            print("Bus 1 Delta (d1)\t\t\tHour %d\t\t%5.3f\t\trad" % (i, model.d1[i]()))
            print("Bus 2 Delta (d2)\t\t\tHour %d\t\t%5.3f\t\trad" % (i, model.d2[i]()))
            print("Bus 3 Delta (d3)\t\t\tHour %d\t\t%5.3f\t\trad" % (i, model.d3[i]()))
            print("Unit 1 Status (u1)\t\t\tHour %d\t\t%5.3f" % (i, model.u1[i]()))
            print("Unit 2 Status (u2)\t\t\tHour %d\t\t%5.3f" % (i, model.u2[i]()))
            print("Unit 1 Ramp-Up (y1)\t\t\tHour %d\t\t%5.3f" % (i, model.y1[i]()))
            print("Unit 2 Ramp-Up (y2)\t\t\tHour %d\t\t%5.3f" % (i, model.y2[i]()))
            print("Unit 1 Ramp-Down (z1)\t\tHour %d\t\t%5.3f" % (i, model.z1[i]()))
            print("Unit 2 Ramp-Down (z2)\t\tHour %d\t\t%5.3f" % (i, model.z2[i]()))

    # Printing Dispatch Cost
    temp = 0
    for i in range(hours):
        temp += cost["fixed"][0] * model.u1[i]() + cost["variable"][0] * model.p1[i]() + cost["startUp"][0] * model.y1[i]() + \
               cost["shutDown"][0] * model.z1[i]() + cost["fixed"][1] * model.u2[i]() + cost["variable"][1] * model.p2[i]() + \
               cost["startUp"][1] * model.y2[i]() + cost["shutDown"][1] * model.z2[i]()
    print("\nTotal Dispatch Cost\t\t\t\t\t\t%5.3f\t\t$/MWh" % temp)

if __name__ == "__main__":
    main()