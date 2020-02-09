# Change-Tumblr-Archive
Changes a Tumblr archive page, replacing liked posts with hearts

Do you collect images of a narrow interest on Tumblr?
Are you tired of seeing hundred times the same image,
but you do not want to see just original posts of a blog
to do not miss reblogs you have not seen yet?
My solution replaces posts you already liked 
with heart symbol, so you can find new posts quicker!

![Example of the original and output page](https://imgur.com/a/Vmgj5Ye)

***

This script for Python 3 has two parts:                     
                                                                
[s] Scrapes image links from given tumblr blog's archive until you stop it with Esc or it reaches end of month after scraping 
given minimum number of posts. Posts which are not images are replaced by image of X. Image links are saved into archivePosts.txt.                                           
                                                                 
[p] Loads archivePosts.txt and goes through the links to determine which posts you liked. Liked posts are replaced by heart symbol and archive page is saved as output.html.                                             
                                                                
It requires your tumblr login information.                  
Please fill variables in settings.py                                                                                                                 
                                                                
***

<b>Steps to use this script</b>

1. install Python 3
2. download change_tumblr_archive.py and settings.py
3. edit settings.py with your information
4. run the script. The script will open itself its own browser and start its work.
if you are running the script first time:
you need to install required python packages.
If you do not know which packages you need, just try to run the script through command line, and it will tell you what you are missing.


<b>Common problems</b>

The script immediately ended with a message: "Session not created: This version of ChromeDriver only supports Chrome version.."! Check what is your version of Chrome and get the correct ChromeDriver from https://chromedriver.chromium.org/downloads and put it into C:/Windows (if you're running Windows).




