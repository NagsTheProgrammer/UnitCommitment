# 230328 - ENEL 693 Assignment 3 - DataPrep.py - AUSTYN NAGRIBIANKO

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from datetime import datetime

def getGenData(season):
# def main():

    # temp settings
    season = "winter"
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

    # Renaming column headers
    df_U1 = df_U1.rename(columns={'MW': 'UC1'})
    df_U2 = df_U2.rename(columns={'MW': 'UC2'})
    df_U3 = df_U3.rename(columns={'MW': 'UC3'})

    # Appending dataset
    # for i in range(len(df_AIL["Date/Time"])):
    #     if df_AIL["Date/Time"][i] != df_U1["Date/Time"][i]:
    #         print(df_AIL["Date/Time"][i])

    df = pd.DataFrame()
    df_list = [df_U2.iloc[:, 1], df_U3.iloc[:, 1], df_AIL.iloc[:, 1]]
    df = pd.concat([df_U1] + df_list, axis=1)

    # Getting datetime objects
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], format='%m/%d/%Y %H:%M')
    df.insert(1, 'Day', df['Date/Time'].dt.dayofweek)
    # df.insert(0, 'Date', df["Date/Time"].dt.strftime('%m/%d/%Y'))
    # df.insert(1, 'Time', pd.to_datetime(df["Date/Time"].dt.time, format='%H:%M'))
    # df = df.drop(["Date/Time"], axis=1)
    df.set_index("Date/Time", inplace=True)

    # Filling NAN with 0
    df = df.fillna(0)

    # Min-Max Normalizing
    df["Load"] = df["Load"]/(df["Load"].max())
    df["UC1"] = (df["UC1"] - df["UC1"].min()) / (df["UC1"].max() - df["UC1"].min())
    df["UC2"] = (df["UC2"] - df["UC2"].min()) / (df["UC2"].max() - df["UC2"].min())
    df["UC3"] = (df["UC3"] - df["UC3"].min()) / (df["UC3"].max() - df["UC3"].min())

    # Scaling
    df["Load"] = df["Load"].apply(lambda x: x*2)
    df["UC1"] = df["UC1"].apply(lambda x: x*1.5)
    df["UC2"] = df["UC2"].apply(lambda x: x*1.5)
    df["UC3"] = df["UC3"].apply(lambda x: x*1.5)

    # Setting seasons
    seasons = {
        "winter": ("2022-01-01", "2022-02-28"),
        "spring": ("2022-03-01", "2022-05-31"),
        "summer": ("2022-06-01", "2022-08-31"),
        "fall": ("2022-09-01", "2022-11-30")
    }

    startDate = pd.to_datetime(seasons[season][0])
    endDate = pd.to_datetime(seasons[season][1])
    df = df.loc[startDate:endDate]

    hourly_mean = df.groupby(lambda idx: (idx.strftime("%H"), idx.strftime("%A"))).mean()
    hourly_mean[['Hour', 'Day']] = pd.DataFrame(hourly_mean.index.tolist(), index=hourly_mean.index)
    hourly_mean = hourly_mean.reset_index(drop=True)
    cols = hourly_mean.columns.tolist()
    cols = cols[:1] + cols[-1:] + cols[4:5] + cols[1:-2]
    hourly_mean = hourly_mean[cols]
    # hourly_mean = hourly_mean[hourly_mean["Day"] == 'Sunday']
    # print(hourly_mean)

    return hourly_mean

# if __name__ == "__main__":
#     main()