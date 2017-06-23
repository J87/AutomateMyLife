import oauth2client.client
import httplib2
import apiclient
import os
import webbrowser
import datetime


"""--------------The Process - Part 2------------
0. See Part 1 of this tutorial - 
https://automatemylife.org/use-python-to-automatically-get-your-google-analytics-report/
1. Get the Analytics service
2. Get certain fields from the Google Analytics Report API
3. Print out those pesky fields
4. Drink an espresso
5. Make a main function to execute all this
-------------------------------------
References
-------------------------------------
Oauth2 2.0 Explained: https://developers.google.com/api-client-library/python/guide/aaa_oauth
Scopes: https://developers.google.com/identity/protocols/googlescopes
Analytics Reporting API: https://developers.google.com/analytics/devguides/reporting/core/v4/
-------------------------------------
"""

def get_credentials():
    """Gets google api credentials, or generates new credentials
    if they don't exist or are invalid."""
    scope = ['https://www.googleapis.com/auth/adsense.readonly',
             'https://www.googleapis.com/auth/analytics.readonly']

    #get your client secret file
    cwd = os.getcwd()
    pathToFile = os.path.join(cwd,
        'YOURCLIENTSECRETPATH.json')
    print "This is your client secret path:",pathToFile

    #first part of the folow process
    #https://developers.google.com/api-client-library/python/guide/aaa_oauth
    flow = oauth2client.client.flow_from_clientsecrets(pathToFile,scope,redirect_uri='urn:ietf:wg:oauth:2.0:oob')#'urn:ietf:wg:oauth:2.0:oob'
    
    #check to see if you have something already
    storage = oauth2client.file.Storage('creds.dat') #this is a made up file name
    credentials = storage.get()
    
    #if they dont exist already go ahead and get them
    if not credentials or credentials.invalid:
        #get authorization url
        auth_url = flow.step1_get_authorize_url()
        #open the url to get a code
        webbrowser.open(auth_url)

        #enter the code to reauth
        codeStr = str(raw_input('enter code here:'))
        credentials = flow.step2_exchange(codeStr)
        #save the code to the dat
        storage = oauth2client.file.Storage('creds.dat')
        storage.put(credentials)
        
        return credentials

    else:
        return credentials


def get_Analytics_service():
    """Returns Google Analytics Report API"""
    #reference: https://developers.google.com/analytics/devguides/reporting/core/v4/
    credentials = get_credentials()
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = apiclient.discovery.build('analytics', 'v4', http=http)
    print "Got Analytics service"

    return service


def get_report(analytics):
    """Queries the Analytics Reporting API V4."""
    
    #define what window of time you are most interested in
    today = datetime.date.today()
    #im only getting one day in the past
    timeDelta = today - datetime.timedelta(days=1)
    print "Checking dates ",timeDelta," to ",today

    #where to get dimensions 
    #https://developers.google.com/analytics/devguides/reporting/core/dimsmets
    return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': str(timeDelta), 'endDate': str(today)}],
          'metrics': [{'expression': 'ga:sessions'},
                      {'expression':'ga:pageviews'},
                      {'expression':'ga:avgSessionDuration'}],
          #'dimensions': [{'name': 'ga:country'}]
        }]
      }
    ).execute()

def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.
    Args:
    response: An Analytics Reporting API V4 response object
    """
    #fyi this is not my code, i grabbed it from github
    #forgot to copy the url though
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])

    for header, dimension in zip(dimensionHeaders, dimensions):
        print header + ': ' + dimension

    for i, values in enumerate(dateRangeValues):
        print 'Date range: ' + str(i)
        for metricHeader, value in zip(metricHeaders, values.get('values')):
            print metricHeader.get('name') + ': ' + value


def runAnalytics():
    """easy function to run everything"""
    #gets OAuth from the API
    analytics = get_Analytics_service()
    #get the object return from the API
    #send that object to print out useful fields
    response = get_report(analytics)
    print_response(response)

#https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#ReportRequest.FIELDS.view_id
VIEW_ID = 'Your View ID here'
global VIEW_ID

runAnalytics()
