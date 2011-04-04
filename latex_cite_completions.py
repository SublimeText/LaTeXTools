import sublime, sublime_plugin
import os, os.path
import re

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

# Based on html_completions.py
# see also latex_ref_completions.py
#
# It expands citations; activated by 
# cite<tab>
# citep<tab> and friends
#
# Furthermore, you can "pre-filter" the completions: e.g. use
#
# cite_sec
#
# to select all citation keywords starting with "sec". 
#
# There is only one problem: if you have a keyword "sec:intro", for instance,
# doing "cite_intro:" will find it correctly, but when you insert it, this will be done
# right after the ":", so the "cite_intro:" won't go away. The problem is that ":" is a
# word boundary. Then again, TextMate has similar limitations :-)
#
# There is also another problem: * is also a word boundary :-( So, use e.g. citeX if
# what you want is \cite*{...}; the plugin handles the substitution

class LatexCiteCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        # Only trigger within LaTeX
        if not view.match_selector(locations[0],
                "text.tex.latex"):
            return []

        # Get the contents of line 0, from the beginning of the line to
        # the current point
        l = locations[0]
        line = view.substr(sublime.Region(view.line(l).a, l))
            

        # Reverse, to simulate having the regex
        # match backwards (cool trick jps btw!)
        line = line[::-1]
        #print line

        # Check the first location looks like a ref, but backward
        # NOTE: use lazy match for the fancy cite part!!!
        rex = re.compile("([^_]*_)?(.*?)etic")
        expr = match(rex, line)
        print expr
        if not expr:
            return []

        # Return the completions
        prefix, fancy_cite = rex.match(expr).groups()
        if prefix:
            prefix = prefix[::-1] # reverse
            prefix = prefix[1:] # chop off #
        if fancy_cite:
            fancy_cite = fancy_cite[::-1]
            # fancy_cite = fancy_cite[1:] # no need to chop off?
            if fancy_cite[-1] == "X":
                fancy_cite = fancy_cite[:-1] + "*"
        print prefix, fancy_cite

        # Reverse back expr
        expr = expr[::-1]

        completions = ["TEST"]

        #### GET COMPLETIONS HERE #####

        # For now we only get completions from ONE bibtex file
        # note improved regex: matching fails with , or }, so no need to be
        # explicit and add it after []+
        bibcmd = view.substr(view.find(r'\\bibliography\{([^,\}]+)',0))
        print bibcmd
        bib_command = view.substr(view.find(r'^[^%]*\\bibliography\{[^\}]+',0))
        bib_files = re.search(r'\{([^\}]+)', bib_command).group(1).split(',')
        if not bib_files:
            print "Error!"
            return []
        bib_files = ([x.strip() for x in bib_files])
        
        print "Files:"
        print bib_files
        # bibp = re.compile(r'\{(.+)') # we dropped last , or } so don't look for it
        # bibmatch = bibp.search(bibcmd)
        # if not bibmatch:
        #     print "Cannot parse bibliography command: " + bibcmd
        #     return
        # bibfname = bibmatch.group(1)
        # print bibfname
        
        completions = []
        kp = re.compile(r'@[^\{]+\{(.+),')
        # new and improved regex
        # we must have "title" then "=", possibly with spaces
        # then either {, maybe repeated twice, or "
        # then spaces and finally the title
        # We capture till the end of the line as maybe entry is broken over several lines
        # and in the end we MAY but need not have }'s and "s
        tp = re.compile(r'\btitle\s*=\s*(?:\{+|")\s*([^,\}]+)[\},]*', re.IGNORECASE)  # note no comma!
        kp2 = re.compile(r'([^\t]+)\t*')

        for bibfname in bib_files:
            if bibfname[-4:] != ".bib":
                bibfname = bibfname + ".bib"
            texfiledir = os.path.dirname(view.file_name())
            # fix from Tobias Schmidt to allow for absolute paths
            bibfname = os.path.normpath(os.path.join(texfiledir, bibfname))
            print bibfname 
            try:
                bibf = open(bibfname)
            except IOError:
                sublime.error_message("Cannot open bibliography file %s !" % (bibfname,))
                return []
            else:
                bib = bibf.readlines()
                bibf.close()
            print "%s has %s lines" % (bibfname, len(bib))
            # note Unicode trickery
            keywords = [kp.search(line).group(1).decode('ascii','ignore') for line in bib if line[0] == '@']
            titles = [tp.search(line).group(1).decode('ascii','ignore') for line in bib if tp.search(line)]
            if len(keywords) != len(titles):
                print "Bibliography " + bibfname + " is broken!"
            completions += zip(keywords, titles)


        #### END COMPLETIONS HERE ####

        print completions
        
        if prefix:
            completions = [comp for comp in completions if prefix.lower() in "%s %s" % (comp[0].lower(),comp[1].lower())]

        # popup is 40chars wide...
        t_end = 40 - len(expr)
        r = [(expr + " "+title[:t_end], "\\cite" + fancy_cite + "{" + keyword + "}") 
                        for (keyword, title) in completions]
        print r
        return r
