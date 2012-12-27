from languages.en_US import translations
defaulttranslations = translations

def setLanguage(lang):
    global translations
    newlang = __import__(lang)
    translations = newlang.translations
    
def unsetLanguage():
    global translations
    translations = defaulttranslations

def translate(phrase):
    if phrase in translations:
        return translations[phrase]
    if phrase in defaulttranslations:
        return defaulttranslations[phrase]
    return phrase