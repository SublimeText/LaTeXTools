import sublime
import sublime_plugin

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    from latextools_utils import settings, tex_directives
    from getTeXRoot import get_tex_root
else:
    _ST3 = True
    from .latextools_utils import settings, tex_directives
    from .getTeXRoot import get_tex_root

try:  # check whether the dictionaries package is installed
    import Dictionaries
    _DICT_INSTALLED = True
except:
    _DICT_INSTALLED = False


class DictMissing(Exception):
    pass


def normalize_locale(loc):
    """normalizes the locale into the used format"""
    return loc.lower().replace("_", "-")

if _DICT_INSTALLED:
    # mapping from the locales to the names in the dictionary package
    _dictionary_mappings = {
        "eu": "Basque.dic",
        "bg": "Bulgarian.dic",
        "ca": "Catalan.dic",
        "hr": "Croatian.dic",
        "cs": "Czech.dic",
        "da": "Danish.dic",
        "nl": "Dutch.dic",
        "nl-be": "Dutch.dic",
        "nl-nl": "Dutch.dic",
        "en": "English (American).dic",
        "en-en": "English (American).dic",
        "en-us": "English (American).dic",
        "en-au": "English (Australian).dic",
        "en-gb": "English (British).dic",
        "en-ca": "English (Canadian).dic",
        "en-za": "English (South African).dic",
        "et": "Estonian.dic",
        "fr": "French.dic",
        "fr-be": "French.dic",
        "fr-ca": "French.dic",
        "fr-fr": "French.dic",
        "de": "German.dic",
        "de-at": "German_de_AT.dic",
        "de-ch": "German_de_CH.dic",
        "de-de": "German_de_DE.dic",
        "el": "Greek.dic",
        "hu": "Hungarian.dic",
        "it": "Italian.dic",
        "it-it": "Italian.dic",
        "it-ch": "Italian.dic",
        "lt": "Lithuanian.dic",
        "mn": "Mongolian.dic",
        "nb": "Norwegian (Bokmal).dic",
        "nn": "Norwegian (Nynorsk).dic",
        "no": "Norwegian (Nynorsk).dic",
        "no-no": "Norwegian (Nynorsk).dic",
        "pl": "Polish.dic",
        "pt-br": "Portuguese (Brazilian).dic",
        "pt": "Portuguese (European).dic",
        "pt-pt": "Portuguese (European).dic",
        "ro": "Romanian (Modern).dic",
        "ro-mo": "Romanian (Modern).dic",
        "ru": "Russian.dic",
        "ru-mo": "Russian.dic",
        "sr": "Serbian (Cyrillic).dic",
        "sr-sp": "Serbian (Cyrillic).dic",
        "sk": "Slovak_sk_SK.dic",
        "sk-sk": "Slovak_sk_SK.dic",
        "sl": "Slovenian.dic",
        "es": "Spanish.dic",
        "es-ar": "Spanish.dic",
        "es-bo": "Spanish.dic",
        "es-cl": "Spanish.dic",
        "es-co": "Spanish.dic",
        "es-cr": "Spanish.dic",
        "es-do": "Spanish.dic",
        "es-ec": "Spanish.dic",
        "es-sv": "Spanish.dic",
        "es-gt": "Spanish.dic",
        "es-hn": "Spanish.dic",
        "es-mx": "Spanish.dic",
        "es-ni": "Spanish.dic",
        "es-pa": "Spanish.dic",
        "es-py": "Spanish.dic",
        "es-pe": "Spanish.dic",
        "es-pr": "Spanish.dic",
        "es-es": "Spanish.dic",
        "es-uy": "Spanish.dic",
        "es-ve": "Spanish.dic",
        "sv": "Swedish.dic",
        "sv-sv": "Swedish.dic",
        "sv-ar": "Swedish.dic",
        "sv-fi": "Swedish.dic",
        "tr": "Turkish.dic",
        "uk": "Ukrainian_uk_UA.dic",
        "uk-ua": "Ukrainian_uk_UA.dic",
        "vi": "Vietnamese_vi_VN.dic",
        "vi-vn": "Vietnamese_vi_VN.dic"
    }

    def get_dict_path(loc):
        loc = normalize_locale(loc)
        try:
            dict_name = _dictionary_mappings[loc]
        except:
            raise DictMissing()
        dict_path = "Packages/Dictionaries/" + dict_name
        return dict_path
else:
    def get_dict_path(loc):
        loc = normalize_locale(loc)
        if loc == "en-gb":
            return "Packages/Language - English/en_GB.dic"
        elif loc in ["en", "en-us", "en-en"]:
            return "Packages/Language - English/en_US.dic"
        else:
            raise DictMissing()


def _get_locale(view):
    sc_option = tex_directives.\
        parse_tex_directives(view, only_for=["spellcheck"])
    return sc_option.get("spellcheck")


def _get_locale_from_tex_root(view):
    tex_root = get_tex_root(view)
    if not tex_root or tex_root == view.file_name():
        return
    return _get_locale(tex_root)


def update_dict_language(view, extract_from_root):
    loc = (_get_locale(view) or
           extract_from_root and _get_locale_from_tex_root(view))
    if not loc:
        return  # no spellcheck directive found

    try:
        user_sc = settings.get_setting("tex_spellcheck_paths", {})
        dict_path = user_sc.get(loc) or get_dict_path(loc)
    except DictMissing:
        print("dict definition missing for locale '{0}'"
              .format(loc))
        return  # no dict defined for locale
    current_dict = view.settings().get("dictionary")
    if current_dict == dict_path:
        return  # the locale is already set
    view.settings().set("dictionary", dict_path)
    print("Changed dictionary to '{0}'".format(dict_path))


class LatexAutoDetectSpellcheckListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if not view.score_selector(0, "text.tex.latex"):
            return
        update_dict_language(view, False)

    def on_load_event(self, view):
        if not view.score_selector(0, "text.tex.latex"):
            return
        update_dict_language(view, True)
    if _ST3:  # update the dict asynchronous in ST3
        on_load_async = on_load_event
    else:
        on_load = on_load_event


class LatexDetectSpellcheckCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        update_dict_language(view)
