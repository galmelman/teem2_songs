import sqlite3
import streamlit as st

# Database setup
def init_db():
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        picture BLOB,
        added_by TEXT NOT NULL,
        votes INTEGER DEFAULT 0,
        url TEXT
    )''')
    conn.commit()
    conn.close()

def add_song_to_db(title, picture, added_by, url):
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('INSERT INTO songs (title, picture, added_by, votes, url) VALUES (?, ?, ?, 0, ?)', (title, picture, added_by, url))
    conn.commit()
    conn.close()

def get_songs_from_db():
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT id, title, picture, added_by, votes, url FROM songs')
    songs = c.fetchall()
    conn.close()
    return songs

def vote_for_song_in_db(song_id):
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('UPDATE songs SET votes = votes + 1 WHERE id = ?', (song_id,))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Streamlit app
st.title("Song Playlist Voting")

# Add a new song
st.header("Add a New Song")
title = st.text_input("Song Title")
picture = st.file_uploader("Upload a Picture (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"])
url = st.text_input("Song URL (optional, e.g., from SUNO)")
added_by = st.text_input("Your Name")

if st.button("Add Song"):
    picture_data = None
    if picture:
        picture_data = picture.read()
    if title and added_by:
        add_song_to_db(title, picture_data, added_by, url)
        st.success("Song added successfully!")
    else:
        st.error("Title and Name are required!")

# Display all songs
st.header("Song Playlist")
songs_data = get_songs_from_db()
for song in songs_data:
    song_id, song_title, song_picture, song_added_by, song_votes, song_url = song
    st.subheader(song_title)
    if song_picture:
        st.image(song_picture, width=100)
    if song_url:
        st.write(f"[Listen here]({song_url})")
    st.write(f"Added by: {song_added_by}")
    st.write(f"Votes: {song_votes}")
    if st.button(f"Vote for {song_title}", key=f"vote_{song_id}"):
        vote_for_song_in_db(song_id)
        st.success(f"Voted for {song_title}!")
