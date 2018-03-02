__pragma__("alias", "S", "$")

from main.authenticate import AuthenticationArea
from main.displayer import Displayer
from main.composer import Composer

openpgp.initWorker({ 'path': 'openpgp/openpgp.worker.min.js' })

def main():
    auth = AuthenticationArea("#login")
    displayer = Displayer(auth)
    composer = Composer(auth, "#composer")


S(main)
