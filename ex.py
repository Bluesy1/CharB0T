import numpy
import pandas as pd
import scipy

df1 = pd.read_csv('/mnt/c/Users/gavin/OneDrive/Documents/GitHub/CharlieTest/example.csv', header=0)
df2 = pd.read_csv('/mnt/c/Users/gavin/OneDrive/Documents/GitHub/CharlieTest/example1.csv', header=0)

def GoodEvent(RPO):
    increase = input('WHat is the change in stock value?')
    df1.loc.loc[RPO, 'Value'] += increase
    print('Complete, new value of RPO ' + RPO + ' is: ' + df1.loc.loc[RPO, 'Value'])
    return('Complete')

def BadEvent(RPO):
    decrease = input('WHat is the change in stock value?')
    df1.loc.loc[RPO, 'Value'] -= decrease
    print('Complete, new value of RPO ' + RPO + ' is: ' + df1.loc.loc[RPO, 'Value'])
    return('Complete')



x = 0
while x == 0:
    call = input('What function? (GoodEvent, BadEvent, ....)')
    if call == 'GoodEvent':
        GoodEvent(input('Which RPO?'))
    elif call == 'BadEvent':
        BadEvent(input('Which RPO?'))
    elif call == 'N/A':
        print('N/A')