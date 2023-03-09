import os

from exceptions.exceptions import UserException
from utils.base import get_homedir


class Account:
    """
    Class of Account.

    Attributes:
        token:  Apitoken that associate to your Quafu account. If not provided, load locally.
    """
    def __init__(self,
                 apitoken: str = None):
        if apitoken is None:
            self.load_account()
        else:
            self._token = apitoken
            # self._url = "http://quafu.baqis.ac.cn/"
            self._url = "http://127.0.0.1:5000/"
    def save_apitoken(self, apitoken):
        """
        Save your apitoken associate your Quafu account.

        TODO: It may storage many apitoken.
        """
        self.apitoken = apitoken
        homedir = get_homedir.get_homedir()
        file_dir = homedir + "/.quafu/"
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        with open(file_dir + "api", "w") as f:
            f.write(self.apitoken + "\n")
            f.write("http://quafu.baqis.ac.cn/")

    def load_account(self) -> None:
        """
        Load your Quafu account.
        """
        homedir = get_homedir()
        file_dir = homedir + "/.quafu/"
        try:
            f = open(file_dir + "api", "r")
            data = f.readlines()
            self.token = data[0].strip("\n")
            self._url = data[1].strip("\n")
        except:
            raise UserException("User configure error. Please set up your token.")

    def get_url(self):
        return self._url

    def get_token(self):
        return self._token


