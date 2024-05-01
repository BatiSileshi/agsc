from bs4 import BeautifulSoup
import re
import pandas as pd


data = pd.read_csv(
    "/home/baty/Downloads/newAgsc.csv",
    encoding='utf-8-sig',
)


#1. Data Cleaning
def clean_data(single_data):
  #removing html tags
  single_data = BeautifulSoup(single_data, 'lxml').get_text()

  single_data = re.sub(r"[^a-zA-Z.!?,;'-]", ' ', single_data)

  single_data = re.sub(r" +", ' ', single_data)
  
  single_data = single_data.lower()

  return single_data

#2. Applying cleaning to each sentences in the dataset
data['cleaned_sentence'] = data['sentence'].apply(lambda x: clean_data(str(x)) if isinstance(x, (str, float)) else '')
data_clean = data['cleaned_sentence'].tolist()

#3. Labeling columns
data.columns = ['sentence', 'label', 'cleaned_sentence']
