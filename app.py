import streamlit as st
import spacy
import os
from time import sleep
import json
import spotipy
import lyricsgenius as lg
from annotated_text import annotated_text

genius_access_token = os.environ['GENIUS_ACCESS_TOKEN']

# genius object
genius = lg.Genius(genius_access_token)

#@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)

def main():
    menu = ['Home', 'About']
    choice = st.sidebar.selectbox("Menu", menu)

    st.title("Instrumental""\nLearn with music!")

    if choice == "Home":
        #Nav search form
        with st.form(key='searchform'):
            nav1, nav2 = st.columns([2,1])

            with nav1:
                search_term = st.text_input("Select an artist")
            with nav2:
                submit_search = st.form_submit_button(label='Search')

        selected_language = st.sidebar.selectbox("Select a language", options=['pt'])
        selected_structures = st.sidebar.multiselect(
            "Select which grammar structures you want to practice",
            options=['PRON', 'NOUN', 'VERB'],
            default=['PRON', 'NOUN', 'VERB'])
        models = load_models()
        selected_model = models[selected_language]
        st.success("Looking for {}'s songs with {}.".format(search_term,selected_structures))
        blank = st.checkbox("Blank?")
        col1, col2 = st.columns([2,1])
        with col1:
            if submit_search:
                artist = genius.search_artist(search_term, max_songs=1, sort="title")
                songs = artist.songs
                #st.write(songs)
                for i in songs:
                    st.write(i.title)
                    st.write(i.lyrics)
                    doc = selected_model(i.lyrics)
                    #with st.button("Song")
                    tokens = process_text(doc, blank=blank)
                    annotated_text(*tokens)

def process_text(doc, blank=False):
    tokens = []
    for token in doc:
        if token.pos_ == "NOUN":
            tokens.append((token.text, "Noun", "#faa"))
        elif token.pos_ == "VERB":
            tokens.append((token.text, "Verb", "#fda"))
        elif token.pos_ == "PRON":
            tokens.append((token.text, "Pron", "#afa"))
        else:
            tokens.append(" " + token.text + " ")

        if blank:
            blank_tokens = []
            for token in tokens:
                if type(token) == tuple:
                    blank_tokens.append(("_" * len(token[0]), token[1], token[2]))
                else:
                    blank_tokens.append(token)
            return blank_tokens
    return tokens

def load_models():
    portuguese_model = spacy.load("./models/pt/")
    models = {"pt": portuguese_model}
    return models


if __name__ == '__main__':
	main()
