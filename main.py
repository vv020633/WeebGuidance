from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QAction, QCompleter
from PyQt5.QtGui import QIcon, QPixmap
from jikanpy import Jikan
import sys, os, time, datetime, pprint, webbrowser, concurrent.futures, random, threading
import urllib.request

#Instance of our Jikan class which allows for communication with the Jikan MyAnimeList API. This is the foundation of this application
jikan = Jikan()

#Here the directory is set to the current directory from which we're running the Python script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

rand_state = True
########### This is the Model class through which all functions that respond to changes in the  UI exist ##################
class Model(QtWidgets.QMainWindow):
    

    def _init_(self):
        print('placeholder')

    #Retrieves values for the main menu's predictive text search bar
    def apiToMainMenu(self, search_field):
        self.search_field = search_field
       
        #If the length of the text field is divisible by 3 or odd numbers over 3 then the values are retreived from the API. This is done to limit the number of inputs sent to the API by the user, which could results in an error
        if len(self.search_field.text()) == 3 or (len(self.search_field.text()) - 3) % 2 == 0:

            self.titles=[]
            #Search parameter is set to retrieve anime only
            self.jikan_search = jikan.search('anime', search_field.text(), page=1)
           
           #Filter the resultes to retrieve TV titles only 
            self.results = self.jikan_search['results']
            for self.result in self.results: 
                if self.result['type'] == 'TV':
                    self.titles.append(self.result['title'])

            #Predictive text feature which display a best guest of search results based on the user's input
            self.completer = QCompleter(self.titles, self)
            self.search_field.setCompleter(self.completer)    

            pprint.pprint(self.results)



    # Function to select a random year to find films and titles for
    def yearRandomize(self, current_year, radiobutton, text_browser, combobox):
        
        #The active variable which will be used to determine how many times the Random button has been clicked
        
        self.current_year = current_year
        self.movie_radiobutton = radiobutton
        self.text_browser = text_browser
        self.combobox = combobox
        
        #Loops through until a year is returned in which series were released
        self.randomize = True
        self.text_browser.clear()
            
        while self.randomize:

            self.year = random.randint(1926, self.current_year + 1)
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
                        self.text_browser.append('******** ' + str(self.year) +  ' Movies' + ' ********' + '\n')

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
                        self.text_browser.append('***** ' + str(self.year) + ' Airing' +  ' Series' + ' *****' + '\n')

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

    #Function that is used to 
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

    #Function which filters data from the Jikan API into something that we can use
    def filterGenre(self, genre_dict, genre_combobox, text_browser):
        self.genre_dict = genre_dict
        self.text_browser = text_browser
        self.genre_combobox = genre_combobox
        self.genre_id = self.genre_dict[self.genre_combobox.currentText()]

        self.series = {}
        self.anime_genre = jikan.genre(type = 'anime', genre_id = self.genre_id)
        # self.movies, self.series = self.movieSeriesSplit(self.anime_genre)
        self.results = self.anime_genre['anime']
        
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
                    
        
                 
        self.text_browser.clear()

        

        for self.show in self.series_sorted:
                self.series_metadata = self.series[self.show]
                self.score = self.series_metadata[0]
                self.url = self.series_metadata[1]
                
                self.text_browser.append( '['+ '<a href="' + self.url+ f'">{self.show}</a>' + ']' + '\n')
                self.text_browser.append('Score: ' + str(self.score))
                self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')

    #Randomize the selection of the user's genre selection   
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

        self.results = self.anime_genre['anime']
        
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
        
        self.text_browser.clear()
        self.text_browser.append('  {' + self.genre_titles[self.random_genre-1]  + '} - Series' + '\n')
        for self.show in self.series_sorted:
                self.series_metadata = self.series[self.show]
                self.score = self.series_metadata[0]
                self.url = self.series_metadata[1]
                
                self.text_browser.append( '['+ '<a href="' + self.url+ f'">{self.show}</a>' + ']' + '\n')
                self.text_browser.append('Score: ' + str(self.score))
                self.text_browser.append('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')

                    
    #Combines the four seasons of anime queries into one year
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
    #
    def randSeason(self):

        

        self.seasons = ['spring', 'summer','fall', 'winter']

        self.now = datetime.datetime.now()

        self.current_year = self.now.year

        self.random_loop = True

        while self.random_loop:
            self.year_list = []

            for self.year in range(1926, self.current_year + 1):
                self.year_list.append(self.year)
        
            #retrieve random values for the year, season, and anime title
            self.rand_year = self.year_list[random.randint(0, len(self.year_list)-1)]
            self.rand_season = self.seasons[random.randint(0, len(self.seasons)-1)]
                
            self.anime_season = jikan.season(year = self.rand_year, season = self.rand_season)

            self.rand_anime = self.anime_season['anime']

            if len(self.rand_anime) >= 1:
                self.random_loop = False
                return self.rand_anime
            else:
                print('None returned')
                time.sleep(0.25)
                continue
            #  self.random_loop = False

    # This function is used to  generate a random anime to be outputted onto the "Random" menu
    def randAnime(self, anime_season):

        self.anime_season = anime_season 
        
        self.rand_choice = random.randint(0, len(self.anime_season) - 1)
        self.rand_anime = self.anime_season[self.rand_choice]
        pprint.pprint(self.rand_anime)


                
    def randYearSetState(self):

        self.rand_state = rand_state
        if self.rand_state == True:
            self.rand_state = False
        
        elif self.rand_state == False:
            self.rand_state == True
        
        return self.rand_state
            
        
    #Used to split an incoming list of titles into movies and series        
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
        

    #Filters data from the JiKan API into the top upcoming data that we can use
    def apiToTopWindow(self):
        
        try:
            #Grabbing the top upcoming anime from the MAL API
            self.top_anime = jikan.top(type='anime', page=1, subtype='upcoming')
        
        except ConnectionError:
            print('Could not connect to the MAL API at: https://api.jikan.moe/v3')
            time.sleep(5)
        
        self.titles = []
        self.ranks = []
        self.start_dates = []
        self.url=[]
        for self.key,self.value  in self.top_anime.items():
          if self.key ==  'top':
                self.anime_data = self.value

        #Loops through the list items in the anime dat list within
        for self.data in self.anime_data:
            for self.key, self.value in self.data.items():

                #If the key matched the values that we want(rank, title, start_dates, url) then we'll grab those values
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
    
    #Download the Images to use for the GUI
    def downloadImage(self, img_count):
        
        self.img_count = img_count

        self.local_file = urllib.request.urlretrieve(self.url[self.img_count], f'img{self.img_count}')
              
    #Create the Image folder to store images
    def createImgFolder(self):

        img_directory = dname + '/img'

        if not os.path.exists(img_directory):  #Create the image directory if it doesn't already exist
            os.makedirs(img_directory)
    
    #Generates the search token that's used to search on each site
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

    ###########Functions to set the search tokens###########
    def setRedditToken(self, reddit_token):
        self.reddit_token = reddit_token
    
    def setWikiToken(self, wiki_token):
        self.wiki_token = wiki_token
    
    def setYoutubeToken(self, youtube_token):
        self.youtube_token = youtube_token
    
    ###########Functions to retrieve the search tokens###########
    def getRedditToken(self):
        return self.reddit_token

    def getWikiToken(self):
        return self.wiki_token

    def getYoutubeToken(self):
        return self.youtube_token

    ###########Functions to search the Internet for data on the target title###########
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
        

##################This is the Main UI through which all functions that will act upon our main Window ##################
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        self.model = Model()
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method

        uic.loadUi('mainWindow.ui', self) #Load the mainwindow .ui file

        self.search_field = self.findChild(QtWidgets.QLineEdit, 'search_field')
        self.top_button = self.findChild(QtWidgets.QPushButton, 'topUpcoming_button')
        self.discover_button = self.findChild(QtWidgets.QPushButton, 'discover_button')
        self.rand_button = self.findChild(QtWidgets.QPushButton, 'rand_button')

        self.top_button.clicked.connect(self.topUpcomingMenu)
        self.discover_button.clicked.connect(self.discoverMenu)
        self.rand_button.clicked.connect(self.randomMenu)
        
        self.search_field.textChanged.connect(lambda: self.model.apiToMainMenu(self.search_field))
        self.show() #Show the GUI


    #Top Upcoming anime GUI
    def topUpcomingMenu(self):
        self.hide() #Hide the main window
        self.top = TopWindow()
        
    #Discovery Menu GUI
    def discoverMenu(self):
        self.hide() #Hide the main window
        self.discover_window = DiscoverWindow()

    # Radnom Menu GUI
    def randomMenu(self):
        self.hide() #Hide the main window
        self.rand_window = RandomWindow()

########### This is the Top UI through which all functions pertaining to the Discover Window will be created ##################
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
    
    #Function to return to the Main Window
    def home(self):

        self.hide()
        main_win = MainWindow()
        
########### This is the Top UI through which all functions pertaining to the Top Window will be created ##################
class TopWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        os.chdir(dname)
        super(TopWindow, self).__init__()

        uic.loadUi('topUpcoming.ui', self) #Load the topUpcoming.ui file
        
        self.show()
        self.model = Model()
        self.model.createImgFolder()
        self.image_directory = dname + '/img'
        self.titles, self.ranks, self.start_dates, self.url = self.model.apiToTopWindow()
    
        os.chdir(self.image_directory) #Change to the image directory
        self.label = self.findChild(QtWidgets.QLabel, 'top_img')
    
        for self.count in range(len(self.titles)):
            try:
                self.top_button = self.findChild(QtWidgets.QPushButton, 'top_button' + str(self.count))
                self.top_button.setText('[' + str(self.count + 1) + ']' + ': ' + self.titles[self.count])
            
            except:
                print(f'Title: {self.titles[self.count]} will not be appended')
            
        with concurrent.futures.ThreadPoolExecutor() as executor: #Multi-threading to execute multiple downloads simultaneously
        
            self.results_cap = [0, 1 ,2 ,3, 4, 5 , 6, 7, 8, 9, 10, 11, 12 ,13 ,14 ,15 ,16 ,17, 18, 19, 20] # The limit of results that will be returned
            self.f1 = executor.map(self.model.downloadImage, self.results_cap) # Download the images for the GUI
          
        #Set the default image to the first image in the image directory
        self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        self.image_path = self.image_directory + '/img0'
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        self.pixmap2 = self.pixmap.scaled(500, 500)

        os.chdir(dname)
    
        # for self.count in range(0,20):
        #     try:
        #         self.top_button = self.findChild(QtWidgets.QPushButton, 'top_button' + str(self.count))   
        #         self.top_button.clicked.connect(lambda : self.changeImage(self.count, self.label))   
        #     except:
        #             print('fail')
        
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

        self.top_button0.clicked.connect(lambda : self.changeImage(0, self.label, self.model))
        self.top_button1.clicked.connect(lambda : self.changeImage(1, self.label, self.model))     
        self.top_button2.clicked.connect(lambda : self.changeImage(2, self.label, self.model))  
        self.top_button3.clicked.connect(lambda : self.changeImage(3, self.label, self.model))  
        self.top_button4.clicked.connect(lambda : self.changeImage(4, self.label, self.model))  
        self.top_button5.clicked.connect(lambda : self.changeImage(5, self.label, self.model))  
        self.top_button6.clicked.connect(lambda : self.changeImage(6, self.label, self.model))  
        self.top_button7.clicked.connect(lambda : self.changeImage(7, self.label, self.model))  
        self.top_button8.clicked.connect(lambda : self.changeImage(8, self.label, self.model))  
        self.top_button9.clicked.connect(lambda : self.changeImage(9, self.label, self.model))  
        self.top_button10.clicked.connect(lambda : self.changeImage(10, self.label, self.model))  
        self.top_button11.clicked.connect(lambda : self.changeImage(11, self.label, self.model))  
        self.top_button12.clicked.connect(lambda : self.changeImage(12, self.label, self.model))  
        self.top_button13.clicked.connect(lambda : self.changeImage(13, self.label, self.model))  
        self.top_button14.clicked.connect(lambda : self.changeImage(14, self.label, self.model))  
        self.top_button15.clicked.connect(lambda : self.changeImage(15, self.label, self.model))  
        self.top_button16.clicked.connect(lambda : self.changeImage(16, self.label, self.model))  
        self.top_button17.clicked.connect(lambda : self.changeImage(17, self.label, self.model))  
        self.top_button18.clicked.connect(lambda : self.changeImage(18, self.label, self.model))  
        self.top_button19.clicked.connect(lambda : self.changeImage(19, self.label, self.model))  
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
        main_win = MainWindow()

    ################## Function to change the display image/Pixmap for the TopUpcoming window ##################
    def changeImage(self, count, label, model):

        super(TopWindow, self).__init__()
        
        
        self.count = count
        self.label = label
        self.model = model
        
        # Naming the image directiroy
        self.image_directory = dname + '/img'

        #Naming the image downloads
        self.image_path = self.image_directory + '/img' + str(self.count) 
        #Set the image as the background
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        self.pixmap2 = self.pixmap.scaled(500, 500)

        try:
            self.search_string = self.titles[self.count]
        except:
            self.search_string = self.titles[0]

        self.redditToken, self.wikiToken, self.youToken =  self.model.generateSearchToken(self.search_string)
        
        #Set tokens
        self.model.setRedditToken(self.redditToken)
        self.model.setWikiToken(self.wikiToken)
        self.model.setYoutubeToken(self.youToken)

########### This is the Random UI through which all functions pertaining to the Random Window will be created ##################
class RandomWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        self.abspath = os.path.abspath(__file__)
        self.dname = os.path.dirname(abspath)
        os.chdir(self.dname)

        super(RandomWindow, self).__init__()

        #Load the random ui file
        uic.loadUi('random.ui', self)

        self.show()
        self.model = Model()
        self.model.createImgFolder()
        self.image_directory_name = self.dname = '/img'

        self.rand_season = self.model.randSeason()
        self.model.randAnime(self.rand_season)
        


def run():
    app = QtWidgets.QApplication(sys.argv) # Creates an instance of our application
    window = MainWindow() # Creates an instance of our window class
    app.exec_()  #Start the app

run()
