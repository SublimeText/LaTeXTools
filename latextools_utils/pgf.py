import re


def get_pgfkeys_value(kv_str, key, strip=False):
    """
    Extract the value of a pgfkeys like string.

    I.e. a string with the format:
    k1=value1, k2={long value 2}
    """
    if not kv_str:
        return
    # TODO this is only heuristically over re search and
    # can still be improved
    m = re.search(key + r"\s*=\s*(\{[^\}]+\}|\w+)", kv_str)
    if not m:
        return
    result = m.group(1)
    if (strip and result and result.startswith("{") and
            result.endswith("}")):
        result = result[1:-1]
    return result
