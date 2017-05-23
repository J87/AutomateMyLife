import oauth2client.client
import httplib2
import apiclient
import os
import webbrowser

import adsense_util_data_collator

"""--------------The Process------------
0. Go to console.developers.google.com and enable APIs you want
1. Authorize the app by using Flow class
2. Create a service using Google API endpoints
3. Interact with the API library
4. Drink a beer
-------------------------------------
References
-------------------------------------
Oauth2 2.0 Explained: https://developers.google.com/api-client-library/python/guide/aaa_oauth
Scopes: https://developers.google.com/identity/protocols/googlescopes
Adsense API Classes: https://developers.google.com/resources/api-libraries/documentation/adsense/v1.4/python/latest/
Analytics Reporting API: https://developers.google.com/analytics/devguides/reporting/core/v4/
-------------------------------------
"""

def get_credentials():
    """Gets google api credentials, or generates new credentials
    if they don't exist or are invalid."""

    #scopes are what you request authorization for
    scope = ['https://www.googleapis.com/auth/adsense.readonly']

    cwd = os.getcwd()
    #this should be where your json file is
    pathToFile = os.path.join(cwd,'myPathTo_Client_Secret.json')
    print pathToFile

    #first step of flow process
    #redirect uri can be a custom url for your app
    #'urn:ietf:wg:oauth:2.0:oob' is localhost
    flow = oauth2client.client.flow_from_clientsecrets(pathToFile,scope,redirect_uri='urn:ietf:wg:oauth:2.0:oob')
 	
    #check to see if you have something already
    storage = oauth2client.file.Storage('MyCreds.dat')
    #if its there then get it
    credentials = storage.get()
    
    if not credentials or credentials.invalid:
        #get authorization url
        auth_url = flow.step1_get_authorize_url()
        #open the url to get a code since its the first time
        #this will default to the redirect_uri you set earlier
        webbrowser.open(auth_url)

        #enter the code to auth
        codeStr = str(raw_input('enter code here:'))
        credentials = flow.step2_exchange(codeStr)
        #save the code to the dat
        storage = oauth2client.file.Storage('MyCreds.dat')
        storage.put(credentials)
        
        return credentials

    else:
        return credentials


def get_AdSense_service():
    """Gets the credentials then Returns api service object"""
    credentials = get_credentials()
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = apiclient.discovery.build('adsense', 'v1.4', http=http)
    print "Woot! Got Google Adsense service"

    return service


def whoAmI():
    """Example I found from documentation to print out your account information"""
    service = get_Adsense_service()
    MAX_PAGE_SIZE = 50

    # Retrieve account list in pages and display data as we receive it.
    request = service.accounts().list(maxResults=MAX_PAGE_SIZE)

    while request is not None:
        result = request.execute()
        accounts = result['items']
        for account in accounts:
            print ('Account with ID "%s" and name "%s" was found. '
               % (account['id'], account['name']))

        request = service.accounts().list_next(request, result)

#run the main function
whoAmI()