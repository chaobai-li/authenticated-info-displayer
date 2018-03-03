__pragma__("alias", "S", "$")

class Composer:

    CLEARTEXT_MIN_LENGTH = 30


    def __init__(self, authenticator, area):
        self.S = lambda i: S(area).find(i) if i else S(area)
        self.key = openpgp.key.readArmored(self.S().html())["keys"]
        self.authenticator = authenticator
        self.database = firebase.database()
        self.__initialize()

    def __initialize(self):
        html = """
            <div class="composer">
                <div class="input">
                    <div>Input anything you want to tell me.</div>
                    <div><textarea></textarea></div>
                    <div>
                        <button class="send">
                            Encrypt And Send (Requires Login)
                        </button>
                        <button class="encrypt">
                            Encrypt Only (No login, you have to send manually)
                        </button>
                        Make sure everything's correct -
                        you will not see above input again!
                    </div>
                </div>
                <div class="output">
                    <div class="sending">Sending in progress...</div>
                    <div class="sent">Done!</div>
                    <div>
                        Take note of the key below!
                        <pre class="user-key"></pre>
                        Answer will be encrypted with this key!
                    </div>
                    <div><textarea readonly></textarea></div>
                    <div>
                        <button class="reset">Reset</button>
                    </div>
                </div>
            </div>
        """
        self.S().html(html)
        self.S("button.encrypt").click(self.__encryptOnly)
        self.S("button.send").click(self.__encryptAndSend)
        self.S("button.reset").click(lambda: self.__resetComposer(False))
        self.__resetComposer(False)
        self.authenticator.eventLogin.append(lambda: self.__disableSend(False))
        self.authenticator.eventLogout.append(lambda: self.__disableSend(True))

    def __disableSend(self, v):
        self.S("button.send").attr("disabled", v)

    def __toggleSending(self, sending, userKey):
        self.S(".input").hide()
        self.S(".output").show()

        self.S(".output .sending").toggle(sending)
        self.S(".output .sent").toggle(not sending)
        self.S("button.reset").attr("disabled", sending)

        if userKey:
            self.S(".output .user-key").text(userKey)

    def __resetComposer(self, keepInput):
        self.S(".output textarea").val("")
        if not keepInput:
            self.S(".input textarea").val("")
        self.S(".input").show()
        self.S(".output").hide()
        self.S(".output .user-key").text("")

    def __attachRandomKey(self, content):
        key = openpgp.util.hexidump(openpgp.crypto.random.getRandomBytes(16))
        content = "Answer may be encrypted with:\n  {}\n\n{}".format(
            key,
            content
        )
        return content, key

    async def __encryptOnly(self):
        await self.__doEncryptAndSend(False)

    async def __encryptAndSend(self):
        await self.__doEncryptAndSend(True)

    async def __doEncryptAndSend(self, send):
        self.S(".output textarea").val("")

        cleartext = self.S(".input textarea").val().strip()
        if len(cleartext) < self.CLEARTEXT_MIN_LENGTH:
            alert("Cleartext too short.")
            return

        cleartext, userKey = self.__attachRandomKey(cleartext)

        try:
            options = {
                "data": cleartext,
                "publicKeys": self.key,
            }
            encrypted = await openpgp.encrypt(options)
            ciphertext = encrypted.data
            self.S(".output textarea").val(ciphertext)
        except:
            return

        if not send:
            self.__toggleSending(False, userKey)
            return

        self.__toggleSending(True, userKey)
        try:
            newMessageRef = self.database.ref("/private").push()
            await newMessageRef.set({
                "content": ciphertext,
                "sender": self.authenticator.getCurrentUser().uid,
                "timestamp": firebase.database.ServerValue.TIMESTAMP,
                "email": self.authenticator.getCurrentUser().email or "none",
            })
            self.__toggleSending(False)
        except:
            alert("Failed sending message. Is message too long?")
            self.__resetComposer(True) # reset but keep original input
