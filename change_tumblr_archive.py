#!/usr/bin/env python

##################################################################
#    9.2.2020                         Author: Michaela Honkova   #
##################################################################
#                                                                #
#    This script for Python 3 has two parts:                     #
#                                                                #
#    [s] Scrapes image links from given tumblr blog's archive    #
#    until you stop it with Esc or it reaches end of month       #
#    after scraping given minimum number of posts.               #
#    Posts which are not images are replaced by image of X.      #
#    Image links are saved into archivePosts.txt.                #
#                                                                # 
#    [p] Loads archivePosts.txt and goes through the links       #
#    to determine which posts you liked. Liked posts are         #
#    replaced by heart symbol and archive page is saved          #
#    as output.html.                                             #
#                                                                #
#    It requires your tumblr login information.                  #
#    Please fill variables in settings.py                        #                                                                                          
#                                                                #
##################################################################

# Import requests
import requests
from lxml import html
from bs4 import BeautifulSoup
from pathlib import Path
import os.path
from itertools import count
import time
import msvcrt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
import sys   
import settings #settings.py

# Performs login to Tumblr site with the credentials given above
def login_tumblr(driver):
    # login page
    wait = WebDriverWait(driver, 10)
    url = "http://www.tumblr.com/login"      
    driver.get(url)    
    # enter email
    e_email = driver.find_element_by_xpath("//input[@id='signup_determine_email']")
    e_email.clear()
    e_email.send_keys(settings.LOGIN) 
    # tap Next
    e_next = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class=\"signup_determine_btn active\"]")))
    e_next.click()
    # tap Use password to log in
    e_usepass = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class=\"magiclink_password_container chrome\"]")))
    e_usepass.click()    
    # insert password
    e_pwd = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='signup_password']")))
    e_pwd.clear()
    e_pwd.send_keys(settings.PASSWORD) 
    # tap Login
    e_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class=\"signup_login_btn active\"]")))
    e_login.click()
    # get cookies
    wait.until(lambda driver: driver.find_element_by_xpath("//nav[@id=\"post_buttons\"]"))
    return True
 

# Scrapes current page of tumbls blog/archive for images
# Returns a dictionary of posts permalinks and image links.
# Posts which are not images are replaced by image of X.
def scrape_archive_page(source):
    soup = BeautifulSoup(source, "lxml") 
    pagePosts = dict() #dictionary
    #all posts        
    divs = soup.find_all("div", attrs={"class": "J9VCO"})
    for div in divs:
        #one post:
        
        #posts image
        img = 'https://i.imgur.com/QTO2GYi.png' #post is not image: X
        divs3 = div.find_all("img", attrs={"class": "_28CuW _31Nl5"}) 
        for div3 in divs3:       
            imgs = div3['srcset'].split()  
            img = imgs[-2:-1]
            img = img[0] #posts image            
        #posts permalink
        divs2 = div.find_all("a", attrs={"class": "_1qux2 _2kYk1"})
        for div2 in divs2:
            link = div2['href']
        #add to output 
        pagePosts[link] = img
    return pagePosts  

# Determines which month of the archive is currently being loaded:
# the last month mentioned at currently loaded page
def last_month_loaded(source):
    soup = BeautifulSoup(source, "lxml")
    months = soup.find_all("h2", attrs={"class": "_3LoFw"})
    return months[-1].text

# Repeatedly scrapes the blog/archive page until user presses Esc 
# or it it has min_count posts and reached the end of month.
# We cant load the whole page and then start grabbing links, all the
# posts not currently on screen would be just blank gradient squares.
# This is why we have to grab links/images on each scrolldown  
def scrape_archive(driver):
    archivePosts = dict() #dictionary
    count = 0
    new_month = ' '
    print("Starting to scrape. Press <Esc> to stop scrolling.")
    while True:
        # scrape page for posts
        pagePosts = scrape_archive_page(driver.page_source)   
        
        # attach new posts to archivePosts dict
        for post in pagePosts:
            #print(post)                 #key=link
            #print(pagePosts[post])      #value=img      
            if post not in archivePosts:
                archivePosts[post] = pagePosts[post]   
                count += 1

        # detect months 
        old_month = new_month
        new_month = last_month_loaded(driver.page_source)
        print(f"Scraping {new_month}, total {count} posts so far")

        # stop if we reached scraping goal (at least minimum posts and end of month)
        if count > settings.MIN_COUNT and old_month != new_month:
            print(f"Reached at least {settings.MIN_COUNT} posts and finished the month. Stopping at start of {new_month}") 
            break
            
        # scroll down   
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        
        # stop on Esc key
        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 27: #until <Esc> press
                break

    # write out info
    print(f"{count} posts were scraped.") 
    print(f"Last month detected was {new_month}.") 
    return archivePosts
 
# Load archivePosts back from given text file
def load_archivePosts_file(fPath):
    archivePosts = dict() #dictionary
    count = 0
    with open(fPath, 'r+') as fIn:
        for line in fIn:
            recs = line.split()
            link = recs[0]
            img = recs[1]
            archivePosts[link] = img
            count += 1
    print(f"{count} posts were loaded.")
    return archivePosts

# Open one post and determine if it was Liked already or not.
# There are two of four buttons at the top strip depending on if post was liked or not.
#
# button1 = soup.find_all("button", attrs={"class": "tx-icon-button like-button"})       
# button2 = soup.find_all("button", attrs={"class": "tx-icon-button unlike-button  hidden"})       
# button3 = soup.find_all("button", attrs={"class": "tx-icon-button like-button hidden"})       
# button4 = soup.find_all("button", attrs={"class": "tx-icon-button unlike-button"})           
#
# not liked:  [xxx][][][]    
# liked:      [][][xxx][xxx]  
#
def post_is_liked(post,driver): 
    # posts permalink 
    print(post)     
    # load post
    driver.get(post)
    body = driver.page_source
    soup = BeautifulSoup(body, "lxml")    
    # load the upper strip with Line/Unlike buttons
    frameLink = soup.find("iframe")["src"]  
    driver.get(frameLink)  
    body = driver.page_source   
    soup = BeautifulSoup(body, "lxml")    
    #if 'like button' is in the code, the post was not yet liked 
    button1 = soup.find_all("button", attrs={"class": "tx-icon-button like-button"}) 
    if not button1: 
        print('Already liked!')
        return True
    else: 
        print('Not liked!') 
        return False


if __name__ == '__main__':

    # write out info
    print('Welcome to archive scraper for tumblr.')
    print(f'The blog of interest is {settings.BLOG}')
    
    # user chooses action
    while True:
        action_choice = input("Scrape archive for links [s] or process last scraped links into html output [p]?")
        if action_choice in ['s','p']:
            break
        else:
            print('Invalid selection.')

    # setup browser
    directory = Path(__file__).parents[0]    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    prefs = {'download.default_directory' : str(directory)}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)   
    login_tumblr(driver)
    cookies = driver.get_cookies()

    # scrape archive for image links and save them into archivePosts.txt
    if action_choice == 's':
    
        # get blogs archive page
        driver.get(settings.BLOG)
        time.sleep(3)

        # cookies consent
        try:
            e_consent = driver.find_element_by_xpath("//button[@class='btn yes']")
            e_consent.click()
        except NoSuchElementException:
            pass
        
        # scrape archive page repeatedly
        archivePosts = scrape_archive(driver)

        # write archivePosts to output text file  
        with open(os.path.join(directory, 'archivePosts.txt'), 'w+') as fOut:
            for link, img in archivePosts.items():
                fOut.write(str(link)+' '+str(img) +'\n')
        print('Output file archivePosts.txt was written.')

        # ask user if he wants to continue with second part
        new_choice = input("Process the scraped links into html output [y/n]?")
        if new_choice == 'y':
            action_choice = 'p'      

    # go through archivePosts.txt to determine liked images and generate output.html
    if action_choice == 'p':

        #load file into archivePosts
        archivePosts = load_archivePosts_file(os.path.join(directory, 'archivePosts.txt'))
        count = len(archivePosts)

        #get ready to write the output    
        #write finished archivePosts to output file
        with open(os.path.join(directory, 'output.html'), 'w+') as fOut:    
                    
            #open each posts pernament link separately to decide which i liked
            num = 0
            for post in archivePosts:
                # open post and find if i liked it    
                liked = post_is_liked(post,driver)
                # if I liked it, change its image to heart
                if liked:  
                    archivePosts[post] = "https://i.imgur.com/pdDaTBV.png" #post already liked: <3   
                #write finished archivePost to output file
                link = post                  #key=link
                img = archivePosts[post]     #value=img   
                fOut.write('<a href="'+str(link)+'"><img src="'+str(img)+'" style="width: 200px;" /></a>\n')

                num += 1
                print(str(num) +'/' +str(count))  

        print('Output file was written.') 

    # end    
    input('Keypress to END.')
    driver.quit()
