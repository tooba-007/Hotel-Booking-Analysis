import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


hotel_data=pd.read_csv("C:\\Users\\Dracula\\Desktop\\PYTHON\\Hotel Booking Cleaning\\hotel_bookings.csv")


#STEP 1 -- Rename
# incase you want to drop a column --> hotel_data.drop(columns=['xyz'], inplace=True)
hotel_data.rename({'adults':'num_adults', 'children':'num_children','babies':'num_babies'}, axis=1,inplace=True)



#STEP 2 -- Nan Values
# print(hotel_data.isnull().sum()*100/len(hotel_data))
# print(hotel_data['agent'].unique())
# print(hotel_data[hotel_data['agent']==5])
hotel_data.fillna({'agent': -1},inplace=True)

# print(hotel_data[hotel_data['country'].isna()])
hotel_data.fillna({'country': 'unkown'},inplace=True)

# dropping rows where there are no num_children values( they are only 4) so using dropna
# print(hotel_data[hotel_data['num_children'].isna()])
hotel_data.dropna(subset=['num_children'], inplace=True)

# dropping 'company' column as it was 94% null
hotel_data.drop(columns=['company'],inplace=True)
# print(hotel_data.isnull().sum())



# STEP 3 -- DATATYPES CHECK/CHANGE we do this after filling NAN values bec datatype cant be changed if column has nan values
hotel_data=hotel_data.astype({'is_canceled':'boolean', 'num_children':'int32','is_repeated_guest':'boolean','agent':'int32'})
# print(hotel_data.dtypes)



# STEP 4 -- Grouped/Bin columns 
# print(hotel_data['lead_time'].unique())
# print(hotel_data['lead_time'].describe())
# pd.cut  is a good way to reduce the number of  unique values you have into groups 
bins=[0,100,200,300,400,500,600,700,800]
labels=['0-100','101-200','201-300','301-400','401-500','501-600','601-700','701-800']
hotel_data['lead_time_binned']=pd.cut(hotel_data['lead_time'], bins=bins, labels=labels)
# print(hotel_data[['lead_time', 'lead_time_binned']])



# STEP 5 -- Seperating data from one column to multiple columns
# hotel_data['arrival_date_month']=hotel_data['arrival_date'].str.split('-',expand=True)[0]
# hotel_data['arrival_date_year']=hotel_data['arrival_date'].str.split('-',expand=True)[1]
# print(hotel_data[['arrival_date_month','arrival_date_year']])
# print(hotel_data.columns)

# code to move the columns
col_to_move=hotel_data.pop('lead_time_binned')
hotel_data.insert(3, 'lead_time_binned', col_to_move)
# print(hotel_data.head(5))



# STEP 6 - String Cleaning, there are only 2 names -- city hotel and resort hotel
# Case sensitivity also displays result under unique list
# print(hotel_data['hotel'].value_counts())

# if hotel resort** --> replace this "[\*\n\^]" with '' (empty string)
hotel_data['hotel']=hotel_data['hotel'].replace(r"[\*\n\^]",'',regex=True)
# print(hotel_data['hotel'].unique())



# STEP 7 -- Removing Duplicates
# print(hotel_data.duplicated(keep=False))
# print(hotel_data.loc[hotel_data.duplicated(keep=False)])   # all the duplicated rows 

hotel_data.drop_duplicates(keep='first', inplace=True)
# print(hotel_data.loc[hotel_data.duplicated(keep=False)])   # now no duplicates 



# INSIGHTS!!!!!

# ONE -- Weekend vs Weekday bookings
hotel_data['arrival_date_full'] = pd.to_datetime(
    hotel_data['arrival_date_year'].astype(str) + '-' +
    hotel_data['arrival_date_month'].astype(str) + '-' +
    hotel_data['arrival_date_day_of_month'].astype(str),
    errors='coerce'   # invalid dates ko NaT bana dega
)
hotel_data['day_of_week'] = hotel_data['arrival_date_full'].dt.dayofweek
hotel_data['is_weekend'] = hotel_data['day_of_week'].isin([5, 6])

# Count bookings
# print(hotel_data['is_weekend'].value_counts())



# TWO -- Stay Duration
hotel_data['total_stay'] = hotel_data['stays_in_weekend_nights'] + hotel_data['stays_in_week_nights']
# print(hotel_data.groupby('hotel')['total_stay'].mean())


# THREE -- Revenue Feature
# ADR (Average Daily Rate) * total stay nights
if 'adr' in hotel_data.columns:
    hotel_data['revenue'] = hotel_data['adr'] * hotel_data['total_stay']
# print(hotel_data.groupby('hotel')['revenue'].sum())
# print(hotel_data.columns.value_counts())


# FOUR -- Booking Cancellation Rate
# print(hotel_data['is_canceled'].value_counts(normalize=True) * 100)


# FIVE -- Guest Type Analysis (Solo / Couple / Family)
def guest_type(row):
    if row['num_adults'] == 1 and row['num_children'] == 0 and row['num_babies'] == 0:
        return 'Solo'
    elif row['num_adults'] == 2 and row['num_children'] == 0 and row['num_babies'] == 0:
        return 'Couple'
    else:
        return 'Family'

hotel_data['guest_type'] = hotel_data.apply(guest_type, axis=1)
# print(hotel_data['guest_type'].value_counts())


# SIX -- Top Countries of Guests
top_countries = hotel_data['country'].value_counts().head(10).reset_index()
top_countries.columns = ['country', 'count']
# print(hotel_data['country'].value_counts().head(5)
print(top_countries.columns)

# try:
#     hotel_data.to_excel("Cleaned_Hotel_Data.xlsx", index=False)
#     print("done!")
# except Exception as e:
#     print(f"Error occurred: {e}")

    
    
# ------------------ Visualizations ------------------
custom_palette = ["#D8949E",  # pastel pink
                  "#B390B3",  # lavender
                  "#8FC4B0",  # mint
                  "#899FA7",  # pastel blue
                  "#E4C2A4"]  # peach
sns.set(style="whitegrid", palette=custom_palette)



# 7. Lead Time Distribution
plt.figure(figsize=(8,5))
sns.countplot(data=hotel_data, x='lead_time_binned', order=labels, palette=custom_palette)
plt.title("Booking Lead Time Distribution", fontsize=14, fontweight="bold")
plt.xlabel("Lead Time (Days)")
plt.ylabel("Number of Bookings")
plt.show()

# 1. Weekend vs Weekday Bookings
plt.figure(figsize=(6,4))
sns.countplot(data=hotel_data, x='is_weekend', palette=custom_palette[:2])
plt.title("Weekend vs Weekday Bookings", fontsize=14, fontweight="bold")
plt.xlabel("Is Weekend?")
plt.ylabel("Number of Bookings")
plt.show()

# 2. Average Stay Duration by Hotel
plt.figure(figsize=(6,4))
sns.barplot(data=hotel_data, x='hotel', y='total_stay', estimator='mean', palette=custom_palette[:2])
plt.title("Average Stay Duration by Hotel Type", fontsize=14, fontweight="bold")
plt.xlabel("Hotel Type")
plt.ylabel("Average Stay (nights)")
plt.show()

# 3. Total Revenue by Hotel
plt.figure(figsize=(6,4))
revenue_by_hotel = hotel_data.groupby('hotel')['revenue'].sum().reset_index()
sns.barplot(data=revenue_by_hotel, x='hotel', y='revenue', palette=custom_palette[:2])
plt.title("Total Revenue by Hotel Type", fontsize=14, fontweight="bold")
plt.xlabel("Hotel Type")
plt.ylabel("Revenue")
plt.show()

# 4. Booking Cancellation Rate
plt.figure(figsize=(6,4))
sns.countplot(data=hotel_data, x='is_canceled', palette=custom_palette[:2])
plt.title("Booking Cancellation Status", fontsize=14, fontweight="bold")
plt.xlabel("Cancelled?")
plt.ylabel("Count")
plt.show()

# 5. Guest Type Distribution
plt.figure(figsize=(6,4))
sns.countplot(data=hotel_data, x='guest_type', order=['Solo','Couple','Family'], palette=custom_palette[:3])
plt.title("Guest Type Distribution", fontsize=14, fontweight="bold")
plt.xlabel("Guest Type")
plt.ylabel("Number of Bookings")
plt.show()

# 6. Top 5 Countries of Guests
plt.figure(figsize=(8,5))
sns.barplot(data=top_countries, x='country', y='count', palette=custom_palette)
plt.title("Top 5 Guest Countries", fontsize=14, fontweight="bold")
plt.xlabel("Country")
plt.ylabel("Number of Bookings")
plt.show()