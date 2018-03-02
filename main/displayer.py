__pragma__("alias", "S", "$")

class Displayer:

    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.authenticator.eventLogin.append(self.__initialize)
        self.authenticator.eventLogin.append(lambda: self.__toggle(True))
        self.authenticator.eventLogout.append(lambda: self.__toggle(False))
        self.initialized = False

    def __toggle(self, v):
        S('[data-auth-display-toggle]').toggle(v)

    def __initialize(self):
        if self.initialized: return

        self.database = firebase.database()

        interests = list(S('[data-auth-display]'))
        for each in interests:
            path = S(each).attr("data-auth-display")
            template = S(each).attr("data-auth-display-template")
            targetAttr = S(each).attr("data-auth-display-attribute")
            useHtml = S(each).attr("data-auth-display-html")
            self.__bindListener(each, path, template, targetAttr, useHtml)

        self.initialized = True

    def __bindListener(self, domObj, path, template, targetAttr, useHtml):
        if not template:
            template = "{}"
        def updater(dbValue):
            text = template.format(dbValue.val())
            if targetAttr:
                S(domObj).attr(targetAttr, text)
            else:
                if useHtml:
                    S(domObj).html(text)
                else:
                    S(domObj).text(text)
        self.database.ref(path).on("value", updater)
