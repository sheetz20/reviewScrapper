from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
# import csv

app = Flask(__name__)

@app.route('/', methods=['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route("/review",methods=['POST','GET'])
@cross_origin()
def index():
    if request.method == "POST":
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            soup = BeautifulSoup(flipkartPage,"html.parser")
            bigboxes = soup.find_all('div',{"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = BeautifulSoup(prodRes.text,'html.parser')
            # print(prod_html)
            commentboxes = prod_html.find_all('div',{"class": "_16PBlm"})
            # print(commentboxes.prettify())
            # filename = searchString + ".csv"
            # fw = open(filename, "w")
            # csv_writer = csv.writer(fw)
            # # headers = "Product, Customer Name, Rating, Heading, Comment \n"
            # csv_writer.writerow(["Product", "Customer", "Name", "Rating", "Heading", "Comment"])
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = "No Name"
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = "No Rating"
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = "No Comment Heading"
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}

                reviews.append(mydict)
                # csv_writer.writerow([searchString, name, rating, commentHead, custComment])
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)