# 230227 - ENEL 693 Assignment 2 - Security Constrained Optimal Power Flow.py - Austyn Nagribianko

import numpy as np
import pyomo
from pyomo.environ import*
from pyomo.opt import SolverFactory
import pandas as pd
import math
import itertools
from DataPrep import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():

    # SYSTEM SETTINGS
    print_schedule = False
    print_summary = True

    # Initializing Seasons, Days vectors
    # seasons = ['winter', 'spring', 'summer', 'fall']
    seasons = ['summer']
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # STATIC VARIABLES
    # Active Power Min and Max and Ramping Limits
    # power = {"min": [0.15, 0.2, 0], "max": [1.5, 1.5, 1.5], "rampDown": [0.2, 0.3, 0], "rampUp": [0.2, 0.3, 0],
             # "shutDown": [0.2, 0.3, 0], "startUp": [0.2, 0.3, 0]} # Original
    power = {"min": [0, 0.2, 0], "max": [1.5, 1.5, 1.5], "rampDown": [0.2, 0.3, 0], "rampUp": [0.2, 0.3, 0],
             "shutDown": [0.2, 0.3, 0], "startUp": [0.2, 0.3, 0]}

    # Unit Costs
    # cost = {"fixed": [1, 1], "variable": [10, 20, 0], "startUp": [5, 2, 0], "shutDown": [1, 1, 0]} # Original
    cost = {"fixed": [1, 1], "variable": [10, 20, 0], "startUp": [5, 2, 0], "shutDown": [1, 1, 0]}

    # Line Power Flow Limitations
    # line = {"maxApPow": [1, 1], "admMag": [1, 1]} # Original
    line = {"maxApPow": [3, 3], "admMag": [1, 1]} # Original


    # Reserve
    reserve = 0.1

    # Bus Voltage and Angle Limits
    busVoltage = {"angMin": [-math.pi], "angMax": [math.pi]}

    # Hour Zero Power Output and Generating Status
    p1_0 = 0.7
    p2_0 = 0.6
    u1_0 = 1
    u2_0 = 1
    u3_0 = 0  # *** fix

    df_annual = pd.DataFrame(columns=['Season', 'Day', 'Hour', 'U1', 'U2', 'U3', 'Load', 'Dispatch Cost'])
    for s in seasons:
        # Getting Seasonal Dataset
        hourly_season = getGenData(s)

        df_season = pd.DataFrame(columns=['Season', 'Day', 'Hour', 'U1', 'U2', 'U3', 'Load', 'Dispatch Cost'])
        for d in days:

            # Printing Study Details
            print('Season: ' + s + ', Day: ' + d)

            # GETTING DATA
            hourly_season_day = hourly_season[hourly_season["Day"] == d]
            hours = len(hourly_season_day)

            # MODEL
            model = ConcreteModel()
            model.dual = Suffix(direction=Suffix.IMPORT)
            # model.dual.pprint()

            # INDICES
            model.I = Set(initialize=range(hours))   # initializing model with indices

            # VARIABLES
            # Active Power Hourly Output
            model.p1 = Var(model.I, domain=NonNegativeReals) # Unit 1 Active Power Output
            model.p2 = Var(model.I, domain=NonNegativeReals) # Unit 2 Active Power Output
            # model.p3 = Var(gen["U3"], domain=NonNegativeReals) # Unit 3 Active Power Output

            # Unit Generating Status Binary Variables
            model.u1 = Var(model.I, domain=Binary) # Unit 1 Generating Status
            model.u2 = Var(model.I, domain=Binary) # Unit 2 Generating Status
            # model.u3 = Var(model.I, domain=Binary) # Unit 3 Generating Status

            # Unit Start-Up Status Binary Variables
            model.y1 = Var(model.I, domain=Binary) # Unit 1 Start-Up Status
            model.y2 = Var(model.I, domain=Binary) # Unit 2 Start-Up Status
            # model.y3 = Var(model.I, domain=Binary) # Unit 3 Start-Up Status

            # Unit Shut-Down Status Binary Variables
            model.z1 = Var(model.I, domain=Binary) # Unit 1 Shut-Down Status
            model.z2 = Var(model.I, domain=Binary) # Unit 2 Shut-Down Status
            # model.z3 = Var(model.I, domain=Binary) # Unit 3 Shut-Down Status

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
            # model.cons.add(expr=model.y3[0] - model.z3[0] == model.u3[0] - u3_0) # Unit 3 Start-Up Shut-Down Equality
            for i in range(1, hours):
                model.cons.add(expr=model.y1[i] - model.z1[i] == model.u1[i] - model.u1[i-1]) # Unit 1 Start-Up Shut-Down Equality
                model.cons.add(expr=model.y2[i] - model.z2[i] == model.u2[i] - model.u2[i-1]) # Unit 2 Start-Up Shut-Down Equality
                # model.cons.add(expr=model.y3[i] - model.z3[i] == model.u3[i] - model.u3[i-1]) # Unit 3 Start-Up Shut-Down Equality

            # Start-Up Shut-Down Limit
            for i in range(hours):
                model.cons.add(expr=model.y1[i] + model.z1[i] <= 1) # Unit 1 Start-Up Shut-Down Limit
                model.cons.add(expr=model.y2[i] + model.z2[i] <= 1) # Unit 2 Start-Up Shut-Down Limit
                # model.cons.add(expr=model.y3[i] + model.z3[i] <= 1) # Unit 2 Start-Up Shut-Down Limit

            # Active Power Limits
            for i in range(hours):
                model.cons.add(expr=model.p1[i] <= power["max"][0] * model.u1[i]) # Unit 1 Active Power Upper Limit
                model.cons.add(expr=model.p1[i] >= power["min"][0] * model.u1[i]) # Unit 1 Active Power Lower Limit
                model.cons.add(expr=model.p2[i] <= power["max"][1] * model.u2[i]) # Unit 2 Active Power Upper Limit
                model.cons.add(expr=model.p2[i] >= power["min"][1] * model.u2[i]) # Unit 2 Active Power Lower Limit
                # model.cons.add(expr=model.p3[i] <= power["max"][1] * model.u3[i]) # Unit 3 Active Power Upper Limit
                # model.cons.add(expr=model.p3[i] >= power["min"][1] * model.u3[i]) # Unit 3 Active Power Lower Limit

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
                model.cons.add(expr=hourly_season_day.iloc[i]["Load"] * (1 + reserve) <= model.u1[i] * power["max"][0] + model.u2[i] * power["max"][1]) # Hourly Reserve Requirement

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
                model.cons.add(expr=model.p1[i] + hourly_season_day.iloc[i]["U3"] == model.p13[i]) # Bus 1 Flow Balance
                model.cons.add(expr=model.p2[i] == model.p23[i]) # Bus 2 Flow Balance
                model.cons.add(expr=-hourly_season_day.iloc[i]["Load"] == model.p32[i] + model.p31[i]) # Bus 3 Flow Balance

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
            # model.pprint() # Printing Variable, Objective, and Constraint Declarations
            opt = SolverFactory("gurobi") # Declaring Solver
            results = opt.solve(model, tee=False) # Calling Optimizer to Solve Model

            # PRINTING RESULTS
            # Initilizing df
            df_day = pd.DataFrame(columns=['Season', 'Day', 'Hour', 'U1', 'U2', 'U3', 'Load', 'Dispatch Cost'])

            # Headers
            if print_schedule:
                print("\n\n{}".format("Objective Optimized".center(50, "-"))) # Printing Header
                print("\nControl Variable Solutions:")

            # Getting Dispatch Cost
            dispatch_cost = 0
            for i in range(hours):
                dispatch_cost += cost["fixed"][0] * model.u1[i]() + cost["variable"][0] * model.p1[i]() + cost["startUp"][0] * model.y1[i]() + \
                       cost["shutDown"][0] * model.z1[i]() + cost["fixed"][1] * model.u2[i]() + cost["variable"][1] * model.p2[i]() + \
                       cost["startUp"][1] * model.y2[i]() + cost["shutDown"][1] * model.z2[i]()

            # Loop Printing
            for i in range(hours):

                # Print Statements
                if print_schedule:
                    print("\nLoad\t\t\t\t\t\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, hourly_season_day.iloc[i]["Load"]))
                    print("Unit 1 Power - Thermal (p1)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p1[i]()))
                    print("Unit 2 Power - Thermal (p2)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p2[i]()))
                    print("Unit 3 Power - Solar (p3)\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, hourly_season_day.iloc[i]["U3"]))
                    # print("Unit Power Total Output\t\t\t\tHour %d\t\t%5.3f\t\tMW" % (i, model.p1[i]() + model.p2[i]() + hourly_winter_sunday.iloc[i]["U3"]))
                    if not print_summary:
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

                # Printing to Dataframe
                row = {'Season': s, 'Day': d, 'Hour': i, 'U1': model.p1[i](), 'U2': model.p2[i](), 'U3': hourly_season_day.iloc[i]["U3"], 'Load': hourly_season_day.iloc[i]["Load"], 'Dispatch Cost': dispatch_cost}
                df_day.loc[len(df_day)] = row

            # Printing Dispatch Cost
            if print_schedule:
                print("\nTotal Dispatch Cost\t\t\t\t\t\t\t\t%5.3f\t\t$/MWh" % dispatch_cost)

            # Appending df_day to df_season
            df_season = pd.concat([df_season, df_day])

        # Appending df_season to df_annual
        df_annual = pd.concat([df_annual, df_season])
        df_annual.to_csv("unit_committment_" + s + "_output.csv")

    # Generating plots
    day_key = {'Sunday': '2', 'Monday': '3', 'Tuesday': '4', 'Wednesday': '5', 'Thursday': '6', 'Friday': '7', 'Saturday': '8'}
    list = []
    for index, row in df_annual.iterrows():
        list.append(day_key[row['Day']])
    df_annual['Day'] = list
    df_annual['timestamp'] = '2022-01-' + df_annual["Day"].astype(str).str.zfill(2) + '-' + df_annual["Hour"].astype(str).str.zfill(2)
    df_annual["timestamp"] = pd.to_datetime(df_annual["timestamp"], format="%Y-%m-%d-%H")


    df_season = df_annual[df_annual["Season"] == s]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.set(xlabel='', ylabel='MW')
    df_annual
    ax1.plot(df_annual["timestamp"], df_annual.Load, color='g', label='Load')
    ax1.plot(df_season["timestamp"], df_season.U1, color='b', label='Unit 1 - Thermal')
    ax1.plot(df_season["timestamp"], df_season.U2, color='r', label='Unit 2 - Thermal')
    ax1.plot(df_season["timestamp"], df_season.U3, color='y', label='Unit 3 - Solar')
    ax1.legend()

    ax1.xaxis.set(
        major_locator=mdates.DayLocator(),
        major_formatter=mdates.DateFormatter("\n\n%A"),
        minor_locator=mdates.HourLocator((0, 12)),
        minor_formatter=mdates.DateFormatter("%H"),
    )
    plt.show()

if __name__ == "__main__":
    main()