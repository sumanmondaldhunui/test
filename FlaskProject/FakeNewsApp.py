
import numpy as np
from flask import Flask,render_template,request,url_for,redirect,flash
import pandas as pd

from sklearn.metrics import classification_report,  accuracy_score, confusion_matrix
import pickle
import newspaper
from newsapi import NewsApiClient
from newspaper import Article
import urllib
import nltk
nltk.download('punkt')

import requests
import string

import re
from PIL import Image

stopwords=nltk.corpus.stopwords.words('english')


#firebase 
import pyrebase

config={
    "apiKey": "AIzaSyC3lVXfWvl7x8zo3ih6CZ9L86Ldlq8s1gU",
    "authDomain": "fake-news-detector-14aea.firebaseapp.com",
    "databaseURL": "https://fake-news-detector-14aea.firebaseio.com",
    "projectId": "fake-news-detector-14aea",
    "storageBucket": "fake-news-detector-14aea.appspot.com",
    "messagingSenderId": "171126639865",
    "appId": "1:171126639865:web:18e81755e434f8de48e628"
}



firebase=pyrebase.initialize_app(config)

db=firebase.database()





app=Flask(__name__)


model1 = pickle.load(open('final_model_logR.sav', 'rb'))

model3 = pickle.load(open('final_model_passive.sav', 'rb'))
model4 = pickle.load(open('final_model_randomClassifier.sav', 'rb'))



news_url="https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=e24a845de6bf43c0ba007c03b39cc67a"

main_url=requests.get(news_url).json()

    
                                         
        

@app.route('/')
def index():

                             
                                          

    articles=main_url['articles']
    news=[]
    des=[]
    img=[]
    url=[]
    text=[]
    date=[]
    content=[]
   
   
    for i in range (len(articles)):
         myarticle=articles[i]
         news.append(myarticle['title'])
         des.append(myarticle['description'])
         img.append(myarticle['urlToImage'])
         url.append(myarticle['url'])
         date.append(myarticle['publishedAt'])
         
         
        

        
         

    for i in range (len(news)):
         myarticle=news[i]

         
         pre=model4.predict([myarticle])
         if (pre==True):
              text.append('Real')
         else:
             text.append('Fake')
        
   
   
    mylist=zip(news,des,img,url,text,date)

  
    return  render_template('home.html',context=mylist)   
        
   
    
    
   
    
    
@app.route('/about_us')
def about_us():
     return  render_template('aboutus.html')   





@app.route('/predection_result',methods=['GET', 'POST'])
def predection_result():
    g=[]
    b=[]
    img=[]
    g.append(request.args.get('news'))
    b.append(request.args.get('result'))
    img.append(request.args.get('img'))
    list=zip(b,g,img)
    
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            db.child("news").push({
				'news_text':g,
				'result':b
				
			 })
			
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
        

    
    return render_template('result.html',h=list) 
  

   
   
       
   

    
   

 


@app.route('/url_check',methods=["GET","POST"])
def url_check():
 url_format='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
 if request.method=="POST":
     url=request.form['q']
     
     if(re.search(url_format,url)):

         url=urllib.parse.unquote(url)
         article=Article(str(url))
         article.download()
        
         
         article.parse()
         article.nlp()
         news=article.text
         txt1="".join(c for c in news if c not in string.punctuation)

         tokens=re.split('\W+',txt1.lower())
         txt=" ".join([word for word in tokens if word not in stopwords])
  
         predict1=model1.predict([txt])
        
         predict3=model3.predict([txt])
         predict4=model4.predict([txt])
         

         final_predict=[predict1,predict3,predict4]
             
         x=True
         y=False

         k=int(final_predict.count(x))
         l=int(final_predict.count(y))
            
         if(k>l):
             a='Real'
             like= like='https://firebasestorage.googleapis.com/v0/b/fake-news-detector-14aea.appspot.com/o/like2.gif?alt=media&token=cd5df8d0-022a-44e0-bc1b-ea8b592e3aea'
             return  redirect(url_for('predection_result',news=news,result=a,img=like))
            
         elif (k==l):
             b='MostlyTrue'
             return  redirect(url_for('predection_result',news=news,result=b))
         else:
             c='Fake'
             dislike='http://aks.roshd.ir/photos/8.1207.medium.aspx'
             return  redirect(url_for('predection_result',news=news,result=c,img=dislike))
     else:
         
         return "invalid url"
              
         

@app.route('/textnews_check',methods=["GET","POST"])
def textnews_check():
 if request.method=="POST":
   
             str_feature=request.form['new']
        
             txt1="".join(c for c in str_feature if c not in string.punctuation)

             tokens=re.split('\W+',txt1.lower())
             txt=" ".join([word for word in tokens if word not in stopwords])
  

             predict1=model1.predict([txt])
             
             predict3=model3.predict([txt])
             predict4=model4.predict([txt])
             


             final_predict=[predict1,predict3,predict4]
             print(final_predict)
            
             x=True
             y=False

             k=int(final_predict.count(x))
             l=int(final_predict.count(y))
             
         
         
         
             if(k>l):
                 a='Real'
                 like='https://firebasestorage.googleapis.com/v0/b/fake-news-detector-14aea.appspot.com/o/like2.gif?alt=media&token=cd5df8d0-022a-44e0-bc1b-ea8b592e3aea'
            
             
                 return  redirect(url_for('predection_result',news=str_feature,result=a,img=like))
             elif (k==l):
                 b='MostlyTrue'
            
                 return  redirect(url_for('predection_result',news=str_feature,result=b))
             else:
                 c='Fake'
                 dislike='http://aks.roshd.ir/photos/8.1207.medium.aspx'
            
                 return  redirect(url_for('predection_result',news=str_feature,result=c,img=dislike))
        
              
     


  
        
         
         
   

    
        
     

       
       
        
         



if __name__ == "__main__":
    app.secret_key='SECRET KEY'
    app.run(port=5001,debug=True)