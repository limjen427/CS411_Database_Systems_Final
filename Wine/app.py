from getpass import getpass
from mysql.connector import connect, Error
from flask import Flask, render_template, request, redirect, url_for, session
import random
from tabulate import tabulate

GET_LIMIT = 20

app = Flask(__name__)
#CORS(app)
# CORS(app, support_credentials=True)
cursor = None

def try_query(query):
    try:
        with connect(
            host="35.202.126.9",
            user="root",
            password="Cksals6815!",
            database="wineDB"
        ) as connection:
            with connection.cursor() as cursor:
                if query[0:3] == "GET":
                    query += " LIMIT " + GET_LIMIT
                print("trying query: " + query)
                cursor.execute(query)
                ret = cursor.fetchall()
                connection.commit()
    except Error as e:
        ret = e
    return str(ret)


@app.route("/")
def main():
    # ing_query = "SELECT * FROM Wine LIMIT 5"
    # return try_query(ing_query)
    return render_template("index.html")

@app.route("/wineSearch.html")
def wineSearchHTML():
    return render_template("wineSearch.html")

@app.route("/newReview.html")
def newReviewHTML():
    return render_template("newReview.html")

@app.route("/oldReview.html")
def oldReviewHTML():
    return render_template("oldReview.html")

@app.route("/wine/all", methods = ['GET'])
def get_wine_all():
    query = """
            SELECT wineID, name
            FROM Wine
            """
    return try_query(query)

@app.route('/wine/search', methods=['GET'])
def search_wine():
    search = request.args.get('search')
    query = "SELECT * FROM Wine WHERE name Like '%" + search + "%'"
    return try_query(query)

# review
@app.route('/rating/create', methods = ['GET'])
def create_rating():
    # ratingID = "NULL" #set to NULL to autogenerate a new ratingID
    wineID = str(request.args.get('wineID'))
    score = str(request.args.get('score'))
    review = str(request.args.get('review'))
    review = "'" + review + "'"
    userID = str(request.args.get('userID'))
    ratingID = str(random.randint(405001, 999999999))
    if None in [wineID, score, review, userID]:
        return "POST request malformed. Must include wineID, score, review, userID"
    # query = """INSERT INTO Rating (ratingID, wineID, score, review, userID)
    #         VALUES ((SELECT COUNT(*) FROM Rating) + 405001), wineID, """ + score + "","" + review + "," + userID + ")"
    query = "INSERT INTO Rating (ratingID, wineID, score, review, userID) VALUES \
        (" + ratingID + ", " + wineID + ", " + score + ", " + review + ", " + userID + ")"
    return [try_query(query), 'Thank you for your review! Your ratingID is ' + str(ratingID) + ', and the recorded userID is ' + str(userID)]

@app.route('/rating/edit', methods = ['GET'])
def edit_rating():
    wineIDtoedit = str(request.args.get('wineID'))
    ratingIDtoedit = str(request.args.get('ratingID'))
    scoretoedit = str(request.args.get('score'))
    reviewtoedit = str(request.args.get('review'))
    reviewtoedit = "'" + reviewtoedit + "'"
    userIDtoedit = str(request.args.get('userID'))
    if len(wineIDtoedit) == 0 or len(ratingIDtoedit) == 0:
        return "Error. You must include both wineID and ratingID to edit or delete your review!"
    if len(scoretoedit) + len(reviewtoedit) - 2 + len(userIDtoedit) == 0:
        query = "DELETE FROM Rating WHERE ratingID = " + ratingIDtoedit
        return [try_query(query), 'Your review is deleted!']
    else:
        query = "UPDATE Rating SET wineID = " + wineIDtoedit + \
            ", score = " + scoretoedit + ", review = " + reviewtoedit + ", userID = " + userIDtoedit + " WHERE ratingID = " + ratingIDtoedit
        return [try_query(query), 'Your review is updated! The reviewID is ' + ratingIDtoedit + ' and the recorded userID is ' + userIDtoedit]
    return None

@app.route('/wine/avgRating', methods = ['GET'])
def get_avgRating_wine():
    query = """
            SELECT w.name, ROUND(AVG(r.score),2) AS AverageRating
            FROM Wine w NATURAL JOIN Rating r JOIN User u on r.userID = u.userID
            WHERE u.userID IN (
                SELECT ux.userID
                FROM Rating rx Natural JOIN User ux
                GROUP BY ux.userID
            )
            GROUP BY wineID
            """
    return try_query(query)

@app.route('/wine/best', methods = ['GET'])
def get_cheap_best_wine():
    query = """
            SELECT w.name, w.price, sub.avgScore, w.points
            FROM Wine w JOIN (
                SELECT wineID, AVG(score) as avgScore
                FROM Rating
                GROUP BY wineID
            ) as sub ON w.wineID = sub.wineID
            WHERE w.price < 20 AND w.points >= 90 AND sub.avgScore >= 4
            """
    return try_query(query)




if __name__ == '__main__':
    app.run()
