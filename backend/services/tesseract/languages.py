import pytesseract


class TesseractLanguages:
    """
    Utility class for managing installed
    Tesseract languages.
    """

    @staticmethod
    def get_installed_languages():
        """
        Returns installed language codes.
        Example:
        ['eng','kan','hin']
        """

        try:
            return sorted(
                pytesseract.get_languages(config="")
            )

        except Exception:
            return []

    @staticmethod
    def is_language_installed(language):

        languages = TesseractLanguages.get_installed_languages()

        return language in languages

    @staticmethod
    def get_language_name(language):

        language_map = {

            "eng": "English",

            "kan": "Kannada",

            "hin": "Hindi",

            "tam": "Tamil",

            "tel": "Telugu",

            "mal": "Malayalam",

            "ben": "Bengali",

            "guj": "Gujarati",

            "mar": "Marathi",

            "ori": "Odia",

            "pan": "Punjabi",

            "urd": "Urdu",

            "fra": "French",

            "deu": "German",

            "spa": "Spanish",

            "ita": "Italian",

            "por": "Portuguese",

            "rus": "Russian",

            "jpn": "Japanese",

            "kor": "Korean",

            "chi_sim": "Chinese (Simplified)",

            "chi_tra": "Chinese (Traditional)"

        }

        return language_map.get(language, language)

    @staticmethod
    def get_languages_for_ui():

        installed = TesseractLanguages.get_installed_languages()

        languages = []

        for lang in installed:

            languages.append({

                "code": lang,

                "name": TesseractLanguages.get_language_name(lang)

            })

        return languages