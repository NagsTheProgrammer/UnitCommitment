# [YYYYMMDD] - [PROJECT NAME] - [FILENAME] - AUSTYN NAGRIBIANKO

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def main():
    # temp settings
    # season = "winter"
    # season = "fall"
    # season = "spring"
    season = "summer"

    # Setting filenames
    dirName = f"D:\\5. School\\5.0 Masters\\2.2 Second Semester\ENEL 693\Assignments\Assignment 3\\"
    fileName_U1 = "AESO_SH2_HOURLY_AVG_2022.csv" # Unit 1 data based off of Sheerness #2, 2022 hourly
    fileName_U2 = "AESO_KH3_HOURLY_AVG_2022.csv" # Unit 2 data based off of Keephills #3, 2022 hourly
    fileName_U3 = "AESO_CLR2_HOURLY_AVG_2022.csv" # Unit 3 data based off of Claresholm #2, 2022 hourly
    fileName_AIL = "AESO_AIL_HOURLY_AVG_2022.csv" # Alberta Interal Load, 2022 hourly

    # Reading .csv data
    df_U1 = pd.read_csv(dirName + fileName_U1, skiprows=4)
    df_U2 = pd.read_csv(dirName + fileName_U2, skiprows=4)
    df_U3 = pd.read_csv(dirName + fileName_U3, skiprows=4)
    df_AIL = pd.read_csv(dirName + fileName_AIL, skiprows=4)

    # Renaming column headers
    df_U1 = df_U1.rename(columns={'MW': 'UC1'})
    df_U2 = df_U2.rename(columns={'MW': 'UC2'})
    df_U3 = df_U3.rename(columns={'MW': 'UC3'})

    # Appending dataset
    df = pd.DataFrame()
    df_list = [df_U2.iloc[:, 1], df_U3.iloc[:, 1], df_AIL.iloc[:, 1]]
    df = pd.concat([df_U1] + df_list, axis=1)

    # Getting datetime objects
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], format='%m/%d/%Y %H:%M')
    df.insert(0, 'Date', df["Date/Time"].dt.date)
    df.insert(1, 'Time', df["Date/Time"].dt.time)
    df = df.drop(["Date/Time"], axis=1)

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

    if season == "winter":
        startDate = datetime(2022, 1, 1)
        endDate = datetime(2022, 2, 28)
    elif season == "spring":
        startDate = datetime(2022, 3, 1)
        endDate = datetime(2022, 5, 31)
    elif season == "summer":
        startDate = datetime(2022, 6, 1)
        endDate = datetime(2022, 8, 31)
    elif season == "fall":
        startDate = datetime(2022, 9, 1)
        endDate = datetime(2022, 11, 31)

    print(df)
    print(df["UC1"].mean())
    print(df["UC2"].mean())
    print(df["UC3"].mean())
    print(df["Load"].mean())

    # x = np.arange(len(df["Load"]))
    # plt.plot(x, df["UC3"])
    # plt.show()

if __name__ == "__main__":
    main()