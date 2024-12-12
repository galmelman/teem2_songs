from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for songs
songs = []

# Route to add a new song
@app.route('/add_song', methods=['POST'])
def add_song():
    data = request.json
    title = data.get('title')
    picture = data.get('picture', '')
    added_by = data.get('added_by')

    if not title or not added_by:
        return jsonify({'error': 'Title and added_by are required'}), 400

    song = {
        'id': len(songs) + 1,
        'title': title,
        'picture': picture,
        'added_by': added_by,
        'votes': 0
    }
    songs.append(song)
    return jsonify({'message': 'Song added successfully', 'song': song}), 201

# Route to get all songs
@app.route('/get_songs', methods=['GET'])
def get_songs():
    return jsonify({'songs': songs}), 200

# Route to vote for a song
@app.route('/vote_song/<int:song_id>', methods=['POST'])
def vote_song(song_id):
    for song in songs:
        if song['id'] == song_id:
            song['votes'] += 1
            return jsonify({'message': 'Vote added', 'song': song}), 200

    return jsonify({'error': 'Song not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
