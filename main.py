import numpy as np
import pandas as pd
import nltk
import requests
from bs4 import BeautifulSoup
import string
import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

# EXTRACTING THE DATASET AND REMOVING NULL VALUES
df = pd.read_csv("D:/SATYAM/20211030 Test Assignment-20221123T141350Z-001/20211030 Test Assignment/Input.csv")
df.dropna(inplace=True)

df['URL_ID'] = df['URL_ID'].astype(np.int64)

# DATA EXTRACTION
urls = [i for i in df['URL']]
ids = [j for j in df['URL_ID']]

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 '
                  'Safari/537.36 '
}

for url in urls:
    raw_page = requests.get(url, headers=headers)

    soup = BeautifulSoup(raw_page.content, 'html.parser')

    f = open(str(ids[urls.index(url)]) + ".txt", "w", encoding="utf-8")

    for data in soup.find_all('title'):
        title_text = data.get_text(strip=True)
        f.writelines(title_text)
        f.write('.\n')

    for data in soup.find_all(['p', 'h2']):
        body_text = data.get_text(strip=True)
        f.writelines(body_text)

    f.close()

# DATA ANALYSIS
avg_sentence_length = []
complex_words = []
percentage_complex_words = []
syllables_per_word = []

for files in range(len(df['URL_ID'])):
    with open(str(files) + ".txt", "r+", encoding="utf-8") as f:
        readable_text = f.read()

        sentences = sent_tokenize(readable_text, 'english')
        words = word_tokenize(readable_text, 'english')

        avg_sent_length = len(words) / len(sentences)

        for word in words:
            complex_count = 0
            syllable_count = 0
            vowels = 0

            if word.endswith("es") or word.endswith("ed") or word.endswith("le"):
                pass
            else:
                for i in word:
                    if i == 'a' or i == 'e' or i == 'i' or i == 'o' or i == 'u':
                        vowels += 1
                if vowels > 2:
                    syllable_count += 1
                if syllable_count > 2:
                    complex_count += 1

        percentage_complex = (complex_count / len(words)) * 100
        syllable_per_word = syllable_count/len(words)

    complex_words.append(complex_count)
    percentage_complex_words.append(percentage_complex)
    avg_sentence_length.append(avg_sent_length)
    syllables_per_word.append(syllable_per_word)

