# 230328 - ENEL 693 Assignment 3 - DataPrep.py - AUSTYN NAGRIBIANKO

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from datetime import datetime

def getGenData(season):
# def main():

    # temp settings
    # season = "winter"
    # season = "fall"
    # season = "spring"
    # season = "summer"

    # Setting filenames
    # dirName = r"D:\\5. School\\5.0 Masters\\2.2 Second Semester\ENEL 693\Assignments\Assignment 3\\"
    dirName = r"C:\Users\Sumedha\Documents\GitHub\UnitCommitment\\"
    fileName_U1 = "AESO_SH2_HOURLY_AVG_2022.csv" # Unit 1 data based off of Sheerness #2, 2022 hourly
    fileName_U2 = "AESO_KH3_HOURLY_AVG_2022.csv" # Unit 2 data based off of Keephills #3, 2022 hourly
    fileName_U3 = "AESO_CLR2_HOURLY_AVG_2022.csv" # Unit 3 data based off of Claresholm #2, 2022 hourly
    fileName_AIL = "AESO_AIL_HOURLY_AVG_2022.csv" # Alberta Interal Load, 2022 hourly

    # Reading .csv data
    df_U1 = pd.read_csv(dirName + fileName_U1, skiprows=4)
    df_U2 = pd.read_csv(dirName + fileName_U2, skiprows=4)
    df_U3 = pd.read_csv(dirName + fileName_U3, skiprows=4)
    df_AIL = pd.read_csv(dirName + fileName_AIL, skiprows=4)
    df_AIL = df_AIL.iloc[:-4,:]

    # Solar Curtailment
    # Min Thermal Generation Issue
    ### write this so that the minimum difference between load and solar is at least 0.2, count # of times it needs to be clipped, return
    ### df_U3.clip(0, num)
    # Line Overloading
    # harder to implement... maybe put this together by just increasing line pow and mention in suggestions

    # Renaming column headers
    df_U1 = df_U1.rename(columns={'MW': 'U1'})
    df_U2 = df_U2.rename(columns={'MW': 'U2'})
    df_U3 = df_U3.rename(columns={'MW': 'U3'})

    # Concatenating df's
    df = pd.DataFrame()
    df_list = [df_U2.iloc[:, 1], df_U3.iloc[:, 1], df_AIL.iloc[:, 1]]
    df = pd.concat([df_U1] + df_list, axis=1)

    # Getting datetime objects
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], format='%m/%d/%Y %H:%M')
    df.insert(1, 'Day', df['Date/Time'].dt.dayofweek)
    df.set_index("Date/Time", inplace=True)

    # Filling NAN with 0
    df = df.fillna(0)

    # Min-Max Normalizing
    df["Load"] = df["Load"]/(df["Load"].max())
    df["U1"] = (df["U1"] - df["U1"].min()) / (df["U1"].max() - df["U1"].min())
    df["U2"] = (df["U2"] - df["U2"].min()) / (df["U2"].max() - df["U2"].min())
    df["U3"] = (df["U3"] - df["U3"].min()) / (df["U3"].max() - df["U3"].min())

    # Scaling
    df["Load"] = df["Load"].apply(lambda x: x*2)
    df["U1"] = df["U1"].apply(lambda x: x*1.5)
    df["U2"] = df["U2"].apply(lambda x: x*1.5)
    df["U3"] = df["U3"].apply(lambda x: x*1.5)

    # Setting seasons
    seasons = {
        "winter": ("2022-01-01", "2022-03-01"),
        "spring": ("2022-03-01", "2022-06-01"),
        "summer": ("2022-06-01", "2022-09-01"),
        "fall": ("2022-09-01", "2022-12-01")
    }

    startDate = pd.to_datetime(seasons[season][0])
    endDate = pd.to_datetime(seasons[season][1])
    df = df.loc[startDate:endDate] # *** append december
    df = df[:-1]

    # hourly_mean = pd.DataFrame(columns={'Day', 'Hour', 'Load', 'U1', 'U2', 'U3'})
    # for t in range(24):
    #     for d in range(7):
    #         df = df.between_time(str(t).zfill(2) + ':00', str(t).zfill(2) + ':59')
    #         df = df[df['Day'] == d]
    #         row = {'Day': }
    #         hourly_mean.loc[]

    hourly_mean = df.groupby(lambda idx: (idx.strftime("%H"), idx.strftime("%A"))).mean()
    hourly_mean[['Hour', 'Day']] = pd.DataFrame(hourly_mean.index.tolist(), index=hourly_mean.index)
    hourly_mean = hourly_mean.reset_index(drop=True)
    cols = hourly_mean.columns.tolist()
    cols = cols[:1] + cols[-1:] + cols[4:5] + cols[1:-2]
    hourly_mean = hourly_mean[cols]

    # hourly_mean.to_csv("hourly_mean_" + str(season) + "_output.csv")

    return hourly_mean

# if __name__ == "__main__":
#     main()