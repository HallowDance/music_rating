from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.exceptions import abort
import json
import os
from spotify_api import create_spotify_client, get_currently_playing_song
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


# Store song information in memory
stored_song_info = {"title": "", "artist": ""}

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        melody_rating = int(request.form["melody_rating"])
        instrumentation_rating = int(request.form["instrumentation_rating"])
        storytelling_rating = int(request.form["storytelling_rating"])
        atmosphere_rating = int(request.form["atmosphere_rating"])
        production_bonus_rating = float(request.form["production_bonus_rating"])

        # Add the new song to the list of songs
        new_song = {
            "title": title,
            "artist": artist,
            "melody_rating": melody_rating,
            "instrumentation_rating": instrumentation_rating,
            "storytelling_rating": storytelling_rating,
            "atmosphere_rating": atmosphere_rating,
            "production_bonus_rating": production_bonus_rating,
        }
        songs.append(new_song)

        # Save the updated list of songs back to the JSON file
        with open("songs_data.json", "w") as file:
            json.dump(songs, file)

        # Update the stored_song_info dictionary with the new song information
        stored_song_info["title"] = title
        stored_song_info["artist"] = artist

        # Calculate the average rating
        average_rating = (
            (melody_rating + instrumentation_rating + storytelling_rating + atmosphere_rating) / 4
            + production_bonus_rating
        ) / 5

        return redirect(url_for("index"))

    return render_template("index.html", song_info=stored_song_info, songs=songs)


@app.route("/store_song_info", methods=["POST"])
def store_song_info():
    data = request.form
    title = data.get("title")
    artist = data.get("artist")
    print(title, artists)

    if title and artist:
        stored_song_info["title"] = title
        stored_song_info["artist"] = artist

        return "Song information stored successfully.", 200

    return "Failed to store song information.", 400

@app.route('/add', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        # This block of code will execute when the form is submitted with data (POST request).
        # It handles adding the new song to the songs list.

        # Retrieve the form data
        title = request.form['title']
        artist = request.form['artist']
        melody_rating = int(request.form['melody'])
        instrumentation_rating = int(request.form['instrumentation'])
        storytelling_rating = int(request.form['storytelling'])
        atmosphere_rating = int(request.form['atmosphere'])
        production_bonus_rating = float(request.form['production_bonus'])

        # Check if the song already exists in the list
        for song in songs:
            if song['title'] == title and song['artist'] == artist:
                flash(f"The song '{title}' by {artist} already exists in the list.")
                return redirect('/add')

        # Create a new song dictionary with the provided details and ratings
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

        # Redirect to the homepage after adding the song
        return redirect('/')
    else:
        # This block of code will execute when the form is requested (GET request).
        # It displays the form where users can add a new song.

        # Get the currently playing song info from Spotify API
        sp = create_spotify_client()
        song_title, artist_name = get_currently_playing_song(sp)
        print(song_title, artist_name)

        # Render the add_song.html template and pass the currently playing song info as context variables
        return render_template('add_song.html', song_title=song_title, artist_name=artist_name)


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

