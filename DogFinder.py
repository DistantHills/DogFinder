# DogFinder.py
#
# Script to search various rescue websites for suitable dogs
# (suitable = available, child-friendly and reasonably local).
# Output is an HTML file with suitable dogs 
# V1 Sep 2021 Estella - initial version

import urllib2, re

########################################################
# Simple class to store key info about a dog
########################################################
class DogInfo(object):
    def __init__(self):
        self.mName = ""
        self.mURL = ""
        # WIBNI - add description and photo from the site
        self.description = ""


########################################################
# Generic base class to provide tools to access a rescue website
#
# @@@ Note to self - consider changing to an abstract class using ABC, 
# because that's basically what this is (abstract class or interface definition)
########################################################
class RescueWebsite(object):
    def __init__(self):
        self.mSiteDisplayName = ""
        self.mCurrentDogListPage = None
        self.mCurrentDogPage = None
        print "RescueWebsite init"
        
    
    # gotoNextDogListPage()
    #
    # First time this is called, downloads the first
    # page listing dogs.  
    # Next time(s) gets the next list page, until 
    # we run out of list pages.
    #
    # Returns True = we got a new page, False = no more list pages
    def gotoNextDogListPage(self):
        self.mCurrentDogPage = None
        gotNextPage = True
        return gotNextPage
    
    # gotoNextDogPage()
    #
    # First time this is called, downloads the page
    # for the first dog on the current list page. 
    # Next time(s) gets the page for the next dog, until 
    # we run out of dogs on that page.
    #
    # Returns True = we got a new dog page, False = no more dogs on the list page
    def gotoNextDogPage(self):
        return False
    
    
    # getCurrentDogInfo()
    #
    # If the dog on the current page is suitable,
    # returns DogInfo with info about the dog, otherwise returns None
    def getCurrentDogInfo(self):
        return None
    
    
########################################################
# Specific class to access the Blue Cross website
# @@@ To do - when to set display name, prob need to add to init() then call super class
########################################################
class BlueCross(RescueWebsite):

    def gotoNextDogListPage(self):
        # @@@ still to be implemented fully
        # For the BlueCross, we're only interested in dogs that:
        # - are not reserved
        # - are in the Oxford or Southampton centres.
        #
        # Notes: 
        # - we ignore the "can live with" options on their page because it's 
        # not clear how the 2 different child options interact, so we'd prefer to
        # check that ourselves
        # - Currently the list looks like it's on a single page.  I can't think of a way to 
        # check if it might go onto multiple pages if they have lots of animals.
        print "@@@ BlueCross, go to next list page"
        urlString = "https://www.bluecross.org.uk/rehome/dog?Location=Hampshire:%20Southampton%20rehoming%20centre,Oxfordshire:%20Burford%20rehoming%20centre&Reserved=No"
        mCurrentDogPage = None
        # @@@ still to be implemented fully
        gotNextPage = False
        return gotNextPage
 
    
########################################################
# Specific class to access the SN Dogs website
# @@@ To do - when to set display name, prob need to add to init() then call super class
########################################################
class SNDogs(RescueWebsite):

    def __init__(self):
        RescueWebsite.__init__(self)
        self.mSiteDisplayName = "SNDogs"
        self.mGoodDogURLs = []
        self.mCurrentGoodDogIndex = -1
        OnCurrentListPage = None
    
    def gotoNextDogListPage(self):
        # For SN Dogs:
        # - no option to filter for locations 
        #   (all dogs are in Swindon) or reserved status.
        # - all results on a single page
        print "@@@" + self.mSiteDisplayName + " list page"
        print self.mSiteDisplayName
        wentToNextListPage = False
        if self.mCurrentDogListPage == None:
            # Store the HTML for dog list page
            print "@@ go to first (& only) page"
            response = urllib2.urlopen("https://www.sndogs.uk/adopt-a-dog/available-dogs/")
            self.mCurrentDogListPage = response.read()
            response.close()
            
            # While we're here, search the HTML and 
            # store a list of all unreserved dog URLs, for use later
            #
            # Each dog starts with <div class="dog-box three-in-a-row odd">
            # followed by the per-dog URL - which we want - 
            # then<div class="dog-photo"> (for a good dog)
            # or <span class="reserved-banner"> for a bad/reserved dog.
            goodDogRegex = '<div class="dog-box three-in-a-row odd">\s+<a href="(\S*)">\s+<div class="dog-photo">'
            
            # @@ for testing - temporarily include reserved dogs, so we can check our bad dog theory
            # goodDogRegex = '<div class="dog-box three-in-a-row odd">\s+<a href="(\S*)">\s+'
            
            self.mGoodDogURLs = re.findall(goodDogRegex, self.mCurrentDogListPage)
            self.mCurrentGoodDogIndex = -1
            self.mCurrentDogPage = None
            wentToNextListPage = True
        return wentToNextListPage

    # Download HTML for next dog page (if available)
    def gotoNextDogPage(self):
        print "@@@" + self.mSiteDisplayName + " goto dog page"
        self.mCurrentDogPage = ""
        wentToNextDogPage = False
        # Note to self - python lists index from 0
        self.mCurrentGoodDogIndex = self.mCurrentGoodDogIndex  + 1
        if self.mCurrentGoodDogIndex < len(self.mGoodDogURLs):
            response = urllib2.urlopen(self.mGoodDogURLs[self.mCurrentGoodDogIndex])
            self.mCurrentDogPage = response.read()
            response.close()
            
            wentToNextDogPage = True
        return wentToNextDogPage
    
    def getCurrentDogInfo(self):
        # For SNDogs, rule out any dogs that say "<p><strong>Can live with children?</strong> No</p>"
        # but otherwise assume they're fine
        dogInfo = None
        
        if re.search("<p><strong>Can live with children\?<\/strong>\s*No", self.mCurrentDogPage) is None:
            dogInfo = DogInfo()
            nameSearch = re.search('<title>(\S+) -', self.mCurrentDogPage)            
            dogInfo.mName = nameSearch.group(1)
            dogInfo.mURL = self.mGoodDogURLs[self.mCurrentGoodDogIndex]
        else:
            print "@@@ Ignore dog who can't live with children"
            
        return dogInfo

########################################################
# Specific class to access the Dogs Trust website
########################################################
class DogsTrust(RescueWebsite):

    def __init__(self):
        RescueWebsite.__init__(self)
        self.mSiteDisplayName = "Dogs Trust"
        self.mGoodDogURLs = []
        mCurrentListPageIndex = 0
        self.mCurrentGoodDogIndex = -1
        OnCurrentListPage = None
    
    def gotoNextDogListPage(self):
        # For DogsTrust:
        # - can only filter for 3 locations.  That's good enough for now - we'll do Evesham, Newbury and Kenilworth
        #   but in future may want to get all dogs, and then manually search for ~5 locations
        #   near us
        # - looks like reserved dogs are already filtered out
        # - results are on multiple pages
        print "@@@" + self.mSiteDisplayName + " list page"
        wentToNextListPage = False
        if self.mCurrentDogListPage == None:
            # Store the HTML for first dog list page
            # We have to spoof a user agent, otherwise the request is blocked
            print "@@ go to first page"
            url = "https://www.dogstrust.org.uk/rehoming/dogs/filters/eve~~~~~n~~sec?extra-centre=ken,new"
            request = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
            response = urllib2.urlopen(request)
            self.mCurrentDogListPage = response.read()
            response.close()
            
            # Search the HTML and 
            # store a list of all dog URLs, for use later
            #
            # Each dog on the list page starts with class="grid__element" href="/rehoming/dogs/dog/filters/~~~~~n~~sec/1249876/alba">
            # From testing, we can access a dog via a simpler URL - https://www.dogstrust.org.uk/rehoming/dogs/dog/1249876/alba
            # Note - this goodDogRegex will need updating if we update the search filter
            goodDogRegex = 'class="grid__element" href="\/rehoming\/dogs\S+sec\/(\S+)\?'
            
            self.mGoodDogURLs = re.findall(goodDogRegex, self.mCurrentDogListPage)
            # Interesting, we can use list comprehension to prefix the URLs in one go (rather like R)
            self.mGoodDogURLs = [("https://www.dogstrust.org.uk/rehoming/dogs/dog/"+ partURL) for partURL in self.mGoodDogURLs]
            
            self.mCurrentListPageIndex= 1
            self.mCurrentGoodDogIndex = -1
            self.mCurrentDogPage = ""
            wentToNextListPage = True
        else:
            # Go to next page, if there is one.
            # Is there a "Next page" button on the current list page?
            # If so, go to its URL @@@ ECLC in progress
            # These have URLs https://www.dogstrust.org.uk/rehoming/dogs/filters/eve~~~~~n~~sec/page/2?extra-centre=ken,new
            
            re.search('id="BodyContent_DogList1_lnkNext" class="btn btn-primary btn--next" rel="next">', self.mCurrentDogListPage)
            
            id="BodyContent_DogList1_lnkNext" class="btn btn-primary btn--next" rel="next">
            href="/rehoming/dogs/filters/eve~~~~~n~~sec/page/2?extra-centre=ken,new" id="BodyContent_DogList1_lnkNext" class="btn btn-primary btn--next" rel="next">Next page
            
            print "@@@ To do - move to next page, if there is one"
            #
        return wentToNextListPage

    # Download HTML for next dog page (if available
    # @@@ Could move this to base class, because SN & DogsTrust are identical
    def gotoNextDogPage(self):
        print "@@@" + self.mSiteDisplayName + " goto dog page"
        self.mCurrentDogPage = ""
        wentToNextDogPage = False
        # Note to self - python lists index from 0
        self.mCurrentGoodDogIndex = self.mCurrentGoodDogIndex  + 1
        if self.mCurrentGoodDogIndex < len(self.mGoodDogURLs):
            request = urllib2.Request(self.mGoodDogURLs[self.mCurrentGoodDogIndex], headers={'User-Agent' : "Magic Browser"}) 
            response = urllib2.urlopen(request)
            self.mCurrentDogPage = response.read()
            response.close()
            
            wentToNextDogPage = True
        return wentToNextDogPage
    
    def getCurrentDogInfo(self):
        # For Dogs Trust - even if you filter for secondary school age-suitable,
        # it still shows some dogs that are adult-only in the description.
        # We need to filter these out
        # Future task - they sometimes give a minimum age - put this into the description (or filter out if too old)
        dogInfo = None
        
        if re.search("adult only", self.mCurrentDogPage) is None:
            dogInfo = DogInfo()
            # The Dogs Trust title sometimes has non-alphanumeric characters, so it's easier to use 
            # <meta property="keywords" content="Evie" /> to get the name
            nameSearch = re.search('<meta property="keywords" content="(\S+)"', self.mCurrentDogPage)            
            dogInfo.mName = nameSearch.group(1)
            dogInfo.mURL = self.mGoodDogURLs[self.mCurrentGoodDogIndex]            
        else:
            print "@@@ Discard adult only dog"
        return dogInfo



########################################################
# Code runs from here
########################################################
# Create a list of sites to search
sitesToSearch = [DogsTrust(), SNDogs()]
#sitesToSearch.append(rescueSite)
    
# Output the results as HTML, for more user-friendly display
outputHTML = '<html lang="en-US"> \
    <!--<![endif]-->  \
    <head>  \
    <meta charset="UTF-8" />    \
    <meta id="viewport" name=viewport content="width=1000"> <title>Possible dogs</title> \r \
    <body> <table>\r'
    
    
for site in sitesToSearch:
    # site.gotoNextDogListPage()
    # site.gotoNextDogListPage()
    
    while (site.gotoNextDogListPage()):
        while (site.gotoNextDogPage()):
            dogInfo = site.getCurrentDogInfo()
            if dogInfo is not None:
                print dogInfo.mName
                outputHTML = outputHTML + "<tr><td>" + site.mSiteDisplayName + \
                         "</td><td> <a href=\"" + dogInfo.mURL + "\">" + dogInfo.mName + "</a></td></tr>"

    # try:
        # site.gotoNextDogListPage()
        # site.gotoNextDogListPage()
        
        # # while (site.gotoNextDogListPage()):
            # # while (site.gotoNextDogPage()):
                # # dogInfo = site.getCurrentDogInfo()
                # # print "@@@ got dog info"
    # except:
        # print "@@@ problem accessing site"
        # print 
        
# Wrap up & finish
outputHTML = outputHTML + "</table> </body>"

with open("results.html", "w") as outputFile:
    outputFile.write(outputHTML)
    
