import os

from ..rtexceptions.rtexceptions import UserException
from ..utils.base import get_homedir


class Account:
    """Class of Account.

    Attributes:
        _token:  Api_token that associate to your Quafu account. If not provided, load locally.

    """
    def __init__(self,
                 api_token: str = None):
        """Account constructor.

        Args:
            api_token: Api Token.
        """
        if api_token is None:
            self.load_account()
        else:
            self._token = api_token
            # self._url = "http://quafu.baqis.ac.cn/"
            self._url = "http://58.205.216.42:5050/"
            self._url_ws = "ws://58.205.216.42:8760"
            # self._url = "http://192.168.220.55:5050/"
            # self._url_ws = "ws://192.168.220.55:8760"
    def save_api_token(self,
                       api_token: str):
        """Save your api_token that associates your quafu account.

        Args:
            api_token: Api Token.
        """
        self._token = api_token
        homedir = get_homedir.get_homedir()
        file_dir = homedir + "/.quafu/"
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        with open(file_dir + "api", "w") as f:
            f.write(self._token + "\n")
            # f.write("http://quafu.baqis.ac.cn/")

    def load_account(self) -> None:
        """Load your Quafu account."""
        homedir = get_homedir()
        file_dir = homedir + "/.quafu/"
        try:
            f = open(file_dir + "api", "r")
            data = f.readlines()
            self._token = data[0].strip("\n")
            # self._url = data[1].strip("\n")
        except Exception as e:
            raise UserException(f"User configure error. Please set up your token. Error: {str(e)}")

    def get_url(self):
        """Get quafu http url."""
        return self._url

    def get_url_ws(self):
        """Get quafu websockets url."""
        return self._url_ws

    def get_token(self):
        """Get user api token."""
        return self._token


