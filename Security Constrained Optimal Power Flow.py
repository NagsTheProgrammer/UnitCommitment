# 230227 - ENEL 693 Assignment 2 - Security Constrained Optimal Power Flow.py - Austyn Nagribianko

import numpy as np
import pyomo
from pyomo.environ import*
from pyomo.opt import SolverFactory
import pandas as pd
import math

def main():

    # CONTINGENCIES
    # 0: no contingency event
    # 1: line a out of service
    # 2: line b out of service
    contingencyString = ["None", "Line (12a) Out of Service", "Line (12b) Out of Service"]
    contingency = 1

    # STATIC VARIABLES
    # Active Power Min and Max and Ramping Limits
    acPow = {"min": [0, 0], "max": [3, 0.8], "ramp": [0.8, 0.3]}
    # Reactive Power Min and Max
    rePow = {"min": [-2, -2], "max": [2, 2]}
    # Unit Costs
    cost = {"cost": [1, 2]}
    # Bus Voltage Magnitude and Angle Limits
    voltage = {"magMin": [0.95, 0.95], "magMax": [1.1, 1.1], "ang": [-math.pi, math.pi]}
    # Line Power Flow Max and Admittance Magnitude and Angle Limits
    line = {"maxApPow": [0.5, 0.5], "admMag": [9.9504, 9.9504], "admAng": [-1.4711, -1.4711]}

    # MODEL
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    model.dual.pprint()

    # OPF VARIABLES
    # Active Power Output
    model.p1 = Var(within=NonNegativeReals) # Unit 1 Active Power Output
    model.p2 = Var(within=NonNegativeReals) # Unit 2 Active Power Output

    # Reactive Power Output
    model.q1 = Var(within=Reals) # Unit 1 Reactive Power Output
    model.q2 = Var(within=Reals) # Unit 2 Reactive Power Output

    # Bus Voltage Angles
    model.d1 = Var(within=Reals) # Bus 1 Voltage Angle
    model.d2 = Var(within=Reals) # Bus 2 Voltage Angle

    # Bus Voltage Magnitudes
    model.v1 = Var(within=Reals) # Bus 1 Voltage Magnitude
    model.v2 = Var(within=Reals) # Bus 2 Voltage Magnitude

    # Active Power Line Flows
    model.p12a = Var(within=Reals) # Line a Bus 1 to 2 Active Power Flow
    model.p12b = Var(within=Reals) # Line b Bus 1 to 2 Active Power Flow
    model.p21a = Var(within=Reals) # Line a Bus 2 to 1 Active Power Flow
    model.p21b = Var(within=Reals) # Line b Bus 2 to 1 Active Power Flow

    # Reactive Power Line Flows
    model.q12a = Var(within=Reals) # Line a Bus 1 to 2 Reactive Power Flow
    model.q12b = Var(within=Reals) # Line b Bus 1 to 2 Reactive Power Flow
    model.q21a = Var(within=Reals) # Line a Bus 2 to 1 Reactive Power Flow
    model.q21b = Var(within=Reals) # Line b Bus 2 to 1 Reactive Power Flow

    # SCOPF VARIABLES
    # Active Power Output
    model.p1w = Var(within=NonNegativeReals) # Unit 1 Active Power Contingency Output
    model.p2w = Var(within=NonNegativeReals) # Unit 2 Active Power Contingency Output

    # Reactive Power Output
    model.q1w = Var(within=Reals) # Unit 1 Reactive Power Contingency Output
    model.q2w = Var(within=Reals) # Unit 2 Reactive Power Contingency Output

    # Bus Voltage Angles
    model.d1w = Var(within=Reals) # Bus 1 Voltage Angle Contingency
    model.d2w = Var(within=Reals) # Bus 2 Voltage Angle Contingency

    # Bus Voltage Magnitudes
    model.v1w = Var(within=Reals) # Bus 1 Voltage Magnitude Contingency
    model.v2w = Var(within=Reals) # Bus 2 Voltage Magnitude Contingency

    # Active Power Line Flows
    model.p12aw = Var(within=Reals) # Line a Bus 1 to 2 Active Power Flow Contingency
    model.p12bw = Var(within=Reals) # Line b Bus 1 to 2 Active Power Flow Contingency
    model.p21aw = Var(within=Reals) # Line a Bus 2 to 1 Active Power Flow Contingency
    model.p21bw = Var(within=Reals) # Line b Bus 2 to 1 Active Power Flow Contingency

    # Reactive Power Line Flows
    model.q12aw = Var(within=Reals) # Line a Bus 1 to 2 Reactive Power Flow Contingency
    model.q12bw = Var(within=Reals) # Line b Bus 1 to 2 Reactive Power Flow Contingency
    model.q21aw = Var(within=Reals) # Line a Bus 2 to 1 Reactive Power Flow Contingency
    model.q21bw = Var(within=Reals) # Line b Bus 2 to 1 Reactive Power Flow Contingency

    # OPF CONSTRAINTS
    # Active Power Limits
    model.c1 = Constraint(expr=model.p1 >= acPow["min"][0]) # Unit 1 Active Power Lower Limit
    model.c2 = Constraint(expr=model.p2 >= acPow["min"][1]) # Unit 2 Active Power Lower Limit
    model.c3 = Constraint(expr=model.p1 <= acPow["max"][0]) # Unit 1 Active Power Upper Limit
    model.c4 = Constraint(expr=model.p2 <= acPow["max"][1]) # Unit 2 Active Power Upper Limit

    # Reactive Power Limits
    model.c5 = Constraint(expr=model.q1 >= rePow["min"][0]) # Unit 1 Reactive Power Lower Limit
    model.c6 = Constraint(expr=model.q2 >= rePow["min"][1]) # Unit 2 Reactive Power Lower Limit
    model.c7 = Constraint(expr=model.q1 <= rePow["max"][0]) # Unit 1 Reactive Power Upper Limit
    model.c8 = Constraint(expr=model.q2 <= rePow["max"][1]) # Unit 2 Reactive Power Upper Limit

    # Voltage Angle Limits and Equalities
    model.c9 = Constraint(expr=model.d1 >= voltage["ang"][0]) # Bus 1 Voltage Angle Lower Limit
    model.c10 = Constraint(expr=model.d1 <= voltage["ang"][1]) # Bus 1 Voltage Angle Upper Limit
    model.c11 = Constraint(expr=model.d2 == 0) # Bus 2 Voltage Angle Equality

    # Voltage Magnitude Limits
    model.c12 = Constraint(expr=model.v1 >= voltage["magMin"][0]) # Bus 1 Voltage Magnitude Lower Limit
    model.c13 = Constraint(expr=model.v2 >= voltage["magMin"][1]) # Bus 2 Voltage Magnitude Lower Limit
    model.c14 = Constraint(expr=model.v1 <= voltage["magMax"][0]) # Bus 1 Voltage Magnitude Upper Limit
    model.c15 = Constraint(expr=model.v2 <= voltage["magMax"][1]) # Bus 2 Voltage Magnitude Upper Limit

    # Active Power Line Equalities
    model.c16 = Constraint(expr=model.p12a == (model.v1**2)*line["admMag"][0]*cos(line["admAng"][0])-model.v1*model.v2*
                                line["admMag"][0]*cos(model.d1-model.d2-line["admAng"][0])) # Line (12a) Active Power
    model.c17 = Constraint(expr=model.p12b == (model.v1**2)*line["admMag"][1]*cos(line["admAng"][1])-model.v1*model.v2*
                                line["admMag"][1]*cos(model.d1-model.d2-line["admAng"][1])) # Line (12b) Active Power
    model.c18 = Constraint(expr=model.p21a == (model.v2**2)*line["admMag"][0]*cos(line["admAng"][0])-model.v2*model.v1*
                                line["admMag"][0]*cos(model.d2-model.d1-line["admAng"][0])) # Line (21a) Active Power
    model.c19 = Constraint(expr=model.p21b == (model.v2**2)*line["admMag"][1]*cos(line["admAng"][1])-model.v2*model.v1*
                                line["admMag"][1]*cos(model.d2-model.d1-line["admAng"][1])) # Line (21b) Active Power

    # Reactive Power Line Equalities
    model.c20 = Constraint(expr=model.q12a == -(model.v1**2)*line["admMag"][0]*sin(line["admAng"][0])-model.v1*model.v2*
                                line["admMag"][0]*sin(model.d1-model.d2-line["admAng"][0])) # Line (12a) Reactive Power
    model.c21 = Constraint(expr=model.q12b == -(model.v1**2)*line["admMag"][1]*sin(line["admAng"][1])-model.v1*model.v2*
                                line["admMag"][1]*sin(model.d1-model.d2-line["admAng"][1])) # Line (12b) Reactive Power
    model.c22 = Constraint(expr=model.q21a == -(model.v2**2)*line["admMag"][0]*sin(line["admAng"][0])-model.v2*model.v1*
                                line["admMag"][0]*sin(model.d2-model.d1-line["admAng"][0])) # Line (21a) Reactive Power
    model.c23 = Constraint(expr=model.q21b == -(model.v2**2)*line["admMag"][1]*sin(line["admAng"][1])-model.v2*model.v1*
                                line["admMag"][1]*sin(model.d2-model.d1-line["admAng"][1])) # Line (21b) Reactive Power

    # Power Balance Formulations
    model.c24 = Constraint(expr=model.p1 == model.p12a+model.p12b+0.8) # Bus 1 Active Power Balance
    model.c25 = Constraint(expr=model.p2 == model.p21a+model.p21b+1.2) # Bus 2 Active Power Balance
    model.c26 = Constraint(expr=model.q1 == model.q12a+model.q12b+0.6) # Bus 1 Reactive Power Balance
    model.c27 = Constraint(expr=model.q2 == model.q21a+model.q21b+0.6) # Bus 2 Reactive Power Balance

    # Line Capacity Limits
    model.c28 = Constraint(expr=line["maxApPow"][0]**2 >= model.p12a**2 + model.q12a**2) # Line (12a) Capacity Limit
    model.c29 = Constraint(expr=line["maxApPow"][1]**2 >= model.p12b**2 + model.q12b**2) # Line (12b) Capacity Limit
    model.c30 = Constraint(expr=line["maxApPow"][0]**2 >= model.p21a**2 + model.q21a**2) # Line (21a) Capacity Limit
    model.c31 = Constraint(expr=line["maxApPow"][1]**2 >= model.p21b**2 + model.q21b**2) # Line (21b) Capacity Limit

    # SCOPF CONSTRAINTS
    # Active Power Limits
    if contingency != 0:
        model.c1w = Constraint(expr=model.p1w >= acPow["min"][0]) # Unit 1 Active Power Contingency Lower Limit
        model.c2w = Constraint(expr=model.p2w >= acPow["min"][1]) # Unit 2 Active Power Contingency Lower Limit
        model.c3w = Constraint(expr=model.p1w <= acPow["max"][0]) # Unit 1 Active Power Contingency Upper Limit
        model.c4w = Constraint(expr=model.p2w <= acPow["max"][1]) # Unit 2 Active Power Contingency Upper Limit

    # Reactive Power Limits
    if contingency != 0: # Contingency Event
        model.c5w = Constraint(expr=model.q1w >= rePow["min"][0]) # Unit 1 Reactive Power Contingency Lower Limit
        model.c6w = Constraint(expr=model.q2w >= rePow["min"][1]) # Unit 2 Reactive Power Contingency Lower Limit
        model.c7w = Constraint(expr=model.q1w <= rePow["max"][0]) # Unit 1 Reactive Power Contingency Upper Limit
        model.c8w = Constraint(expr=model.q2w <= rePow["max"][1]) # Unit 2 Reactive Power Contingency Upper Limit

    # Voltage Angle Limits and Equalities
    if contingency != 0: # Contingency Event
        model.c9w = Constraint(expr=model.d1w >= voltage["ang"][0]) # Bus 1 Voltage Angle Contingency Lower Limit
        model.c10w = Constraint(expr=model.d1w <= voltage["ang"][1]) # Bus 1 Voltage Angle Contingency Upper Limit
        model.c11w = Constraint(expr=model.d2w == 0) # Bus 1 Voltage Angle Contingency Equality

    # Voltage Magnitude Limits
    if contingency != 0: # Contingency Event
        model.c12w = Constraint(expr=model.v1w >= voltage["magMin"][0]) # Bus 1 Voltage Magnitude Contingency Lower Limit
        model.c13w = Constraint(expr=model.v2w >= voltage["magMin"][1]) # Bus 2 Voltage Magnitude Contingency Lower Limit
        model.c14w = Constraint(expr=model.v1w <= voltage["magMax"][0]) # Bus 1 Voltage Magnitude Contingency Upper Limit
        model.c15w = Constraint(expr=model.v2w <= voltage["magMax"][1]) # Bus 2 Voltage Magnitude Contingency Upper Limit

    # Active Power Line Equalities
    if contingency == 1: # Line (12a) Out of Service
        model.c17w = Constraint(expr=model.p12bw == (model.v1w**2)*line["admMag"][1]*
                                     cos(line["admAng"][1])-model.v1w*model.v2w*line["admMag"][1]*
                                     cos(model.d1w-model.d2w-line["admAng"][1])) # Line (12b) Active Power Contingency
        model.c19w = Constraint(expr=model.p21bw == (model.v2w**2)*line["admMag"][1]*
                                     cos(line["admAng"][1])-model.v2w*model.v1w*line["admMag"][1]*
                                     cos(model.d2w-model.d1w-line["admAng"][1])) # Line (21b) Active Power Contingency
    elif contingency == 2: # Line (12b) Out of Service
        model.c16w = Constraint(expr=model.p12aw == (model.v1w**2)*line["admMag"][0]*
                                     cos(line["admAng"][0])-model.v1w*model.v2w*line["admMag"][0]*
                                     cos(model.d1w-model.d2w-line["admAng"][0])) # Line (12a) Active Power Contingency
        model.c18w = Constraint(expr=model.p21aw == (model.v2w**2)*line["admMag"][0]*
                                     cos(line["admAng"][0])-model.v2w*model.v1w*line["admMag"][0]*
                                     cos(model.d2w-model.d1w-line["admAng"][0])) # Line (21a) Active Power Contingency


    # Reactive Power Line Equalities
    if contingency == 1: # Line (12a) Out of Service
        model.c21w = Constraint(expr=model.q12bw == -(model.v1**2)*line["admMag"][1]*
                                     sin(line["admAng"][1])-model.v1*model.v2*line["admMag"][1]*
                                     sin(model.d1-model.d2-line["admAng"][1])) # Line (12b) Reactive Power Contingency
        model.c23w = Constraint(expr=model.q21bw == -(model.v2**2)*line["admMag"][1]*
                                     sin(line["admAng"][1])-model.v2*model.v1*line["admMag"][1]*
                                     sin(model.d2-model.d1-line["admAng"][1])) # Line (21b) Reactive Power Contingency
    elif contingency == 2: # Line (12b) Out of Service
        model.c20w = Constraint(expr=model.q12aw == -(model.v1**2)*line["admMag"][0]*
                                     sin(line["admAng"][0])-model.v1*model.v2*line["admMag"][0]*
                                     sin(model.d1-model.d2-line["admAng"][0])) # Line (12a) Reactive Power Contingency
        model.c22w = Constraint(expr=model.q21aw == -(model.v2**2)*line["admMag"][0]*
                                     sin(line["admAng"][0])-model.v2*model.v1*line["admMag"][0]*
                                     sin(model.d2-model.d1-line["admAng"][0])) # Line (21a) Reactive Power Contingency

    # Power Balance Formulations
    if contingency == 1: # Line (12a) Out of Service
        model.c24wb = Constraint(expr=model.p1w == model.p12bw+0.8) # Bus 1 Active Power Contingency Balance
        model.c25wb = Constraint(expr=model.p2w == model.p21bw+1.2) # Bus 2 Active Power Contingency Balance
        model.c26wb = Constraint(expr=model.q1w == model.q12bw+0.6) # Bus 1 Reactive Power Contingency Balance
        model.c27wb = Constraint(expr=model.q2w == model.q21bw+0.6) # Bus 2 Reactive Power Contingency Balance
    elif contingency == 2: # Line (12b) Out of Service
        model.c24wa = Constraint(expr=model.p1w == model.p12aw+0.8) # Bus 1 Active Power Contingency Balance
        model.c25wa = Constraint(expr=model.p2w == model.p21aw+1.2) # Bus 2 Active Power Contingency Balance
        model.c26wa = Constraint(expr=model.q1w == model.q12aw+0.6) # Bus 1 Reactive Power Contingency Balance
        model.c27wa = Constraint(expr=model.q2w == model.q21aw+0.6) # Bus 2 Reactive Power Contingency Balance

    # Line Capacity Limits
    if contingency == 1: # Line (12a) Out of Service
        model.c29w = Constraint(expr=line["maxApPow"][1]**2 >= model.p12bw**2 + model.q12bw**2) # Line (12b) Contingency Capacity Limit
        model.c31w = Constraint(expr=line["maxApPow"][1]**2 >= model.p21bw**2 + model.q21bw**2) # Line (21b) Contingency Capacity Limit
    elif contingency == 2: # Line (12b) Out of Service
        model.c28w = Constraint(expr=line["maxApPow"][0]**2 >= model.p12aw**2 + model.q12aw**2) # Line (12a) Contingency Capacity Limit
        model.c30w = Constraint(expr=line["maxApPow"][0]**2 >= model.p21aw**2 + model.q21aw**2) # Line (21a) Contingency Capacity Limit

    # Ramping Constraints
    if contingency != 0: # Contingency Event
        model.c32w = Constraint(expr=model.p1w-model.p1 <= acPow["ramp"][0]) # Unit 1 Active Power Ramp Limits
        model.c33w = Constraint(expr=model.p1-model.p1w <= acPow["ramp"][0]) # Unit 1 Active Power Ramp Limits
        model.c34w = Constraint(expr=model.p2w-model.p2 <= acPow["ramp"][1]) # Unit 2 Active Power Ramp Limits
        model.c35w = Constraint(expr=model.p2-model.p2w <= acPow["ramp"][1]) # Unit 2 Active Power Ramp Limits

    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=cost["cost"][0]*model.p1+cost["cost"][1]*model.p2, sense=minimize)

    # SOLVING
    model.pprint() # Printing Variable, Objective, and Constraint Declarations
    opt = SolverFactory("ipopt") # Declaring Solver
    results = opt.solve(model) # Calling Optimizer to Solve Model

    # PRINTING RESULTS
    # Headers
    print("\n\n{}".format("Objective Optimized".center(50, "-"))) # Printing Header
    print("\nContingency Event:\t\t", contingencyString[contingency]) # Printing Contingency

    # Printing Control Variables
    print("\nControl Variable Solutions:")
    print("p1:\t\t%5.3f" % model.p1())
    print("p2:\t\t%5.3f" % model.p2())
    print("q1:\t\t%5.3f" % model.q1())
    print("q2:\t\t%5.3f" % model.q2())
    print("d1:\t\t%5.3f" % model.d1())
    print("d2:\t\t%5.3f" % model.d2())
    print("v1:\t\t%5.3f" % model.v1())
    print("v2:\t\t%5.3f" % model.v2())

    # Printing State Variables
    print("\nState Solutions:")
    print("p12a:\t%5.3f" % model.p12a())
    print("p12b:\t%5.3f" % model.p12b())
    print("p21a:\t%5.3f" % model.p21a())
    print("p21b:\t%5.3f" % model.p21b())
    print("q12a:\t%5.3f" % model.q12a())
    print("q12b:\t%5.3f" % model.q12b())
    print("q21a:\t%5.3f" % model.q21a())
    print("q21b:\t%5.3f" % model.q21b())

    # Printing Contingency Control Variables
    if contingency != 0: # Contingency Event
        print("\nSCOPF Control Variable Solutions:")
        print("p1w:\t\t%5.3f" % model.p1w())
        print("p2w:\t\t%5.3f" % model.p2w())
        print("q1w:\t\t%5.3f" % model.q1w())
        print("q2w:\t\t%5.3f" % model.q2w())
        print("d1w:\t\t%5.3f" % model.d1w())
        print("d2w:\t\t%5.3f" % model.d2w())
        print("v1w:\t\t%5.3f" % model.v1w())
        print("v2w:\t\t%5.3f" % model.v2w())
        print("\nSCOPF State Solutions:")

    # Printing Contingency State Variables
    if contingency == 1: # Line (12a) Out of Service
        print("p12bw:\t%5.3f" % model.p12bw())
        print("p21bw:\t%5.3f" % model.p21bw())
        print("q12bw:\t%5.3f" % model.q12bw())
        print("q21bw:\t%5.3f" % model.q21bw())
    elif contingency == 2: # Line (12b) Out of Service
        print("p12aw:\t%5.3f" % model.p12aw())
        print("p21aw:\t%5.3f" % model.p21aw())
        print("q12aw:\t%5.3f" % model.q12aw())
        print("q21aw:\t%5.3f" % model.q21aw())

    # Printing Costs
    print("\nCost:", cost["cost"][0] * model.p1() + cost["cost"][1] * model.p2())
    if contingency != 0: # Contingency Event
        print("Contingency Cost:", cost["cost"][0] * model.p1w() + cost["cost"][1] * model.p2w())

if __name__ == "__main__":
    main()