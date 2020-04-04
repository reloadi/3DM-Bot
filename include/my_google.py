"""
    un ptit wrapper pour faire des search sur google.

"""

import html
from googleapiclient.discovery import build   #Import the library


class Google():
    def __init__(self, **config):
        self.api_key    = config['api_key']
        self.cse_id     = config['cse_id']
        self.results    = []

    def google_query(self, query, api_key, cse_id, **kwargs):
        """return all results or false if none was found"""
        query_service = build("customsearch", "v1", developerKey=self.api_key )  
        query_results = query_service.cse().list(q=query, cx=cse_id, **kwargs ).execute()
        
        r = False
        try:
            r = query_results['items'][0]
        except:
            pass
        return r

    def search(self, search, nb=1):
        """shortcut for search"""
        return self.google_query(search, self.api_key, self.cse_id, num = nb )
