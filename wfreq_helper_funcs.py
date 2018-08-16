
# coding: utf-8

# In[1]:
import os
import glob
import argparse
import re, string, unicodedata
import numpy as np
import pandas as pd
import nltk
# nltk.download()
import contractions
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer

def splitter(text):
    return " ".join(text.split("|"))

# Detaching concatenated words
def detach_words(text):
    """Detach Concatenated Words"""
    idx = 0
    new_text = []
    for i in text:
        idx+=1
        if i.isupper():
            if not text[idx-1] == '-':# or not text[idx-3] == ' - ':
                new_text.append(' ' + i)
            else:
                new_text.append(i)
    new_text = re.sub("w/","", re.sub("^ ","", re.sub("  "," ", "".join(new_text))))
    new_text = re.sub(" -","-", re.sub("- ","-", re.sub(" - ","-", new_text)))
    new_text = re.sub("^/","", re.sub("^-","", new_text))
    return new_text
    
# Replace contractions
def replace_contractions(text):
    """Replace contractions in string of text"""
    try:
        x = contractions.fix(text)
    except UnicodeEncodeError as e:
        return ""
    return x

# Tokenize
def tokenize_text(text):
    try:
        x = nltk.word_tokenize(text.decode("UTF-8"))
    except UnicodeEncodeError as e:
        return ""
    return sorted(set(x))

# Remove non ascii characters
def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        word = re.sub("[ ]"," ", re.sub("^/","", re.sub("^-","",word)))
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return sorted(set(new_words))

# Convert every word to lowercase
def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.split('([a-zA-Z]+)/', word.lower())
        new_words.extend(new_word)
    return sorted(set(new_words))

# Remove punctuations
def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^/\w\s-]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return sorted(set(new_words))

# Replace numbers
def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return sorted(set(new_words))

# Remove stopwords
def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return sorted(set(new_words))

def remove_single_letters(words):
    """Removes single letter words"""
    new_words = []
    for i in words:
        if len(i) > 2:
            new_words.append(i)
    return sorted(set(new_words))

def remove_only_numbers(words):
    """Removes only numbers without any letters"""
    new_words = []
    for i in words:
        if re.search("\d",i):
            if re.search("[a-zA-Z]",i):
                new_words.append(i)
        else:
            new_words.append(i)
    return sorted(set(new_words))

def pos_tagger(words):
    """Returns only nouns and adjectives"""
    new_words = []
    for word,tag in nltk.pos_tag(words):
        if tag.startswith('J') or tag.startswith('N'):
            new_words.append(word)
    return sorted(set(new_words))

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems

def read_master_list(path):
    dic = pd.read_csv(path,header=None,names=['keyword'])
    master_list = []
    x = dic.keyword.apply(lambda x: re.split('([a-zA-Z]+)/', str(x)))
    for i in x:
        master_list+=i
    words = tokenize_text(" ".join(master_list))
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = remove_only_numbers(words)
    words = remove_stopwords(words)
    words = remove_single_letters(words)
    master_list = pos_tagger(words)
    return sorted(list(set(master_list)))
    
def remove_similar_words(word_list, master_list):
    # Could replace double for-loops with itertools.combinations ?
    new_words = []
    stemmer = LancasterStemmer()
    for i in sorted(set(word_list)):
        x = []
        ii = re.sub("[^\w\s]","",i)
        ii = re.sub("_","",ii)
        ii = re.sub("[ ]"," ",ii)
        ii = stemmer.stem(ii)
        for j in sorted(master_list):
            jj = re.sub("[^\w\s]","",j.decode('UTF-8'))
            jj = re.sub("_","",jj)
            jj = re.sub("[ ]"," ",jj)
            if i[:3]==j[:3]:
                jj = stemmer.stem(jj)
                if ii == jj:
                    sim = nltk.edit_distance(i,j)
                    if sim > 1:
                        x.append(i)
                else:
                    x.append(i)
        x = list(set(x))
        new_words+=x
    new_words = list(set(new_words))
    master_list=list(set(master_list))
    new_words = [i for i in new_words if i not in master_list]
    master_list.extend(list(set(new_words)))
    return new_words, master_list

def clean_master_list(path):
    """Cleans Master list, Run this code after new terms are added to the list"""
    # This will clean the master list
    # Removes near similar words based on edit distance
    master_list = read_master_list(path)
    stemmer = LancasterStemmer()
    for i,j in itertools.combinations(master_list,2):
        if i[:3] == j[:3]:
            ii = stemmer.stem(str(i).decode('UTF-8'))
            jj = stemmer.stem(str(j).decode('UTF-8'))
            if ii == jj:
                dist1 = nltk.edit_distance(i[-3:], j[-3:], substitution_cost=1)
                if dist1 <= 1:
                    try:
                        print(i,j, dist1)
                        master_list.remove(i)
                    except ValueError as e:
                        pass

    return master_list

# This function should return 2 values
def get_word_frequency_from_cat(text, master_list, remove_similar=False):
    text = " ".join(text.split('|'))
    text = replace_contractions(text)
    words = tokenize_text(text)
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = remove_only_numbers(words)
    words = remove_stopwords(words)
    words = pos_tagger(words)
    words = remove_single_letters(words)
    if remove_similar:
        words, master_list = remove_similar_words(words, master_list)
    return words, master_list

def get_word_frequency_from_pn(text, master_list, remove_similar=False):
    text = " ".join(text.split(' '))
    text = replace_contractions(text)
    words = tokenize_text(text)
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = remove_only_numbers(words)
    words = remove_stopwords(words)
    words = pos_tagger(words)
    words = remove_single_letters(words)
    if remove_similar:
        words, master_list = remove_similar_words(words, master_list)
    return words, master_list

def get_word_frequency_from_pd(text, master_list, remove_similar=False):
    try:
        text = " ".join(str(text).split('|')[2:])
    except UnicodeEncodeError as e:
        pass
    text = replace_contractions(text)
    words = tokenize_text(text)
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = remove_only_numbers(words)
    words = remove_stopwords(words)
    words = pos_tagger(words)
    words = remove_single_letters(words)
    if remove_similar:
        words, master_list = remove_similar_words(words, master_list)
    return words, master_list

