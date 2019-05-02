import requests

class Fleep():
    """ Sending messages over fleep """

    def __init__(self, token, user=None):
        self.token = token
        self.user = user

    def send(self, message, user=None):
        url = "https://fleep.io/hook/{}".format(self.token)
        sender = user if user is not None else self.user
        requests.post(url, json={"message": message, "user": sender})
