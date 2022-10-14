import streamlit as st
import spacy
import os
import lyricsgenius as lg
from annotated_text import annotated_text

genius_access_token = os.environ['GENIUS_ACCESS_TOKEN']

# genius object
genius = lg.Genius(genius_access_token)


# @st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def main():
    st.sidebar.image("./assets/book.png", width=120)
    st.sidebar.title('Instrumental')
    menu = ['Home', 'About']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.title("Find songs to practice with!")
        # Nav search form
        with st.form(key='searchform'):
            nav1, nav2, nav3, nav4 = st.columns([4, 3, 2, 1])

            with nav1:
                search_term = st.text_input("Select an artist", value="Pitty")
                mode = st.radio('Mode', ('Read', 'Highlight chosen structure', 'Fill in the blanks file'))
                submit_search = st.form_submit_button(label='Search')
            with nav2:
                selected_structures = st.selectbox("Select a grammar structure",
                                                   options=['Pronouns', 'Nouns', 'Verbs',
                                                            'Subject',
                                                            'Relative Pronouns',
                                                            'Verbs in Present Tense'])
            with nav3:
                selected_language = st.selectbox("Select a language", options=['pt', 'en'])

        models = load_models()
        selected_model = models[selected_language]
        with st.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                if submit_search:
                    st.success("Looking for {}'s songs containing {}.".format(search_term, selected_structures))
                    artist = genius.search_artist(search_term, max_songs=5, sort="popularity")
                    songs = artist.songs
                    for i in songs:
                        lyrics = i.lyrics
                        lines = lyrics.split('\n')
                        if mode == 'Read':
                            for line in lines:
                                if line.endswith("Embed"):
                                    line = line[:-5]
                                st.write(line)
                            st.download_button('Download File', lyrics)
                            break
                        elif mode == 'Fill in the blanks file':
                            exercise = ''
                            for line in lines:
                                doc = selected_model(line)
                                token_list = process_text(doc, selected_structures, blank=True, highlight=False)
                                for token in token_list:
                                    exercise = exercise + token + " "
                                exercise = exercise + '\n'
                            st.write(exercise)
                            st.download_button('Download File', exercise)
                            if "_" in exercise:
                                break
                        elif mode == 'Highlight chosen structure':
                            doc = selected_model(lyrics)
                            tokens = process_text(doc, selected_structures, blank=False, highlight=True)
                            annotated_text(*tokens)
                            break

    elif choice == 'About':
        st.title("About Instrumental")
        body = 'This app was created with language learners and teachers in mind.\nIn the language learning journey, especially in the early stages,' \
               'we find ourselves looking for fun ways to practice, but everything we find seems so... Difficult.\n ' \
               'Not anymore!\n ' \
               'Feel free to find song lyrics which contain exactly what you are currently learning.\n' \
               'Students, find songs and sing along!\n' \
               'Teachers, print some good-old feel-in-the-blanks exercises and have a fun class!\n\n'

        st.caption(body, unsafe_allow_html=False)
        coming_soon = 'Look forward to...\n\n' \
                      '- Dynamic fill-in-the-blanks exercises\n' \
                      '- Audio support\n' \
                      '- Listening comprehension exercises\n' \
                      '- More grammar structures\n' \
                      '- More songs\n' \
                      '- More languages!'

        st.subheader('Coming Soon')
        st.caption(coming_soon, unsafe_allow_html=False)

        st.subheader('Credits')
        credit = '- Lyrics: genius.com\n' \
                 '- NLP: Spacy\n' \
                 '- Logo: flaticon.com'
        st.caption(credit, unsafe_allow_html=False)

        st.subheader('Disclaimer')
        disclaimer = 'This app is a non-commercial, proof-of-concept project\n\n\n'
        st.caption(disclaimer, unsafe_allow_html=False)

        st.subheader('Contact')
        contact = 'luisa.ribeiro94@gmail.com'
        st.caption(contact, unsafe_allow_html=False)


def process_text(doc, selected_structures, blank=False, highlight=False):
    grammar_structures = {'Pronouns': 'PRON', 'Nouns': "NOUN", 'Verbs': 'VERB',
                          'Subject': 'nsubj', 'Relative Pronouns': 'PronType=Rel',
                          'Verbs in Present Tense': 'Tense=Pres'}
    structure = grammar_structures[selected_structures]
    tokens = []
    new_line = ''
    if blank:
        for token in doc:
            if token.pos_ == structure:
                space = ("____" * len(token.text))
                new_line = new_line + " " + space
            elif token.dep_ == structure:
                space = ("____" * len(token.text))
                new_line = new_line + " " + space
            elif structure in token.morph:
                space = ("____" * len(token.text))
                new_line = new_line + " " + space
            elif token.text.endswith('Embed'):
                word = token.text.replace('Embed', '')
                new_line = new_line + word + " "
            else:
                new_line = new_line + token.text + " "
        tokens.append(new_line)

    elif highlight:
        for token in doc:
            if token.pos_ == structure:
                tokens.append((token.text, structure, "#faa"))
            elif token.dep_ == structure:
                tokens.append((token.text, structure, "#afa"))
            elif structure in token.morph:
                tokens.append((token.text, structure, "#aaf"))
            elif token.text.endswith('Embed'):
                word = token.text.replace('Embed', '')
                tokens.append((" " + word + " "))
            else:
                tokens.append((" " + token.text + " "))

    return tokens


def load_models():
    portuguese_model = spacy.load("pt_core_news_lg-3.4.0/")
    english_model = spacy.load("en_core_web_sm-3.4.0")
    models = {"pt": portuguese_model, 'en': english_model}
    return models


if __name__ == '__main__':
    main()
