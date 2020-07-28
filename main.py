from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMdiArea, QAction, QMdiSubWindow
from PyQt5.QtGui import QIcon, QPixmap
from jikanpy import Jikan
import sys, os, time, datetime, pprint, webbrowser, concurrent.futures, random
import urllib.request

#Instance of our Jikan class which allows for communication with the Jikan MyAnimeList API
jikan = Jikan()

#Here the directory is set to the current directory from which we're running the Python script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

rand_state = True
########### This is the Model class through which all functions that respond to changes in the  ##################
class Model(QtWidgets.QMainWindow):
    

    def _init_(self):
        print('placeholder')

    #Function which filters data from the Jikan API into something that we can use
    def jikanToYearMenu(self, year_combo, movie_radiobutton, text_browser):
        #Assign the widgets within the window
        self.year_combo = year_combo
        self.year = str(self.year_combo.currentText())
        self.movie_radiobutton = movie_radiobutton
        self.text_browser = text_browser
        

        try:
            try:
                self.year_spring_anime = jikan.season(year=int(self.year), season='spring')
            except:
                print('None returned')
            try:
                self.year_summer_anime = jikan.season(year=int(self.year), season='summer')
            except:
                print('None returned')
            try:
                self.year_fall_anime = jikan.season(year=int(self.year), season='fall')
            except:
                print('None returned')
            try:
                self.year_winter_anime = jikan.season(year=int(self.year), season='winter')
            except:
                print('None returned')

            self.one_year_anime = self.year_spring_anime['anime'] + self.year_summer_anime['anime'] + self.year_fall_anime['anime'] + self.year_winter_anime['anime']
            
          
            #Split the movies and titles
            self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)
            #Create lists of keys
            self.movies_keys = self.movies.keys()
            self.series_keys = self.series.keys()
            #Create alphabetically sorted lists of keys
            self.series_sorted = sorted(self.series_keys)
            self.movies_sorted = sorted(self.movies_keys)
            

            #series without duplicates
            self.series_distinct = []

            #Remove duplicate entries from being displayed
            for self.anime in self.series_sorted:
                if self.anime not in self.series_distinct:
                    self.series_distinct.append(self.anime)
            
            
            if self.movie_radiobutton.isChecked() == True:
                self.text_browser.clear()
                pprint.pprint(self.movies_sorted)
                if len(self.movies_sorted) == 0:
                    self.text_browser.append('Could not locate any titles matching this criteria. Sorry mate, better luck elsewhere.')
                else:
                    self.text_browser.append('******** ' + str(self.year) +  'Movies' + ' ********' + '\n')
                    for self.movie in self.movies_sorted:
                        self.text_browser.append( '['+ '<a href="' + self.movies[self.movie] + f'">{self.movie}</a>' + ']' + '\n')
                    
            
            elif self.movie_radiobutton.isChecked() == False:
                self.text_browser.clear()
                pprint.pprint(self.series_sorted)
                if len(self.series_sorted) == 0:
                    self.text_browser.append('Could not locate any titles matching this criteria. Sorry mate, better luck elsewhere.')
                else:  
                    self.text_browser.append('***** ' + str(self.year) + ' Airing' +  ' Series' + ' *****' + '\n')
                    for self.show in self.series_sorted:
                        self.text_browser.append( '['+ '<a href="' + self.series[self.show] + f'">{self.show}</a>' + ']' + '\n')


        except ConnectionError:
            print('Could not connect to the MAL API at: https://api.jikan.moe/v3')

        except:
            self.text_browser.clear()
            self.text_browser.append('Could not locate any titles matching this criteria. Sorry mate, better luck elsewhere.')
            

    def yearRandomize(self, current_year, radiobutton, text_browser, combobox):
        
        #The active variable which will be used to determine how many times the Random button has been clicked
        
        self.current_year = current_year
        self.movie_radiobutton = radiobutton
        self.text_browser = text_browser
        self.combobox = combobox
        
        self.rand_state = False

        if self.rand_state == False:

            #Loops through until a year is returned with valid series
            self.randomize = True
            while self.randomize:

                self.year = random.randint(1926, self.current_year + 1)
                try:                                   
                    self.year_spring_anime = jikan.season(year= self.year, season='spring')
                except:
                    print('No titles found for the spring')
                try:                                  
                    self.year_summer_anime = jikan.season(year= self.year, season='summer')
                except:
                    print('No titles found for the summer') 
                try:        
                    self.year_fall_anime = jikan.season(year= self.year, season='fall')
                except:
                    print('No titles found for the fall') 
                try:
                    self.year_winter_anime = jikan.season(year= self.year, season='winter')
                except:
                    print('No titles found for the winter')
                
                self.one_year_anime = self.year_spring_anime['anime'] + self.year_summer_anime['anime'] + self.year_fall_anime['anime'] + self.year_winter_anime['anime']

                #Split the movies and titles
                self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)

                if self.movie_radiobutton.isChecked() == False and len(self.series) == 0:
                    continue

                elif self.movie_radiobutton.isChecked() == True and len(self.movies) == 0:
                    continue

                else:
                    self.randomize = False
                    #Split the movies and titles
                    self.movies, self.series = self.movieSeriesSplit(self.one_year_anime)
                    #Create lists of keys
                    self.movies_keys = self.movies.keys()
                    self.series_keys = self.series.keys()
                    #Create alphabetically sorted lists of keys
                    self.series_sorted = sorted(self.series_keys)
                    self.movies_sorted = sorted(self.movies_keys)

                    if self.movie_radiobutton.isChecked() == True:
                        self.text_browser.clear()
                        self.text_browser.append('******** ' + str(self.year) +  ' Movies' + ' ********' + '\n')
                        
                        self.rand_state = False

                        for self.movie in self.movies_sorted:
                            self.text_browser.append( '['+ '<a href="' + self.movies[self.movie] + f'">{self.movie}</a>' + ']' + '\n')
                            


                    elif self.movie_radiobutton.isChecked() == False:
                        self.text_browser.clear()
                        self.text_browser.append('***** ' + str(self.year) + ' Airing' +  ' Series' + ' *****' + '\n')

                        self.rand_state = False

                        for self.show in self.series_sorted:
                            self.text_browser.append( '['+ '<a href="' + self.series[self.show] + f'">{self.show}</a>' + ']' + '\n')

        # elif self.rand_state == True and self.movie_radiobutton.isChecked() == True:                
        #     self.rand_url = self.movies_sorted[random.randint(len(self.movies_sorted))]
        #     try:
        #         webbrowser.open_new_tab(self.rand_url)
        #     except:
        #         print('Connection could not be established')
                
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
        
        #Split the movie titles and their urls
        for self.anime_dict in self.anime_list:
            for self.key, self.value in self.anime_dict.items():
                if self.key == 'type':
                    if self.value == 'Movie':
                        self.title = self.anime_dict['title']
                        self.url = self.anime_dict['url']
                        self.movies[self.title] = self.url
                    #Split the show titles and their urls
                    else:
                        self.title = self.anime_dict['title']
                        self.url = self.anime_dict['url']
                        self.series[self.title] = self.url
          

        return self.movies, self.series       
        

    #Function which filters data from the JiKan API into something that we can use
    def jikanToTopWindow(self):
        
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
              

    def createImgFolder(self):

        img_directory = dname + '/img'

        if not os.path.exists(img_directory):  #Create the image directory if it doesn't already exist
            os.makedirs(img_directory)
    
    #Generates the search token that's used to search on each site
    def generateSearchToken(self, title):

        self.title = title

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

        
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method

        uic.loadUi('mainWindow.ui', self) #Load the mainwindow .ui file

        self.top_button = self.findChild(QtWidgets.QPushButton, 'topUpcoming_button')
        self.discover_button = self.findChild(QtWidgets.QPushButton, 'discover_button')

        self.top_button.clicked.connect(self.topUpcomingMenu)
        self.discover_button.clicked.connect(self.discoverMenu)

        self.show() #Show the GUI



    #Top Upcoming anime GUI
    def topUpcomingMenu(self):
        self.hide() #Hide the main window
        self.top = TopWindow()
        

    #Discovery Menu GUI
    def discoverMenu(self):
        self.hide() #Hide the main window
        self.discover_window = DiscoverWindow()
    
    def randomMenu(self):
        print('Placeholder')

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

        #Values to fill the genrecombobox with
        self.genres = ['Action', 'Adventure', 'Cars', 'Comedy', 'Dementia', 'Demons', 'Mystery', 'Drama', 'Ecchi',
        'Fantasy', 'Game', 'Hentai', 'Historical', 'Horror', 'Kids', 'Magic', 'Martial Arts',
        'Mecha', 'Music', 'Parody', 'Samurai', 'Romance', 'School', 'Sci Fi', 'Shoujo',
        'Shoujo Ai', 'Shounen', 'Shounen Ai', 'Space', 'Sports', 'Super Power', 'Vampire', 'Yaoi',
        'Yuri', 'Harem', 'Slice Of Life', 'Supernatural', 'Military', 'Police', 'Psychological', 'Thriller',
        'Seinen', 'Josei']

        #Assigning the widgets within the window
        self.filter_year_button = self.findChild(QtWidgets.QPushButton, 'filter_year_button')
        self.year_combo = self.findChild(QtWidgets.QComboBox, 'year')
        self.genre_combo = self.findChild(QtWidgets.QComboBox, 'genre_combo')
        self.text_browser = self.findChild(QtWidgets.QTextBrowser, 'year_textBrowser')
        self.series_radiobutton = self.findChild(QtWidgets.QRadioButton, 'series_radioButton')
        self.series_radiobutton_2 = self.findChild(QtWidgets.QRadioButton, 'series_radioButton_2')
        self.movies_radiobutton = self.findChild(QtWidgets.QRadioButton, 'movies_radioButton')
        self.back_button = self.findChild(QtWidgets.QCommandLinkButton, 'backButton')
        self.back_button_2 = self.findChild(QtWidgets.QCommandLinkButton, 'backButton_2')
        self.rand_button = self.findChild(QtWidgets.QPushButton, 'randButton')

        #Set the series radio button to be the one that's checked on startup
        self.series_radiobutton.setChecked(True)
        self.series_radiobutton_2.setChecked(True)
        

        self.filter_year_button.clicked.connect(lambda: self.model.jikanToYearMenu(self.year_combo, self.movies_radiobutton, self.text_browser))

        #Assign click events to the main menu buttons
        self.back_button.clicked.connect(self.home)
        self.back_button_2.clicked.connect(self.home)
        

        #Get the current date/year
        self.now = datetime.datetime.now()
        self.current_year = self.now.year

        self.rand_button.clicked.connect(lambda: self.model.yearRandomize(self.current_year, self.movies_radiobutton, self.text_browser, self.year_combo))

       
        #Fill the combobox with values ranging from 1926 up until the current year. 1926 should be where the first record dates back to
        for self.year in range(1926, self.current_year + 1):
            self.year_combo.addItem(str(self.year))

        #Fill the combobox with the genre values that MAL uses to categorize their anime
        for self.genre in self.genres:
            self.genre_combo.addItem(str(self.genre))
    
    def home(self):

        self.hide()
        self.mainWindow = MainWindow()
        
        
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
        self.titles, self.ranks, self.start_dates, self.url = self.model.jikanToTopWindow()
    
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
        os.chdir(dname)
        self.mainWindow = MainWindow()

    ################## Function to change the display image/Pixmap for the TopUpcoming window ##################
    def changeImage(self, count, label, model):

        super(TopWindow, self).__init__()
        
        
        self.count = count
        self.label = label
        self.model = model
        self.image_directory = dname + '/img'

        # self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        self.image_path = self.image_directory + '/img' + str(self.count) 
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



def run():
    app = QtWidgets.QApplication(sys.argv) # Creates an instance of our application
    window = MainWindow() # Creates an instance of our window class
    app.exec_()  #Start the app

run()
