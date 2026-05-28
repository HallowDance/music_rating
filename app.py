from flask import Flask, render_template, request, redirect, flash, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import abort
import hmac
import json
import os
from spotify_api import create_spotify_client, get_currently_playing_song as get_spotify_now_playing
from jellyfin_api import create_jellyfin_client, get_currently_playing_song as get_jellyfin_now_playing
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load env variables
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

auth_username = os.getenv("FLASK_USERNAME")
auth_password = os.getenv("FLASK_PASSWORD")

# Which service to query for the "currently playing" track on the Add page.
# Supported: "spotify" (default), "jellyfin", or "none" to disable autofill.
now_playing_source = os.getenv("NOW_PLAYING_SOURCE", "spotify").strip().lower()


def fetch_currently_playing():
    """Return (title, artist) from the configured source, or (None, None).

    Network/credential/availability failures degrade gracefully so the Add
    page always renders.
    """
    try:
        if now_playing_source == "jellyfin":
            return get_jellyfin_now_playing(create_jellyfin_client())
        if now_playing_source == "spotify":
            return get_spotify_now_playing(create_spotify_client())
        # "none" or anything unrecognised: no autofill.
        return None, None
    except Exception as exc:
        app.logger.warning("Now-playing lookup (%s) failed: %s", now_playing_source, exc)
        return None, None


@auth.verify_password
def verify(username, password):
    # Constant-time comparison; both credentials must match the configured values.
    if (auth_username and auth_password
            and hmac.compare_digest(username, auth_username)
            and hmac.compare_digest(password, auth_password)):
        return username


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
@auth.login_required
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
    app.logger.info("store_song_info: %s - %s", title, artist)

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

        # Get the currently playing song from the configured source
        # (Spotify or Jellyfin). Degrades gracefully to empty fields when the
        # source is unavailable, so the Add page always renders.
        song_title, artist_name = fetch_currently_playing()

        # Render the add_song.html template and pass the currently playing song info as context variables
        return render_template('add_song.html', song_title=song_title,
                               artist_name=artist_name, source=now_playing_source.title())


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

    # Render the rating-distribution histogram, themed to match the UI.
    surface = '#221b18'
    text_color = '#ece7e3'
    grid_color = '#3a2c26'
    series = [
        ('Melody', [s['melody_rating'] for s in songs], '#ef4444'),
        ('Instrumentation', [s['instrumentation_rating'] for s in songs], '#f97316'),
        ('Storytelling', [s['storytelling_rating'] for s in songs], '#facc15'),
        ('Atmosphere', [s['atmosphere_rating'] for s in songs], '#ec4899'),
    ]

    bins = range(1, 12)  # one bin per integer rating 1..10
    fig, ax = plt.subplots(figsize=(9, 5), dpi=110)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)

    for label, data, color in series:
        ax.hist(data, bins=bins, alpha=0.55, label=label, color=color,
                edgecolor=surface, linewidth=1.2, align='left', rwidth=0.92)

    ax.set_xlabel('Rating', color=text_color, fontsize=11)
    ax.set_ylabel('Frequency', color=text_color, fontsize=11)
    ax.set_xticks(range(1, 11))
    ax.tick_params(colors=text_color)
    ax.grid(axis='y', color=grid_color, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(grid_color)

    legend = ax.legend(loc='upper right', frameon=True, facecolor='#2c2320',
                       edgecolor=grid_color, labelcolor=text_color)

    fig.tight_layout()
    fig.savefig('static/histogram.png', facecolor=surface)
    plt.close(fig)

    return render_template('statistics.html', num_songs=num_songs,
                           total_average=total_average,
                           melody_std_dev=melody_std_dev,
                           instrumentation_std_dev=instrumentation_std_dev,
                           storytelling_std_dev=storytelling_std_dev,
                           atmosphere_std_dev=atmosphere_std_dev,
                           total_production_bonus=total_production_bonus,
                           production_bonus_std_dev=production_bonus_std_dev)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)

