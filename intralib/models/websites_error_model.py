class WebsitesError():
    def __init__(self, url, status, date):
         self.url = url
         self.status = status
         self.date = date

class WebsitesCertificate():
    def __init__(self, url, message="", date=None):
         self.url = url
         self.message = message
         self.date = date

