import pickle
import pandas as pd
import requests
from flask import Flask, request, render_template, redirect
from random import randint


'''
Please download model from below link:
url: https://drive.google.com/drive/folders/1bOm5Aezrcs97k2jaaWK70cKvKmh4-8qU?usp=sharing
'''

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
movie_id = movies['movie_id'].values

app = Flask(__name__)


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=925be80231d3f71801573cc6870a83e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    id = data['id']
    name = data['original_title']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    link_data = "https://www.themoviedb.org/movie/{}-{}".format(id, name)
    return full_path, link_data

# https://click.justwatch.com/a?cx=eyJzY2hlbWEiOiJpZ2x1OmNvbS5zbm93cGxvd2FuYWx5dGljcy5zbm93cGxvdy9jb250ZXh0cy9qc29uc2NoZW1hLzEtMC0wIiwiZGF0YSI6W3sic2NoZW1hIjoiaWdsdTpjb20uanVzdHdhdGNoL2NsaWNrb3V0X2NvbnRleHQvanNvbnNjaGVtYS8xLTItMCIsImRhdGEiOnsicHJvdmlkZXIiOiJIb3RzdGFyIiwibW9uZXRpemF0aW9uVHlwZSI6ImZsYXRyYXRlIiwicHJlc2VudGF0aW9uVHlwZSI6InNkIiwiY3VycmVuY3kiOiJJTlIiLCJwcmljZSI6MCwib3JpZ2luYWxQcmljZSI6MCwiYXVkaW9MYW5ndWFnZSI6IiIsInN1YnRpdGxlTGFuZ3VhZ2UiOiIiLCJjaW5lbWFJZCI6MCwic2hvd3RpbWUiOiIiLCJpc0Zhdm9yaXRlQ2luZW1hIjpmYWxzZSwicGFydG5lcklkIjo2LCJwcm92aWRlcklkIjoxMjIsImNsaWNrb3V0VHlwZSI6Imp3LWNvbnRlbnQtcGFydG5lci1leHBvcnQtYXBpIn19LHsic2NoZW1hIjoiaWdsdTpjb20uanVzdHdhdGNoL3RpdGxlX2NvbnRleHQvanNvbnNjaGVtYS8xLTAtMCIsImRhdGEiOnsidGl0bGVJZCI6NjQ5NTcsIm9iamVjdFR5cGUiOiJtb3ZpZSIsImp3RW50aXR5SWQiOiJ0bTY0OTU3Iiwic2Vhc29uTnVtYmVyIjowLCJlcGlzb2RlTnVtYmVyIjowfX1dfQ&r=https%3A%2F%2Fwww.hotstar.com%2Fin%2F1660000015&uct_country=in


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    distances1 = sorted(list(enumerate(similarity[index])), key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    not_recommended_movie_names = []
    not_recommended_movie_posters = []
    not_recommended_movie_link = []
    recommended_movie_link = []
    for i in distances[1:10]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        image_link, trailer = fetch_poster(movie_id)
        recommended_movie_posters.append(image_link)
        recommended_movie_link.append(trailer)
        recommended_movie_names.append(movies.iloc[i[0]].title)

    for j in distances1[1:10]:
        # fetch the movie poster
        movie_id = movies.iloc[j[0]].movie_id
        image_link, trailer = fetch_poster(movie_id)
        not_recommended_movie_posters.append(image_link)
        not_recommended_movie_link.append(trailer)
        not_recommended_movie_names.append(movies.iloc[j[0]].title)

    return zip(recommended_movie_names,recommended_movie_posters,not_recommended_movie_names, not_recommended_movie_posters, recommended_movie_link, not_recommended_movie_link)


@app.route("/")
def index():
    ERROR = ""
    try:
        rcm = recommend(movie_list[randint(0, len(movie_list))])
        rcm = [i for i in rcm]
        my_collection = [[i[4], i[1]] for i in rcm]
        my_collection2 = [[i[5], i[3]] for i in rcm]
        datas = {"Trending Movies": my_collection, "You Might Like":my_collection2}
        return render_template("main.html", movies=movie_list, categories=datas, ERROR=ERROR)
    except Exception as E:
        print("ERROR: ", E)
        return redirect("/")


@app.route("/get_movie", methods=["GET", "POST"])
def recomend():
    if request.method == "POST":
        name = request.form["airports"]
        if name:
            # print("Name: ", name)
            ERROR = name
            rcm = recommend(name)
            rcm = [i for i in rcm]
            my_collection = [[i[4], i[1]] for i in rcm]
            my_collection2 = [[i[5], i[3]] for i in rcm]
            datas = {"Recomended Movies": my_collection, "Not Recomended Movies":my_collection2, "Today Selection":my_collection2}
            return render_template("main.html", movies=movie_list, categories=datas, ERROR=ERROR)
        else:
            ERROR = "Baklol ho kya, movie to select karo pahle."
            return redirect("/")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')