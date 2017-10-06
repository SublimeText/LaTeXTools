import bs4
import functools
import re

from . import external_command
from .distro_utils import using_miktex


@functools.lru_cache()
def get_doc_path():
    if using_miktex():
        command = ["mthelp", "--list-only", "latex2e.html"]
    else:
        command = ["texdoc", "-l", "-M", "latex2e.html"]

    return_code, stdout, _ = external_command.execute_command(command)

    if return_code != 0:
        print("Error on retrieving the documentation path.")
        return ""

    doc_path = stdout.strip()

    return doc_path


# from https://stackoverflow.com/a/23243553/5963435
def bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)
    html = re.sub('\n', ' ', html)
    html = re.sub('[\s]+<', '<', html)
    html = re.sub('>[\s]+', '>', html)
    return html


@functools.lru_cache()
def get_doc_content(doc_path):
    with open(doc_path) as fh:
        content = fh.read()
    return content


@functools.lru_cache()
def get_doc_soup_handler():
    doc_path = get_doc_path()
    content = get_doc_content(doc_path)
    soup = bs4.BeautifulSoup(content, 'html.parser')
    return soup


@functools.lru_cache()
def _get_command_href_map():
    soup = get_doc_soup_handler()

    command_index = soup.find("a", {"name": "Command-Index_fn_symbol-7"})

    first_row = command_index.parent.parent
    first_row = first_row.next_sibling.next_sibling
    first_row = first_row.next_sibling.next_sibling

    command_href_map = {}

    i = 0
    row = first_row
    while i < 1000 and row.name != "hr":
        i += 1
        # the section ends at a hr line
        if row.name == "hr" or row.hr is not None:
            break
        try:
            children = list(row.children)
        except AttributeError:
            row = row.next_sibling
            continue
        try:
            code = children[1].code
            href = children[3].a["href"]
        except IndexError:
            print("IndexError at parsing {}".format(row))
            break
        except KeyError:
            print("KeyError at parsing href from {}".format(row))
            break

        command = str(next(code.children)).strip()

        command_href_map[command] = href

        row = row.next_sibling.next_sibling

    return command_href_map


@functools.lru_cache()
def _get_env_href_map():
    soup = get_doc_soup_handler()

    command_index = soup.find("a", {"name": "Command-Index_fn_letter-A"})

    first_row = command_index.parent.parent
    first_row = first_row.next_sibling.next_sibling
    first_row = first_row.next_sibling.next_sibling

    env_href_map = {}

    i = 0
    row = first_row
    while i < 1000 and row:
        i += 1
        # the section ends at a hr line
        try:
            children = list(row.children)
        except AttributeError:
            row = row.next_sibling
            continue

        try:
            is_env = children[1].span.text == "environment"
        except Exception:
            is_env = False

        if is_env:
            try:
                code = children[1].code
                href = children[3].a["href"]
            except IndexError:
                print("IndexError at parsing {}".format(row))
                break
            except KeyError:
                print("KeyError at parsing href from {}".format(row))
                break

            env = str(next(code.children)).strip()

            env_href_map[env] = href

        try:
            row = row.next_sibling.next_sibling
        except AttributeError:
            break

    return env_href_map


def read_command_documentation(command):
    command_href_map = _get_command_href_map()

    try:
        href = command_href_map[command]
    except KeyError:
        return

    return read_href_section(href)


def read_env_documentation(env):
    env_href_map = _get_env_href_map()

    try:
        href = env_href_map[env]
    except KeyError:
        return

    return read_href_section(href)


@functools.lru_cache(maxsize=1024)
def read_href_section(href):
    return _read_section(_follow_href(href))


def _follow_href(href):
    soup = get_doc_soup_handler()
    target = soup.find("a", {"name": href.lstrip("#")})
    start = target
    return start


def _has_class(node, css_class):
    try:
        return css_class in node["class"]
    except AttributeError:
        return False


def _read_section(start_node):
    content = []
    current = start_node
    while current is not None:
        if current.name == "div" and _has_class(current, "header"):
            pass
        else:
            content.append(current)
        current = current.next_sibling
        if current.name in ("hr",):
            break

    return "\n".join(str(c) for c in content)
