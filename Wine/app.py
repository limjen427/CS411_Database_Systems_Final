from getpass import getpass
from mysql.connector import connect, Error
from flask import Flask, render_template, request, redirect, url_for, session

#from flask_mysqldb import MySQL
#from flask_cors import CORS, cross_origin
#import MySQLdb.cursorsenv

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
            LIMIT 20
            """
    return try_query(query)

@app.route('/wine/user', methods = ['GET'])
def get_recipe_by_user():
    userID = request.args.get('userID')
    if userID is None:
        return "GET request malformed. Must include userID"
    query = """
            SELECT rat.ratingID, rec.name, rat.score, rat.review
	        FROM Rating rat NATURAL JOIN Wine rec
	        WHERE userID = """ + str(userID)
    return try_query(query)

# review
@app.route('/rating/create', methods = ['POST'])
def create_rating():
    ratingID = "NULL" #set to NULL to autogenerate a new ratingID
    wineID = request.args.get('wineID')
    score = request.args.get('score')
    review = request.args.get('review')
    review = "'" + review + "'"
    userID = request.args.get('userID')
    if None in [wineID, score, review, userID]:
        return "POST request malformed. Must include wineID, score, review, userID"
    query = """INSERT INTO Rating (ratingID, wineID, score, review, userID)
            VALUES (""" + ratingID + ", " + wineID + "," + score + ", " + review + ", " + userID + ")"
    return try_query(query)

@app.route('/rating/read', methods = ['GET'])
def read_rating():
    ratingID = request.args.get('ratingID')
    userID = request.args.get('userID')
    score = request.args.get('score')
    wineID = request.args.get('wineID')

    first_flag = False
    cond = " WHERE "

    if ratingID is not None:
        cond += "ratingID = " + ratingID
        first_flag = True
    
    if userID is not None:
        if first_flag == False:
            first_flag = True
        else:
            cond += " AND "
        cond += "userID = " + userID
    
    if score is not None:
        if first_flag == False:
            first_flag = True
        else:
            cond += " AND "
        cond += "socre = " + score
    
    if wineID is not None:
        if first_flag == False:
            first_flag = True
        else:
            cond += " AND "
        cond += "wineID = " + wineID

    query = "SELECT * FROM Rating"
    if first_flag == False:
        return try_query(query)
    else:
        print(query + cond)
        return try_query(query + cond)


@app.route('/rating/update', methods = ['PUT'])
def update_rating():
    ratingID = request.args.get('ratingID')
    if ratingID is None:
        return "UPDATE queries must contain a ratingID."
    score = request.args.get('score')
    review = request.args.get('review')
    # review = review

    first_flag = False
    fragment = " SET "
    if score is not None:
        fragment += "score = " + score
        first_flag = True
    
    if review is not None:
        if first_flag == False:
            first_flag = True
        else:
            fragment += ", "
        fragment += "review = " + review
    
    if first_flag == False:
        return "UPDATE queries must contain at least 1 value to update."
    query = "UPDATE Rating" + fragment + " WHERE ratingID = " + ratingID
    return try_query(query)

@app.route('/rating/delete', methods = ['DELETE'])
def delete_rating():
    ratingID = request.args.get('ratingID')
    if ratingID is None:
        return 'DELETE request malformed. Must include ratingID'
    query = 'DELETE FROM Rating WHERE ratingID = ' + ratingID
    return try_query(query)

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
            LIMIT 20
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
            LIMIT 40
            """
    return try_query(query)




if __name__ == '__main__':
    app.run()
