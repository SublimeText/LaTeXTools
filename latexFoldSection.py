from __future__ import print_function
import sublime
import sublime_plugin
import re

if sublime.version() < '3000':
    _ST3 = False
else:
    _ST3 = True

SECTION_TYPES = ['part', 'chapter', 'section', 'subsection',
                 'subsubsection', 'paragraph', 'subparagraph']

def get_begin_mark_patter(sec_type):
    return r'\\' + sec_type + r'\*?(?:\[.*\])?\{.*\}(?:\s*%\s\(fold\))?'

def get_end_mark_patter(sec_type):
    return r'%\s*' + sec_type + r'.*\s*\(end\)'

# Find top level's mark name in this buffer
# return None if find failed
def find_top_level(view):
    top_level = None
    for i in SECTION_TYPES:
        regions = view.find_all(get_begin_mark_patter(i))
        if len(regions) == 0:
            continue
        else:
            top_level = i
            break
    return top_level

def get_Region(a, b):

    if _ST3:
        return sublime.Region(a, b)
    else:
        return sublime.Region(long(a), long(b))


# Retrive all segments by section types
# returned result is a list, each element in it 
# is a tuple in the form of
# [Region of this sec_type, Fold start mark's Region, Fold End mark's region]
# the first one is the area really needed to fold
# latter ones are used to judge whether the current cursor's position
# is in fold start mark or end mark
def find_sec_regions(view, sec_type):

    extrame_fold = sublime.load_settings("LaTeXTools.sublime-settings").get('extreme_fold')

    if extrame_fold != "ALL":
        extrame_fold = True
    else:
        extrame_fold = False

    begin_mark = get_begin_mark_patter(sec_type)
    end_mark = get_end_mark_patter(sec_type)

    # Find sec_type's parent mark in region range a to b
    # if find, return first match's index, else return None
    def find_parent_tags(sec_type, a, b):
        
        result = []
        s = view.substr(get_Region(a,b))
        for i in SECTION_TYPES[:SECTION_TYPES.index(sec_type)]:
            rs = re.findall(get_begin_mark_patter(i), s)
            if len(rs) != 0:
                for r in rs:
                    m_pos = s.find(r)
                    m_size = len(r)
                    result.append(get_Region(a + m_pos, a + m_pos + m_size))

        # sorted by apperance
        return sorted(result, key = lambda x: x.begin())

    # Find sec_type's parent mark in region range a to b
    # if find, return first match's index, else return None
    def find_child_tags(sec_type, a, b):
        result = []
        s = view.substr(get_Region(a,b))
        for i in SECTION_TYPES[SECTION_TYPES.index(sec_type) + 1:]:
            rs = re.findall(get_begin_mark_patter(i), s)
            if len(rs) != 0:
                for r in rs:
                    m_pos = s.find(r)
                    m_size = len(r)
                    result.append(get_Region(a + m_pos, a + m_pos + m_size))

        return sorted(result, key = lambda x: x.begin())

    start_regions = view.find_all(begin_mark)
    code_segs = []

    for i in range(len(start_regions)):
        current_mark = start_regions[i]
        if i + 1 < len(start_regions):
            next_mark = start_regions[i + 1]
        else:
            next_mark = view.line(view.size()) # last line

        parent_tags = find_parent_tags(sec_type, current_mark.end(), next_mark.begin())
        
        # if there is no parent tags
        if len(parent_tags) != 0:
            next_mark = parent_tags[0]

        child_tags = find_child_tags(sec_type, current_mark.end(), next_mark.begin())

        if extrame_fold: # if extreme_fold set to all, ignore the end mark in the form of '% ... (end)'
            if len(child_tags) != 0:
                first_end_mark = view.find(end_mark, child_tags[-1].end())
            else:
                first_end_mark = view.find(end_mark, current_mark.end())

            if not _ST3 and first_end_mark == None:
                first_end_mark = sublime.Region(-1, -1)        

            # if there is no end mark or next end mark is bellow next same level's mark
            # or a parents' mark
            if first_end_mark.begin() == -1 or first_end_mark.begin() > next_mark.begin():
                current_end_mark = next_mark
            else:
                current_end_mark = first_end_mark
        else:
            current_end_mark = next_mark

        # if just one line at the last
        if current_mark.end() == current_end_mark.end():
            content = get_Region(current_mark.end(), current_mark.end())
        else:
            content = get_Region(current_mark.end(), 
                view.line(current_end_mark.begin()).begin() - 1)
        code_segs.append([content, current_mark, current_end_mark])

    return code_segs


# Functions to find all foldable code segments
# This function is only used for fold to toc when
# extreme_fold set to None
def find_all_fold(view, depth = None):

    # Find fold depth
    if depth != None:
        top_level = find_top_level(view)
        if top_level != None:
            top_level = SECTION_TYPES.index(top_level)
            if top_level + depth - 1 > len(SECTION_TYPES):
                search_secs = SECTION_TYPES[top_level:]
            else:
                search_secs = SECTION_TYPES[top_level:top_level + depth]
    else:
        search_secs = SECTION_TYPES

    # Finding all regions need to be folded
    result = []
    for sec in search_secs:
        r = find_sec_regions(view, sec)
        if len(r) == 0:
            continue
        result += r

    return result

# Reform the whole buffer to foldable regions following 
# the struct of TOC. Return result format is identical to 
# find_sec_regions function, this function is only used for
# none extreme_fold satuations
def get_toc(view):
    s = sublime.load_settings("LaTeXTools.sublime-settings")
    fold_toc_depth = s.get('fold_toc_depth')

    if fold_toc_depth == None:
        fold_toc_depth = 4
        
    # Get all codes
    code_segs = find_all_fold(view, depth = fold_toc_depth)

    # Sorted by start mark position
    code_segs = sorted(code_segs, key = lambda x: x[0].begin())

    # Generating toc fold region
    toc_strc = []
    for i in code_segs:
        if code_segs.index(i) < len(code_segs) - 1:
            j = code_segs[code_segs.index(i) + 1]
            if i[0].end() > j[0].begin():
                    toc_strc.append([
                        get_Region(i[0].begin(), view.line(j[0].begin()).begin() - 1),
                        i[1], # i's start mark as new start mark
                        j[1]  # j's start mark as new end mark
                    ])
            else:
                toc_strc.append(i)
        else:
            toc_strc.append(i)

    return toc_strc

def extreme_fold(view, FocusCurrent = False):
    depth = sublime.load_settings("LaTeXTools.sublime-settings").get('fold_toc_depth')

    if depth == None:
        depth = 4

    top_level = find_top_level(view)

    if top_level != None:
        top_level = SECTION_TYPES.index(top_level)
        if top_level + depth - 1 > len(SECTION_TYPES):
            search_secs = SECTION_TYPES[top_level:]
        else:
            search_secs = SECTION_TYPES[top_level:top_level + depth]

    s = r'|'.join([get_begin_mark_patter(x) for x in search_secs])
    # print(get_begin_mark_patter(s))
    regions = view.find_all(s)
        
    for r in regions:
        if r != regions[-1]:
            j = regions[regions.index(r) + 1]
            nr = sublime.Region(view.line(r.end()).end(), view.line(j.begin()).begin() - 1)
        else:
            if view.line(r.end()).end() != view.size():
                nr = sublime.Region(view.line(r.end()).end(), view.size())
            else:
                nr = None

        if FocusCurrent and (nr == None or nr.contains(view.sel()[0].b)):
            continue
        else:
            view.fold(nr)

# Fold whole buffer to "Table of Contents",
# TOC depth is set by "fold_toc_depth" in settings files 
class LatexFoldTocCommand(sublime_plugin.TextCommand):

    def run(self, edit, FocusCurrent = False):

        view = self.view

        extrame_fold = sublime.load_settings("LaTeXTools.sublime-settings").get('extreme_fold')

        if extrame_fold == None or extrame_fold == 'TOC':
            extreme_fold(view, FocusCurrent)
            return

        # Getting fold_toc_depth from settings
        toc_strc = get_toc(view)

        point = view.sel()[0].end()
        for i in toc_strc:

            region_span = i[0].cover(i[1])

            # whether end mark is in the form of '% ... (end) form'
            # if it is, end mark should be in the region
            if re.search(r'%\s*.*\(end\)', view.substr(i[2])) != None:
                region_span = region_span.cover(i[2])

            if FocusCurrent and region_span.contains(point):
                continue
            else:
                view.fold(i[0])



# Command to fold expect levels.
class LatexFoldLevelCommand(sublime_plugin.TextCommand):

    def run(self, edit, FoldLevel = 1):

        view = self.view

        # Get top level mark
        top_level = find_top_level(view) 

        # Only work when there exist top level marks
        if top_level != None:

            top_level = SECTION_TYPES.index(top_level)
            fold_level = top_level + (FoldLevel - 1)

            # make sure FoldLevel do not exceed the scope of secion_types
            if fold_level >= len(SECTION_TYPES):
                fold_level = len(SECTION_TYPES) - 1

            sec_type = SECTION_TYPES[fold_level]

            fold_regions = find_sec_regions(view, sec_type)
            for i in fold_regions:
                view.fold(i[0])
                

# Fold current section
class LatexFoldCurrentCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        extrame_fold = sublime.load_settings("LaTeXTools.sublime-settings").get('extreme_fold')

        view = self.view
        point = view.sel()[0].end()

        for sec in SECTION_TYPES[::-1]: # Searching from the direct parent.
            regions = find_sec_regions(view, sec)
            for i in regions:

                region_span = i[0].cover(i[1])

                # if end mark is a norm end mark
                if extrame_fold != 'ALL':
                    if re.search(r'%\s*.*\(end\)', view.substr(i[2])) != None:
                        region_span = region_span.cover(i[2])

                if region_span.contains(point):

                    # if current foldable segment contains current point
                    # and have not been folded then fold it, or go to parent
                    # segment
                    if view.fold(i[0]) == True:
                        return
                    else:
                        break

# Unfold current section.
class LatexUnfoldCurrentCommand(sublime_plugin.TextCommand):

    def run(self, edit): 

        extrame_fold = sublime.load_settings("LaTeXTools.sublime-settings").get('extreme_fold')

        view = self.view
        point = view.sel()[0].end()

        for sec in SECTION_TYPES[::-1]: # Searching from the direct parent.
            regions = find_sec_regions(view, sec)
            for i in regions:

                region_span = i[0].cover(i[1])

                # print(i[2])

                # if end mark is a norm end mark
                if extrame_fold != 'ALL':
                    if re.search(r'%\s*.*\(end\)', view.substr(i[2])) != None:
                        region_span = region_span.cover(i[2])

                if region_span.contains(point):
                    regions = view.unfold(i[0])
                    if len(regions) > 0:
                        view.sel().clear()
                        view.sel().add(i[0])
                        return
