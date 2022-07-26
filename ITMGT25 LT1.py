# importing

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# opening json file

with open ('transaction-data-adhoc-analysis.json','r') as f:
    data = json.load(f)
    
# creating a pandas dataframe from the json file

df = pd.read_json('transaction-data-adhoc-analysis.json')

# dataframe dump

print(df)

# filter dataframe to relevant columns only

filtered_df = df[['transaction_date','username','transaction_value','transaction_items']]
print(filtered_df)

# figuring out individual prices of items

print(filtered_df.head(20))

# getting value of full transaction_items from original dataframe

print(filtered_df.iat[13,3]) # changing this allows me to look for the price of an individual item

# CREATING A NEW DATAFRAME FOR PRICES (will be multiplied to count later on to get total value)

pricelist = [{'item':'Beef Chicharon','price':1299},
            {'item':'Gummy Vitamins','price':1500},
            {'item':'Gummy Worms','price':150},
            {'item':'Kimchi and Seaweed','price':799},
            {'item':'Nutrional Milk','price':1990},
            {'item':'Orange Beans','price':199},
            {'item':'Yummy Vegetables','price':500}]
pricelist_df = pd.DataFrame(pricelist)
print(pricelist_df)

# 1 PRODUCT PER ROW

fixed_rows_df = filtered_df.set_index(['transaction_date','username','transaction_value']).apply(lambda x: x.str.split(';').explode()).reset_index()
print(fixed_rows_df)

# CREATING A PIVOT TABLE FOR PRODUCT BREAKDOWN

# Create dataframe copy, and new column for only the month name

pivot_df = fixed_rows_df.copy()

def month(transaction_date):
    if '2022/01' in transaction_date:
        return 'January'
    elif '2022/02' in transaction_date:
        return 'February'
    elif '2022/03' in transaction_date:
        return 'March'
    elif '2022/04' in transaction_date:
        return 'April'
    elif '2022/05' in transaction_date:
        return 'May'
    elif '2022/06' in transaction_date:
        return 'June'

pivot_df['month'] = pivot_df['transaction_date'].apply(month)

print(pivot_df)

# split transaction_items
new_pivot = pivot_df.transaction_items.str.split(pat=',',expand=True)

# call to check
print(new_pivot)

# rename columns in new_pivot
new_pivot.rename(columns = {0:'brand', 1:'item', 2:'quantity'}, inplace = True)

#convert values in quantity column to integers
new_pivot['quantity'] = new_pivot['quantity'].str.replace(r'\D', '')
new_pivot['quantity'] = new_pivot['quantity'].astype('int')

# call dataframe
print(new_pivot)

# concatenate pivot_df and new_pivot
final_pivot = pd.concat([pivot_df, new_pivot], axis=1)

# call final_pivot
print(final_pivot)

# drop transaction_date, transaction_value, and transaction_items in final_pivot (not permanent)
final_pivot.drop(columns=['transaction_date','transaction_value','transaction_items'])

# create new dataframe (where columns have been dropped) to be sure
PIVOT_DATAFRAME = final_pivot.drop(columns=['transaction_date','transaction_value','transaction_items'])
print(PIVOT_DATAFRAME)

# Pivot Table for Item Breakdown (order count per item)
total_item_count = pd.pivot_table(data=PIVOT_DATAFRAME, 
                        index=['item'], 
                        columns=['month'], 
                        values='quantity',
                        aggfunc='sum')
print(total_item_count[['January','February','March','April','May','June']])

# Table for Item Value Breakdown (total sale value per item)

total_sale_value = total_item_count.mul([pricelist_df.loc[0]['price'],pricelist_df.loc[1]['price'],pricelist_df.loc[2]['price'],
                pricelist_df.loc[3]['price'],pricelist_df.loc[4]['price'],pricelist_df.loc[5]['price'],
                pricelist_df.loc[6]['price']], axis=0)
print(total_sale_value[['January','February','March','April','May','June']])

# CREATING A LOYALTY PROGRAM DATAFRAME

# describes customers' monthly engagement w the company

# create a list of all customers through their usernames using unique()
all_customers = list(filtered_df['username'].unique())

# create loyalty_program dataframe where usernames make up the data
loyalty_program = pd.DataFrame(all_customers,columns=['username'])
print(loyalty_program)

# creating dataframes and lists of customers who purchased in a specific month

january_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('January')]
january_customers = list(january_transactions['username'].unique())

february_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('February')]
february_customers = list(february_transactions['username'].unique())

march_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('March')]
march_customers = list(march_transactions['username'].unique())

april_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('April')]
april_customers = list(april_transactions['username'].unique())

may_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('May')]
may_customers = list(may_transactions['username'].unique())

june_transactions = PIVOT_DATAFRAME[PIVOT_DATAFRAME['month'].str.contains('June')]
june_customers = list(june_transactions['username'].unique())

# add boolean columns to dataframe (TRUE if customer purchased in that month, FALSE if not) by vectorizing a function (applying it to a column)

# all functions

def jan_customers_function(username):
    return username in january_customers

def feb_customers_function(username):
    return username in february_customers

def mar_customers_function(username):
    return username in march_customers

def apr_customers_function(username):
    return username in april_customers

def may_customers_function(username):
    return username in may_customers

def june_customers_function(username):
    return username in june_customers

# creating the boolean columns

loyalty_program['january purchase'] = loyalty_program['username'].apply(jan_customers_function)
loyalty_program['february purchase'] = loyalty_program['username'].apply(feb_customers_function)
loyalty_program['march purchase'] = loyalty_program['username'].apply(mar_customers_function)
loyalty_program['april purchase'] = loyalty_program['username'].apply(apr_customers_function)
loyalty_program['may purchase'] = loyalty_program['username'].apply(may_customers_function)
loyalty_program['june purchase'] = loyalty_program['username'].apply(june_customers_function)

print(loyalty_program)

# CUSTOMER TABLE

# variables

JAN_TRUE = loyalty_program['january purchase']==True
FEB_TRUE = loyalty_program['february purchase']==True
MAR_TRUE = loyalty_program['march purchase']==True
APR_TRUE = loyalty_program['april purchase']==True
MAY_TRUE = loyalty_program['may purchase']==True
JUN_TRUE = loyalty_program['june purchase']==True

JAN_FALSE = loyalty_program['january purchase']==False
FEB_FALSE = loyalty_program['february purchase']==False
MAR_FALSE = loyalty_program['march purchase']==False
APR_FALSE = loyalty_program['april purchase']==False
MAY_FALSE = loyalty_program['may purchase']==False
JUN_FALSE = loyalty_program['june purchase']==False

# REPEATERS

january_repeaters = "N/A" # since there is no previous month
february_repeaters = len(loyalty_program[(JAN_TRUE) & (FEB_TRUE)])
march_repeaters = len(loyalty_program[(MAR_TRUE) & (FEB_TRUE)])
april_repeaters = len(loyalty_program[(MAR_TRUE) & (APR_TRUE)])
may_repeaters = len(loyalty_program[(MAY_TRUE) & (APR_TRUE)])
june_repeaters = len(loyalty_program[(MAY_TRUE) & (JUN_TRUE)])

print(loyalty_program[(JAN_TRUE) & (FEB_TRUE)]) # sample for february repeaters (count = num of rows, or use len())

# INACTIVE

january_inactive = "N/A" # since there is no previous month
february_inactive = len(loyalty_program[(JAN_TRUE) & (FEB_FALSE)])
march_inactive = len(loyalty_program[((JAN_TRUE) | (FEB_TRUE)) & (MAR_FALSE)])
april_inactive = len(loyalty_program[((JAN_TRUE) | (FEB_TRUE) | (MAR_TRUE)) & (APR_FALSE)])
may_inactive = len(loyalty_program[((JAN_TRUE) | (FEB_TRUE) | (MAR_TRUE) | (APR_TRUE)) & (MAY_FALSE)])
june_inactive = len(loyalty_program[((JAN_TRUE) | (FEB_TRUE) | (MAR_TRUE) | (APR_TRUE) | (MAY_TRUE)) & (JUN_FALSE)])

print(loyalty_program[(JAN_TRUE) & (FEB_FALSE)]) # sample for february inactive (count = num of rows, or use len())

# ENGAGED

january_engaged = len(loyalty_program[JAN_TRUE])
february_engaged = len(loyalty_program[JAN_TRUE & FEB_TRUE])
march_engaged = len(loyalty_program[(JAN_TRUE) & (FEB_TRUE) & (MAR_TRUE)])
april_engaged = len(loyalty_program[(JAN_TRUE) & (FEB_TRUE) & (MAR_TRUE) & (APR_TRUE)])
may_engaged = len(loyalty_program[(JAN_TRUE) & (FEB_TRUE) & (MAR_TRUE) & (APR_TRUE) & (MAY_TRUE)])
june_engaged = len(loyalty_program[(JAN_TRUE) & (FEB_TRUE) & (MAR_TRUE) & (APR_TRUE) & (MAY_TRUE) & (JUN_TRUE)])

print(loyalty_program[(JAN_TRUE) & (FEB_TRUE) & (MAR_TRUE)]) # sample for march engaged (count = num of rows, or use len())

# customer activity table

customer_activity = {'Customer Categories':['Repeaters','Inactive','Engaged'],
                        'January':[january_repeaters,january_inactive,january_engaged],
                        'February':[february_repeaters,february_inactive,february_engaged],
                        'March':[march_repeaters,march_inactive,march_engaged],
                        'April':[april_repeaters,april_inactive,april_engaged],
                        'May':[may_repeaters,may_inactive,may_engaged],
                        'June':[june_repeaters,june_inactive,june_engaged]}
customer_activity_df = pd.DataFrame(customer_activity)
print(customer_activity_df)

# matplotlib charts

# pie chart for item count

item_labels = ['Beef Chicharon', 'Gummy Vitamins', 'Gummy Worms', 'Kimchi and Seaweed', 'Nutrional Milk', 'Orange Beans', 'Yummy Vegetables']
count_dataframe = total_item_count.sum(axis=1)
plt.pie(count_dataframe, labels=item_labels)
plt.show()

# pie chart for item value contribution to total revenue

sales_dataframe = total_sale_value.sum(axis=1)
plt.pie(sales_dataframe, labels=item_labels)
plt.show()