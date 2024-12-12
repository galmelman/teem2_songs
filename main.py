import streamlit as st

# In-memory storage for songs
songs = []

# Function to add a new song
def add_song(title, picture, added_by):
    if not title or not added_by:
        return {'error': 'Title and added_by are required'}

    song = {
        'id': len(songs) + 1,
        'title': title,
        'picture': picture,
        'added_by': added_by,
        'votes': 0
    }
    songs.append(song)
    return {'message': 'Song added successfully', 'song': song}

# Function to get all songs
def get_songs():
    return {'songs': songs}

# Function to vote for a song
def vote_song(song_id):
    for song in songs:
        if song['id'] == song_id:
            song['votes'] += 1
            return {'message': 'Vote added', 'song': song}

    return {'error': 'Song not found'}

# Streamlit app
st.title("Song Playlist Voting")

# Add a new song
st.header("Add a New Song")
title = st.text_input("Song Title")
picture = st.file_uploader("Upload a Picture (optional)", type=["png", "jpg", "jpeg"])
added_by = st.text_input("Your Name")

if st.button("Add Song"):
    picture_url = None
    if picture:
        picture_url = f"data:image/jpeg;base64,{picture.getvalue().decode('latin1')}"
    result = add_song(title, picture_url, added_by)
    if 'error' in result:
        st.error(result['error'])
    else:
        st.success(result['message'])

# Display all songs
st.header("Song Playlist")
songs_data = get_songs()['songs']
for song in songs_data:
    st.subheader(song['title'])
    if song['picture']:
        st.image(song['picture'], width=100)
    st.write(f"Added by: {song['added_by']}")
    st.write(f"Votes: {song['votes']}")
    if st.button(f"Vote for {song['title']}", key=f"vote_{song['id']}"):
        vote_result = vote_song(song['id'])
        if 'error' in vote_result:
            st.error(vote_result['error'])
        else:
            st.success(vote_result['message'])
