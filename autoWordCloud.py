"""
Automate My Life's Word Cloud Generator
=======================================
---Objective --------------------------
Create a web-crawler that ingests a url,
retrieves the words from said url
and generates a word cloud image
---------------------------------------
The Process
1. Create a simple web crawler
2. Save words to a file
3. Process a colored input image
4. Output a wordCloud
---------------------------------------
"""

import os
import pandas as pd
import numpy as np

#imports for web crawling
import urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup

#imports for manipulating words
import nltk
from nltk.tokenize import sent_tokenize

#imaging stuff
import cv2
import imutils

##imports for wordcloud
from os import path
from PIL import Image
import seaborn
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS



#initialize some arrays you will use
visitedLinks = []
badList = ["WORDS and PHRASES THAT YOU USE TO HELP WEED OUT CRAWLING EFFORT"
          ]

def openPageGetSource(url):
    """opens a url and ingests the sites source code"""
    try:
        soup = urlopen(url).read()
    except Exception,e:
        print str(e)
        
    #save the source code just in case you want to run offline
    saveFile = open('source.txt','w')
    saveFile.write(soup)
    saveFile.write('\n')
    saveFile.close()
    
    return soup

def getGrayImage(imageFname):
    """this converts any color image to binary - black and white - for wordcloud"""
    imagePath = os.path.join(os.getcwd(),'imgs',imageFname)
    im_gray = cv2.imread(imagePath,cv2.CV_LOAD_IMAGE_GRAYSCALE)
    im_gray = imutils.resize(im_gray,width=1000)

    #this calculates the threshold for you and makes it black and white
    (thresh, im_bw) = cv2.threshold(im_gray,128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    #bw image is great but wordcloud assigns words to black space - need inverse
    mask_inv = cv2.bitwise_not(im_bw)

    #cv2.imshow('Orig',im_gray)
    #cv2.imshow('Gray',im_bw)
    #save to call the files
    outF1 = os.path.join(os.getcwd(),"imgs","gray_"+imageFname)
    outF2 = os.path.join(os.getcwd(),"imgs","bw_"+imageFname)
    cv2.imwrite(outF1,im_gray)
    cv2.imwrite(outF2,mask_inv)
    

def getWordCloud(textInput,imageFname):
    """this ingests a word csv and image file name to create a wordcloud"""
    d = os.getcwd()

    # Read the whole text.
    text = open(path.join(d,textInput)).read()
    
    # make the mask image
    getGrayImage(imageFname)
    
    # taken from
    img_mask = np.array(Image.open(path.join(d,'imgs','bw_'+imageFname)))

    stopwords = set(STOPWORDS)
    stopwords.add("said") #add any extra stopwords
    stopwords.add("repositories")

    #inputs for wordcloud
    wc = WordCloud(background_color="white", max_words=20000, mask=img_mask,
                   stopwords=stopwords)
    
    # generate word cloud
    wc.generate(text)

    # store to file
    wc.to_file(path.join(d,'imgs','wc_'+imageFname))

    # show
    plt.imshow(wc)
    plt.axis("off")
    plt.figure()
    plt.imshow(img_mask, cmap=plt.cm.gray)
    plt.axis("off")
    plt.show()



def mineWebsite(randomURL,imageFname):
    """this should take a url input and return a txt file with words in it"""

    """
    #uncomment if you want to run offline
    with open('source.txt','r') as f:
        sourceCode = f.read()
        f.close()
    """

    #arrays that we will write to
    aLinks = []
    pContent = []
    wordArray = []

    c = 0
    #i only want to run it once
    if c <= 1:
        #get the page
        sourceCode = openPageGetSource(randomURL)
        soup = BeautifulSoup(sourceCode)
        #print soup.prettify()
        
        for a in soup.body.find_all('a', href=True):
            link = a['href']
            #first level data check
            if link not in visitedLinks and link not in badList and "automatemylife.org" in link and "-" in link and "category" not in link:
                #second level data check
                if "#" not in link:
                    print "Found --> ",link
                    #limit switch if you only want the original website
                    #otherwise, this will take all the a hrefs from the website you visit
                    #and keep going to the number
                    stopNum = 0
                    if c <= stopNum:
                        c +=1
                        
                        #follow link to get new sourcecode
                        linkContent = openPageGetSource(link)
                        linkSC = BeautifulSoup(linkContent)
                        print "Fetched source from --> ",link
                        
                        #add this link to the visited list
                        visitedLinks.append(link)
                        print "\n-------------",link
                        
                        for p in linkSC.find_all('p'):
                            if p.string is not None:
                                print "Tokenizing...."
                                print p.string
                                
                                #add to the words to content array
                                tokens = nltk.word_tokenize(p.string)
                                
                                #running list of links
                                for t in tokens:
                                    if t not in badList:
                                        #print t
                                        try:
                                            a = str(t) #should weed out any ascii fails
                                            wordArray.append(t)
                                        except Exception,e:
                                            print str(e) #this is due to ascii fail
                                    else:

                                        pass
                                    
                        #add the words to a dataframe
                        DF = pd.DataFrame(wordArray,columns=['Tokens'])
                        #print DF

                        #make a quick graph
                        DF['Count'] = 1
                        a = DF.groupby('Tokens').sum().reset_index()
                        b = a[a['Count']>1]
                        print b
                        b= b.sort('Count',ascending=False)
                        ax = b.plot(kind='bar',stacked=False)
                        ax.set_ylabel('Frequency')
                        ax.set_xticklabels(b['Tokens'].values)
                        plt.show()
                        
                        
                        #send to an output file -- or this could be a DB
                        DF.to_csv('outputTest.csv')

                        #go get the wordCloud based on the input image
                        print "Getting wordCloud...."
                        getWordCloud("outputTest.csv",imageFname)

                        del DF #delete df so you can rewrite over it
                        os.remove('outputTest.csv')
                        
                    else:
                        print "Sorry, I only run one at a time"
   
    else:
        print "Finished"

        
#inputs to start wordcloud
randomURL = "ENTER YOUR URL HERE"
imageFname = "PICTURE FILENAME HERE"
mineWebsite(randomURL,imageFname)
