# 230227 - ENEL 693 Assignment 2 - Security Constrained Optimal Power Flow.py - Austyn Nagribianko

import numpy as np
import pyomo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import math
import gnuplotpy as gp


def main():
    # STATIC VARIABLES
    # Active Power Min and Max and Ramping Limits
    power = {"min": [0.15, 0.2], "max": [1.5, 1.5], "rampDown": [0.2, 0.3], "rampUp": [0.2, 0.3],
             "shutDown": [0.2, 0.3], "startUp": [0.2, 0.3]}
    # Unit Costs
    cost = {"fixed": [3, 1], "variable": [10, 20], "startUp": [5, 2], "shutDown": [1, 1]}
    # Line Power Flow Limitations
    line = {"maxApPow": [1, 1], "admMag": [1, 1]}
    # Hourly Load and Reserve for Hours [1, 2, 3, 4]
    demand = {"load": [1, 0.9, 1.3, 1.5], "reserve": [0.1, 0.09, 0.13, 0.15]}
    # Bus Voltage and Angle Limits
    busVoltage = {"magMin": [0.95], "magMax": [1.1], "angMin": [-math.pi], "angMax": [math.pi]}
    # Hour Zero Power Output and Generating Status
    p1_0 = 0.7
    p2_0 = 0.6
    u1_0 = 1
    u2_0 = 1

    # MODEL
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    model.dual.pprint()

    # VARIABLES
    # Active Power Hourly Output
    model.p1_1 = Var(within=NonNegativeReals)  # Unit 1 Active Power Output - Hour 1
    model.p2_1 = Var(within=NonNegativeReals)  # Unit 2 Active Power Output - Hour 1

    model.p1_2 = Var(within=NonNegativeReals)  # Unit 1 Active Power Output - Hour 2
    model.p2_2 = Var(within=NonNegativeReals)  # Unit 2 Active Power Output - Hour 2

    model.p1_3 = Var(within=NonNegativeReals)  # Unit 1 Active Power Output - Hour 3
    model.p2_3 = Var(within=NonNegativeReals)  # Unit 2 Active Power Output - Hour 3

    model.p1_4 = Var(within=NonNegativeReals)  # Unit 1 Active Power Output - Hour 4
    model.p2_4 = Var(within=NonNegativeReals)  # Unit 2 Active Power Output - Hour 4

    # Unit Generating Status Binary Variables
    model.u1_1 = Var(domain=Binary)  # Unit 1 Generating Status - Hour 1
    model.u2_1 = Var(domain=Binary)  # Unit 2 Generating Status - Hour 1

    model.u1_2 = Var(domain=Binary)  # Unit 1 Generating Status - Hour 2
    model.u2_2 = Var(domain=Binary)  # Unit 2 Generating Status - Hour 2

    model.u1_3 = Var(domain=Binary)  # Unit 1 Generating Status - Hour 3
    model.u2_3 = Var(domain=Binary)  # Unit 2 Generating Status - Hour 3

    model.u1_4 = Var(domain=Binary)  # Unit 1 Generating Status - Hour 4
    model.u2_4 = Var(domain=Binary)  # Unit 2 Generating Status - Hour 4

    # Unit Start-Up Status Binary Variables
    model.y1_1 = Var(domain=Binary)  # Unit 1 Start-Up Status - Hour 1
    model.y2_1 = Var(domain=Binary)  # Unit 2 Start-Up Status - Hour 1

    model.y1_2 = Var(domain=Binary)  # Unit 1 Start-Up Status - Hour 2
    model.y2_2 = Var(domain=Binary)  # Unit 2 Start-Up Status - Hour 2

    model.y1_3 = Var(domain=Binary)  # Unit 1 Start-Up Status - Hour 3
    model.y2_3 = Var(domain=Binary)  # Unit 2 Start-Up Status - Hour 3

    model.y1_4 = Var(domain=Binary)  # Unit 1 Start-Up Status - Hour 4
    model.y2_4 = Var(domain=Binary)  # Unit 2 Start-Up Status - Hour 4

    # Unit Shut-Down Status Binary Variables
    model.z1_1 = Var(domain=Binary)  # Unit 1 Shut-Down Status - Hour 1
    model.z2_1 = Var(domain=Binary)  # Unit 2 Shut-Down Status - Hour 1

    model.z1_2 = Var(domain=Binary)  # Unit 1 Shut-Down Status - Hour 2
    model.z2_2 = Var(domain=Binary)  # Unit 2 Shut-Down Status - Hour 2

    model.z1_3 = Var(domain=Binary)  # Unit 1 Shut-Down Status - Hour 3
    model.z2_3 = Var(domain=Binary)  # Unit 2 Shut-Down Status - Hour 3

    model.z1_4 = Var(domain=Binary)  # Unit 1 Shut-Down Status - Hour 4
    model.z2_4 = Var(domain=Binary)  # Unit 2 Shut-Down Status - Hour 4

    # Bus Voltage Angles
    model.d1_1 = Var(within=Reals)  # Bus 1 Voltage Angle - Hour 1
    model.d2_1 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 1
    model.d3_1 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 1

    model.d1_2 = Var(within=Reals)  # Bus 1 Voltage Angle - Hour 2
    model.d2_2 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 2
    model.d3_2 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 2

    model.d1_3 = Var(within=Reals)  # Bus 1 Voltage Angle - Hour 3
    model.d2_3 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 3
    model.d3_3 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 3

    model.d1_4 = Var(within=Reals)  # Bus 1 Voltage Angle - Hour 4
    model.d2_4 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 4
    model.d3_4 = Var(within=Reals)  # Bus 2 Voltage Angle - Hour 4

    # Line Flows
    model.p13_1 = Var(within=Reals)  # Line 13 Line Flow - Hour 1
    model.p31_1 = Var(within=Reals)  # Line 31 Line Flow - Hour 1
    model.p23_1 = Var(within=Reals)  # Line 23 Line Flow - Hour 1
    model.p32_1 = Var(within=Reals)  # Line 32 Line Flow - Hour 1

    model.p13_2 = Var(within=Reals)  # Line 13 Line Flow - Hour 2
    model.p31_2 = Var(within=Reals)  # Line 31 Line Flow - Hour 2
    model.p23_2 = Var(within=Reals)  # Line 23 Line Flow - Hour 2
    model.p32_2 = Var(within=Reals)  # Line 32 Line Flow - Hour 2

    model.p13_3 = Var(within=Reals)  # Line 13 Line Flow - Hour 3
    model.p31_3 = Var(within=Reals)  # Line 31 Line Flow - Hour 3
    model.p23_3 = Var(within=Reals)  # Line 23 Line Flow - Hour 3
    model.p32_3 = Var(within=Reals)  # Line 32 Line Flow - Hour 3

    model.p13_4 = Var(within=Reals)  # Line 13 Line Flow - Hour 4
    model.p31_4 = Var(within=Reals)  # Line 31 Line Flow - Hour 4
    model.p23_4 = Var(within=Reals)  # Line 23 Line Flow - Hour 4
    model.p32_4 = Var(within=Reals)  # Line 32 Line Flow - Hour 4

    # UNIT COMMITMENT CONSTRAINTS
    # Start-Up Shut-Down Equality
    model.c1a = Constraint(expr=model.y1_1 - model.z1_1 == model.u1_1 - u1_0)  # Unit 1 Start-Up Shut-Down - Hour 1
    model.c2a = Constraint(expr=model.y2_1 - model.z2_1 == model.u2_1 - u2_0)  # Unit 2 Start-Up Shut-Down - Hour 1

    model.c1b = Constraint(
        expr=model.y1_2 - model.z1_2 == model.u1_2 - model.u1_1)  # Unit 1 Start-Up Shut-Down - Hour 2
    model.c2b = Constraint(
        expr=model.y2_2 - model.z2_2 == model.u2_2 - model.u2_1)  # Unit 2 Start-Up Shut-Down - Hour 2

    model.c1c = Constraint(
        expr=model.y1_3 - model.z1_3 == model.u1_3 - model.u1_2)  # Unit 1 Start-Up Shut-Down - Hour 3
    model.c2c = Constraint(
        expr=model.y2_3 - model.z2_3 == model.u2_3 - model.u2_2)  # Unit 2 Start-Up Shut-Down - Hour 3

    model.c1d = Constraint(
        expr=model.y1_4 - model.z1_4 == model.u1_4 - model.u1_3)  # Unit 1 Start-Up Shut-Down - Hour 4
    model.c2d = Constraint(
        expr=model.y2_4 - model.z2_4 == model.u2_4 - model.u2_3)  # Unit 2 Start-Up Shut-Down - Hour 4

    model.c3a = Constraint(expr=model.y1_1 + model.z1_1 <= 1)  # Unit 1 Start-Up Shut-Down Limit - Hour 1
    model.c4a = Constraint(expr=model.y2_1 + model.z2_1 <= 1)  # Unit 2 Start-Up Shut-Down Limit - Hour 1

    model.c3b = Constraint(expr=model.y1_2 + model.z1_2 <= 1)  # Unit 1 Start-Up Shut-Down Limit - Hour 2
    model.c4b = Constraint(expr=model.y2_2 + model.z2_2 <= 1)  # Unit 2 Start-Up Shut-Down Limit - Hour 2

    model.c3c = Constraint(expr=model.y1_3 + model.z1_3 <= 1)  # Unit 1 Start-Up Shut-Down Limit - Hour 3
    model.c4c = Constraint(expr=model.y2_3 + model.z2_3 <= 1)  # Unit 2 Start-Up Shut-Down Limit - Hour 3

    model.c3d = Constraint(expr=model.y1_4 + model.z1_4 <= 1)  # Unit 1 Start-Up Shut-Down Limit - Hour 4
    model.c4d = Constraint(expr=model.y2_4 + model.z2_4 <= 1)  # Unit 2 Start-Up Shut-Down Limit - Hour 4

    # Active Power Limits
    model.c5a = Constraint(expr=model.p1_1 <= power["max"][0] * model.u1_1)  # Unit 1 Active Power Upper Limit - Hour 1
    model.c6a = Constraint(expr=model.p1_1 >= power["min"][0] * model.u1_1)  # Unit 1 Active Power Lower Limit - Hour 1
    model.c7a = Constraint(expr=model.p2_1 <= power["max"][1] * model.u2_1)  # Unit 2 Active Power Upper Limit - Hour 1
    model.c8a = Constraint(expr=model.p2_1 >= power["min"][1] * model.u2_1)  # Unit 2 Active Power Lower Limit - Hour 1

    model.c5b = Constraint(expr=model.p1_2 <= power["max"][0] * model.u1_2)  # Unit 1 Active Power Upper Limit - Hour 2
    model.c6b = Constraint(expr=model.p1_2 >= power["min"][0] * model.u1_2)  # Unit 1 Active Power Lower Limit - Hour 2
    model.c7b = Constraint(expr=model.p2_2 <= power["max"][1] * model.u2_2)  # Unit 2 Active Power Upper Limit - Hour 2
    model.c8b = Constraint(expr=model.p2_2 >= power["min"][1] * model.u2_2)  # Unit 2 Active Power Lower Limit - Hour 2

    model.c5c = Constraint(expr=model.p1_3 <= power["max"][0] * model.u1_3)  # Unit 1 Active Power Upper Limit - Hour 3
    model.c6c = Constraint(expr=model.p1_3 >= power["min"][0] * model.u1_3)  # Unit 1 Active Power Lower Limit - Hour 3
    model.c7c = Constraint(expr=model.p2_3 <= power["max"][1] * model.u2_3)  # Unit 2 Active Power Upper Limit - Hour 3
    model.c8c = Constraint(expr=model.p2_3 >= power["min"][1] * model.u2_3)  # Unit 2 Active Power Lower Limit - Hour 3

    model.c5d = Constraint(expr=model.p1_4 <= power["max"][0] * model.u1_4)  # Unit 1 Active Power Upper Limit - Hour 4
    model.c6d = Constraint(expr=model.p1_4 >= power["min"][0] * model.u1_4)  # Unit 1 Active Power Lower Limit - Hour 4
    model.c7d = Constraint(expr=model.p2_4 <= power["max"][1] * model.u2_4)  # Unit 2 Active Power Upper Limit - Hour 4
    model.c8d = Constraint(expr=model.p2_4 >= power["min"][1] * model.u2_4)  # Unit 2 Active Power Lower Limit - Hour 4

    # Ramp Up Limits
    model.c9a = Constraint(expr=model.p1_1 - p1_0 <= power["rampUp"][0] * u1_0 +
                                power["startUp"][0] * model.y1_1)  # Unit 1 Ramp-Up Limits - Hour 1
    model.c10a = Constraint(expr=model.p2_1 - p2_0 <= power["rampUp"][1] * u2_0 +
                                 power["startUp"][1] * model.y2_1)  # Unit 2 Ramp-Up Limits - Hour 1

    model.c9b = Constraint(expr=model.p1_2 - model.p1_1 <= power["rampUp"][0] * model.u1_1 +
                                power["startUp"][0] * model.y1_2)  # Unit 1 Ramp-Up Limits - Hour 2
    model.c10b = Constraint(expr=model.p2_2 - model.p2_1 <= power["rampUp"][1] * model.u2_1 +
                                 power["startUp"][1] * model.y2_2)  # Unit 2 Ramp-Up Limits - Hour 2

    model.c9c = Constraint(expr=model.p1_3 - model.p1_2 <= power["rampUp"][0] * model.u1_2 +
                                power["startUp"][0] * model.y1_3)  # Unit 1 Ramp-Up Limits - Hour 3
    model.c10c = Constraint(expr=model.p2_3 - model.p2_2 <= power["rampUp"][1] * model.u2_2 +
                                 power["startUp"][1] * model.y2_3)  # Unit 2 Ramp-Up Limits - Hour 3

    model.c9d = Constraint(expr=model.p1_4 - model.p1_3 <= power["rampUp"][0] * model.u1_3 +
                                power["startUp"][0] * model.y1_4)  # Unit 1 Ramp-Up Limits - Hour 4
    model.c10d = Constraint(expr=model.p2_4 - model.p2_3 <= power["rampUp"][1] * model.u2_3 +
                                 power["startUp"][1] * model.y2_4)  # Unit 2 Ramp-Up Limits - Hour 4

    # Ramp Down Limits
    model.c11a = Constraint(expr=p1_0 - model.p1_1 <= power["rampDown"][0] * model.u1_1 +
                                 power["shutDown"][0] * model.z1_1)  # Unit 1 Ramp-Down Limits - Hour 1
    model.c12a = Constraint(expr=p2_0 - model.p2_1 <= power["rampDown"][1] * model.u2_1 +
                                 power["shutDown"][1] * model.z2_1)  # Unit 2 Ramp-Down Limits - Hour 1

    model.c11b = Constraint(expr=model.p1_1 - model.p1_2 <= power["rampDown"][0] * model.u1_2 +
                                 power["shutDown"][0] * model.z1_2)  # Unit 1 Ramp-Down Limits - Hour 2
    model.c12b = Constraint(expr=model.p2_1 - model.p2_2 <= power["rampDown"][1] * model.u2_2 +
                                 power["shutDown"][1] * model.z2_2)  # Unit 2 Ramp-Down Limits - Hour 2

    model.c11c = Constraint(expr=model.p1_2 - model.p1_3 <= power["rampDown"][0] * model.u1_3 +
                                 power["shutDown"][0] * model.z1_3)  # Unit 1 Ramp-Down Limits - Hour 3
    model.c12c = Constraint(expr=model.p2_2 - model.p2_3 <= power["rampDown"][1] * model.u2_3 +
                                 power["shutDown"][1] * model.z2_3)  # Unit 2 Ramp-Down Limits - Hour 3

    model.c11d = Constraint(expr=model.p1_3 - model.p1_4 <= power["rampDown"][0] * model.u1_4 +
                                 power["shutDown"][0] * model.z1_4)  # Unit 1 Ramp-Down Limits - Hour 4
    model.c12d = Constraint(expr=model.p2_3 - model.p2_4 <= power["rampDown"][1] * model.u2_4 +
                                 power["shutDown"][1] * model.z2_4)  # Unit 2 Ramp-Down Limits - Hour 4

    # Hourly Reserve Requirements
    model.c14a = Constraint(
        expr=demand["load"][0] + demand["reserve"][0] <= model.u1_1 * power["max"][0] + model.u2_1 * power["max"][1])
    model.c14b = Constraint(
        expr=demand["load"][1] + demand["reserve"][1] <= model.u1_2 * power["max"][0] + model.u2_2 * power["max"][1])
    model.c14c = Constraint(
        expr=demand["load"][2] + demand["reserve"][2] <= model.u1_3 * power["max"][0] + model.u2_3 * power["max"][1])
    model.c14d = Constraint(
        expr=demand["load"][3] + demand["reserve"][3] <= model.u1_4 * power["max"][0] + model.u2_4 * power["max"][1])

    # Line Flows
    model.c15a = Constraint(
        expr=model.p13_1 == (model.d1_1 - model.d3_1) * line["admMag"][0])  # Line 13 Active Power - Hour 1
    model.c16a = Constraint(
        expr=model.p31_1 == (model.d3_1 - model.d1_1) * line["admMag"][0])  # Line 31 Active Power - Hour 1
    model.c17a = Constraint(
        expr=model.p23_1 == (model.d2_1 - model.d3_1) * line["admMag"][1])  # Line 23 Active Power - Hour 1
    model.c18a = Constraint(
        expr=model.p32_1 == (model.d3_1 - model.d2_1) * line["admMag"][1])  # Line 32 Active Power - Hour 1

    model.c15b = Constraint(
        expr=model.p13_2 == (model.d1_2 - model.d3_2) * line["admMag"][0])  # Line 13 Active Power - Hour 2
    model.c16b = Constraint(
        expr=model.p31_2 == (model.d3_2 - model.d1_2) * line["admMag"][0])  # Line 31 Active Power - Hour 2
    model.c17b = Constraint(
        expr=model.p23_2 == (model.d2_2 - model.d3_2) * line["admMag"][1])  # Line 23 Active Power - Hour 2
    model.c18b = Constraint(
        expr=model.p32_2 == (model.d3_2 - model.d2_2) * line["admMag"][1])  # Line 32 Active Power - Hour 2

    model.c15c = Constraint(
        expr=model.p13_3 == (model.d1_3 - model.d3_3) * line["admMag"][0])  # Line 13 Active Power - Hour 3
    model.c16c = Constraint(
        expr=model.p31_3 == (model.d3_3 - model.d1_3) * line["admMag"][0])  # Line 31 Active Power - Hour 3
    model.c17c = Constraint(
        expr=model.p23_3 == (model.d2_3 - model.d3_3) * line["admMag"][1])  # Line 23 Active Power - Hour 3
    model.c18c = Constraint(
        expr=model.p32_3 == (model.d3_3 - model.d2_3) * line["admMag"][1])  # Line 32 Active Power - Hour 3

    model.c15d = Constraint(
        expr=model.p13_4 == (model.d1_4 - model.d3_4) * line["admMag"][0])  # Line 13 Active Power - Hour 4
    model.c16d = Constraint(
        expr=model.p31_4 == (model.d3_4 - model.d1_4) * line["admMag"][0])  # Line 31 Active Power - Hour 4
    model.c17d = Constraint(
        expr=model.p23_4 == (model.d2_4 - model.d3_4) * line["admMag"][1])  # Line 23 Active Power - Hour 4
    model.c18d = Constraint(
        expr=model.p32_4 == (model.d3_4 - model.d2_4) * line["admMag"][1])  # Line 32 Active Power - Hour 4

    # Voltage Angle Limits
    model.c19a = Constraint(expr=model.d1_1 >= busVoltage["angMin"][0])  # Bus 1 Voltage Angle Lower Limit - Hour 1
    model.c20a = Constraint(expr=model.d1_1 <= busVoltage["angMax"][0])  # Bus 1 Voltage Angle Upper Limit - Hour 1
    model.c21a = Constraint(expr=model.d2_1 >= busVoltage["angMin"][0])  # Bus 2 Voltage Angle Lower Limit - Hour 1
    model.c22a = Constraint(expr=model.d2_1 <= busVoltage["angMax"][0])  # Bus 2 Voltage Angle Upper Limit - Hour 1
    model.c23a = Constraint(expr=model.d3_1 == 0)  # Bus 3 Voltage Angle Equality - Hour 1

    model.c19b = Constraint(expr=model.d1_2 >= busVoltage["angMin"][0])  # Bus 1 Voltage Angle Lower Limit - Hour 2
    model.c20b = Constraint(expr=model.d1_2 <= busVoltage["angMax"][0])  # Bus 1 Voltage Angle Upper Limit - Hour 2
    model.c21b = Constraint(expr=model.d2_2 >= busVoltage["angMin"][0])  # Bus 2 Voltage Angle Lower Limit - Hour 2
    model.c22b = Constraint(expr=model.d2_2 <= busVoltage["angMax"][0])  # Bus 2 Voltage Angle Upper Limit - Hour 2
    model.c23b = Constraint(expr=model.d3_2 == 0)  # Bus 3 Voltage Angle Equality - Hour 2

    model.c19c = Constraint(expr=model.d1_3 >= busVoltage["angMin"][0])  # Bus 1 Voltage Angle Lower Limit - Hour 3
    model.c20c = Constraint(expr=model.d1_3 <= busVoltage["angMax"][0])  # Bus 1 Voltage Angle Upper Limit - Hour 3
    model.c21c = Constraint(expr=model.d2_3 >= busVoltage["angMin"][0])  # Bus 2 Voltage Angle Lower Limit - Hour 3
    model.c22c = Constraint(expr=model.d2_3 <= busVoltage["angMax"][0])  # Bus 2 Voltage Angle Upper Limit - Hour 3
    model.c23c = Constraint(expr=model.d3_3 == 0)  # Bus 3 Voltage Angle Equality - Hour 3

    model.c19d = Constraint(expr=model.d1_4 >= busVoltage["angMin"][0])  # Bus 1 Voltage Angle Lower Limit - Hour 4
    model.c20d = Constraint(expr=model.d1_4 <= busVoltage["angMax"][0])  # Bus 1 Voltage Angle Upper Limit - Hour 4
    model.c21d = Constraint(expr=model.d2_4 >= busVoltage["angMin"][0])  # Bus 2 Voltage Angle Lower Limit - Hour 4
    model.c22d = Constraint(expr=model.d2_4 <= busVoltage["angMax"][0])  # Bus 2 Voltage Angle Upper Limit - Hour 4
    model.c23d = Constraint(expr=model.d3_4 == 0)  # Bus 3 Voltage Angle Equality - Hour 4

    # Line Flow Power Balance
    model.c24a = Constraint(expr=model.p1_1 == model.p13_1)  # Bus 1 Flow Balance - Hour 1
    model.c25a = Constraint(expr=model.p2_1 == model.p23_1)  # Bus 2 Flow Balance - Hour 1
    model.c26a = Constraint(expr=-demand["load"][0] == model.p32_1 + model.p31_1)  # Bus 3 Flow Balance - Hour 1

    model.c24b = Constraint(expr=model.p1_2 == model.p13_2)  # Bus 1 Flow Balance - Hour 2
    model.c25b = Constraint(expr=model.p2_2 == model.p23_2)  # Bus 2 Flow Balance - Hour 2
    model.c26b = Constraint(expr=-demand["load"][1] == model.p32_2 + model.p31_2)  # Bus 3 Flow Balance - Hour 2

    model.c24c = Constraint(expr=model.p1_3 == model.p13_3)  # Bus 1 Flow Balance - Hour 3
    model.c25c = Constraint(expr=model.p2_3 == model.p23_3)  # Bus 2 Flow Balance - Hour 3
    model.c26c = Constraint(expr=-demand["load"][2] == model.p32_3 + model.p31_3)  # Bus 3 Flow Balance - Hour 3

    model.c24d = Constraint(expr=model.p1_4 == model.p13_4)  # Bus 1 Flow Balance - Hour 4
    model.c25d = Constraint(expr=model.p2_4 == model.p23_4)  # Bus 2 Flow Balance - Hour 4
    model.c26d = Constraint(expr=-demand["load"][3] == model.p32_4 + model.p31_4)  # Bus 3 Flow Balance - Hour 4

    # Line Flow Limits
    model.c27a = Constraint(expr=model.p13_1 <= line["maxApPow"][0])  # Line 13 Line Limits - Hour 1
    model.c28a = Constraint(expr=model.p31_1 <= line["maxApPow"][0])  # Line 31 Line Limits - Hour 1
    model.c29a = Constraint(expr=model.p23_1 <= line["maxApPow"][1])  # Line 23 Line Limits - Hour 1
    model.c30a = Constraint(expr=model.p32_1 <= line["maxApPow"][1])  # Line 32 Line Limits - Hour 1

    model.c27b = Constraint(expr=model.p13_2 <= line["maxApPow"][0])  # Line 13 Line Limits - Hour 2
    model.c28b = Constraint(expr=model.p31_2 <= line["maxApPow"][0])  # Line 31 Line Limits - Hour 2
    model.c29b = Constraint(expr=model.p23_2 <= line["maxApPow"][1])  # Line 23 Line Limits - Hour 2
    model.c30b = Constraint(expr=model.p32_2 <= line["maxApPow"][1])  # Line 32 Line Limits - Hour 2

    model.c27c = Constraint(expr=model.p13_3 <= line["maxApPow"][0])  # Line 13 Line Limits - Hour 3
    model.c28c = Constraint(expr=model.p31_3 <= line["maxApPow"][0])  # Line 31 Line Limits - Hour 3
    model.c29c = Constraint(expr=model.p23_3 <= line["maxApPow"][1])  # Line 23 Line Limits - Hour 3
    model.c30c = Constraint(expr=model.p32_3 <= line["maxApPow"][1])  # Line 32 Line Limits - Hour 3

    model.c27d = Constraint(expr=model.p13_4 <= line["maxApPow"][0])  # Line 13 Line Limits - Hour 4
    model.c28d = Constraint(expr=model.p31_4 <= line["maxApPow"][0])  # Line 31 Line Limits - Hour 4
    model.c29d = Constraint(expr=model.p23_4 <= line["maxApPow"][1])  # Line 23 Line Limits - Hour 4
    model.c30d = Constraint(expr=model.p32_4 <= line["maxApPow"][1])  # Line 32 Line Limits - Hour 4

    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=
                          cost["fixed"][0] * model.u1_1 + cost["variable"][0] * model.p1_1 + cost["startUp"][
                              0] * model.y1_1 + cost["shutDown"][0] * model.z1_1 +
                          cost["fixed"][0] * model.u1_2 + cost["variable"][0] * model.p1_2 + cost["startUp"][
                              0] * model.y1_2 + cost["shutDown"][0] * model.z1_2 +
                          cost["fixed"][0] * model.u1_3 + cost["variable"][0] * model.p1_3 + cost["startUp"][
                              0] * model.y1_3 + cost["shutDown"][0] * model.z1_3 +
                          cost["fixed"][0] * model.u1_4 + cost["variable"][0] * model.p1_4 + cost["startUp"][
                              0] * model.y1_4 + cost["shutDown"][0] * model.z1_4 +
                          cost["fixed"][1] * model.u2_1 + cost["variable"][1] * model.p2_1 + cost["startUp"][
                              1] * model.y2_1 + cost["shutDown"][1] * model.z2_1 +
                          cost["fixed"][1] * model.u2_2 + cost["variable"][1] * model.p2_2 + cost["startUp"][
                              1] * model.y2_2 + cost["shutDown"][1] * model.z2_2 +
                          cost["fixed"][1] * model.u2_3 + cost["variable"][1] * model.p2_3 + cost["startUp"][
                              1] * model.y2_3 + cost["shutDown"][1] * model.z2_3 +
                          cost["fixed"][1] * model.u2_4 + cost["variable"][1] * model.p2_4 + cost["startUp"][
                              1] * model.y2_4 + cost["shutDown"][1] * model.z2_4)

    # SOLVING
    model.pprint()  # Printing Variable, Objective, and Constraint Declarations
    opt = SolverFactory("gurobi")  # Declaring Solver
    results = opt.solve(model)  # Calling Optimizer to Solve Model

    # PRINTING RESULTS
    # Headers
    print("\n\n{}".format("Objective Optimized".center(50, "-")))  # Printing Header

    # Printing Control Variables
    print("\nControl Variable Solutions:")
    print("\nLoad\t\t\t\t\t\tHour 1\t\t%5.3f\t\tMW" % demand["load"][0])
    print("Unit 1 Power (p1_1)\t\t\tHour 1\t\t%5.3f\t\tMW" % model.p1_1())
    print("Unit 2 Power (p2_1)\t\t\tHour 1\t\t%5.3f\t\tMW" % model.p2_1())
    print("Line 13 Flow (p13_1)\t\tHour 1\t\t%5.3f\t\tMW" % model.p13_1())
    print("Line 31 Flow (p31_1)\t\tHour 1\t\t%5.3f\t\tMW" % model.p31_1())
    print("Line 23 Flow (p23_1)\t\tHour 1\t\t%5.3f\t\tMW" % model.p23_1())
    print("Line 32 Flow (p32_1)\t\tHour 1\t\t%5.3f\t\tMW" % model.p32_1())
    print("Bus 1 Delta (d1_1)\t\t\tHour 1\t\t%5.3f\t\trad" % model.d1_1())
    print("Bus 2 Delta (d2_1)\t\t\tHour 1\t\t%5.3f\t\trad" % model.d2_1())
    print("Bus 3 Delta (d3_1)\t\t\tHour 1\t\t%5.3f\t\trad" % model.d3_1())
    print("Unit 1 Status (u1_1)\t\tHour 1\t\t%5.3f" % model.u1_1())
    print("Unit 2 Status (u2_1)\t\tHour 1\t\t%5.3f" % model.u2_1())
    print("Unit 1 Ramp-Up (y1_1)\t\tHour 1\t\t%5.3f" % model.y1_1())
    print("Unit 2 Ramp-Up (y2_1)\t\tHour 1\t\t%5.3f" % model.y2_1())
    print("Unit 1 Ramp-Down (z1_1)\t\tHour 1\t\t%5.3f" % model.z1_1())
    print("Unit 2 Ramp-Down (z2_1)\t\tHour 1\t\t%5.3f" % model.z2_1())

    print("\nLoad\t\t\t\t\t\tHour 2\t\t%5.3f\t\tMW" % demand["load"][1])
    print("Unit 1 Power (p1_2)\t\t\tHour 2\t\t%5.3f\t\tMW" % model.p1_2())
    print("Unit 2 Power (p2_2)\t\t\tHour 2\t\t%5.3f\t\tMW" % model.p2_2())
    print("Line 13 Flow (p13_2)\t\tHour 2\t\t%5.3f\t\tMW" % model.p13_2())
    print("Line 31 Flow (p31_2)\t\tHour 2\t\t%5.3f\t\tMW" % model.p31_2())
    print("Line 23 Flow (p23_2)\t\tHour 2\t\t%5.3f\t\tMW" % model.p23_2())
    print("Line 32 Flow (p32_2)\t\tHour 2\t\t%5.3f\t\tMW" % model.p32_2())
    print("Bus 1 Delta (d1_2)\t\t\tHour 2\t\t%5.3f\t\trad" % model.d1_2())
    print("Bus 2 Delta (d2_2)\t\t\tHour 2\t\t%5.3f\t\trad" % model.d2_2())
    print("Bus 3 Delta (d3_2)\t\t\tHour 2\t\t%5.3f\t\trad" % model.d3_2())
    print("Unit 1 Status (u1_2)\t\tHour 2\t\t%5.3f" % model.u1_2())
    print("Unit 2 Status (u2_2)\t\tHour 2\t\t%5.3f" % model.u2_2())
    print("Unit 1 Ramp-Up (y1_2)\t\tHour 2\t\t%5.3f" % model.y1_2())
    print("Unit 2 Ramp-Up (y2_2)\t\tHour 2\t\t%5.3f" % model.y2_2())
    print("Unit 1 Ramp-Down (z1_2)\t\tHour 2\t\t%5.3f" % model.z1_2())
    print("Unit 2 Ramp-Down (z2_2)\t\tHour 2\t\t%5.3f" % model.z2_2())

    print("\nLoad\t\t\t\t\t\tHour 3\t\t%5.3f\t\tMW" % demand["load"][2])
    print("Unit 1 Power (p1_3)\t\t\tHour 3\t\t%5.3f\t\tMW" % model.p1_3())
    print("Unit 2 Power (p2_3)\t\t\tHour 3\t\t%5.3f\t\tMW" % model.p2_3())
    print("Line 13 Flow (p13_3)\t\tHour 3\t\t%5.3f\t\tMW" % model.p13_3())
    print("Line 31 Flow (p31_3)\t\tHour 3\t\t%5.3f\t\tMW" % model.p31_3())
    print("Line 23 Flow (p23_3)\t\tHour 3\t\t%5.3f\t\tMW" % model.p23_3())
    print("Line 32 Flow (p32_3)\t\tHour 3\t\t%5.3f\t\tMW" % model.p32_3())
    print("Bus 1 Delta (d1_3)\t\t\tHour 3\t\t%5.3f\t\trad" % model.d1_3())
    print("Bus 2 Delta (d2_3)\t\t\tHour 3\t\t%5.3f\t\trad" % model.d2_3())
    print("Bus 3 Delta (d3_3)\t\t\tHour 3\t\t%5.3f\t\trad" % model.d3_3())
    print("Unit 1 Status (u1_3)\t\tHour 3\t\t%5.3f" % model.u1_3())
    print("Unit 2 Status (u2_3)\t\tHour 3\t\t%5.3f" % model.u2_3())
    print("Unit 1 Ramp-Up (y1_3)\t\tHour 3\t\t%5.3f" % model.y1_3())
    print("Unit 2 Ramp-Up (y2_3)\t\tHour 3\t\t%5.3f" % model.y2_3())
    print("Unit 1 Ramp-Down (z1_3)\t\tHour 3\t\t%5.3f" % model.z1_3())
    print("Unit 2 Ramp-Down (z2_3)\t\tHour 3\t\t%5.3f" % model.z2_3())

    print("\nLoad\t\t\t\t\t\tHour 4\t\t%5.3f\t\tMW" % demand["load"][3])
    print("Unit 1 Power (p1_4)\t\t\tHour 4\t\t%5.3f\t\tMW" % model.p1_4())
    print("Unit 2 Power (p2_4)\t\t\tHour 4\t\t%5.3f\t\tMW" % model.p2_4())
    print("Line 13 Flow (p13_4)\t\tHour 4\t\t%5.3f\t\tMW" % model.p13_4())
    print("Line 31 Flow (p31_4)\t\tHour 4\t\t%5.3f\t\tMW" % model.p31_4())
    print("Line 23 Flow (p23_4)\t\tHour 4\t\t%5.3f\t\tMW" % model.p23_4())
    print("Line 32 Flow (p32_4)\t\tHour 4\t\t%5.3f\t\tMW" % model.p32_4())
    print("Bus 1 Delta (d1_4)\t\t\tHour 4\t\t%5.3f\t\trad" % model.d1_4())
    print("Bus 2 Delta (d2_4)\t\t\tHour 4\t\t%5.3f\t\trad" % model.d2_4())
    print("Bus 3 Delta (d3_4)\t\t\tHour 4\t\t%5.3f\t\trad" % model.d3_4())
    print("Unit 1 Status (u1_4)\t\tHour 4\t\t%5.3f" % model.u1_4())
    print("Unit 2 Status (u2_4)\t\tHour 4\t\t%5.3f" % model.u2_4())
    print("Unit 1 Ramp-Up (y1_4)\t\tHour 4\t\t%5.3f" % model.y1_4())
    print("Unit 2 Ramp-Up (y2_4)\t\tHour 4\t\t%5.3f" % model.y2_4())
    print("Unit 1 Ramp-Down (z1_4)\t\tHour 4\t\t%5.3f" % model.z1_4())
    print("Unit 2 Ramp-Down (z2_1)\t\tHour 4\t\t%5.3f" % model.z2_4())

    # x = [0, 1, 2, 3, 4]
    # u1 = [u1_0, model.u1_1(), model.u1_2(), model.u1_3(), model.u1_4()]
    # u2 = [u2_0, model.u2_1(), model.u2_2(), model.u2_3(), model.u2_4()]
    #
    # gp.plot( (x, u1, {'legend': 'Unit 1'}),
    #          (x, u2, {'legend': 'Unit 2'}),
    #          # (x, demand["load"], {'legend': 'Load'}),
    #          _with = 'lines',
    #          terminal = 'dumb 80, 40',
    #          unset = 'grid')

    # Printing Costs
    solutionCost = cost["fixed"][0] * model.u1_1() + cost["variable"][0] * model.p1_1() + cost["startUp"][
        0] * model.y1_1() + \
                   cost["shutDown"][0] * model.z1_1() + cost["fixed"][0] * model.u1_2() + cost["variable"][
                       0] * model.p1_2() + \
                   cost["startUp"][0] * model.y1_2() + cost["shutDown"][0] * model.z1_2() + cost["fixed"][
                       0] * model.u1_3() + \
                   cost["variable"][0] * model.p1_3() + cost["startUp"][0] * model.y1_3() + cost["shutDown"][
                       0] * model.z1_3() + \
                   cost["fixed"][0] * model.u1_4() + cost["variable"][0] * model.p1_4() + cost["startUp"][
                       0] * model.y1_4() + \
                   cost["shutDown"][0] * model.z1_4() + cost["fixed"][1] * model.u2_1() + cost["variable"][
                       1] * model.p2_1() + \
                   cost["startUp"][1] * model.y2_1() + cost["shutDown"][1] * model.z2_1() + cost["fixed"][
                       1] * model.u2_2() + \
                   cost["variable"][1] * model.p2_2() + cost["startUp"][1] * model.y2_2() + cost["shutDown"][
                       1] * model.z2_2() + \
                   cost["fixed"][1] * model.u2_3() + cost["variable"][1] * model.p2_3() + cost["startUp"][
                       1] * model.y2_3() + \
                   cost["shutDown"][1] * model.z2_3() + cost["fixed"][1] * model.u2_4() + cost["variable"][
                       1] * model.p2_4() + \
                   cost["startUp"][1] * model.y2_4() + cost["shutDown"][1] * model.z2_4()
    print("\nSolution Cost:", solutionCost)


if __name__ == "__main__":
    main()