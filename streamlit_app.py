import streamlit as st
import random
import pandas as pd
import requests
import json
from typing import List
import numpy as np
from transformers import BertTokenizer, BertModel
from bert_score import BERTScorer
import math
# {"integers": integer_list})



df = pd.read_csv("content_df.csv")
df = df.reset_index()
if "x" not in st.session_state:
    st.session_state.x = df.sample()
    st.session_state.xscorer = BERTScorer(model_type='bert-base-uncased')
    
x = st.session_state.x
xscorer = st.session_state.xscorer
def get_recommendations(title):
    # df = df.reset_index()
    indices = pd.Series(df.index, index=df['parent_asin'])
    idx = indices[title]
    idx = idx
    # sim_scores = list(enumerate(cosine_sim[idx]))
    loaded_scores = np.load('cosine_scores.npy')
    sim_scores = list(enumerate(loaded_scores[idx]))
    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    product_indices = [i[0] for i in sim_scores]
    products = df.iloc[product_indices][['title_y', 'parent_asin', 'weighted_rating']]
    # return titles.iloc[product_indices]
    return products


def send_metrics(metric_values, user_feedback):
    
    print(metric_values)
    res2 = requests.post(url = "http://127.0.0.1:8000/collectMetrics", json = {"integers": metric_values})
    print('API Response: ', res2.json())
    res1 = requests.post(url = "http://127.0.0.1:8000/collectFeedback", json = user_feedback)
    print('API Response: ', res1.json())

def getBertScore(reference, candidate):
    
    P, R, F1 = xscorer.score([candidate], [reference])
    print("P.mean():",P.mean())
    # print(int(math.ceil(P.mean())))
    return P.mean()

st.set_page_config(page_title='E-Commerce Recommendation', layout='wide', initial_sidebar_state='collapsed')

with st.container(border=True):
    st.title("E-Commerce Simulator! 🛍️",)

prod_id = x['parent_asin'].values[0]
prod_name = x['title_y'].values[0]

df_new = get_recommendations(prod_id)
# Sample data
# data = {
#     'product_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
#     'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
#     # 'price': [10.99, 12.99, 9.99, 15.99, 8.99],
#     'rating': [4.5, 4.0, 4.8, 3.9, 4.2]
# }

# user_list = ["user_1", "user_2", "user_3"]
# random_user = random.choice(user_list)
random_user = x['user_id'].values[0]
welcome_message= f"Welcome to the platform: {random_user}"
st.subheader(welcome_message)

st.button("Generate recommendations")
# Create DataFrame
# df = pd.DataFrame(data)
# Display DataFrame in Streamlit
st.write("Product Data")
st.write("Previously Bought: ",prod_name)
st.dataframe(df_new.head(), use_container_width=True, hide_index=True)
reference = prod_name
relevance = []
counter = 0
mrr = 0
for row in df_new.head().itertuples():
    counter += 1
    candidate = row.title_y
# BERTScore calculation
    p = getBertScore(reference, candidate)
    if p >= 0.3:
        mrr += 1/counter
    print("MRR:",mrr)
    # print(f"BERTScore Precision: {P.mean():.4f}, Recall: {R.mean():.4f}, F1: {F1.mean():.4f}")
# products = [
#     {"id": 1234, "name": "Product A"},
#     {"id": 4321, "name": "Product B"},
#     {"id": 7890, "name": "Product C"},
#     {"id": 8765, "name": "Product D"},
#     {"id": 8456, "name": "Product E"},
# ]

products = df_new.to_json(orient='records')

df_new = df_new.reset_index()
df_new = df_new.head()

user_feedback = []
product_ratings = {}
counter=0
ctr_count = 0
tot_products = 0
purchased_products = []
metric_values = []
print("NEW SESSION")
# Display products with sliders for ratings

with st.container(border=True):
    col1, col2= st.columns(2)
    with col1:
        st.subheader("Please provide your reviews:")
        for index, row in df_new.iterrows():
            counter+=1
            st.write(f"**{row['title_y']}** (ID: {row['parent_asin']})")
            feedback = st.feedback("stars", key={f"counter_{counter}"})
            product_ratings = {'user_id': str(random_user), 'product_id': str(row['parent_asin']), 'feedback': str(feedback)}
            user_feedback.append(product_ratings)
            # print("******")
            # print(f"counter: {product['name']}, feedback: {feedback+1}")
            st.write("")
            st.write("---")
        # print(json.dumps(user_feedback))
        # user_feedback.insert(0, counter)
        
    with col2:
        st.subheader("Would you buy this product?")
        for index, row in df_new.iterrows():
            tot_products+=1
            counter+=1
            st.write(f"**{row['title_y']}** (ID: {row['parent_asin']})")
            button = st.toggle("Add to Cart", key={f"counter_{counter}"})
            if button:
                #productIDs for MRR
                purchased_products.append(row['parent_asin'])
                ctr_count+=1
            st.write("---")
            # print(button)
        #CTR
        ctr = (ctr_count/tot_products)*100
        print(ctr)
        metric_values.append(math.ceil((mrr/5)*100))
        metric_values.append(ctr)
        metric_values = metric_values + purchased_products
print(metric_values)
st.button("Submit", on_click=send_metrics, args=(metric_values, user_feedback))


