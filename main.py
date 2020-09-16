import atexit
import bs4
import concurrent.futures 
import datetime
import os 
import pprint
import random 
import requests
import re
import sys
import sqlite3
import time 
import tempfile 
import threading 
import urllib.request
import webbrowser

from bs4 import BeautifulSoup
from jikanpy import Jikan
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QAction, QCompleter
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


#Instance of our Jikan class which allows for communication with the Jikan MyAnimeList API. This is the foundation of this application
jikan = Jikan()

#Here the directory is set to the current directory from which we're running the Python script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

tmp_path = dname + '/tmp'

#Create the temporary directory if it doesn't already exist
if not os.path.exists(tmp_path):  
    os.makedirs(tmp_path)

#The path of our temp folder which will store files that will be wiped after closing the app
tmp_directory = tempfile.TemporaryDirectory(dir=tmp_path) 


###########* This is the Model class through which all functions that respond to changes in the  UI exist *##################
class Model(QtWidgets.QMainWindow):
    

    def __init__(self):
        super(Model, self).__init__()
    
    ###########* SQLITE DB functions *###########
    
    #* Establish connection with SQLITE DB
    def dbConnect(self):
        
        self.dbPath()
        
        try:
            self.connection = sqlite3.connect('weebguidance.db')
            self.cursor = self.connection.cursor()
            return self.connection
            
        except ConnectionError as error:
            print(error)
        
    #* DB directory    
    def dbPath(self):
        self.db_path = dname + '/db'
        
        if not os.path.exists(self.db_path):  
            os.makedirs(self.db_path)
            
        os.chdir(self.db_path)
        
    #*Create a DB table for the completed series    
    def createTable(self, connection, collection_list):
        
        self.connection = connection
        self.collection_list = collection_list
        
        self.cursor = self.connection.cursor()
        
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS completed (
                                        title_id integer PRIMARY KEY,
                                        title text NOT NULL
                                    ); ''')
            print('table created')
            self.connection.commit()
            
            self.displayCollection(self.cursor, self.collection_list)
            
        except TypeError as error:
            print(error)
            print('Cannot form DB connection')
        
        
        
    #* Adds series to the SQLite Database
    def addSeries(self, search_bar, collection_list):
        
        self.dbPath()
        
        self.id = 1
        self.row_id_count = []
        self.row_title_count = []
        self.search_bar = search_bar
        self.title = self.search_bar.text()

        try:
            #Form a connection to the DB
            self.connection = sqlite3.connect('weebguidance.db')
            self.cursor = self.connection.cursor()

            #If there's a response from the connection then proceed
            if self.cursor is not None:
                #Try to enter the default index + value. If the index or title already exists then this should catch it
                try:
                    self.cursor.execute("INSERT INTO completed VALUES (?,?)", (self.id, self.title))
                    self.connection.commit()
                    
                except sqlite3.IntegrityError as error:
                    
                    #Fill list with returned title ids
                    for self.row in self.cursor.execute("SELECT * FROM completed"):
                        self.row_title_count.append(self.row[1])
                    
                    if self.title in self.row_title_count:
                            print('duplicate entry detected')
                    else:
                        #Fill list with returned title strings
                        for self.row in self.cursor.execute("SELECT * FROM completed"):
                            self.row_id_count.append(self.row[0])
                            
                        #Find the largest title id in the database and add 1 to it
                        self.max_title_id = self.row_id_count[-1]
                        self.id += self.max_title_id
        
                        self.cursor.execute("INSERT INTO completed VALUES (?,?)", (self.id, self.title))
                        self.connection.commit()
                        self.displayCollection(self.cursor, self.collection_list)
                        
        except:        
            print(error)
                
        finally:
            self.connection.close()
            
     #*Remove the series selected from the QList and the database       
    def removeSeries(self, search_field, collection_list):
        
        self.search_field = search_field
        self.search_value = search_field.text()
        self.collection_list = collection_list
        self.collection_list = self.collection_list
        self.items = []
        
        if search_field.text() is None:
            print('Please Enter text value')
            
        else:
            try:
                #Form a connection to the DB
                self.connection = sqlite3.connect('weebguidance.db')
                self.cursor = self.connection.cursor()
                self.cursor.execute("DELETE FROM completed WHERE title=?", (self.search_value,))
                self.connection.commit()
                self.displayCollection(self.cursor, self.collection_list)


            except ConnectionError as error:
                print(error)
            
            finally:
                self.connection.close()
         
                #########################################################################* 
                  
    #* Update the collection menu search field based on the user's selection on the Qlist
    def updateField(self, search_field, collection_list):
        self.dbPath()
            
        self.search_field = search_field
        self.collection_list = collection_list
        
        
        self.selected_list = self.collection_list.selectedItems()
        self.title = self.selected_list[0].text()
        self.list_row = self.collection_list.row(self.selected_list[0])
        
        self.search_field.setText(self.title)
        

    #* Displays the results of the completed table on the list widget           
    def displayCollection(self, cursor, collection_list ):
        self.collection_list = collection_list
        self.cursor = cursor
        
        self.collection_list.clear()
                
        try:
        
            for self.row in self.cursor.execute("SELECT * FROM completed"):
                self.collection_list.insertItem(self.row[0], self.row[1])
            
            self.collection_list.sortItems()
    
        except TypeError as error:
            print(error)
        
    
    #* Makes a request to the webpage and returns a request code. This will be used to test the vailidity of URLs 
    #Animixplay returns a page with an html error embedded in the html, so this method works better than pinging the webpage
    def pingURL(self, search_url):

        #Make a request to the webpage and use BeautifulSoup to search for a 404 error or signs of one being loaded
        self.search_url = search_url
        self.request = requests.get(self.search_url)
        self.source = self.request.content
        self.soup = BeautifulSoup(self.source, 'html.parser')
        self.error_span = self.soup.find('span', class_ = 'animetitle')
        
        if self.error_span.text == 'Generating...' or self.error_span.text == '404 Not Found':
            return False

        else:
            return True
    
    #* Displays the current connectivity of the API to the user based on the status messages that are retunred by the jikan API
    def apiStatus(self, text_edit):
        self.text_edit = text_edit
        
        try:
            self.code = urllib.request.urlopen('https://api.jikan.moe/v3').getcode()
            
            if str(self.code) == '200':
                self.text_edit.setText(f'Status Code: {str(self.code)} [OK] - Connection successful')
                
            elif str(self.code) == '304':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Not Modified]- You have the latest data')
                
            elif str(self.code) == '400':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Bad Request] - An invalid request has been made')
                
            elif str(self.code) == '404':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Not Found] - Resource not found')
                
            elif str(self.code) == '405':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Method Not Allowed] - requested method is not supported for resource ')
                
            elif str(self.code) == '429':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Too Many Requests] - You are being rate limited or JIkan is being rate limited by MyAnimeList ')

            elif str(self.code) == '500':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Internal Server Error] - Something is wrong (Jikan API Error)')
                
            elif str(self.code) == '503':
                self.text_edit.setText(f'Status Code: {str(self.code)} [Service Unavailable] - Something is not working on MyAnimeList\'s end')

            
        except:
            self.text_edit.setText('A Connection could not be established at this time. Please Check Connectivity and try again.')
            
    #* Creates the search URL that will be used to search for the web page of a specific series
    def createSearchURL(self, search_string):

        # TODO: Wrap this in a try catch to account for failed connections
    
        self.search_string = search_string
        #If the search string has any blank spaces separating the words then it will trigger this set of if else statements to match animixplay's search strings
        if ' ' in self.search_string:
            self.search_list = self.search_string.split()  
            self.animix_search_token = '-'.join(self.search_list)
            self.setAnimixToken(self.animix_search_token) #Storing this token for later use
            self.search_url = f'https://animixplay.com/v1/{self.animix_search_token.lower()}'
            
            self.response = self.pingURL(self.search_url)
            

            if self.response == True:
                return self.search_url
            
            else:
                #Remove any characters that aren't alphanumerical and join the string 
                self.count = 0
                
                for self.string in self.search_list:
                    #Join alphanumerics
                    self.new_string = ''.join(self.character for self.character in self.string if self.character.isalnum())
                    #If a new string has been created, replace the original
                    if self.new_string:
                        self.search_list[self.count] = self.new_string
                        
                    self.count += 1
                    
                self.animix_search_token = '-'.join(self.search_list) 
                self.setAnimixToken(self.animix_search_token) #Storing this token for later use
                self.search_url = f'https://animixplay.com/v1/{self.animix_search_token.lower()}'
                self.response = self.pingURL(self.search_url)
            

                if self.response == True:
                    return self.search_url 
                else:

                    #Removes the colon from the second word. This is a pretty specific replacement
                    self.second_word = self.search_list[1]
                    if ':' in self.second_word:
                        self.second_word = self.second_word.replace(':', '') # TODO: double-check this is actually working


                    self.animix_search_token = self.search_list[0] + '-' + self.second_word + '-'
                    self.search_url = f'https://animixplay.com/v1/{self.animix_search_token}'
                    self.response = self.pingURL(self.search_url)
                    self.setAnimixToken(self.animix_search_token)

                    if self.response == True:
                        return self.search_url
                    
                    #Replace colons with blank space
                    else:
                        self.search_list = search_string.split()
                        self.count = 0
                        for self.word in self.search_list:
                            if ':' in self.word:
                                self.new_word = self.word.replace(':', '')
                                self.search_list[self.count] = self.new_word
                            else:
                                self.count += 1
                        self.animix_search_token = '-'.join(self.search_list)
                        self.setAnimixToken(self.animix_search_token)
                        self.search_url = f'https://animixplay.com/v1/{self.animix_search_token.lower()}'
                        self.response = self.pingURL(self.search_url)

                        if self.response == True:
                            return self.search_url
                        
                        #Try using the v4 link address as opposed to the v1 link address
                        else:
                            self.search_url = f'https://animixplay.com/v4/4-{self.animix_search_token.lower()}'
                            self.response = self.pingURL(self.search_url)

                            if self.response == True:
                                return self.search_url
        
        else:
            self.search_url = f'https://animixplay.com/v1/{self.search_string.lower()}'
            self.setAnimixToken(self.search_string.lower())
            self.response = self.pingURL(self.search_url)

            if self.response == True:
                return self.search_url
            
            else:
                self.search_url = f'https://animixplay.com/v4/4-{self.search_string.lower()}'
                self.setAnimixToken(self.search_string.lower())
                self.response = self.pingURL(self.search_url)
                
                if self.response == True:
                    return self.search_url
            
                else:
                    #Replace non alphanumerical characters with a dash
                    self.search_string = re.sub('[^A-Za-z0-9]+', '-', self.search_string)
                    self.search_url = f'https://animixplay.com/v4/4-{self.search_string.lower()}'
                    self.setAnimixToken(self.search_string.lower())
                    self.response = self.pingURL(self.search_url)

                    if self.response == True:
                        return self.search_url
    
    #* This function will be used to grab the latest episode from the streaming site's webpage
    #This is to account for series which are 'ongoing' and thus will not return an episode count from the API
    def getLatestEpisode(self):

        # TODO: Add a try catch block to account for animixplay responding with a 404 error
        
        
        self.animix_token = self.getAnimixToken()
        self.animix_url = f'https://animixplay.com/v1/{self.animix_token}'
        self.request = requests.get(self.animix_url)
        self.source = self.request.content
        self.soup = BeautifulSoup(self.source, 'html.parser')
        
        #Div which holds the episode count
        self.epslist_div = self.soup.find('div', id = 'epslistplace')
        self.character_count = ''
        self.total_found = False
        self.eptotal_loop = True
        
        #If the episode total is found in this div then grab it and return it
        for self.character in range(0, len(self.epslist_div.text)):
            self.character_count += self.epslist_div.text[self.character]
            if 'eptotal' in self.character_count:
                
                
                self.total_episodes = ' '
                self.count = 3
                
                while self.eptotal_loop:
                    self.total_episodes+= self.epslist_div.text[self.character + self.count]
                    self.count+=1
                    if self.epslist_div.text[self.character + self.count] == ',':
                        
                        self.eptotal_loop = False
                        self.total_found = True
                        return int(self.total_episodes)
            else:
                # TODO: FUNCTION THAT FINDS THE LATEST EPISODE USING ALTERNATIVE METHOD
                return 5
        
    
    def home_path(self):

        self.abspath = os.path.abspath(__file__)
        self.dname = os.path.dirname(abspath)
        os.chdir(self.dname)

    #* Retrieves values for the main menu's predictive text search bar
    def apiToSearchBar(self, search_field, start_time):
        

        self.search_field = search_field

        self.start_time = start_time

        self.time_loop = True
        
        self.end_time = datetime.datetime.now()
            
        self.total_time = self.end_time - self.start_time

            
        #If the length of the text field is divisible by 3 or odd numbers over 3 then the values are retreived from the API. This is done to limit the number of inputs sent to the API by the user, which could results in an error
        if len(self.search_field.text()) >= 3 and self.total_time.seconds % 4 == 0:

            self.titles = []

            self.titles_episode_count = {}
            #Search parameter is set to retrieve anime only
            self.jikan_search = jikan.search('anime', search_field.text(), page=1)
            
            #Filter the results to retrieve TV titles only 
            self.results = self.jikan_search['results']
            for self.result in self.results: 
                if self.result['type'] == 'TV':
                    self.titles.append(self.result['title'])

                    try:
                        self.titles_episode_count[self.result['title']] = self.result['episodes']
                    except ValueError:
                        self.titles_episode_count[self.result['title']] = 'None'
                    
                    

            #Predictive text feature which display a best guest of search results based on the user's input
            self.completer = QCompleter(self.titles, self)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.search_field.setCompleter(self.completer)   

            self.setEpisodeCount(self.titles_episode_count)
             

    def randEpisode(self, search_field):

        self.search_field = search_field

        
        #Create url based on the text field
        self.url = self.createSearchURL(self.search_field.text())
        
        
        #Get episode count if it exists
        self.episode_count_dict = self.getEpisodeCount()
            

        #get the episode count of the anime that the user has chosen
        self.episode_count =  self.episode_count_dict[self.search_field.text()]

        #If the series is ongoing it will have an episode count of none, in which case the
        #Episode count will be gathered from the html in the webpage   
        
        if self.episode_count == 0 or self.episode_count == 'None':
            
            self.episode_count = self.getLatestEpisode()
            self.episode_number = random.randint(1, int(self.episode_count))
            self.episode_url = self.url + '/ep' + str(self.episode_number)
            webbrowser.open(self.episode_url)
            
        else:
            
            self.episode_number = random.randint(1, int(self.episode_count))
            self.episode_url = self.url + '/ep' + str(self.episode_number)
            webbrowser.open(self.episode_url)
            
    # TODO: Rename these two functions to have more suitable names. Build 3rd function to handle randomisation
    def randEpCollection(self, search_field):
        self.search_field = search_field
        
        #Create url based on the text field
        self.url = self.createSearchURL(self.search_field.text())
        
        self.titles = []

        self.titles_episode_count = {}
        #Search parameter is set to retrieve anime only
        self.jikan_search = jikan.search('anime', search_field.text(), page=1)
        
        #Filter the results to retrieve TV titles only 
        self.results = self.jikan_search['results']
        for self.result in self.results: 
            if self.result['type'] == 'TV' or self.result['type'] == 'OVA':
                self.titles.append(self.result['title'])
                try:
                    self.titles_episode_count[self.result['title']] = self.result['episodes']
                    
                except ValueError:
                    self.titles_episode_count[self.result['title']] = 'None'
                except KeyError as error:
                    print(error)
                    
        self.setEpisodeCount(self.titles_episode_count)           
        
        #Get episode count if it exists
        try:
            self.episode_count =  self.titles_episode_count[self.search_field.text()]
        except:
            self.episode_count = 'None'
            
        if self.episode_count == 0 or self.episode_count == 'None':
            
            self.episode_count = self.getLatestEpisode()
            self.episode_number = random.randint(1, int(self.episode_count))
            self.episode_url = self.url + '/ep' + str(self.episode_number)
            webbrowser.open(self.episode_url)
            
        else:
            
            self.episode_number = random.randint(1, int(self.episode_count))
            self.episode_url = self.url + '/ep' + str(self.episode_number)
            webbrowser.open(self.episode_url)
            
        
    #* Function to select a random year to find films and titles for
    def yearRandomize(self, current_year, radiobutton, text_browser, combobox):
        
        self.current_year = current_year
        self.movie_radiobutton = radiobutton
        self.text_browser = text_browser
        self.combobox = combobox
        
        #Loops through until a year is returned in which series were released
        self.randomize = True
        self.text_browser.clear()
            
        while self.randomize:
            
            self.year = random.randint(1926, self.current_year)
            self.one_year_anime = self.combineSeasons(self.year)
                
            #Split the movies and titles
            self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)

            try:
                    
                #Split the movies and titles
                self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)
                #Create lists of keys
                self.movies_keys = self.movies.keys()
                self.series_keys = self.series.keys()
                #Create alphabetically sorted lists of keys
                self.series_sorted = sorted(self.series_keys)
                self.movies_sorted = sorted(self.movies_keys)
                
                #If the user has selected the movie option then we output the movies to the Text Browser
                if self.movie_radiobutton.isChecked() == True:
                    if len(self.movies) >= 1:
                        self.randomize = False
                        self.text_browser.clear()
                        self.text_browser.append('********{' + str(self.year) +  '} Movies' + ' ********' + '\n')

                        for self.film in self.movies_sorted:
                            #Filter out the url and score from the dictionary to append to the screen
                            self.film_metadata = self.movies[self.film]
                            self.url = self.film_metadata[0]
                            self.score = self.film_metadata[1]
                            self.text_browser.append( '['+ '<a href="' + self.url + f'">{self.film}</a>' + ']' + '\n')
                            self.text_browser.append('Score: ' + str(self.score) ) 
                            self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
                    else:
                        continue
                            

                #If the user has selected the series option then we output the series to the Text Browser
                elif self.movie_radiobutton.isChecked() == False:
                    if len(self.series) >=1:
                        self.randomize = False
                        self.text_browser.clear()
                        self.text_browser.append('*****{' + str(self.year) + ' Airing' +  '} Series' + ' *****' + '\n')

                        for self.show in self.series_sorted:

                            self.series_metadata = self.series[self.show]
                            self.url = self.series_metadata[0]
                            self.score = self.series_metadata[1]
                            self.text_browser.append( '['+ '<a href="' + self.url + f'">{self.show}</a>' + ']' + '\n')
                            self.text_browser.append('Score: ' + str(self.score) ) 
                            self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
                    else:
                        continue
            except TypeError:
                continue

    #* Function that is used to 
    def filterYear(self, year, text_browser,movie_radiobutton ):
        
        self.year = year
        self.text_browser = text_browser
        self.movie_radiobutton = movie_radiobutton

        #Combine Seasons and split based on if they're movies or titles
        self.one_year_anime = self.combineSeasons(self.year.currentText())
        self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)

        self.movies_keys = self.movies.keys()
        self.series_keys = self.series.keys()

        #Create alphabetically sorted lists of keys
        self.series_sorted = sorted(self.series_keys)
        self.movies_sorted = sorted(self.movies_keys)

        #If the user has chosen movie
        if self.movie_radiobutton.isChecked() == True:
            self.text_browser.clear()

            if not self.movies_sorted:
                self.text_browser.append('Could not find retrieve any movies from ' + self.year)

            else:
                self.text_browser.append('******** ' + self.year +  ' Movies' + ' ********' + '\n')

                
                for self.film in self.movies_sorted:
                    #Retrieve the url and score values from the movie dictionary to append to the list
                    self.series_metadata = self.movies[self.film]
                    self.url = self.series_metadata[0]
                    self.score = self.series_metadata[1]
                    self.text_browser.append( '['+ '<a href="' + self.url + f'">{self.film}</a>' + ']' + '\n')
                    self.text_browser.append('Score: ' + str(self.score))
                    self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        else:
            self.text_browser.clear()
            if not self.series_sorted :
                self.text_browser.append('Could not find retrieve any series from ' + self.year)
            else:
                self.text_browser.append('***** ' + self.year + ' Airing Series' + ' *****' + '\n')  
                for self.show in self.series_sorted:
                    self.series_metadata = self.series[self.show]
                    self.url = self.series_metadata[0]
                    self.score = self.series_metadata[1]
                    
                    self.text_browser.append( '['+ '<a href="' + self.url+ f'">{self.show}</a>' + ']' + '\n')
                    self.text_browser.append('Score: ' + str(self.score) ) 
                    self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')

    #* Function which filters data from the Jikan API into something that we can use
    def filterGenre(self, genre_dict, genre_combobox, text_browser):
        self.genre_dict = genre_dict
        self.text_browser = text_browser
        self.genre_combobox = genre_combobox
        
        #Grabbing the genre id value which each genre of anime is assigned
        self.genre_id = self.genre_dict[self.genre_combobox.currentText()]

        self.series = {}

        #Query the Jikan API for titles that fall under the chosen genre
        self.anime_genre = jikan.genre(type = 'anime', genre_id = self.genre_id)
        #Filter results  to return only titles classified as 'anime'
        self.results = self.anime_genre['anime']
        
        #Retrieve the title, score, and url values from the results and store them for retrieval
        for self.result in self.results:
            for self.key, self.value in self.result.items():
                if self.key == 'title':
                    self.title = self.value
                if self.key == 'score':
                    self.score = self.value
                if self.key =='url':
                    self.url = self.value
            self.series_metadata = [self.score, self.url]
            self.series[self.title] = self.series_metadata
            self.series_sorted = sorted(self.series.keys())

        #Clear the text browser             
        self.text_browser.clear()

        #Append series to the text browser using the values that were collected
        for self.show in self.series_sorted:
                self.series_metadata = self.series[self.show]
                self.score = self.series_metadata[0]
                self.url = self.series_metadata[1]
                
                self.text_browser.append( '['+ '<a href="' + self.url+ f'">{self.show}</a>' + ']' + '\n')
                self.text_browser.append('Score: ' + str(self.score))
                self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')

    #* Randomize the selection of the user's genre selection   
    def genreRandomize(self, text_browser, combo_box, genre):
        self.text_browser = text_browser
        self.combobox = combo_box
        self.genre = genre
        self.random_genre = random.randint(1, len(self.genre))
        self.anime_genre =  jikan.genre('anime', self.random_genre)

        self.genre_titles = []
        self.series = {}

        #Placing the titles of the the genre dictionary into a list so that they can be retrieved using their id
        for self.title in self.genre.keys():
            self.genre_titles.append(self.title)

        #Filter results to return only values values that are considered to be 'anime'
        self.results = self.anime_genre['anime']
        
        for self.result in self.results:

            #Store the titles, scores, and urls, for retrieveal
            for self.key, self.value in self.result.items():

                if self.key == 'title':
                    self.title = self.value

                if self.key == 'score':
                    self.score = self.value

                if self.key =='url':
                    self.url = self.value

            self.series_metadata = [self.score, self.url]
            self.series[self.title] = self.series_metadata
            self.series_sorted = sorted(self.series.keys())

        # Clear the text
        self.text_browser.clear()
        self.text_browser.append('  {' + self.genre_titles[self.random_genre-1]  + '} - Series' + '\n')

        # Append the stored values to the text browser
        for self.show in self.series_sorted:

                self.series_metadata = self.series[self.show]
                self.score = self.series_metadata[0]
                self.url = self.series_metadata[1]
                
                self.text_browser.append( '['+ '<a href="' + self.url+ f'">{self.show}</a>' + ']' + '\n')
                self.text_browser.append('Score: ' + str(self.score))
                self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')

                    
    #* Combines the four seasons of anime queries into one year
    def combineSeasons(self, year):
        self.year = year
        self.seasons = ['spring', 'summer','fall', 'winter']
        self.one_year_anime =[]

        #Loop over the data returned by querying over each season
        for self.season in self.seasons:

            #This try block is structured to filter down the list/dictionary of data returned by the json query and return the combined list of values
            try:
                self.seasonal_list = jikan.season(year=self.year, season= self.season)
                self.seasonal_anime = self.seasonal_list['anime']
                for self.anime in self.seasonal_anime:
                    self.one_year_anime.append(self.anime)

                return self.one_year_anime
            except:
                print('No titles found for the' + self.season)
    
    #* Selects a random season to choose an anime from
    def randSeason(self):

        self.seasons = ['spring', 'summer','fall', 'winter']

        self.now = datetime.datetime.now()

        self.current_year = self.now.year

        self.random_loop = True

        while self.random_loop:
            self.year_list = []

            #Fill the year list with values starting from 1926
            for self.year in range(1926, self.current_year + 1):
                self.year_list.append(self.year)
        
            #retrieve random values for the year, season, and anime title
            self.rand_year = self.year_list[random.randint(0, len(self.year_list)-1)]
            self.rand_season = self.seasons[random.randint(0, len(self.seasons)-1)]

            #Query the JIkan API for a title based on a random year and season 
            self.anime_season = jikan.season(year = self.rand_year, season = self.rand_season)

            self.rand_anime = self.anime_season['anime']

            if len(self.rand_anime) >= 1:
                self.random_loop = False
                return self.rand_anime
            else:
                print('None returned')
                time.sleep(0.25)
                continue
            

    #* This function is used to  generate a random anime to be outputted onto the "Random" menu
    def randAnime(self, anime_season):

        self.anime_season = anime_season 
        
        #Generate a random number within the length of the season in order to selecet a random anime
        self.rand_choice = random.randint(0, len(self.anime_season) - 1)
        self.rand_anime = self.anime_season[self.rand_choice]

        #Assign values from the dictionary to separate variables to be returned
        self.title = self.rand_anime['title']
        self.url = self.rand_anime['url']
        self.image_url = self.rand_anime['image_url']
        self.episodes = self.rand_anime['episodes']
        self.score = self.rand_anime['score']
        self.synopsis = self.rand_anime['synopsis']

        return self.title, self.url, self.image_url, self.episodes, self.score, self.synopsis

    #* Function which splits an anime list into two separate lists composed of series and movies  
    def movieSeriesSplit(self, anime_list):

        self.anime_list = anime_list 

        self.movies = {}
        self.series = {}
        try:
            #Split the movie titles and their urls
            for self.anime_dict in self.anime_list:
                for self.key, self.value in self.anime_dict.items():
                    if self.key == 'type':
                        if self.value == 'Movie':
                            self.title = self.anime_dict['title']
                            self.url = self.anime_dict['url']
                            self.rating = self.anime_dict['score']
                            self.movie_metadata = [self.url, self.rating]
                            self.movies[self.title] = self.movie_metadata
                            
                        #Split the show titles and their urls
                        else:
                            self.title = self.anime_dict['title']
                            self.url = self.anime_dict['url']
                            self.rating = self.anime_dict['score']
                            self.series_metadata = [self.url, self.rating]
                            self.series[self.title] = self.series_metadata

        except TypeError as error:
            print('This value is empty. Skipping value')
            print(error)

        #If either the movies or titles return None as a value then we want to replace it with an empty list    
        if self.movies is None:

            self.movies = []

        if self.series is None:

            self.movies = []
          
        return self.movies, self.series       
        
    #* Filters data from the JiKan API into the top upcoming data that we can use
    def apiToTopWindow(self):
        
        try:
            #Grabbing the top upcoming anime from the MAL API
            self.top_anime = jikan.top(type='anime', page=1, subtype='upcoming')
        
        except ConnectionError as error:
            try:
                connection_window = ConnectionDialogue()
                connection_window.text_edit.setText(error)
                print('Could not connect to the MAL API at: https://api.jikan.moe/v3')
                
            except:
                print('Failed to connect to the MAL API at: https://api.jikan.moe/v3')
        
        self.titles = []
        self.ranks = []
        self.start_dates = []
        self.url=[]

        #Filter the original data down to all values that fall under the 'top' dictionary value
        for self.key,self.value  in self.top_anime.items():

          if self.key ==  'top':

                self.anime_data = self.value

        #Loops through the list items in the anime dat list within
        for self.data in self.anime_data:

            for self.key, self.value in self.data.items():

                #If the key matched the values that we want(rank, title, start_dates, url) then grab those values
                if self.key == 'rank':

                    self.ranks.append(self.value)

                elif self.key == 'title':

                    self.titles.append(self.value)

                elif self.key == 'start_date':

                    self.start_dates.append(self.value)

                elif self.key == 'image_url':

                    self.url.append(self.value)

                    #Some values arrived as NoneTypes so this is there to remedy that
                    for self.date in range(0,len(self.start_dates)):

                        if self.start_dates[self.date] is None:

                            self.start_dates[self.date] = '-'

        #returns titles, ranks, and start_dates , and the url for the image          
        return self.titles, self.ranks, self.start_dates, self.url
    
    #* Download the Images to use for the GUI
    def downloadImage(self, img_count):
        
        self.img_count = img_count
        self.local_file = urllib.request.urlretrieve(self.url[self.img_count], f'img{self.img_count}')
              
    #* Generates the search token that's used to search on each site
    def generateSearchToken(self, title):

        self.title = title

        #If there is a space in the title then we'll need to join the titles together using their respective website delimeters 
        if ' ' in self.title:
            self.title_list = self.title.split()
            self.reddit_search_token = '%20'.join(self.title_list)
            self.wikipedia_search_token = '_'.join(self.title_list)
            self.youtube_search_token = '+'.join(self.title_list)
        
        else:

            self.reddit_search_token = self.title
            self.wikipedia_search_token = self.title
            self.youtube_search_token = self.title

        return self.reddit_search_token, self.wikipedia_search_token, self.youtube_search_token

    #* Function to set the dictionary filled with titles and episodes that we're going to use for the episode count
    def setEpisodeCount(self, episode_dictionary):
        self.episode_dictionary = episode_dictionary

    ###########* Functions to set the search tokens *###########
    def setRedditToken(self, reddit_token):
        self.reddit_token = reddit_token
    
    def setWikiToken(self, wiki_token):
        self.wiki_token = wiki_token
    
    def setYoutubeToken(self, youtube_token):
        self.youtube_token = youtube_token
        
    def setAnimixToken(self, animix_token):
        self.animix_token= animix_token
    
    ###########* Functions to retrieve the search tokens *###########
    def getRedditToken(self):
        return self.reddit_token

    def getWikiToken(self):
        return self.wiki_token

    def getYoutubeToken(self):
        return self.youtube_token
    
    def getAnimixToken(self):
        return self.animix_token

    #* Function to get the dictionary filled with titles and episodes that  are going to be used for the episode count
    def getEpisodeCount(self):
        return self.episode_dictionary
        
    ###########* Functions to search the Internet for data on the target title *###########
    def redditSearch(self, reddit_token):

        self.reddit_token = reddit_token

        self.reddit_link = f'https://www.reddit.com/r/anime/search/?q={self.reddit_token}&restrict_sr=1'

        try:
            webbrowser.open_new_tab(self.reddit_link)

        except ConnectionError:
            print(f'Could not connect to destination: {self.search_link}' )

    def wikiSearch(self, wiki_token):

        self.wiki_token = wiki_token
        
        self.wiki_link = f'https://en.wikipedia.org/wiki/{self.wiki_token}'

        try:
            webbrowser.open_new_tab(self.wiki_link)
        except ConnectionError:
            print(f'Could not connect to destination: {self.wiki_link}' )

    def youTubeSearch(self, youtube_token):


        self.youtube_token

        self.youtube_link = f'https://www.youtube.com/results?search_query={self.youtube_token}'

        try:
            webbrowser.open_new_tab(self.youtube_link)

        except ConnectionError:
            print(f'Could not connect to destination: {self.youtube_link}' )
        

##################* This is the Main UI through which all functions that will act upon our main Window *##################
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
    
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('mainWindow.ui', self) #Load the mainwindow .ui file

        self.model = Model()

        #Menu bar bitcoin donation
        self.bitcoin_action = self.findChild(QtWidgets.QAction, 'actionBitcoin')
        self.bitcoin_action.triggered.connect(self.donateBitcoinWindow)
        
        self.monero_action = self.findChild(QtWidgets.QAction, 'actionMonero')
        self.monero_action.triggered.connect(self.donateMoneroWindow)

        #Menu bar paypal donation
        self.paypal_action = self.findChild(QtWidgets.QAction, 'actionPaypal')
        self.paypal_action.triggered.connect(self.donatePaypal)
        
        #Menu bar status option for API connectivity
        self.connect_status = self.findChild(QtWidgets.QAction, 'actionStatus')
        self.connect_status.triggered.connect(self.status)
        
        #Menu bar option for mongodb collection
        self.collection_action = self.findChild(QtWidgets.QAction, 'actionCollection')
        self.collection_action.triggered.connect(self.collection)
        
        self.search_field = self.findChild(QtWidgets.QLineEdit, 'search_field')
        self.top_button = self.findChild(QtWidgets.QPushButton, 'topUpcoming_button')
        self.discover_button = self.findChild(QtWidgets.QPushButton, 'discover_button')
        self.rand_button = self.findChild(QtWidgets.QPushButton, 'rand_button')

        self.top_button.clicked.connect(self.topUpcomingMenu)
        self.discover_button.clicked.connect(self.discoverMenu)
        self.rand_button.clicked.connect(self.randomMenu)
        
        self.start_time = datetime.datetime.now()
        self.search_field.textChanged.connect(lambda: self.model.apiToSearchBar(self.search_field, self.start_time))

        self.titles, self.ranks, self.start_dates, self.url = self.model.apiToTopWindow()

        self.img_directory = tmp_directory.name

    
        os.chdir(self.img_directory) #Change to the image directory
        
            
        with concurrent.futures.ThreadPoolExecutor() as executor: #Multi-threading to execute multiple downloads simultaneously
            # The limit of results that will be returned
            self.results_cap = [0, 1 ,2 ,3, 4, 5 , 6, 7, 8, 9, 10, 11, 12 ,13 ,14 ,15 ,16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
                                 
            self.f1 = executor.map(self.model.downloadImage, self.results_cap) # Download the images for the GUI

        self.show() #Show the GUI

    #* Handles what to do if the user presses the enter button. There's a better method of doing this 
    #https://forum.qt.io/topic/103613/how-to-call-keypressevent-in-pyqt5-by-returnpressed/2
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.model.randEpisode(self.search_field)

    #* Top Upcoming anime GUI
    def topUpcomingMenu(self):
        self.hide() #Hide the main window
        self.top = TopWindow()
        
    #* Discovery Menu GUI
    def discoverMenu(self):
        self.hide() #Hide the main window
        self.discover_window = DiscoverWindow()

    #* Random Menu GUI
    def randomMenu(self):
        self.hide() #Hide the main window
        self.rand_window = RandomWindow()
        
    #* Bitcoin Dialogue
    def donateBitcoinWindow(self):
        self.donate_dialogue = BtcDonateDialogue()
        
     #* Monero Dialogue
    def donateMoneroWindow(self):
        self.donate_dialogue = XmrDonateDialogue()
        
    #* Open Paypal link
    def donatePaypal(self):
        webbrowser.open('https://paypal.me/McLaughlin007')
    
    #* Open Status Dialogue
    def status(self):
        self.connection_dialogue = ConnectionDialogue()
        
    #* Open Status Dialogue
    def collection(self):
        self.collection_window = CollectionWindow()
        
###########* This is the Top UI through which all functions pertaining to the Discover Window will be created *##################
class DiscoverWindow(QtWidgets.QMainWindow):

    def __init__(self):
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
    
        super(DiscoverWindow, self).__init__()
        uic.loadUi('discover.ui', self)


        self.show()

        self.model = Model()

        #Genres and their respective genre ids. This will be used to fill the genre combobox with values and to query the API
        self.genres = {'Action' : 1, 'Adventure' : 2, 'Cars' : 3, 'Comedy' : 4, 'Dementia' : 5, 'Demons' : 6, 'Mystery' : 7, 'Drama' : 8, 'Ecchi' : 9,
        'Fantasy' : 10, 'Game' : 11, 'Hentai' : 12, 'Historical' : 13, 'Horror' : 14, 'Kids' : 15, 'Magic' : 16, 'Martial Arts' : 17,
        'Mecha' : 18, 'Music' : 19, 'Parody' : 20, 'Samurai' : 21, 'Romance' : 22, 'School' : 23, 'Sci Fi' : 24, 'Shoujo' : 25,
        'Shoujo Ai' : 26, 'Shounen' : 27, 'Shounen Ai' : 28, 'Space' : 29, 'Sports' : 30, 'Super Power' : 31, 'Vampire' : 32, 'Yaoi' : 33,
        'Yuri' : 34, 'Harem' : 35, 'Slice Of Life' : 36, 'Supernatural' : 37, 'Military' : 38, 'Police' : 39, 'Psychological' : 40, 'Thriller' : 41,
        'Seinen' : 42, 'Josei' : 43}

        #Assigning the widgets within the window
        self.filter_year_button = self.findChild(QtWidgets.QPushButton, 'filter_year_button')
        self.filter_genre_button = self.findChild(QtWidgets.QPushButton, 'filter_genre_button')
        self.year_combo = self.findChild(QtWidgets.QComboBox, 'year')
        self.genre_combo = self.findChild(QtWidgets.QComboBox, 'genre_combo')
        self.year_textbrowser = self.findChild(QtWidgets.QTextBrowser, 'year_textBrowser')
        self.genre_textbrowser = self.findChild(QtWidgets.QTextBrowser, 'genre_textBrowser')
        self.series_radiobutton = self.findChild(QtWidgets.QRadioButton, 'series_radioButton')
        self.movies_radiobutton = self.findChild(QtWidgets.QRadioButton, 'movies_radioButton')
        self.back_button = self.findChild(QtWidgets.QCommandLinkButton, 'backButton')
        self.back_button_2 = self.findChild(QtWidgets.QCommandLinkButton, 'backButton_2')
        self.rand_button = self.findChild(QtWidgets.QPushButton, 'randButton')
        self.rand_button_2 = self.findChild(QtWidgets.QPushButton, 'randButton_2')


        #Set the series radio button to be the one that's checked on startup
        self.series_radiobutton.setChecked(True)
        

        self.filter_year_button.clicked.connect(lambda: self.model.filterYear(self.year_combo, self.year_textbrowser, self.movies_radiobutton))
        self.filter_genre_button.clicked.connect(lambda: self.model.filterGenre(self.genres, self.genre_combo, self.genre_textbrowser))

        #Assign click events to the main menu buttons
        self.back_button.clicked.connect(self.home)
        self.back_button_2.clicked.connect(self.home)
        

        #Get the current date/year
        self.now = datetime.datetime.now()
        self.current_year = self.now.year
        self.rand_button.clicked.connect(lambda: self.model.yearRandomize(self.current_year, self.movies_radiobutton, self.year_textbrowser, self.year_combo))
        self.rand_button_2.clicked.connect(lambda: self.model.genreRandomize(self.genre_textbrowser, self.genre_combo, self.genres))

       
        #Fill the combobox with values ranging from 1926 up until the current year. 1926 should be where the first record dates back to
        for self.year in range(1926, self.current_year + 1):
            self.year_combo.addItem(str(self.year))

        #Fill the combobox with the genre values that MAL uses to categorize their anime
        for self.genre in self.genres.keys():
            self.genre_combo.addItem(str(self.genre))
    
    #* Function to return to the Main Window
    def home(self):

        self.hide()
        main_win3 = MainWindow()
        
###########* This is the Top UI through which all functions pertaining to the Top Window will be created *##################
class TopWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        os.chdir(dname)
        super(TopWindow, self).__init__()

        #Load the topUpcoming.ui file
        uic.loadUi('topUpcoming.ui', self) 
        
        self.show()
        self.model = Model()
        self.img_directory = tmp_directory.name
    
        #Set the default image to the first image in the image directory
        self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        self.image_path = self.img_directory + '/img0'
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        self.pixmap2 = self.pixmap.scaled(500, 500)

        #Change to main directory
        os.chdir(dname)
    
        # for self.count in range(0,20):
        #     try:
        #         self.top_button = self.findChild(QtWidgets.QPushButton, 'top_button' + str(self.count))   
        #         self.top_button.clicked.connect(lambda : self.changeImage(self.count, self.label))   
        #     except:
        #             print('fail')

        self.titles, self.ranks, self.start_dates, self.url = self.model.apiToTopWindow()

        for self.count in range(len(self.titles)):
            try:
                #Set the buttons on the TopUpcoming menu to match the names of the series they reference
                self.top_button = self.findChild(QtWidgets.QPushButton, 'top_button' + str(self.count))
                self.top_button.setText('[' + str(self.count + 1) + ']' + ': ' + self.titles[self.count])
            
            except:
                print(f'Title: {self.titles[self.count]} will not be appended')


        self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        
        self.back_button = self.findChild(QtWidgets.QCommandLinkButton, 'backButton')

        self.top_button0 = self.findChild(QtWidgets.QPushButton, 'top_button0')
        self.top_button1 = self.findChild(QtWidgets.QPushButton, 'top_button1')
        self.top_button2 = self.findChild(QtWidgets.QPushButton, 'top_button2')
        self.top_button3 = self.findChild(QtWidgets.QPushButton, 'top_button3')
        self.top_button4 = self.findChild(QtWidgets.QPushButton, 'top_button4')
        self.top_button5 = self.findChild(QtWidgets.QPushButton, 'top_button5')
        self.top_button6 = self.findChild(QtWidgets.QPushButton, 'top_button6')
        self.top_button7 = self.findChild(QtWidgets.QPushButton, 'top_button7')
        self.top_button8 = self.findChild(QtWidgets.QPushButton, 'top_button8')
        self.top_button9 = self.findChild(QtWidgets.QPushButton, 'top_button9')
        self.top_button10 = self.findChild(QtWidgets.QPushButton, 'top_button10')
        self.top_button11 = self.findChild(QtWidgets.QPushButton, 'top_button11')
        self.top_button12 = self.findChild(QtWidgets.QPushButton, 'top_button12')
        self.top_button13 = self.findChild(QtWidgets.QPushButton, 'top_button13')
        self.top_button14 = self.findChild(QtWidgets.QPushButton, 'top_button14')
        self.top_button15 = self.findChild(QtWidgets.QPushButton, 'top_button15')
        self.top_button16 = self.findChild(QtWidgets.QPushButton, 'top_button16')
        self.top_button17 = self.findChild(QtWidgets.QPushButton, 'top_button17')
        self.top_button18 = self.findChild(QtWidgets.QPushButton, 'top_button18')
        self.top_button19 = self.findChild(QtWidgets.QPushButton, 'top_button19')
        self.top_button20 = self.findChild(QtWidgets.QPushButton, 'top_button20')
        self.top_button21 = self.findChild(QtWidgets.QPushButton, 'top_button21')
        self.top_button22 = self.findChild(QtWidgets.QPushButton, 'top_button22')
        self.top_button23 = self.findChild(QtWidgets.QPushButton, 'top_button23')
        self.top_button24 = self.findChild(QtWidgets.QPushButton, 'top_button24')
        self.top_button25 = self.findChild(QtWidgets.QPushButton, 'top_button25')
        self.top_button26 = self.findChild(QtWidgets.QPushButton, 'top_button26')
        self.top_button27 = self.findChild(QtWidgets.QPushButton, 'top_button27')
        self.top_button28 = self.findChild(QtWidgets.QPushButton, 'top_button28')
        self.top_button29 = self.findChild(QtWidgets.QPushButton, 'top_button29')

        self.top_button0.clicked.connect(lambda : self.changeImage(0, self.label, self.model, self.img_directory))
        self.top_button1.clicked.connect(lambda : self.changeImage(1, self.label, self.model, self.img_directory))     
        self.top_button2.clicked.connect(lambda : self.changeImage(2, self.label, self.model, self.img_directory))  
        self.top_button3.clicked.connect(lambda : self.changeImage(3, self.label, self.model, self.img_directory))  
        self.top_button4.clicked.connect(lambda : self.changeImage(4, self.label, self.model, self.img_directory))  
        self.top_button5.clicked.connect(lambda : self.changeImage(5, self.label, self.model, self.img_directory))  
        self.top_button6.clicked.connect(lambda : self.changeImage(6, self.label, self.model, self.img_directory))  
        self.top_button7.clicked.connect(lambda : self.changeImage(7, self.label, self.model, self.img_directory))  
        self.top_button8.clicked.connect(lambda : self.changeImage(8, self.label, self.model, self.img_directory))  
        self.top_button9.clicked.connect(lambda : self.changeImage(9, self.label, self.model, self.img_directory))  
        self.top_button10.clicked.connect(lambda : self.changeImage(10, self.label, self.model, self.img_directory))  
        self.top_button11.clicked.connect(lambda : self.changeImage(11, self.label, self.model, self.img_directory))  
        self.top_button12.clicked.connect(lambda : self.changeImage(12, self.label, self.model, self.img_directory))  
        self.top_button13.clicked.connect(lambda : self.changeImage(13, self.label, self.model, self.img_directory))  
        self.top_button14.clicked.connect(lambda : self.changeImage(14, self.label, self.model, self.img_directory))  
        self.top_button15.clicked.connect(lambda : self.changeImage(15, self.label, self.model, self.img_directory))  
        self.top_button16.clicked.connect(lambda : self.changeImage(16, self.label, self.model, self.img_directory))  
        self.top_button17.clicked.connect(lambda : self.changeImage(17, self.label, self.model, self.img_directory))  
        self.top_button18.clicked.connect(lambda : self.changeImage(18, self.label, self.model, self.img_directory))  
        self.top_button19.clicked.connect(lambda : self.changeImage(19, self.label, self.model, self.img_directory))
        self.top_button20.clicked.connect(lambda : self.changeImage(20, self.label, self.model, self.img_directory)) 
        self.top_button21.clicked.connect(lambda : self.changeImage(21, self.label, self.model, self.img_directory)) 
        self.top_button22.clicked.connect(lambda : self.changeImage(22, self.label, self.model, self.img_directory)) 
        self.top_button23.clicked.connect(lambda : self.changeImage(23, self.label, self.model, self.img_directory)) 
        self.top_button24.clicked.connect(lambda : self.changeImage(24, self.label, self.model, self.img_directory)) 
        self.top_button25.clicked.connect(lambda : self.changeImage(25, self.label, self.model, self.img_directory)) 
        self.top_button26.clicked.connect(lambda : self.changeImage(26, self.label, self.model, self.img_directory)) 
        self.top_button27.clicked.connect(lambda : self.changeImage(27, self.label, self.model, self.img_directory)) 
        self.top_button28.clicked.connect(lambda : self.changeImage(28, self.label, self.model, self.img_directory)) 
        self.top_button29.clicked.connect(lambda : self.changeImage(29, self.label, self.model, self.img_directory))   
        ##################Assigning Variables for the search buttons ##################
        self.reddit_button = self.findChild(QtWidgets.QPushButton, 'reddit_button')
        self.wiki_button = self.findChild(QtWidgets.QPushButton, 'wiki_button')
        self.youtube_button = self.findChild(QtWidgets.QPushButton, 'youtube_button')
        ################## Assigning search functions to buttons ##################
        self.reddit_button.clicked.connect(lambda : self.model.redditSearch(self.model.getRedditToken()))
        self.wiki_button.clicked.connect(lambda : self.model.wikiSearch(self.model.getWikiToken()))
        self.youtube_button.clicked.connect(lambda : self.model.youTubeSearch(self.model.getYoutubeToken()))
        #Back to the home window
        self.back_button.clicked.connect(lambda : self.home())

    def home(self):
    
        self.hide()
        main_win4 = MainWindow()

    #* Function to change the display image/Pixmap for the TopUpcoming window
    def changeImage(self, count, label, model, img_directory):
        
        self.count = count
        self.label = label
        self.model = model
        self.img_directory = self.img_directory
        

        #Naming the image downloads
        self.image_path = self.img_directory + '/img' + str(self.count) 
        #Set the image/Pixmap as the background of the label
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        

        try:
            self.search_string = self.titles[self.count]
        except:
            self.search_string = self.titles[0]

        self.redditToken, self.wikiToken, self.youToken =  self.model.generateSearchToken(self.search_string)
        
        #Set tokens
        self.model.setRedditToken(self.redditToken)
        self.model.setWikiToken(self.wikiToken)
        self.model.setYoutubeToken(self.youToken)

###########* This is the Random UI through which all functions pertaining to the Random Window will be created *##################
class RandomWindow(QtWidgets.QMainWindow):
    

    def __init__(self):
        
        self.model = Model()
        self.model.home_path()

        super(RandomWindow, self).__init__()

        #Load the random ui file
        uic.loadUi('random.ui', self)
        self.show()

        self.rand_button = self.findChild(QtWidgets.QPushButton, 'rand_button')

        self.appendRandom()
    
        self.rand_button.clicked.connect(self.appendRandom)
        
        
    def appendRandom(self):
        
        #Titles that have already been randomly selected
        self.already_viewed = []

        self.random_loop = True

        while self.random_loop:

            #Select a random season
            self.rand_season = self.model.randSeason()
            #Select a random title based on that season
            self.title, self.url, self.image_url, self.episodes, self.score, self.synopsis = self.model.randAnime(self.rand_season)

            #Only append the data if the title hasn't already been viewed in the Random anime window
            if self.title not in self.already_viewed:

                self.random_loop = False

                self.title_value = self.findChild(QtWidgets.QLabel, 'title_value')
                self.episodes_value = self.findChild(QtWidgets.QLabel, 'episodes_value')
                self.score_value = self.findChild(QtWidgets.QLabel, 'score_value')
                self.synopsis_value = self.findChild(QtWidgets.QLabel, 'synopsis_value')
                self.image = self.findChild(QtWidgets.QLabel, 'rand_image')
                self.home_button = self.findChild(QtWidgets.QCommandLinkButton, 'back_button')

                #Append this title to the list of viewed titles
                self.already_viewed.append(self.title)

                #Download the corresponding image
                os.chdir(tmp_directory.name)
                self.local_file = urllib.request.urlretrieve(self.image_url, self.title)
                self.image_path = tmp_directory.name + '/' + self.title
                self.pixmap = QPixmap(self.image_path)
                self.image.setPixmap(self.pixmap)
                self.pixmap2 = self.pixmap.scaled(2000, 2000)
                os.chdir(dname)

                #Append the values to the screen
                self.title_value.setText( '{'+ '<a href="' + self.url + f'">{self.title}</a>' + '}')
                self.episodes_value.setText('[' + str(self.episodes) + ']')
                self.score_value.setText('[' + str(self.score) + ']')
                self.synopsis_value.setText(self.synopsis)

                #Home button
                self.home_button.clicked.connect(self.home)

            else:
                continue

     #Function to return to the Main Window
    def home(self):

        self.hide()
        main_win2 = MainWindow()
        
        
###########* This is the Collection Dialogue UI  *##################
class CollectionWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        self.model = Model()
        self.model.home_path()

        super(CollectionWindow, self).__init__()

        #Load the connection ui file
        uic.loadUi('collection.ui', self)
        
        self.search_field = self.findChild(QtWidgets.QLineEdit, 'search_field')

        self.connection = self.model.dbConnect()
        self.model.createTable(self.connection, self.collection_list)
        
        self.collection_list = self.findChild(QtWidgets.QListWidget, 'collection_list')
        self.collection_list.itemClicked.connect(lambda: self.model.updateField(self.search_field, self.collection_list))
        
        
        self.add_button = self.findChild(QtWidgets.QPushButton, 'add_button')
        self.add_button.clicked.connect(lambda: self.model.addSeries(self.search_field, self.collection_list))
        
        self.remove_button = self.findChild(QtWidgets.QPushButton, 'remove_button')
        self.remove_button.clicked.connect(lambda: self.model.removeSeries(self.search_field, self.collection_list))
        
        self.rand_button = self.findChild(QtWidgets.QPushButton, 'rand_button')
        self.rand_button.clicked.connect(lambda: self.model.randEpCollection(self.search_field))
        
        
        self.start_time = datetime.datetime.now()
        self.search_field.textChanged.connect(lambda: self.model.apiToSearchBar(self.search_field, self.start_time))
        
        
        self.show()
        
        
        
###########* This is the BTC Donation Dialogue UI  *##################
class BtcDonateDialogue(QtWidgets.QDialog):
    
    def __init__(self):
        
        self.model = Model()
        self.model.home_path()

        super(BtcDonateDialogue, self).__init__()

        #Load the btc ui file
        uic.loadUi('btc.ui', self)
        self.show()
        
###########* This is the XMR Donation Dialogue UI  *##################
class XmrDonateDialogue(QtWidgets.QDialog):
    
    def __init__(self):
        
        self.model = Model()
        self.model.home_path()

        super(XmrDonateDialogue, self).__init__()

        #Load the btc ui file
        uic.loadUi('xmr.ui', self)
        self.show()
        
###########* This is the ConnectionDialogue UI  *##################
class ConnectionDialogue(QtWidgets.QDialog):
    
    def __init__(self):
        
        self.model = Model()
        self.model.home_path()

        super(ConnectionDialogue, self).__init__()

        #Load the connection ui file
        uic.loadUi('conn.ui', self)
        
        
        self.text_edit = self.findChild(QtWidgets.QTextEdit, 'textEdit')
        self.model.apiStatus(self.text_edit)
        self.show()
               
        
def run():
    app = QtWidgets.QApplication(sys.argv) # Creates an instance of our application
    window = MainWindow() # Creates an instance of our window class
    app.exec_()  #Start the app

#Tasks to do upon closing the application
def exit_handler():
    tmp_directory.cleanup()

atexit.register(exit_handler)
run()