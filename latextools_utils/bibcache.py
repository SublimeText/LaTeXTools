import os
import time

import sublime

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import bibformat, cache, get_setting
else:
    _ST3 = True
    from . import bibformat, cache, get_setting

_VERSION = 1


def write_fmt(bib_name, bib_file, bib_entries):
    """
    Writes the entries resulting from the bibliography into the cache.
    The entries are pre-formatted to improve the time for the cite
    completion command.
    These pre-formatted entries are returned and should be used in the
    to improve the time and be consistent with the return values.

    Arguments:
    bib_name -- the (unique) name of the bibliography
    bib_file -- the bibliography file, which resulted in the entries
    bib_entries -- the entries, which are parsed from the bibliography

    Returns:
    The pre-formatted entries, which should be passed to the cite
    completions
    """
    cache_name, formatted_cache_name = _cache_name(bib_name, bib_file)

    current_time = time.time()

    # write the full unformatted bib entries into the cache together
    # with a time stamp
    print("Writing bibliography into cache {0}".format(cache_name))
    cache.write_global(cache_name, (current_time, bib_entries))

    # create and cache the formatted entries
    formatted_entries = _create_formatted_entries(formatted_cache_name,
                                                  bib_entries, current_time)
    return formatted_entries


def read_fmt(bib_name, bib_file):
    """
    Reads the cache file of a bibliography file.
    If the bibliography file has been changed after the caching, this
    will result in a CacheMiss.
    These entries are pre-formatted and compatible with cite
    completions.

    Arguments:
    bib_name -- the (unique) name of the bibliography
    bib_file -- the bibliography file, which resulted in the entries

    Returns:
    The cached pre-formatted entries, which should be passed to the
    cite completions
    """
    cache_name, formatted_cache_name = _cache_name(bib_name, bib_file)

    try:
        meta_data, formatted_entries = cache.read_global(formatted_cache_name)
    except:
        raise cache.CacheMiss()

    # raise a cache miss if the modification took place after the caching
    modified_time = os.path.getmtime(bib_file)
    if modified_time > meta_data["cache_time"]:
        raise cache.CacheMiss()

    # validate the version and format strings are still valid
    if (meta_data["version"] != _VERSION or
            any(meta_data[s] != get_setting("cite_" + s)
                for s in ["panel_format", "autocomplete_format"])):
        print("Formatting string has changed, updating cache...")
        # read the base information from the unformatted cache
        current_time, bib_entries = cache.read_global(cache_name)
        # format and cache the entries
        formatted_entries = _create_formatted_entries(formatted_cache_name,
                                                      bib_entries,
                                                      current_time)

    return formatted_entries


def _cache_name(bib_name, bib_file):
    file_hash = cache.hash_digest(bib_file)
    cache_name = "bib_{0}_{1}".format(bib_name, file_hash)
    formatted_cache_name = "bib_{0}_fmt_{1}".format(bib_name, file_hash)
    return cache_name, formatted_cache_name


def _create_formatted_entries(formatted_cache_name, bib_entries, cache_time):
    # create the formatted entries
    autocomplete_format = get_setting("cite_autocomplete_format")
    panel_format = get_setting("cite_panel_format")

    meta_data = {
        "cache_time": cache_time,
        "version": _VERSION,
        "autocomplete_format": autocomplete_format,
        "panel_format": panel_format
    }
    formatted_entries = [
        {
            "keyword": entry["keyword"],
            "<prefix_match>": bibformat.create_prefix_match_str(entry),
            "<panel_formatted>": [
                bibformat.format_entry(s, entry) for s in panel_format
            ],
            "<autocomplete_formatted>":
                bibformat.format_entry(autocomplete_format, entry)
        }
        for entry in bib_entries
    ]

    cache.write_global(formatted_cache_name, (meta_data, formatted_entries))
    return formatted_entries
