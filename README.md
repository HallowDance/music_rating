
# Music Rating

A web application to store and manage your music ratings.

## Features

- **User Authentication**: Secure login system to manage personal ratings.
- **Spotify Integration**: Fetches currently playing tracks from Spotify.
- **Rating System**: Allows users to rate and comment on songs.
- **Notification Service**: Notifies users about new releases from favorite artists.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/HallowDance/music_rating.git
   cd music_rating
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following content:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8080
   ```

5. **Run the Application**:
   ```bash
   flask run
   ```
   The application will be accessible at `http://127.0.0.1:5000/`.

## Usage

- **Home Page**: View a list of rated songs and their details.
- **Add a Rating**: Search for a song and add your rating and comments.
- **Spotify Sync**: Connect your Spotify account to fetch currently playing tracks.

## File Structure

```
music_rating/
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ...
├── .env
├── .gitignore
├── app.py
├── requirements.txt
├── ...
```

- `app.py`: The main Flask application file.
- `templates/`: HTML templates for rendering pages.
- `static/`: Static files like CSS and JavaScript.
- `requirements.txt`: List of Python dependencies.

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your_feature_name
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your_feature_name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/): A lightweight Python library for the Spotify Web API.
- [Flask](https://flask.palletsprojects.com/): A micro web framework written in Python.

