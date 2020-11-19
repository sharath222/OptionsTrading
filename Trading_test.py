import pandas as pd
import numpy as np
import pandas as pd
from datetime import timezone
from datetime import datetime

#load data and remove un-neccesary fields and make data column string due to date format incosistency in csv file
# data = pd.read_csv("2020-09-05-AccountStatement.csv",dtype={'DATE': str})
data = pd.read_csv("2020-09-05-AccountStatement.csv",dtype={'DATE': str})

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

data["Call + Premium"] = None
data["Put - Premium"] = None

data = data.sort_values(by=['Strategy'])

vertical = data[data["Strategy"].str.contains("VERTICAL", na = False)]

for i in range(len(vertical)):
    if(vertical.iloc[i,10] == "CALL"):
        vertical.iloc[i,17] = float(vertical.iloc[i,13]) + float(vertical.iloc[i,11])
    elif(vertical.iloc[i,10] == "PUT"):
        vertical.iloc[i,18] = float(vertical.iloc[i,16]) - float(vertical.iloc[i,11])
        
vertical["actual premium"] = None

# vertical["Profit/Loss"] = None

# vertical["actual Call + Premium"] = None
# vertical["actual Put - Premium"] = None
    
for i in range(len(vertical)):
    if(vertical.iloc[i,10] == "CALL"):
        ticker = vertical.iloc[i,5]
        expiry = datetime(2020,11,20)
        
        timestamp = int(expiry.replace(tzinfo=timezone.utc).timestamp())

        timestamp = str(timestamp)

        temp = pd.read_html("https://finance.yahoo.com/quote/"+ticker+"/options?date="+timestamp+"&p="+ticker+"&straddle=true") 
        
        temp = temp[0]
        
        temp.head
       
        call = vertical.iloc[i,13]
        
        for x in range(len(temp)):
            if (float(temp.iloc[x,5]) == float(call)):
                vertical.iloc[i,19] = temp.iloc[x,0]
    
    elif(vertical.iloc[i,10] == "PUT"):
        
        put = vertical.iloc[i,16]
        
        for x in range(len(temp)):
            if (float(temp.iloc[x,5]) == float(put)):
                vertical.iloc[i,19] = temp.iloc[x,0]

vertical["actual premium"] = vertical["actual premium"].fillna(0)
                
# for i in range(len(vertical)):
#     if(vertical.iloc[i,2] == "BOT"):
#         if(vertical.iloc[i,10] == "CALL"):
#             if(float(vertical.iloc[i,11]) > float(vertical.iloc[i,19])):
#                 vertical.iloc[i,20] = "Loss"
#             else:
#                 vertical.iloc[i,20] = "Profit"
#         else:
#             if(float(vertical.iloc[i,11]) > float(vertical.iloc[i,19])):
#                 vertical.iloc[i,20] = "Profit"
#             else:
#                 vertical.iloc[i,20] = "Loss"
    
#     if(vertical.iloc[i,2] == "SOLD"):
#         if(vertical.iloc[i,10] == "CALL"):
#             if(float(vertical.iloc[i,11]) < float(vertical.iloc[i,19])):
#                 vertical.iloc[i,20] = "Loss"
#             else:
#                 vertical.iloc[i,20] = "Profit"
#         else:
#             if(float(vertical.iloc[i,11]) < float(vertical.iloc[i,19])):
#                 vertical.iloc[i,20] = "Profit"
#             else:
#                 vertical.iloc[i,20] = "Loss"
                
vertical[["Temp1","Temp2"]] = vertical["Quantity"].str.split("+", expand = True)
vertical[["Temp1","Temp3"]] = vertical["Quantity"].str.split("-", expand = True)

vertical["PnL"] = None

for i in range(len(vertical)):
    if(vertical.iloc[i,21] == None):
        vertical.iloc[i,21] = vertical.iloc[i,22]
        
for i in range(len(vertical)):
    vertical.iloc[i,23] = float(vertical.iloc[i,11]) - float(vertical.iloc[i,19])
        
vertical["PL_Amount"] = None
        
for i in range(len(vertical)):
    if(vertical.iloc[i,10] == "CALL"):
        vertical.iloc[i,24] = vertical.iloc[i,23]*100
    if(vertical.iloc[i,10] == "PUT"):
        vertical.iloc[i,24] = vertical.iloc[i,23]*100
        
vertical = vertical.drop(columns = ["Temp1","Temp2","Temp3","Strike Price"])

vertical["Profit/Loss"] = np.nan 

for i in range(len(vertical)):
    if(vertical.iloc[i,20] < -1):
        vertical.iloc[i,21] = "Loss"
    else:
        vertical.iloc[i,21] = "Profit"


vertical.to_csv("options.csv")
