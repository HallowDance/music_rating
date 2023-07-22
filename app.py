from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Set the secret key for flash messages
app.secret_key = 'samosex_prostosex'  # Replace 'your_secret_key' with a secure secret key


# Check if the JSON file exists
if os.path.exists('songs_data.json'):
    # If the file exists and is not empty, load the data from it
    with open('songs_data.json', 'r') as file:
        try:
            songs = json.load(file)
        except json.decoder.JSONDecodeError:
            # If the file is empty or contains invalid JSON, initialize with an empty list
            songs = []
else:
    # If the file does not exist, initialize with an empty list
    songs = []


@app.route('/')
def index():
    return render_template('index.html', songs=songs)


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        # Check if the song with the same title and artist already exists
        existing_song = next((song for song in songs if song['title'] == title and song['artist'] == artist), None)
        if existing_song:
            flash('This song already exists in the database.', 'error')
        else:
            melody_rating = int(request.form['melody_rating'])
            instrumentation_rating = int(request.form['instrumentation_rating'])
            storytelling_rating = int(request.form['storytelling_rating'])
            atmosphere_rating = int(request.form['atmosphere_rating'])
            production_bonus_rating = float(request.form['production_bonus_rating'])

            new_song = {
                'title': title,
                'artist': artist,
                'melody_rating': melody_rating,
                'instrumentation_rating': instrumentation_rating,
                'storytelling_rating': storytelling_rating,
                'atmosphere_rating': atmosphere_rating,
                'production_bonus_rating': production_bonus_rating
            }

            songs.append(new_song)

            # Save the updated data back to the JSON file
            with open('songs_data.json', 'w') as file:
                json.dump(songs, file)

            flash('Song added successfully!', 'success')

            return redirect(url_for('index'))

    return render_template('add_song.html')

@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    song = songs[song_id - 1]

    if request.method == 'POST':
        # Form handling to update the song details and ratings
        title = request.form['title']
        artist = request.form['artist']
        melody_rating = int(request.form['melody_rating'])
        instrumentation_rating = int(request.form['instrumentation_rating'])
        storytelling_rating = int(request.form['storytelling_rating'])
        atmosphere_rating = int(request.form['atmosphere_rating'])
        production_bonus_rating = float(request.form['production_bonus_rating'])

        # Update the song with the modified details and ratings
        song['title'] = title
        song['artist'] = artist
        song['melody_rating'] = melody_rating
        song['instrumentation_rating'] = instrumentation_rating
        song['storytelling_rating'] = storytelling_rating
        song['atmosphere_rating'] = atmosphere_rating
        song['production_bonus_rating'] = production_bonus_rating

        # Save the updated data back to the JSON file
        with open('songs_data.json', 'w') as file:
            json.dump(songs, file)

        return redirect(url_for('song_detail', song_id=song_id))

    return render_template('song_detail.html', song=song, song_id=song_id)


@app.route('/song_detail/<int:song_id>')
def song_detail(song_id):
    song = songs[song_id - 1]
    return render_template('song_detail.html', song=song, song_id=song_id)

# app.py

# ... (existing code)

@app.route('/statistics')
def statistics():
    # Calculate statistics
    num_songs = len(songs)
    if num_songs > 0:
        melody_ratings = [song['melody_rating'] for song in songs]
        instrumentation_ratings = [song['instrumentation_rating'] for song in songs]
        storytelling_ratings = [song['storytelling_rating'] for song in songs]
        atmosphere_ratings = [song['atmosphere_rating'] for song in songs]
        production_bonus_ratings = [song['production_bonus_rating'] for song in songs]

        total_average = sum((melody_ratings + instrumentation_ratings +
                            storytelling_ratings + atmosphere_ratings)) / (4 * num_songs)

        production_bonus_sum = sum(production_bonus_ratings)
        total_production_bonus = production_bonus_sum / num_songs

        # Calculate standard deviation
        def calculate_standard_deviation(ratings_list, average):
            return (sum((rating - average) ** 2 for rating in ratings_list) / len(ratings_list)) ** 0.5

        melody_std_dev = calculate_standard_deviation(melody_ratings, total_average)
        instrumentation_std_dev = calculate_standard_deviation(instrumentation_ratings, total_average)
        storytelling_std_dev = calculate_standard_deviation(storytelling_ratings, total_average)
        atmosphere_std_dev = calculate_standard_deviation(atmosphere_ratings, total_average)
        production_bonus_std_dev = calculate_standard_deviation(production_bonus_ratings, total_production_bonus)
    else:
        total_average = 0
        melody_std_dev = 0
        instrumentation_std_dev = 0
        storytelling_std_dev = 0
        atmosphere_std_dev = 0
        total_production_bonus = 0
        production_bonus_std_dev = 0

    # Calculate the histogram data
    num_bins = 10
    plt.figure(figsize=(8, 6))
    plt.hist([song['melody_rating'] for song in songs], bins=num_bins, alpha=0.5, label='Melody')
    plt.hist([song['instrumentation_rating'] for song in songs], bins=num_bins, alpha=0.5, label='Instrumentation')
    plt.hist([song['storytelling_rating'] for song in songs], bins=num_bins, alpha=0.5, label='Storytelling')
    plt.hist([song['atmosphere_rating'] for song in songs], bins=num_bins, alpha=0.5, label='Atmosphere')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.title('Average Rating Histogram')
    plt.legend(loc='upper right')

    # Save the histogram plot to a file (optional)
    plt.savefig('static/histogram.png')

    return render_template('statistics.html', num_songs=num_songs,
                           total_average=total_average,
                           melody_std_dev=melody_std_dev,
                           instrumentation_std_dev=instrumentation_std_dev,
                           storytelling_std_dev=storytelling_std_dev,
                           atmosphere_std_dev=atmosphere_std_dev,
                           total_production_bonus=total_production_bonus,
                           production_bonus_std_dev=production_bonus_std_dev)

if __name__ == '__main__':
    app.run(debug=True)

