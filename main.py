import os
from flask import Flask, render_template, Response
from camera import Video
import glob
import random
from flask_jsonpify import jsonpify

app = Flask(__name__)
root_path = os.path.dirname(os.path.abspath(__file__))
folders = ["Happy", "Sad", "Neutral"]
global folder_count
camera = Video()


def get_songs(folder):
    songs = []
    path = f"{root_path}/static/songs/{folder}"
    song_list = os.listdir(path)
    thumbnail_list = [path.replace(f"{root_path}", "") for path in glob.glob(f'{root_path}/static/img/thumbnails/*.jpg')]
    for song in song_list:
        song_dict = {'name': song.replace('.mp3', ''), 'path': f"/static/songs/{folder}/{song}", 'folder': folder,
                     'thumbnail':random.choice(thumbnail_list)}
        songs.append(song_dict)
    return songs


def generate_video():
    while True:
        try:
            print(camera.get_label())
            frame = camera.get_frame(reset_predictions=False)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            continue


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/music", methods=["GET", "POST"])
def music():
    songs = get_songs(random.choice(folders))
    print(songs[0])
    return render_template('musicPlayer.html', song=songs[0], reset=camera.reset_label())


@app.route("/musicapi", methods=["GET", "POST"])
def musicapi():
    playlist = max(zip(camera.get_label().values(), camera.get_label().keys()))[1]
    songs = get_songs(playlist)
    JSONP_data = jsonpify(random.choice(songs))
    camera.reset_label()
    return JSONP_data


@app.route("/video", methods=["GET", "POST"])
def video():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)

