import os
import sqlite3
import streamlit as st

# Database setup
def get_db_connection():
    """Create a database connection with proper error handling."""
    try:
        # Ensure the database path is absolute and in a writable directory
        db_path = os.path.join(os.getcwd(), 'songs.db')
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def init_db():
    """Initialize the database with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
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
        return True
    except sqlite3.Error as e:
        st.error(f"Error initializing database: {e}")
        return False

def add_song_to_db(title, picture, added_by, url):
    """Add a song to the database with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        c = conn.cursor()
        c.execute('INSERT INTO songs (title, picture, added_by, votes, url) VALUES (?, ?, ?, 0, ?)', 
                  (title, picture, added_by, url))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Error adding song: {e}")
        return False

def get_songs_from_db():
    """Retrieve songs from the database with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        
        c = conn.cursor()
        c.execute('SELECT id, title, picture, added_by, votes, url FROM songs ORDER BY votes DESC')
        songs = c.fetchall()
        conn.close()
        return songs
    except sqlite3.Error as e:
        st.error(f"Error retrieving songs: {e}")
        return []

def vote_for_song_in_db(song_id):
    """Vote for a song with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        c = conn.cursor()
        c.execute('UPDATE songs SET votes = votes + 1 WHERE id = ?', (song_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Error voting for song: {e}")
        return False

# Ensure database is initialized
if init_db():
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
            if add_song_to_db(title, picture_data, added_by, url):
                st.success("Song added successfully!")
                # Rerun to refresh the page and show the new song
                st.experimental_rerun()
            else:
                st.error("Failed to add song. Please try again.")
        else:
            st.error("Title and Name are required!")

    # Display all songs
    st.header("Song Playlist")
    songs_data = get_songs_from_db()

    if not songs_data:
        st.write("No songs in the playlist yet. Add your first song!")

    for song in songs_data:
        song_id, song_title, song_picture, song_added_by, song_votes, song_url = song
        
        # Create a container for each song
        song_container = st.container()
        with song_container:
            st.subheader(song_title)
            
            # Display image if exists
            if song_picture:
                try:
                    st.image(song_picture, width=100)
                except Exception as e:
                    st.error(f"Error displaying picture: {e}")
            
            # Display URL if exists
            if song_url:
                st.write(f"[Listen here]({song_url})")
            
            st.write(f"Added by: {song_added_by}")
            st.write(f"Votes: {song_votes}")
            
            # Vote button
            if st.button(f"Vote for {song_title}", key=f"vote_{song_id}"):
                if vote_for_song_in_db(song_id):
                    st.success(f"Voted for {song_title}!")
                    # Rerun to refresh the vote count
                    st.experimental_rerun()
else:
    st.error("Failed to initialize database. Please check permissions and try again.")
