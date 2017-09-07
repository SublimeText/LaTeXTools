import sublime
import sublime_plugin
import re


class LatexChangeEnvironmentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        new_regions = _find_env_regions(view)
        if not new_regions:
            return

        view.sel().clear()
        for r in new_regions:
            view.sel().add(r)

class LatexToggleEnvironmentStarCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        new_regions = _find_env_regions(view)
        if not new_regions:
            return

        # replace '*' with '' or vice versa for each region
        for r in reversed(new_regions):
            if view.substr(r).endswith('*'):
                view.replace(edit, r, view.substr(r)[:-1])
            else:
                view.replace(edit, r, view.substr(r) + "*")

def _find_env_regions(view):
    """returns the regions corresponding to nearest matching environments"""
    begin_re = r"\\begin(?:\[[^\]]*\])?\{([^\}]*)\}"
    end_re = r"\\end\{([^\}]*)\}"
    begins = view.find_all(begin_re, sublime.IGNORECASE)
    ends = view.find_all(end_re, sublime.IGNORECASE)
    # compile the begin_re (findall does not work if its compiled)
    begin_re = re.compile(begin_re)

    comment_line_re = re.compile(r"\s*%.*")

    def is_comment(reg):
        line_str = view.substr(view.line(reg))
        return comment_line_re.match(line_str) is not None
    begins = [b for b in begins if not is_comment(b)]
    ends = [e for e in ends if not is_comment(e)]

    def extract_begin_region(region):
        """creates a sublime.Region: \\begin{|text|}"""
        s = view.substr(region)
        boffset = len("\\begin{")
        m = begin_re.search(s)
        if m:
            boffset = m.regs[1][0]
        return sublime.Region(region.begin() + boffset, region.end() - 1)

    def extract_end_region(region):
        """creates a sublime.Region: \\end{|text|}"""
        boffset = len("\\end{")
        return sublime.Region(region.begin() + boffset, region.end() - 1)

    new_regions = []
    one_sel = len(view.sel()) == 1

    for sel in view.sel():
        # partition the open and closed environments
        begin_before, begin_after =\
            _partition(begins, lambda b: b.begin() <= sel.begin())
        end_before, end_after =\
            _partition(ends, lambda e: e.end() < sel.begin())

        # get the nearest open environments
        try:
            begin = _get_closest_begin(begin_before, end_before)
            end = _get_closest_end(end_after, begin_after)
        except NoEnvError as e:
            if one_sel:
                sublime.status_message(e.args[0])
                return []
            else:
                continue

        # extract the regions for the environments
        begin_region = extract_begin_region(begin)
        end_region = extract_end_region(end)

        # validity check: matching env name
        if view.substr(begin_region) == view.substr(end_region):
            new_regions.append(begin_region)
            new_regions.append(end_region)
        elif one_sel:
            sublime.status_message(
                "The environment begin and end does not match:"
                "'{0}' and '{1}'"
                .format(view.substr(begin_region), view.substr(end_region))
            )
    if not new_regions:
        sublime.status_message("Environment detection failed")

    return new_regions


def _partition(env_list, is_before):
    """partition the list in the list items before and after the sel"""
    before, after = [], []
    iterator = iter(env_list)
    while True:
        try:
            item = next(iterator)
        except:
            break
        if is_before(item):
            before.append(item)
        else:
            after.append(item)
            after.extend(iterator)
            break
    return before, after


class NoEnvError(Exception):
    pass


def _get_closest_begin(begin_before, end_before):
    """returns the closest \\begin, that is open"""
    end_iter = reversed(end_before)
    begin_iter = reversed(begin_before)
    while True:
        try:
            b = next(begin_iter)
        except:
            raise NoEnvError("No open environment detected")
        try:
            e = next(end_iter)
        except:
            break
        if not b.begin() < e.begin():
            break
    return b


def _get_closest_end(end_after, begin_after):
    """returns the closest \\end, that is open"""
    end_iter = iter(end_after)
    begin_iter = iter(begin_after)
    while True:
        try:
            e = next(end_iter)
        except:
            raise NoEnvError("No closing environment detected")
        try:
            b = next(begin_iter)
        except:
            break
        if not e.begin() > b.begin():
            break
    return e
