__pragma__("alias", "S", "$")

from main.authenticate import AuthenticationArea
from main.displayer import Displayer


def main():
    auth = AuthenticationArea("#login")
    displayer = Displayer(auth)


S(main)
