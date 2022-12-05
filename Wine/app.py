from getpass import getpass
from mysql.connector import connect, Error
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
from tabulate import tabulate
import os
import requests

app = Flask(__name__)
#CORS(app)
# CORS(app, support_credentials=True)
cursor = None

@app.route('/weather', methods=['GET'])
def POST_weather():
    weather_r = requests.get("https://api.weather.gov/gridpoints/ILX/95,71/forecast/hourly")
    weather_data = weather_r.json().get('properties').get('periods')

    weather = []

    for i in range(3):
        data = weather_data[i]
        startTime = data['startTime'][0:10] + ' ' + data['startTime'][11:13] + ':00:00'
        endTime = data['endTime'][0:10] + ' ' + data['endTime'][11:13] + ':00:00'
        temperature = data['temperature']
        shortForecast = data['shortForecast']

        weather.append({
            "forecastTime": startTime + " - " + endTime,
            "temperature": temperature,
            "shortForecast": shortForecast
        })

    return weather, 200

GET_LIMIT = 20



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

def try_procedure(query):
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
                cursor.callproc(query)
                ret = [r.fetchall() for r in cursor.stored_results()]

                #df = pd.DataFrame(results, columns=[i[0] for i in results.description])
                print("RET: " + str(ret))
                connection.commit()
    except Error as e:
        print("FAILED")
        ret = e
        print(ret)
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
        return [try_query(query), 'Your review is updated! The reviewID is ' + ratingIDtoedit + ' and the recorded userID is ' + userIDtoedit + '. Your new review message is ' + reviewtoedit]
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



@app.route('/wine/ranking', methods = ['GET'])
def refresh_rank():
    # query = '''
    #         CREATE TRIGGER bonus BEFORE INSERT ON Rating FOR EACH ROW
    #         BEGIN
    #             SET @bonus = (SELECT AVG(score)
    #                                 FROM Rating
    #                                 WHERE wineID = NEW.wineID);
    #             SET @price = (SELECT price FROM Wine WHERE wineID = NEW.wineID);
    #             IF (@bonus * 10 - @price < 0) THEN
    #                 UPDATE Wine
    #                 SET bonuspoints = 0
    #                 WHERE Wine.wineID = NEW.wineID;
    #             ELSE
    #                 UPDATE Wine
    #                 SET bonuspoints = @bonus * 10 - @price
    #                 WHERE Wine.wineID = NEW.wineID;
    #             END IF;
    #         END;
    #         '''
    # query = '''
    # CREATE PROCEDURE BestReviewer ()
    # BEGIN
    #     DECLARE finished INTEGER DEFAULT 0;
    #     DECLARE curuserID INTEGER DEFAULT 0;
    #     DECLARE curLengthSum INTEGER DEFAULT 0;
    #     DECLARE cur CURSOR FOR (SELECT userID, SUM(LENGTH(review)) \
    #         AS LengthSum FROM Rating NATURAL JOIN User GROUP BY userID);
    #     DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = 1;
    #     DROP TABLE IF EXISTS Ranking;
    #     CREATE TABLE Ranking (
    #         userID INT,
    #         userRank VARCHAR(255),
    #         LengthSum INT
    #     );

    #     OPEN cur;

    #     c: LOOP
    #         FETCH cur INTO curuserID, curLengthSum;
    #         IF finished = 1 THEN
    #             LEAVE c;
    #         END IF;
    #         IF curLengthSum < 5 THEN
    #             INSERT INTO Ranking VALUES (curuserID, 'Bronze', curLengthSum);
    #         ELSEIF curLengthSum >= 5 AND curLengthSum < 10 THEN
    #             INSERT INTO Ranking VALUES (curuserID, 'Silver', curLengthSum);
    #         ELSE
    #             INSERT INTO Ranking VALUES (curuserID, 'Gold', curLengthSum);
    #         END IF;
    #     END LOOP c;
    #     CLOSE cur;
    # SELECT userID, userRank, ratingCount FROM Ranking NATURAL JOIN (SELECT userID, COUNT(ratingID) AS ratingCount FROM Rating GROUP BY userID) AS joinedtable \
    #  ORDER BY LengthSum DESC;
    # END;
    # '''
    # return try_query(query)
    return try_procedure("BestReviewer")

if __name__ == '__main__':
    app.run()