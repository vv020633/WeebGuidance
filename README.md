# Weeb Guidance

Weeb Guidance is a GUI tool built atop the functionality of the Jikan anime API and the content available at https://animixplay.to/ The user can select a random episode of an anime series of their choice. This will be handy if you have a series in mind that you want to watch or simply have on in the background, but you don't have a specific episode number in mind. The search bar can be slightly unresponsive at times due to the limitations of the API, So the collection windows provides the opportunity to save titles in a collection (manually input or copy+paste a title) which can be retrieved immediately.

## Top Upcoming Menu
-View Top Upcoming Anime series
-Search for more information on Reddit
-Search for more information on YouTube

## Discover Series Menu
-Discover Titles based on their Genre
-Discover Titles based on the year of their release

## Random Menu
-Generate a random title

## Installation

### Linux

Use the package manager pip to install weeb-guidance
```bash
pip install weeb-guidance
```
or

```bash
pip3 install weeb-guidance
```


### Windows

Download the release and run the installer
## Requirements

Weeb Guidance is available for download on any of the operating systems mentioned:
( Windows 7/ Windows 8 / Windows 10/ Linux )

Google Chrome must be installed in order to run this because it utilizes chrome driver to pull information from web pages The installer should handle the installation of any other dependencies that have been outlined, but I've made a note of them below. 

-bs4
```bash
pip install beautifulsoup4
```

-chromedriver_autoinstaller
```bash
pip install chromedriver-autoinstaller
```

-jikanpy
```bash
pip install jikanpy
```

-pyqt5
```bash
pip install PyQt5
```

-selenium
```bash
pip install selenium
```


## Usage

### Linux

```bash
python3 -m weeb-guidance
```

### Windows

Navigate to shortcut or installation path -> Right-click executable file -> Run as administrator

You should run as administrator!!! Otherwise, Weeb-Guidance won't have full access to the temp file location that it creates which can result in some strange crashes. No bueno.

After running Weeb Guidance you'll likely notice this Window:

*************************************************************************************************************************
![DevToolsListening](https://user-images.githubusercontent.com/33399376/102270518-ff003980-3f15-11eb-8450-d73ac7312684.PNG)
*************************************************************************************************************************


Not to worry as this is the chromedriver loading up. Don't close it, but keep it minimized if you must. Ideally this wouldn't need to be opened, but its a bit of a pain to try to remove it, and an even bigger pain trying to rebuild this using a different method


![MainMenu](https://user-images.githubusercontent.com/33399376/99194364-c9c9c580-2776-11eb-8e43-41b007a65bc5.png)
![Collection](https://user-images.githubusercontent.com/33399376/99194396-04336280-2777-11eb-9372-4da49da4b87b.png)
![DiscoverGenre](https://user-images.githubusercontent.com/33399376/99194406-131a1500-2777-11eb-9b11-1aa1c8a13a03.png)
![DiscoverYear](https://user-images.githubusercontent.com/33399376/99194409-16150580-2777-11eb-8a95-7fee3b04d41f.png)
![TopUpcoming](https://user-images.githubusercontent.com/33399376/99194493-99365b80-2777-11eb-9c10-607f8bee23ef.png)
![Random](https://user-images.githubusercontent.com/33399376/99194421-2f1db680-2777-11eb-9953-167a31e0875e.png)


## Authors and acknowledgment
I would like to thank Humza Younus for crafting the icon/symbol. I would like to thank Grand Wizard/Professor Pat Parslow for not outright failing me in Business Programming when my code was a steaming heap of garbage. LOOK PAT! YOUR ENCOURAGMENT HAS BIRTHED THE CULMINATION OF MY IDEALS. MY MAGNUM OPUS. WITNESS ME!!! 

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate. If anyone wants to build this for MAC, please feel free to reach out.

## Support

Drop me an e-mail at weebguidance@gmail.com if you have any questions, bugs you'd like me to fix, suggestions, collaboration, etc. This is really just something that I've put together as a side project, but if its something you'd like to see improved, then feel free to donate. Guidance.

## License

[MIT](https://choosealicense.com/licenses/mit/)

