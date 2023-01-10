import numpy as np
import pandas as pd
import nltk
import requests
from bs4 import BeautifulSoup
import string
import re
import os
import glob
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

# 1.EXTRACTING THE DATASET AND REMOVING NULL VALUES
df = pd.read_csv("D:/SATYAM/20211030 Test Assignment-20221123T141350Z-001/20211030 Test Assignment/Input.csv")
df.dropna(inplace=True)
df['URL_ID'] = df['URL_ID'].astype(np.int64)

# 2.CREATING TEXT FILES FOR EACH URL
urls = [i for i in df['URL']]
ids = [j for j in df['URL_ID']]

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 '
                  'Safari/537.36 '
}

for url in urls:
    raw_page = requests.get(url, headers=headers)

    soup = BeautifulSoup(raw_page.content, 'html.parser')

    f = open(str(ids[urls.index(url)]) + ".txt", "w", encoding="utf-8")  # CREATING FILE FOR EACH URL

    for data in soup.find_all('title'):  # WRITING TITLE TO FILE
        title_text = data.get_text(strip=True)
        f.writelines(title_text)
        f.write('.\n')

    for data in soup.find_all(['p', 'h2']):  # WRITING BODY TEXT TO FILE
        body_text = data.get_text(strip=True)
        f.writelines(body_text.replace(".", ". ").replace("?", "? "))

    f.close()

# 3.AGGREGATING ALL THE STOP WORDS
file_list = glob.glob(os.path.join(os.getcwd(), "D:/SATYAM/20211030 Test Assignment-20221123T141350Z-001/20211030 "
                                                "Test Assignment/StopWords", "*.txt"))

stopwords = []

for file_path in file_list:
    with open(file_path, 'r') as f:
        stopwords.extend(f.read().lower().splitlines())

# 4.GETTING POSITIVE AND NEGATIVE WORD LIST
file = open(r'D:\SATYAM\Stop Words\dat\MasterDictionary\negative-words.txt', 'r')
neg_words = file.read().split()  # NEGATIVE WORD LIST
file = open(r'D:\SATYAM\Stop Words\dat\MasterDictionary\positive-words.txt', 'r')
pos_words = file.read().split()  # POSITIVE WORD LIST

# 5.DATA ANALYSIS
avg_sentence_length = []
complex_words = []
percentage_complex_words = []
syllables_per_word = []
fog_index = []
personal_pronouns = []
avg_word_length = []
word_count = []
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

for files in ids:

    with open(str(files) + ".txt", "r+", encoding="utf-8") as f:
        readable_text = f.read()

        sentences = sent_tokenize(readable_text, 'english')
        my_punctuation = string.punctuation.replace("’", "").replace("“", "")
        words = word_tokenize(readable_text.lower().translate(str.maketrans('', '', my_punctuation)))
        words = list(filter(None, [e.encode('ascii', 'ignore').decode("utf-8") for e in words]))

        word_syl = []
        final_words = []
        count = 0
        positive_points = 0
        negative_points = 0

        for word in words:
            count = count + len(word)  # LENGTH OF EACH WORD
            complex_count = 0
            syllable_count = 0

            if word not in stopwords:  # REMOVING STOP WORDS
                final_words.append(word)

            if word in pos_words:  # GETTING POSITIVE AND NEGATIVE SCORE
                positive_points = positive_points + 1
            elif word in neg_words:
                negative_points = negative_points + 1

            if word.endswith("es") or word.endswith("ed") or word.endswith("le"):
                pass
            else:
                for i in word:
                    if i == 'a' or i == 'e' or i == 'i' or i == 'o' or i == 'u':
                        syllable_count += 1
                word_syl.append([word, syllable_count])

            syl_sum = 0
            w_len = 0
            for i in word_syl:
                if i[-1] >= 2:
                    complex_count += 1  # COUNTING COMPLEX WORDS
                syl_sum = syl_sum + i[1]
                w_len = w_len + len(i[0])
            try:
                syllable_per_word = (syl_sum / w_len)  # COUNTING SYLLABLES PER WORD
            except ZeroDivisionError:
                syllable_per_word = 'INF'
        percentage_complex = (complex_count / len(words)) * 100

        pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b', re.I)  # GETTING PERSONAL PRONOUNS
        pronouns = pronounRegex.findall(readable_text)

    # LISTING ALL REQUIRED PARAMETERS
    complex_words.append(complex_count)
    percentage_complex_words.append(percentage_complex)
    avg_sentence_length.append(len(words) / len(sentences))
    fog_index.append(0.4 * float((len(words) / len(sentences)) + percentage_complex))
    personal_pronouns.append(len(pronouns))
    avg_word_length.append(count / len(words))
    word_count.append(len(final_words))
    positive_score.append(positive_points)
    negative_score.append(negative_points)
    try:
        polarity_score.append(((positive_points - negative_points) / (positive_points + negative_points)) + 0.000001)
        subjectivity_score.append((positive_points + negative_points) / (len(final_words) + 0.000001))
    except ZeroDivisionError:
        polarity_score.append('INF')
        subjectivity_score.append('INF')


# 6. CREATING THE FINAL DATAFRAME
df['POSITIVE_SCORE'] = pd.Series(positive_score)
df['NEGATIVE_SCORE'] = pd.Series(negative_score)
df['POLARITY_SCORE'] = pd.Series(polarity_score)
df['SUBJECTIVITY_SCORE'] = pd.Series(subjectivity_score)
df['AVG_SENTENCE_LENGTH'] = pd.Series(avg_sentence_length)
df['PERCENTAGE_OF_COMPLEX_WORDS'] = pd.Series(percentage_complex_words)
df['FOG_INDEX'] = pd.Series(fog_index)
df['AVERAGE_NUMBER_OF_WORDS_PER_SENTENCE'] = pd.Series(avg_sentence_length)
df['COMPLEX_WORD_COUNT'] = pd.Series(complex_words)
df['WORD_COUNT'] = pd.Series(word_count)
df['SYLLABLE_PER_WORD'] = pd.Series(syllables_per_word)
df['PERSONAL_PRONOUNS'] = pd.Series(personal_pronouns)
df['AVG_WORD_LENGTH'] = pd.Series(avg_word_length)
df.set_index('URL_ID', inplace=True)

# 7. EXPORTING DATAFRAME AS CSV
df.to_csv('Stop_Words.csv')
