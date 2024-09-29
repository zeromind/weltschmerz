from flask import Flask, escape, request, render_template, redirect
import weltschmerz.anime as anime
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", default="sqlite:///:memory:"
)
_sqlalchemy_echo = os.environ.get("SQLALCHEMY_ECHO", default="False")
app.config["SQLALCHEMY_ECHO"] = _sqlalchemy_echo.lower() in {"1", "true"}
dbs = anime.DatabaseSession(
    app.config["SQLALCHEMY_DATABASE_URI"], app.config["SQLALCHEMY_ECHO"]
)


@app.route("/anime/<int:anime_id>/files", methods=["GET"])
def anime_files(anime_id: int) -> str:
    (directory, baseurl) = get_anime_path(anime_id)
    files = (
        dbs.session.query(anime.LocalFile)
        .filter_by(directory=directory)
        .order_by(anime.LocalFile.filename)
        .all()
    )
    # return '\n'.join([ local_file.filename for local_file in files ])
    return render_template(
        "anime_files.html",
        anime_id=anime_id,
        directory=directory,
        baseurl=baseurl,
        files=files,
    )


@app.route("/file/ed2k/<string:ed2k>", methods=["GET"])
def file_by_ed2k(ed2k: str):
    file: anime.LocalFile = (
        dbs.session.query(anime.LocalFile).filter_by(hash_ed2k=ed2k).first()
    )
    try:
        if file.directory.startswith("/vintergatan/anime/by-id/"):
            return redirect(
                os.path.join(file.directory.replace("/vintergatan", ""), file.filename)
            )
        else:
            return f"no access to {file.directory}", 403
    except AttributeError:
        return "got nothin", 404


@app.route("/screenshots/", methods=["GET"])
@app.route("/screenshots/<int:anime_id>", methods=["GET"])
def screenshots(anime_id: int = None) -> str:
    if anime_id == None:
        anime_list = (
            dbs.session.query(anime.TitleScreenShot)
            .join(anime.Anime)
            .distinct(anime.Anime.aid)
            .join(anime.Episode)
            .all()
        )
        return render_template("anime_list_screenshots.html", anime_list=anime_list)
    else:
        show_source_details = request.args.get("details", default=0, type=int)
        (directory, baseurl) = get_screenshot_path(anime_id)
        screenshots = (
            dbs.session.query(anime.TitleScreenShot)
            .filter_by(aid=anime_id)
            .join(anime.Episode)
            .order_by(
                anime.Episode.ep,
                anime.TitleScreenShot.time_position,
                anime.TitleScreenShot.source_file_name,
            )
            .all()
        )
        return render_template(
            "screenshots.html",
            anime_id=anime_id,
            directory=directory,
            baseurl=baseurl,
            screenshots=screenshots,
            show_source_details=show_source_details,
        )


@app.route("/screenshots/file/<int:file_id>", methods=["GET"])
def file_screenshots(file_id: int) -> str:
    screenshots = (
        dbs.session.query(anime.TitleScreenShot)
        .filter_by(fid=file_id)
        .join(anime.Episode)
        .order_by(
            anime.TitleScreenShot.time_position,
        )
        .all()
    )
    return render_template(
        "file_screenshots.html",
        file_id=file_id,
        screenshots=screenshots,
    )


@app.route("/screenshots/episode/<int:episode_id>", methods=["GET"])
def episode_screenshots(episode_id: int) -> str:
    screenshots = (
        dbs.session.query(anime.TitleScreenShot)
        .filter_by(eid=episode_id)
        .join(anime.Episode)
        .order_by(
            anime.TitleScreenShot.time_position,
        )
        .all()
    )
    return render_template(
        "episode_screenshots.html",
        episode_id=episode_id,
        screenshots=screenshots,
    )


def get_anime_path(
    anime_id: int,
    url_basedir: str = "/anime",
    anime_basedir: str = "/vintergatan/anime",
    anime_id_pad_width: int = 6,
    anime_id_chunk_size: int = 2,
):
    anime_id_padded = str(anime_id).zfill(anime_id_pad_width)
    anime_id_path = [
        anime_id_padded[i : i + anime_id_chunk_size]
        for i in range(0, anime_id_pad_width, anime_id_chunk_size)
    ]
    return (
        os.path.join(anime_basedir, "by-id", *anime_id_path),
        os.path.join(url_basedir, "by-id", *anime_id_path),
    )


def get_screenshot_path(
    anime_id: int,
    url_basedir: str = "/screenshots",
    screenshot_basedir: str = "/anime/screenshots",
    anime_id_pad_width: int = 6,
    anime_id_chunk_size: int = 2,
):
    anime_id_padded = str(anime_id).zfill(anime_id_pad_width)
    anime_id_path = [
        anime_id_padded[i : i + anime_id_chunk_size]
        for i in range(0, anime_id_pad_width, anime_id_chunk_size)
    ]
    return (
        os.path.join(screenshot_basedir, "by-id", *anime_id_path),
        os.path.join(url_basedir, "by-id", *anime_id_path),
    )
