import os
import time

import sublime

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import bibformat, cache, get_setting
else:
    _ST3 = True
    from . import bibformat, cache, get_setting


def write(bib_name, bib_file, bib_entries):
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


def read(bib_name, bib_file):
    cache_name, formatted_cache_name = _cache_name(bib_name, bib_file)

    try:
        meta_data, formatted_entries = cache.read_global(formatted_cache_name)
    except:
        raise cache.CacheMiss()

    # raise a cache miss if the modification took place after the caching
    modified_time = os.path.getmtime(bib_file)
    if modified_time > meta_data["cache_time"]:
        raise cache.CacheMiss()

    # validate the format string are still valid
    if any(meta_data[s] != get_setting("cite_" + s)
           for s in ["panel_format", "autocomplete_format"]):
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
        "autocomplete_format": autocomplete_format,
        "panel_format": panel_format
    }
    # TODO we might need to keep keys like "author"
    formatted_entries = [
        {
            "keyword": entry["keyword"],
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
