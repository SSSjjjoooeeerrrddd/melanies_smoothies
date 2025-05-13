## Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

## Create a title and first text
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

## Enter your name
name_on_order = st.text_input("Name on Smoothie")
st.write("The name of your smoothie will be:", name_on_order)

# We start a session because we are going to load data from a table in the cloud (Sf database)
cnx = st.connection("snowflake")
session = cnx.session()

## Get table as df and write df
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))
# st.dataframe(data=my_dataframe, use_container_width=True)
## Convert to pandas so we can use .loc[]
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

## Create a multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:"
    ,my_dataframe
    ,max_selections=5
)

if ingredients_list:
    ## Create and write string of chosen fruits
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    #st.write(ingredients_string)

    # Create SQL statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    # st.write(my_insert_stmt) 
    # st.stop() # GREAT FOR TESTING: stops running here, which is nice bc we dont wanna execute the sql statement yet, just test it

    ## Add a submit button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
