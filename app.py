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


# @st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)

def main():
    menu = ['Home', 'About']
    choice = st.sidebar.selectbox("Menu", menu)

    st.title("Instrumental""\nLearn with music!")

    if choice == "Home":
        # Nav search form
        with st.form(key='searchform'):
            nav1, nav2 = st.columns([2, 1])

            with nav1:
                search_term = st.text_input("Select an artist")
            with nav2:
                submit_search = st.form_submit_button(label='Search')

        selected_language = st.sidebar.selectbox("Select a language", options=['pt'])
        selected_structures = st.sidebar.selectbox(
            "Select a grammar structure",
            options=['PRON', 'NOUN', 'VERB'])
        models = load_models()
        selected_model = models[selected_language]
        st.success("Looking for {}'s songs with {}.".format(search_term, selected_structures))
        blank = st.checkbox("Blank?")
        col1, col2 = st.columns([2, 1])
        with col1:
            if submit_search:
                artist = genius.search_artist(search_term, max_songs=3, sort="title")
                songs = artist.songs
                for i in songs:
                    title = i.title
                    doc = selected_model(i.lyrics)
                    tokens = process_text(doc, title, selected_structures, blank=blank)
                    annotated_text(*tokens)
                    if len(tokens) > 0:
                        break


def process_text(doc, title, selected_structures, blank=False):
    tokens = []
    for token in doc:
        if token.pos_ == selected_structures:
            tokens.append((" " + "___" * len(token.text) + " "))
        else:
            tokens.append((" " + token.text + " "))
    return tokens


def load_models():
    portuguese_model = spacy.load("./models/pt/")
    models = {"pt": portuguese_model}
    return models


if __name__ == '__main__':
    main()
