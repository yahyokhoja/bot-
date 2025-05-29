from googletrans import Translator

# Функция перевода текста на таджикский
def translate_to_tajik(text):
    translator = Translator()
    translated = translator.translate(text, src='auto', dest='tg')
    return translated.text
