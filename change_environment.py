import sublime
import sublime_plugin
import re


class LatexChangeEnvironmentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        begin_re = r"\\begin(?:\[.*\])?\{(.*)\}"
        end_re = r"\\end\{(.*)\}"
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

        if len(view.sel()) != 1:
            message = "Only one cursor is supported for 'change_environment'!"
            sublime.status_message(message)
            return

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

        sel = view.sel()[0]

        # partition the open and closed environments
        begin_before, begin_after = _partition_begins(begins, sel)
        end_before, end_after = _partition_ends(ends, sel)

        # get the nearest open environments
        try:
            begin = _get_closest_begin(begin_before, end_before)
            end = _get_closest_end(end_after, begin_after)
        except NoEnvError as e:
            sublime.status_message(e.args[0])
            return

        # extract the regions for the environments
        begin_region = extract_begin_region(begin)
        end_region = extract_end_region(end)

        # validity check: matching env name
        if view.substr(begin_region) == view.substr(end_region):
            view.sel().clear()
            view.sel().add(begin_region)
            view.sel().add(end_region)
            return
        else:
            message = "The environment begin and end does not match:"\
                "'{0}' and '{1}'"\
                .format(view.substr(begin_region), view.substr(end_region))
            sublime.status_message(message)


def _partition_begins(begins, sel):
    """partition the begins in the begins befor and after the sel"""
    begin_before, begin_after = [], []
    begin_iter = iter(begins)
    while True:
        try:
            b = next(begin_iter)
        except:
            break
        if b.begin() <= sel.begin():
            begin_before.append(b)
        else:
            begin_after.append(b)
            begin_after.extend(begin_iter)
            break
    return begin_before, begin_after


def _partition_ends(ends, sel):
    """partition the ends in the ends befor and after the sel"""
    end_before, end_after = [], []
    end_iter = iter(ends)
    while True:
        try:
            e = next(end_iter)
        except:
            break
        if e.end() < sel.begin():
            end_before.append(e)
        else:
            end_after.append(e)
            end_after.extend(end_iter)
            break
    return end_before, end_after


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
