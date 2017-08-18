import requests


class HttpHandler:
    def __init__(self):
        self.s = requests.Session()
        headers = {
            'Accept': 'application/javascript, */*;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0'
        }
        self.s.headers.update(headers)

    def Get(self, url, refer=None):
        try:
            if refer:
                res = self.s.get(url, headers={"Referer": refer})
            else:
                res = self.s.get(url)
            res.encoding = "utf-8"
            print(res.text)
            return res.text
        except Exception as e:
            print(e)

    def Post(self, url, data, refer=None):

        try:
            if refer:
                res = self.s.post(url, data, headers={"Referer": refer})
            else:
                res = self.s.post(url, data)
            res.encoding = "utf-8"
            return res.text
        except Exception as e:
            print(e)

    def Download(self, url):
        with open("./qrcode.png", "wb") as f:
            f.write(self.s.get(url).content)
