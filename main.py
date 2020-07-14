from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap
from jikanpy import Jikan
import sys, os, time, pprint
import urllib.request

#Instance of our Jikan class which allows for communication with the Jikan MyAnimeList API
jikan = Jikan()

#Here the directory is set to the current directory from which we're running the Python script
def pathHere():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
    
########### This is the Model class through which all functions that respond to changes in the  ##################
class Model(QtWidgets.QMainWindow):
    def _init_(self):
        print('placeholder')

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

    def downloadImage(self, img_count):
        self.img_count = img_count

        for self.count in range(len(self.img_count)):
            self.local_file = urllib.request.urlretrieve(self.url[self.count], f'img{self.count}')
              

    def createImgFolder(self):

        img_directory = dname + '/img'

        if not os.path.exists(img_directory):  #Create the image directory if it doesn't already exist
            os.makedirs(img_directory)

    def redditSearch(self):
        print('placeholder')
    def wikiSearch(self):
        print('placeholder')
    def youTubeSearch(self):
        print('placeholder')   

########### This is the Main UI through which all functions that will act upon our main Window ##################
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('mainWindow.ui', self) #Load the mainwindow .ui file

        self.top_button = self.findChild(QtWidgets.QPushButton, 'topUpcoming_button')
        self.top_button.clicked.connect(self.topUpcomingMenu)

        self.show() #Show the GUI



    #Top Upcoming anime GUI
    def topUpcomingMenu(self):
        self.top = TopWindow()
        

    #Discovery Menu GUi 
    def discoverMenu(self):
        print('Placeholder')
    
    def randomMenu(self):
        print('Placeholder')

########### This is the Top UI through which all functions pertaining to the Top Window will be created ##################
class TopWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(TopWindow, self).__init__()
        uic.loadUi('topUpcoming.ui', self) #Load the topUpcoming.ui file

        self.show()
        
        self.model = Model()
        self.model.createImgFolder()
        self.image_directory = dname + '/img'
        self.titles, self.ranks, self.start_dates, self.url = self.model.jikanToTopWindow()
        
        os.chdir(self.image_directory)

        self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        
        for self.count in range(len(self.titles)):
            try:
                self.top_button = self.findChild(QtWidgets.QPushButton, 'top_button' + str(self.count))
                self.top_button.setText('[' + str(self.count + 1) + ']' + ': ' + self.titles[self.count])
                

            except:
                print(f'Title: {self.titles[self.count]} will not be appended')
        
        self.model.downloadImage(self.url)
              

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

        self.top_button0.clicked.connect(lambda : self.changeImage(0, self.label))
        self.top_button1.clicked.connect(lambda : self.changeImage(1, self.label))     
        self.top_button2.clicked.connect(lambda : self.changeImage(2, self.label))  
        self.top_button3.clicked.connect(lambda : self.changeImage(3, self.label))  
        self.top_button4.clicked.connect(lambda : self.changeImage(4, self.label))  
        self.top_button5.clicked.connect(lambda : self.changeImage(5, self.label))  
        self.top_button6.clicked.connect(lambda : self.changeImage(6, self.label))  
        self.top_button7.clicked.connect(lambda : self.changeImage(7, self.label))  
        self.top_button8.clicked.connect(lambda : self.changeImage(8, self.label))  
        self.top_button9.clicked.connect(lambda : self.changeImage(9, self.label))  
        self.top_button10.clicked.connect(lambda : self.changeImage(10, self.label))  
        self.top_button11.clicked.connect(lambda : self.changeImage(11, self.label))  
        self.top_button12.clicked.connect(lambda : self.changeImage(12, self.label))  
        self.top_button13.clicked.connect(lambda : self.changeImage(13, self.label))  
        self.top_button14.clicked.connect(lambda : self.changeImage(14, self.label))  
        self.top_button15.clicked.connect(lambda : self.changeImage(15, self.label))  
        self.top_button16.clicked.connect(lambda : self.changeImage(16, self.label))  
        self.top_button17.clicked.connect(lambda : self.changeImage(17, self.label))  
        self.top_button18.clicked.connect(lambda : self.changeImage(18, self.label))  
        self.top_button19.clicked.connect(lambda : self.changeImage(19, self.label))  



  
    def changeImage(self, count, label):
        super(TopWindow, self).__init__()
        
        
        self.count = count
        self.label = label
        self.image_directory = dname + '/img'

        # self.label = self.findChild(QtWidgets.QLabel, 'top_img')
        self.image_path = self.image_directory + '/img' + str(self.count) 
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        self.pixmap2 = self.pixmap.scaled(500, 500)




def run():
    app = QtWidgets.QApplication(sys.argv) # Creates an instance of our application
    window = MainWindow() # Creates an instance of our window class
    app.exec_()  #Start the app

run()
