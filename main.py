import os
import sqlite3
import streamlit as st

# Database setup with migration support
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

def migrate_db():
    """Migrate database schema to latest version."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        c = conn.cursor()
        
        # Check existing columns
        c.execute("PRAGMA table_info(songs)")
        columns = [column[1] for column in c.fetchall()]
        
        # Add missing columns if not exist
        if 'url' not in columns:
            try:
                c.execute('ALTER TABLE songs ADD COLUMN url TEXT')
            except sqlite3.OperationalError:
                # Column might already exist or can't be added
                pass
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Error migrating database: {e}")
        return False

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
        
        # Attempt migration
        return migrate_db()
    except sqlite3.Error as e:
        st.error(f"Error initializing database: {e}")
        return False

def add_song_to_db(title, picture, added_by, url=None):
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

def edit_song_in_db(song_id, title=None, picture=None, url=None):
    """Edit a song in the database with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        c = conn.cursor()
        # Prepare update query dynamically based on provided parameters
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append('title = ?')
            params.append(title)
        
        if picture is not None:
            update_fields.append('picture = ?')
            params.append(picture)
        
        if url is not None:
            update_fields.append('url = ?')
            params.append(url)
        
        if not update_fields:
            st.error("No update fields provided")
            return False
        
        # Add song_id to params
        params.append(song_id)
        
        # Execute update
        query = f'UPDATE songs SET {", ".join(update_fields)} WHERE id = ?'
        c.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Error editing song: {e}")
        return False

def delete_song_from_db(song_id):
    """Delete a song from the database with error handling."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        c = conn.cursor()
        c.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Error deleting song: {e}")
        return False

# Ensure database is initialized
if init_db():
    # Streamlit app
    st.title("Song Playlist Voting")

    # Sidebar for navigation
    menu = st.sidebar.selectbox("Menu", ["Add Song", "View Playlist", "Edit/Delete Songs"])

    def display_playlist():
        """Display the playlist regardless of the menu selection."""
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
                        st.experimental_rerun()

    if menu == "Add Song":
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
                else:
                    st.error("Failed to add song. Please try again.")
            else:
                st.error("Title and Name are required!")
        display_playlist()

    elif menu == "View Playlist":
        display_playlist()

    elif menu == "Edit/Delete Songs":
        st.header("Edit or Delete Songs")
        
        # Fetch songs for editing/deleting
        songs_data = get_songs_from_db()
        
        if not songs_data:
            st.write("No songs in the playlist to edit or delete.")
        else:
            # Create a selectbox to choose a song to edit/delete
            song_options = [f"{song[1]} (Added by {song[3]})" for song in songs_data]
            selected_song_index = st.selectbox("Select a song to edit or delete", 
                                               range(len(song_options)), 
                                               format_func=lambda x: song_options[x])
            
            # Get the selected song's details
            selected_song = songs_data[selected_song_index]
            song_id, song_title, song_picture, song_added_by, song_votes, song_url = selected_song
            
            # Edit section
            st.subheader("Edit Song Details")
            new_title = st.text_input("New Title (leave blank to keep current)", value=song_title)
            new_url = st.text_input("New URL (leave blank to keep current)", value=song_url or "")
            new_picture = st.file_uploader("Upload a New Picture (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"])
            
            # Edit button
            if st.button("Update Song"):
                picture_data = None
                if new_picture:
                    picture_data = new_picture.read()
                
                # Prepare update parameters
                update_params = {
                    'title': new_title if new_title != song_title else None,
                    'picture': picture_data if new_picture else None,
                    'url': new_url if new_url != song_url else None
                }
                
                # Only pass non-None values
                filtered_params = {k: v for k, v in update_params.items() if v is not None}
                
                if filtered_params:
                    if edit_song_in_db(song_id, **filtered_params):
                        st.success("Song updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update song.")
            
            # Delete section
            st.subheader("Delete Song")
            if st.button("Delete this Song", type="primary"):
                # Confirm deletion
                if st.checkbox("I confirm I want to delete this song"):
                    if delete_song_from_db(song_id):
                        st.success("Song deleted successfully!")
                        #st.experimental_rerun()

        display_playlist()

else:
    st.error("Failed to initialize database. Please check permissions and try again.")
