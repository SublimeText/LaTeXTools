"""latex_chars.py

Character translation utilities for LaTeX-formatted text.

Usage:
 - codecs.encode(string,'latex')
 - codecs.decode('latex')
are both available just by letting "import latex_chars" find this file.
 - unicode(string,'latex+latin1')
 - ustring.decode('latex+latin1')
where latin1 can be replaced by any other known encoding, also
become available by calling latex.register().

We also make public a dictionary latex_equivalents,
mapping ord(unicode char) to LaTeX code.

Modified from https://code.activestate.com/recipes/252124-latex-codec/

D. Eppstein, October 2003.
"""
import codecs
import re


def register():
    """Enable encodings of the form 'latex+x' where x describes another encoding.
    Unicode characters are translated to or from x when possible, otherwise
    expanded to latex.
    """
    codecs.register(_registry)


def getregentry():
    """Encodings module API."""
    return _registry("latex")


def _registry(encoding):
    if encoding == "latex":
        encoding = None
    elif encoding.startswith("latex+"):
        encoding = encoding[6:]
    else:
        return None

    class Codec(codecs.Codec):
        def encode(self, input, errors="strict"):
            """Convert unicode string to latex."""
            output = []
            for c in input:
                if encoding:
                    try:
                        output.append(c.encode(encoding))
                        continue
                    except Exception:
                        pass
                if ord(c) in latex_equivalents:
                    output.append(latex_equivalents[ord(c)])
                else:
                    output += ["{\\char", str(ord(c)), "}"]
            return "".join(output), len(input)

        def decode(self, input, errors="strict"):
            """Convert latex source string to unicode."""
            if encoding:
                input = codecs.decode(input, encoding, errors)

            x = _unlatex(input)
            return "".join(x), len(input)

    class StreamWriter(Codec, codecs.StreamWriter):
        pass

    class StreamReader(Codec, codecs.StreamReader):
        pass

    return (Codec().encode, Codec().decode, StreamReader, StreamWriter)


def _tokenize(tex):
    """Convert latex source into sequence of single-token substrings."""
    start = 0
    try:
        pos = next(_stoppers.finditer(tex)).span()[0]
    except StopIteration:
        yield tex
        return

    while 1:
        if pos > start:
            yield tex[start:pos]
            if tex[start] == "\\" and not (tex[pos - 1].isdigit() and tex[start + 1].isalpha()):
                while pos < len(tex) and tex[pos].isspace():  # skip blanks after csname
                    pos += 1

        while pos < len(tex) and tex[pos] in _ignore:
            pos += 1  # flush control characters
        if pos >= len(tex):
            return
        start = pos
        if tex[pos : pos + 2] in {"$$": None, "/~": None}:  # protect ~ in urls
            pos += 2
        elif tex[pos].isdigit():
            while pos < len(tex) and tex[pos].isdigit():
                pos += 1
        elif tex[pos] == "-":
            while pos < len(tex) and tex[pos] == "-":
                pos += 1
        elif tex[pos] != "\\" or pos == len(tex) - 1:
            pos += 1
        elif not tex[pos + 1].isalpha():
            pos += 2
        else:
            pos += 1
            while pos < len(tex) and tex[pos].isalpha():
                pos += 1
            if tex[start:pos] == "\\char" or tex[start:pos] == "\\accent":
                while pos < len(tex) and tex[pos].isdigit():
                    pos += 1


class _unlatex:
    """Convert tokenized tex into sequence of unicode strings.  Helper for decode()."""

    def __init__(self, tex):
        """Create a new token converter from a string."""
        self.tex = tuple(_tokenize(tex))  # turn tokens into indexable list
        self.pos = 0  # index of first unprocessed token
        self.lastoutput = "x"  # lastoutput must always be nonempty string

    def __iter__(self):
        """Turn self into an iterator.  It already is one, nothing to do."""
        return self

    def __getitem__(self, n):
        """Return token at offset n from current pos."""
        p = self.pos + n
        t = self.tex
        return t[p] if p < len(t) else None

    def next(self):
        return self.__next__()

    def __next__(self):
        """Find and return another piece of converted output."""
        if self.pos >= len(self.tex):
            raise StopIteration
        nextoutput = self.chunk()
        if self.lastoutput[0] == "\\" and self.lastoutput[-1].isalpha() and nextoutput[0].isalpha():
            nextoutput = " " + nextoutput  # add extra space to terminate csname
        self.lastoutput = nextoutput
        return nextoutput

    def chunk(self):
        """Grab another set of input tokens and convert them to an output string."""
        for delta, c in self.candidates(0):
            if c in _l2u:
                self.pos += delta
                return chr(_l2u[c])
            elif len(c) == 2 and c[1] == "i" and (c[0], "\\i") in _l2u:
                self.pos += delta  # correct failure to undot i
                return chr(_l2u[(c[0], "\\i")])
            elif len(c) == 1 and c[0].startswith("\\char") and c[0][5:].isdigit():
                self.pos += delta
                return chr(int(c[0][5:]))

        # nothing matches, just pass through token as-is
        self.pos += 1
        return self[-1]

    def candidates(self, offset):
        """Generate pairs delta,c where c is a token or tuple of tokens from tex
        (after deleting extraneous brackets starting at pos) and delta
        is the length of the tokens prior to bracket deletion.
        """
        t = self[offset]
        if t in _blacklist:
            return
        elif t == "{":
            for delta, c in self.candidates(offset + 1):
                if self[offset + delta + 1] == "}":
                    yield delta + 2, c
        elif t == "\\mbox":
            for delta, c in self.candidates(offset + 1):
                yield delta + 1, c
        elif t == "$" and self[offset + 2] == "$":
            yield 3, (t, self[offset + 1], t)
        else:
            q = self[offset + 1]
            if q == "{" and self[offset + 3] == "}":
                yield 4, (t, self[offset + 2])
            elif q:
                yield 2, (t, q)
            yield 1, t


latex_equivalents = {
    0x0009: " ",
    0x000A: "\n",
    0x0023: "{\\#}",
    0x0026: "{\\&}",
    0x00A0: "{~}",
    0x00A1: "{!`}",
    0x00A2: "{\\not{c}}",
    0x00A3: "{\\pounds}",
    0x00A7: "{\\S}",
    0x00A8: '{\\"{}}',
    0x00A9: "{\\copyright}",
    0x00AF: "{\\={}}",
    0x00AC: "{\\neg}",
    0x00AD: "{\\-}",
    0x00B0: "{\\mbox{$^\\circ$}}",
    0x00B1: "{\\mbox{$\\pm$}}",
    0x00B2: "{\\mbox{$^2$}}",
    0x00B3: "{\\mbox{$^3$}}",
    0x00B4: "{\\'{}}",
    0x00B5: "{\\mbox{$\\mu$}}",
    0x00B6: "{\\P}",
    0x00B7: "{\\mbox{$\\cdot$}}",
    0x00B8: "{\\c{}}",
    0x00B9: "{\\mbox{$^1$}}",
    0x00BF: "{?`}",
    0x00C0: "{\\`A}",
    0x00C1: "{\\'A}",
    0x00C2: "{\\^A}",
    0x00C3: "{\\~A}",
    0x00C4: '{\\"A}',
    0x00C5: "{\\AA}",
    0x00C6: "{\\AE}",
    0x00C7: "{\\c{C}}",
    0x00C8: "{\\`E}",
    0x00C9: "{\\'E}",
    0x00CA: "{\\^E}",
    0x00CB: '{\\"E}',
    0x00CC: "{\\`I}",
    0x00CD: "{\\'I}",
    0x00CE: "{\\^I}",
    0x00CF: '{\\"I}',
    0x00D1: "{\\~N}",
    0x00D2: "{\\`O}",
    0x00D3: "{\\'O}",
    0x00D4: "{\\^O}",
    0x00D5: "{\\~O}",
    0x00D6: '{\\"O}',
    0x00D7: "{\\mbox{$\\times$}}",
    0x00D8: "{\\O}",
    0x00D9: "{\\`U}",
    0x00DA: "{\\'U}",
    0x00DB: "{\\^U}",
    0x00DC: '{\\"U}',
    0x00DD: "{\\'Y}",
    0x00DF: "{\\ss}",
    0x00E0: "{\\`a}",
    0x00E1: "{\\'a}",
    0x00E2: "{\\^a}",
    0x00E3: "{\\~a}",
    0x00E4: '{\\"a}',
    0x00E5: "{\\aa}",
    0x00E6: "{\\ae}",
    0x00E7: "{\\c{c}}",
    0x00E8: "{\\`e}",
    0x00E9: "{\\'e}",
    0x00EA: "{\\^e}",
    0x00EB: '{\\"e}',
    0x00EC: "{\\`\\i}",
    0x00ED: "{\\'\\i}",
    0x00EE: "{\\^\\i}",
    0x00EF: '{\\"\\i}',
    0x00F1: "{\\~n}",
    0x00F2: "{\\`o}",
    0x00F3: "{\\'o}",
    0x00F4: "{\\^o}",
    0x00F5: "{\\~o}",
    0x00F6: '{\\"o}',
    0x00F7: "{\\mbox{$\\div$}}",
    0x00F8: "{\\o}",
    0x00F9: "{\\`u}",
    0x00FA: "{\\'u}",
    0x00FB: "{\\^u}",
    0x00FC: '{\\"u}',
    0x00FD: "{\\'y}",
    0x00FF: '{\\"y}',
    0x0100: "{\\=A}",
    0x0101: "{\\=a}",
    0x0102: "{\\u{A}}",
    0x0103: "{\\u{a}}",
    0x0104: "{\\c{A}}",
    0x0105: "{\\c{a}}",
    0x0106: "{\\'C}",
    0x0107: "{\\'c}",
    0x0108: "{\\^C}",
    0x0109: "{\\^c}",
    0x010A: "{\\.C}",
    0x010B: "{\\.c}",
    0x010C: "{\\v{C}}",
    0x010D: "{\\v{c}}",
    0x010E: "{\\v{D}}",
    0x010F: "{\\v{d}}",
    0x0112: "{\\=E}",
    0x0113: "{\\=e}",
    0x0114: "{\\u{E}}",
    0x0115: "{\\u{e}}",
    0x0116: "{\\.E}",
    0x0117: "{\\.e}",
    0x0118: "{\\c{E}}",
    0x0119: "{\\c{e}}",
    0x011A: "{\\v{E}}",
    0x011B: "{\\v{e}}",
    0x011C: "{\\^G}",
    0x011D: "{\\^g}",
    0x011E: "{\\u{G}}",
    0x011F: "{\\u{g}}",
    0x0120: "{\\.G}",
    0x0121: "{\\.g}",
    0x0122: "{\\c{G}}",
    0x0123: "{\\c{g}}",
    0x0124: "{\\^H}",
    0x0125: "{\\^h}",
    0x0128: "{\\~I}",
    0x0129: "{\\~\\i}",
    0x012A: "{\\=I}",
    0x012B: "{\\=\\i}",
    0x012C: "{\\u{I}}",
    0x012D: "{\\u\\i}",
    0x012E: "{\\c{I}}",
    0x012F: "{\\c{i}}",
    0x0130: "{\\.I}",
    0x0131: "{\\i}",
    0x0132: "{IJ}",
    0x0133: "{ij}",
    0x0134: "{\\^J}",
    0x0135: "{\\^\\j}",
    0x0136: "{\\c{K}}",
    0x0137: "{\\c{k}}",
    0x0139: "{\\'L}",
    0x013A: "{\\'l}",
    0x013B: "{\\c{L}}",
    0x013C: "{\\c{l}}",
    0x013D: "{\\v{L}}",
    0x013E: "{\\v{l}}",
    0x0141: "{\\L}",
    0x0142: "{\\l}",
    0x0143: "{\\'N}",
    0x0144: "{\\'n}",
    0x0145: "{\\c{N}}",
    0x0146: "{\\c{n}}",
    0x0147: "{\\v{N}}",
    0x0148: "{\\v{n}}",
    0x014C: "{\\=O}",
    0x014D: "{\\=o}",
    0x014E: "{\\u{O}}",
    0x014F: "{\\u{o}}",
    0x0150: "{\\H{O}}",
    0x0151: "{\\H{o}}",
    0x0152: "{\\OE}",
    0x0153: "{\\oe}",
    0x0154: "{\\'R}",
    0x0155: "{\\'r}",
    0x0156: "{\\c{R}}",
    0x0157: "{\\c{r}}",
    0x0158: "{\\v{R}}",
    0x0159: "{\\v{r}}",
    0x015A: "{\\'S}",
    0x015B: "{\\'s}",
    0x015C: "{\\^S}",
    0x015D: "{\\^s}",
    0x015E: "{\\c{S}}",
    0x015F: "{\\c{s}}",
    0x0160: "{\\v{S}}",
    0x0161: "{\\v{s}}",
    0x0162: "{\\c{T}}",
    0x0163: "{\\c{t}}",
    0x0164: "{\\v{T}}",
    0x0165: "{\\v{t}}",
    0x0168: "{\\~U}",
    0x0169: "{\\~u}",
    0x016A: "{\\=U}",
    0x016B: "{\\=u}",
    0x016C: "{\\u{U}}",
    0x016D: "{\\u{u}}",
    0x016E: "{\\r{U}}",
    0x016F: "{\\r{u}}",
    0x0170: "{\\H{U}}",
    0x0171: "{\\H{u}}",
    0x0172: "{\\c{U}}",
    0x0173: "{\\c{u}}",
    0x0174: "{\\^W}",
    0x0175: "{\\^w}",
    0x0176: "{\\^Y}",
    0x0177: "{\\^y}",
    0x0178: '{\\"Y}',
    0x0179: "{\\'Z}",
    0x017A: "{\\'Z}",
    0x017B: "{\\.Z}",
    0x017C: "{\\.Z}",
    0x017D: "{\\v{Z}}",
    0x017E: "{\\v{z}}",
    0x01C4: "{D\\v{Z}}",
    0x01C5: "{D\\v{z}}",
    0x01C6: "{d\\v{z}}",
    0x01C7: "{LJ}",
    0x01C8: "{Lj}",
    0x01C9: "{lj}",
    0x01CA: "{NJ}",
    0x01CB: "{Nj}",
    0x01CC: "{nj}",
    0x01CD: "{\\v{A}}",
    0x01CE: "{\\v{a}}",
    0x01CF: "{\\v{I}}",
    0x01D0: "{\\v\\i}",
    0x01D1: "{\\v{O}}",
    0x01D2: "{\\v{o}}",
    0x01D3: "{\\v{U}}",
    0x01D4: "{\\v{u}}",
    0x01E6: "{\\v{G}}",
    0x01E7: "{\\v{g}}",
    0x01E8: "{\\v{K}}",
    0x01E9: "{\\v{k}}",
    0x01EA: "{\\c{O}}",
    0x01EB: "{\\c{o}}",
    0x01F0: "{\\v\\j}",
    0x01F1: "{DZ}",
    0x01F2: "{Dz}",
    0x01F3: "{dz}",
    0x01F4: "{\\'G}",
    0x01F5: "{\\'g}",
    0x01FC: "{\\'\\AE}",
    0x01FD: "{\\'\\ae}",
    0x01FE: "{\\'\\O}",
    0x01FF: "{\\'\\o}",
    0x02C6: "{\\^{}}",
    0x02DC: "{\\~{}}",
    0x02D8: "{\\u{}}",
    0x02D9: "{\\.{}}",
    0x02DA: "{\\r{}}",
    0x02DD: "{\\H{}}",
    0x02DB: "{\\c{}}",
    0x02C7: "{\\v{}}",
    0x03C0: "{\\mbox{$\\pi$}}",
    # consider adding more Greek here
    0xFB01: "{fi}",
    0xFB02: "{fl}",
    0x2013: "{--}",
    0x2014: "{---}",
    0x2018: "{`}",
    0x2019: "{'}",
    0x201C: "{``}",
    0x201D: "{''}",
    0x2020: "{\\dag}",
    0x2021: "{\\ddag}",
    0x2122: "{\\mbox{$^\\mbox{TM}$}}",
    0x2022: "{\\mbox{$\\bullet$}}",
    0x2026: "{\\ldots}",
    0x2202: "{\\mbox{$\\partial$}}",
    0x220F: "{\\mbox{$\\prod$}}",
    0x2211: "{\\mbox{$\\sum$}}",
    0x221A: "{\\mbox{$\\surd$}}",
    0x221E: "{\\mbox{$\\infty$}}",
    0x222B: "{\\mbox{$\\int$}}",
    0x2248: "{\\mbox{$\\approx$}}",
    0x2260: "{\\mbox{$\\neq$}}",
    0x2264: "{\\mbox{$\\leq$}}",
    0x2265: "{\\mbox{$\\geq$}}",
}
for _i in range(0x0020):
    if _i not in latex_equivalents:
        latex_equivalents[_i] = ""
for _i in range(0x0020, 0x007F):
    if _i not in latex_equivalents:
        latex_equivalents[_i] = chr(_i)

# Characters that should be ignored and not output in tokenization
_ignore = set([chr(i) for i in list(range(32)) + [127]]) - set("\t\n\r")

# Regexp of chars not in blacklist, for quick start of tokenize
_stoppers = re.compile("[\x00-\x1f!$\\-?\\{~\\\\`']")

_blacklist = set(" \n\r")
_blacklist.add(None)  # shortcut candidate generation at end of data

# Construction of inverse translation table
_l2u = {"\\ ": ord(" ")}  # unexpanding space makes no sense in non-TeX contexts

for _tex in latex_equivalents:
    if _tex <= 0x0020 or (_tex <= 0x007F and len(latex_equivalents[_tex]) <= 1):
        continue  # boring entry
    _toks = tuple(_tokenize(latex_equivalents[_tex]))
    if _toks[0] == "{" and _toks[-1] == "}":
        _toks = _toks[1:-1]
    if _toks[0].isalpha():
        continue  # don't turn ligatures into single chars
    if len(_toks) == 1 and (_toks[0] == "'" or _toks[0] == "`"):
        continue  # don't turn ascii quotes into curly quotes
    if _toks[0] == "\\mbox" and _toks[1] == "{" and _toks[-1] == "}":
        _toks = _toks[2:-1]
    if len(_toks) == 4 and _toks[1] == "{" and _toks[3] == "}":
        _toks = (_toks[0], _toks[2])
    if len(_toks) == 1:
        _toks = _toks[0]
    _l2u[_toks] = _tex

# Shortcut candidate generation for certain useless candidates:
# a character is in _blacklist if it can not be at the start
# of any translation in _l2u.  We use this to quickly skip through
# such characters before getting to more difficult-translate parts.
# _blacklist is defined several lines up from here because it must
# be defined in order to call _tokenize, however it is safe to
# delay filling it out until now.

for i in range(0x0020, 0x007F):
    _blacklist.add(chr(i))
_blacklist.remove("{")
_blacklist.remove("$")
for candidate in _l2u:
    if isinstance(candidate, tuple):
        if not candidate or not candidate[0]:
            continue
        firstchar = candidate[0][0]
    else:
        firstchar = candidate[0]
    _blacklist.discard(firstchar)
