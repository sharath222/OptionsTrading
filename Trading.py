import pandas as pd
import numpy as np
from datetime import timezone
from datetime import datetime
import time  
 
def convertMonth(month):
    if month == 'JAN':
        month = int(1)
    elif month == 'FEB':
        month = int(2)
    elif month == 'MAR':
        month = int(3)
    elif month == 'APR':
        month = int(4)
    elif month == 'MAY':
        month = int(5)
    elif month == 'JUN':
        month = int(6)
    elif month == 'JUL':
        month = int(7)
    elif month == 'AUG':
        month = int(8)
    elif month == 'SEP':
        month = int(9)
    elif month == 'OCT':
        month = int(10)
    elif month == 'NOV':
        month = int(11)
    else:
        month = int(12)    
    # month = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    # Nmonth = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    # for i in range(len(month)):
    #     for j in range(len(Nmonth)):
    #         if value == month[i]:
    #             value = Nmonth[j]
    return str(month)

def convertYear(year):
    year = str(20) + year  
    return str(year)

def utcConvert(value):
        exp = data["Expiry Date"].str.split("-", expand = True)
        exp1 = exp.iloc[i]
        expiry = datetime(int(exp1.iloc[2]), int(exp1.iloc[1]), int(exp1.iloc[0]))
        timestamp = int(expiry.replace(tzinfo=timezone.utc).timestamp())
        timestamp = str(timestamp)
        return timestamp
# Using for loop 
start = time.time()

#load data and remove un-neccesary fields and make data column string due to date format incosistency in csv file
data = pd.read_csv("2021-01-05-AccountStatement.csv",dtype={'DATE': str})
# data = pd.read_csv("2020-09-27-AccountStatement.csv",dtype={'DATE': str})

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

otherStrategy = data[data["Strategy"].str.contains("VERT-ROLL|DIAGONAL|CALENDER|COMBO|COVERED|STRADDLE|STRANGLE", na = False)]
data = data[~data["Strategy"].str.contains("VERT-ROLL|DIAGONAL|CALENDAR|COMBO|COVERED|STRADDLE|STRANGLE", na = False)]

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
    month = convertMonth(data.iloc[i,10])
    year = convertYear(data.iloc[i,11])
    date = data.iloc[i,9]
    data.iloc[i,9] =  date + '-' + month + '-' + year
        
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
        elif (data.iloc[i,10] == 'PUT'):
            if(data.iloc[i,17] == False):
                data.iloc[i,16] = data.iloc[i,9]
    elif (data.iloc[i,2] == 'SOLD'):
        if (data.iloc[i,10] == 'CALL'):
            if(data.iloc[i,17] == False):
                data.iloc[i,14] = data.iloc[i,9]
        elif (data.iloc[i,10] == 'PUT'):
            if(data.iloc[i,17] == False):
                data.iloc[i,15] = data.iloc[i,9]

data["Temp1"] = None
data["Temp2"] = None
data["Temp3"] = None
data["Temp4"] = None

data[["Temp1","Temp2","Temp3","Temp4"]] = data["Strike Price"].str.split("/", expand = True)

for i in range(len(data)):
    if (data.iloc[i,19] != None):
        if (data.iloc[i,20] == None and data.iloc[i,21] == None):
            if (data.iloc[i,2] == 'BOT'): 
                if (data.iloc[i,10] == 'CALL'):
                    data.iloc[i,13] = data.iloc[i,18]
                    data.iloc[i,14] = data.iloc[i,19]
                elif (data.iloc[i,10] == 'PUT'):
                    data.iloc[i,16] = data.iloc[i,18]
                    data.iloc[i,15] = data.iloc[i,19]
            else:
                if (data.iloc[i,10] == 'CALL'):
                    data.iloc[i,14] = data.iloc[i,18]
                    data.iloc[i,13] = data.iloc[i,19]
                elif (data.iloc[i,10] == 'PUT'):
                    data.iloc[i,15] = data.iloc[i,18]
                    data.iloc[i,16] = data.iloc[i,19]
            

for i in range(len(data)):
    if (data.iloc[i,18] != None and data.iloc[i,19] != None and data.iloc[i,20] != None and data.iloc[i,21] != None):
        if (data.iloc[i,2] == 'BOT'):  
                data.iloc[i,13] = data.iloc[i,18]
                data.iloc[i,14] = data.iloc[i,19]
                data.iloc[i,16] = data.iloc[i,20]
                data.iloc[i,15] = data.iloc[i,21]

        if (data.iloc[i,2] == 'SOLD'):  
                data.iloc[i,13] = data.iloc[i,19]
                data.iloc[i,14] = data.iloc[i,18]
                data.iloc[i,16] = data.iloc[i,21]
                data.iloc[i,15] = data.iloc[i,20]


data = data.drop(columns = ["Temp","Temp1","Temp2","Temp3","Temp4"])

data["Call + Premium"] = np.nan
data["Put - Premium"] = np.nan

data['Call Buy'] = data['Call Buy'].fillna('-')
data['Call Sell'] = data['Call Sell'].fillna('-')
data['Put Buy'] = data['Put Buy'].fillna('-')
data['Put Sell'] = data['Put Sell'].fillna('-')
data['Strike Price'] = data['Strike Price'].fillna('-')

data = data.sort_values(by=['Strategy'])

# for naked
for i in range(len(data)):
    if(data.iloc[i,13] != '-' and data.iloc[i,14] == '-' and data.iloc[i,15] == '-' and data.iloc[i,16] == '-'):
        if(data.iloc[i,10] == "CALL"):
            if (data.iloc[i,2] == 'BOT'):
                if(data.iloc[i,13] != '-' and data.iloc[i,14] == '-' and data.iloc[i,15] == '-' and data.iloc[i,16] == '-'):
                    data.iloc[i,18] = float(data.iloc[i,13]) - float(data.iloc[i,11])
            elif (data.iloc[i,2] == 'SOLD'):
                if(data.iloc[i,13] != '-'):
                    data.iloc[i,18] = float(data.iloc[i,16]) + float(data.iloc[i,11])
        elif(data.iloc[i,10] == "PUT"):
            if (data.iloc[i,2] == 'BOT'):
                if(data.iloc[i,13] != '-' and data.iloc[i,14] == '-' and data.iloc[i,15] == '-' and data.iloc[i,16] == '-'):
                    data.iloc[i,18] = float(data.iloc[i,16]) - float(data.iloc[i,11])
            elif (data.iloc[i,2] == 'SOLD'):
                if(data.iloc[i,13] != '-'):
                    data.iloc[i,18] = float(data.iloc[i,16]) + float(data.iloc[i,11])

for i in range(len(data)):
    if(data.iloc[i,10] == "CALL"):
        if(data.iloc[i,13] == '-' and data.iloc[i,14] != '-' and data.iloc[i,15] == '-' and data.iloc[i,16] == '-'):
            if (data.iloc[i,2] == 'BOT'):
                data.iloc[i,17] = float(data.iloc[i,14]) - float(data.iloc[i,11])
            elif (data.iloc[i,2] == 'SOLD'):
                if(data.iloc[i,13] != '-'):
                   data.iloc[i,17] = float(data.iloc[i,14]) + float(data.iloc[i,11])
    elif(data.iloc[i,10] == "PUT"):
        if (data.iloc[i,2] == 'BOT'):
            if(data.iloc[i,13] != '-'):
                data.iloc[i,18] = float(data.iloc[i,16]) - float(data.iloc[i,11])
        elif (data.iloc[i,2] == 'SOLD'):
            if(data.iloc[i,13] != '-'):
                data.iloc[i,18] = float(data.iloc[i,16]) + float(data.iloc[i,11])
                
# for i in range(len(data)):
#     if(data.iloc[i,10] == "CALL"):
#         if(data.iloc[i,14] != '-' and data.iloc[i,15] != '-' and data.iloc[i,16] != '-'):
#             data.iloc[i,17] = float(data.iloc[i,13]) + float(data.iloc[i,11])
#     elif(data.iloc[i,10] == "PUT"):
#         if (data.iloc[i,2] == 'BOT'):
#             if(data.iloc[i,13] != '-'):
#                 data.iloc[i,18] = float(data.iloc[i,16]) - float(data.iloc[i,11])
#         elif (data.iloc[i,2] == 'SOLD'):
#             if(data.iloc[i,13] != '-'):

# data["actual premium"] = None
    
# for i in range(len(data)):
#     if(data.iloc[i,10] == "CALL"):
#         ticker = data.iloc[i,5]
        
#         try:
#             timestamp = utcConvert(i)
#             start = time.time()
#             temp = pd.read_html("https://finance.yahoo.com/quote/"+ticker+"/options?date="+timestamp+"&p="+ticker+"&straddle=true")
#             totalTime =  time.time()-start
#             temp = temp[0]
#             call = data.iloc[i,13]
        
#             for x in range(len(temp)):
#                 if (float(temp.iloc[x,5]) == float(call)):
#                     data.iloc[i,19] = temp.iloc[x,0]
#         except:
#             data.iloc[i,19] = 0
             
    
#     elif(data.iloc[i,10] == "PUT"):
        
#         put = data.iloc[i,16]
#         try:
#             for x in range(len(temp)):
#                 if (float(temp.iloc[x,5]) == float(put)):
#                     data.iloc[i,19] = temp.iloc[x,0]
#         except:
#             data.iloc[i,19] = 0
                
# data["Present Premium"] = data["actual premium"].fillna(0)                
# data[["Temp1","Temp2"]] = data["Quantity"].str.split("+", expand = True)
# data[["Temp1","Temp3"]] = data["Quantity"].str.split("-", expand = True)

# data["PnL"] = None

# for i in range(len(data)):
#     if(data.iloc[i,21] == None):
#         data.iloc[i,21] = data.iloc[i,22]
        
# for i in range(len(data)):
#     try:
#         data.iloc[i,23] = float(data.iloc[i,11]) - float(data.iloc[i,19])
#     except:
#         data.iloc[i,23] = 0
# data["PL_Amount"] = None
        
# for i in range(len(data)):
#     if(data.iloc[i,10] == "CALL"):
#         data.iloc[i,24] = data.iloc[i,23]*100
#     if(data.iloc[i,10] == "PUT"):
#         data.iloc[i,24] = data.iloc[i,23]*100
        
# data = data.drop(columns = ["Temp1","Temp2","Temp3","Strike Price"])

# data["Profit/Loss"] = np.nan 

# for i in range(len(data)):
#     try:
#         if(data.iloc[i,20] < -1):
#             data.iloc[i,21] = "Loss"
#         else:
#             data.iloc[i,21] = "Profit"
#     except:
#         data.iloc[i,21] = "NA"

# data.to_csv("options.csv")


