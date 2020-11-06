import pandas as pd
import numpy as np

#load data and remove un-neccesary fields and make data column string due to date format incosistency in csv file
# data = pd.read_csv("2020-09-05-AccountStatement.csv",dtype={'DATE': str})
data = pd.read_csv("2020-09-27-AccountStatement.csv",dtype={'DATE': str})

# rename columns
data = data.rename(columns=data.iloc[2])
data = data.iloc[5:, 0:9]

#filter data based on BOT/SOLD, PUT/CALL
data = data[data["DESCRIPTION"].str.contains("BOT|SOLD", na = False)]
data = data[data["DESCRIPTION"].str.contains("PUT|CALL", na = False)]

#Remove unnecassary columns 
data = data.drop(columns=["REF #","TYPE","Misc Fees","Commissions & Fees","AMOUNT","BALANCE"])

#split data according to fields required and length of descrition column
try:
    data[["BOT/SOLD","Quantity","Strategy","Strategy1","Ticker","Total Stocks","Weekly/Monthly","Expiry Date","Month","Year","AM/PM","Strike Price","Call/Put","Premium","Trade"]] = data["DESCRIPTION"].str.split(" ", expand = True)
    data = data.drop("DESCRIPTION", axis=1)
except ValueError:
    data[["BOT/SOLD","Quantity","Strategy","Strategy1","Ticker","Total Stocks","Weekly/Monthly","Expiry Date","Month","Year","Strike Price","Call/Put","Premium","Trade"]] = data["DESCRIPTION"].str.split(" ", expand = True)
    data = data.drop("DESCRIPTION", axis=1)
    data["AM/PM"] = None
    data.columns = ["DATE","TIME","BOT/SOLD","Quantity","Strategy","Strategy1","Ticker","Total Stocks","Weekly/Monthly","Expiry Date","Month","Year","AM/PM","Strike Price","Call/Put","Premium","Trade"]
     
#remove unncessary values
data["BOT/SOLD"] = data["BOT/SOLD"].replace('WEB:API_TDAM:iPhone', np.nan)
data["BOT/SOLD"] = data["BOT/SOLD"].replace('tIP', np.nan)

#shift data to left 1 column to fill nan with BOT/SOLD data
mask = data["BOT/SOLD"].isna()
data.loc[mask, "BOT/SOLD":] = data.loc[mask, "BOT/SOLD":].shift(-1, axis=1)

#loop through strategy and strategy1 column to combine related values
for i in range(len(data)):
    if (data.iloc[i,5] == "CONDOR" or data.iloc[i,5] == "ROLL"):
        data.iloc[i,4] = data.iloc[i,4] + '-' + data.iloc[i,5]

#remove unnecessary values
data["Strategy1"] = data["Strategy1"].replace('CONDOR', np.nan)
data["Strategy1"] = data["Strategy1"].replace('ROLL', np.nan)
##################
mask = data["Strategy1"].isna()
data.loc[mask, "Strategy1":] = data.loc[mask, "Strategy1":].shift(-1, axis=1)

data["Strategy1"] = data["Strategy1"].replace("100", np.nan)

mask = data["Strategy1"].isna()
data.loc[mask, "Strategy":] = data.loc[mask, "Strategy":].shift(1, axis=1)

otherStrategy = data[data["Strategy"].str.contains("VERT-ROLL|DIAGONAL|CALENDER", na = False)]
data = data[~data["Strategy"].str.contains("VERT-ROLL|DIAGONAL|CALENDAR", na = False)]

mask = data["Trade"].isna()
data.loc[mask, "Strategy1":] = data.loc[mask, "Strategy1":].shift(1, axis=1)
data["Strategy"] = data["Strategy"].fillna("NAKED")

data["Call/Put"] = data["Call/Put"].fillna("-")

truthTable = data["Call/Put"].str.contains('@')
for i in range(len(truthTable)):
    if (truthTable.iloc[i] == True):
        if (data.iloc[i,15] == np.nan):
            data.iloc[i,15] = "-"

mask = data["Premium"].isna()
data.loc[mask, "Weekly/Monthly":] = data.loc[mask, "Weekly/Monthly":].shift(1, axis=1)

for i in range(len(data)):
    if (data.iloc[i,9] == "(Weeklys)"):
        data.iloc[i,8] = data.iloc[i,9]
        data.iloc[i,9] = np.nan
        
mask = data["Expiry Date"].isna()
data.loc[mask, "Expiry Date":] = data.loc[mask, "Expiry Date":].shift(-1, axis=1)        

truthTable = data["Premium"].str.contains('@')
for i in range(len(data)):
    if (truthTable.iloc[i,] == False):
        data.iloc[i,16] = data.iloc[i,15]
        data.iloc[i,15] = np.nan

mask = data["Premium"].isna()
data.loc[mask, "AM/PM":"Premium"] = data.loc[mask, "AM/PM":"Premium"].shift(1, axis=1)

for i in range(len(data)):
    if (data.iloc[i,11] == '[AM]'):
        data.iloc[i,12] = data.iloc[i,11]
        data.iloc[i,11] = np.nan

data["AM/PM"] = data["AM/PM"].fillna("[PM]")

mask = data["Year"].isna()
data.loc[mask, "Weekly/Monthly":"Year"] = data.loc[mask, "Weekly/Monthly":"Year"].shift(1, axis=1)

data["Weekly/Monthly"] = data["Weekly/Monthly"].fillna("Monthly")

data["Trade"] = data["Trade"].fillna("-")

for i in range(len(data)):
    data.iloc[i,9] = data.iloc[i,9] + '-' + data.iloc[i,10] + '-' + data.iloc[i,11]
        
data = data.drop(columns = ["Strategy1", "Total Stocks", "Month", "Year"])

data[["Junk","Premium"]] = data["Premium"].str.split("@", expand = True)
data = data.drop(columns = ["Junk"])

data["Call Buy"] = None
data["Call Sell"] = None
data["Put Sell"] = None
data["Put Buy"] = None

data["Temp"] = data["Strike Price"].str.contains("/", na = False)

for i in range(len(data)):
    if (data.iloc[i,2] == 'BOT'):        
        if (data.iloc[i,10] == 'CALL'):
            if(data.iloc[i,17] == False):
                data.iloc[i,13] = data.iloc[i,9]
                data.iloc[i,9] = None
        elif (data.iloc[i,10] == 'PUT'):
            if(data.iloc[i,17] == False):
                data.iloc[i,16] = data.iloc[i,9]
                data.iloc[i,9] = None
    elif (data.iloc[i,2] == 'SOLD'):
        if (data.iloc[i,10] == 'CALL'):
            if(data.iloc[i,17] == False):
                data.iloc[i,14] = data.iloc[i,9]
                data.iloc[i,9] = None
        elif (data.iloc[i,10] == 'PUT'):
            if(data.iloc[i,17] == False):
                data.iloc[i,15] = data.iloc[i,9]
                data.iloc[i,9] = None

data["Temp1"] = None
data["Temp2"] = None
data["Temp3"] = None
data["Temp4"] = None

data[["Temp1","Temp2","Temp3","Temp4"]] = data["Strike Price"].str.split("/", expand = True)

for i in range(len(data)):
    if (data.iloc[i,19] != None):
        if (data.iloc[i,20] == None and data.iloc[i,21] == None):
            if (data.iloc[i,10] == 'CALL'):
                data.iloc[i,13] = data.iloc[i,18]
                data.iloc[i,14] = data.iloc[i,19]
                data.iloc[i,18] = None
                data.iloc[i,19] = None
                data.iloc[i,9] = None

for i in range(len(data)):
    if (data.iloc[i,19] != None):
        if (data.iloc[i,20] == None and data.iloc[i,21] == None):
            if (data.iloc[i,10] == 'PUT'):
                data.iloc[i,16] = data.iloc[i,18]
                data.iloc[i,15] = data.iloc[i,19]
                data.iloc[i,18] = None
                data.iloc[i,19] = None
                data.iloc[i,9] = None

for i in range(len(data)):
    if (data.iloc[i,18] != None and data.iloc[i,19] != None and data.iloc[i,20] != None and data.iloc[i,21] != None):
        if (data.iloc[i,2] == 'BOT'):  
                data.iloc[i,13] = data.iloc[i,18]
                data.iloc[i,14] = data.iloc[i,19]
                data.iloc[i,16] = data.iloc[i,20]
                data.iloc[i,15] = data.iloc[i,21]
                data.iloc[i,18] = None
                data.iloc[i,19] = None
                data.iloc[i,20] = None
                data.iloc[i,21] = None
                data.iloc[i,9] = None
        if (data.iloc[i,2] == 'SOLD'):  
                data.iloc[i,13] = data.iloc[i,19]
                data.iloc[i,14] = data.iloc[i,18]
                data.iloc[i,16] = data.iloc[i,21]
                data.iloc[i,15] = data.iloc[i,20]
                data.iloc[i,18] = None
                data.iloc[i,19] = None
                data.iloc[i,20] = None
                data.iloc[i,21] = None
                data.iloc[i,9] = None

data = data.drop(columns = ["Temp","Temp1","Temp2","Temp3","Temp4"])

data = data.sort_values(by=['Strategy'])

vertical = data["Ticker"]

data.to_csv("options.csv")

data["Call + Premium"] = None
data["Put - Premium"] = None


# for i in range(len(data)):
#     data.iloc[i,17] = float(data.iloc[i,13]) + float(data.iloc[i,11])
#     data.iloc[i,18] = float(data.iloc[i,16]) - float(data.iloc[i,11])





        
        


                