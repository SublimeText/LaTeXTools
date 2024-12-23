import sublime, sublime_plugin

from .deprecated_command import deprecate

__all__ = ["LatextoolsTexMacroCommand"]

macros = {
'a' : '\\alpha',
'b' : '\\beta',
'c' : '\\chi',
'd' : '\\delta',
'e' : '\\epsilon',
'f' : '\\phi',
'g' : '\\gamma',
'h' : '\\eta',
'i' : '\\iota',
'j' : '\\phi',
'k' : '\\kappa',
'l' : '\\lambda',
'm' : '\\mu',
'n' : '\\nu',
'o' : '\\omicron',
'p' : '\\pi',
'q' : '\\theta',
'r' : '\\rho',
's' : '\\sigma',
't' : '\\tau',
'u' : '\\upsilon',
'v' : '\\psi',
'w' : '\\omega',
'x' : '\\xi',
'y' : '\\vartheta',
'z' : '\\zeta',
'A' : '\\forall',
'B' : 'FREE',
'C' : '\\Chi',
'D' : '\\Delta',
'E' : '\\exists',
'F' : '\\Phi',
'G' : '\\Gamma',
'H' : 'FREE',
'I' : '\\bigcap',
'J' : '\\Phi',
'K' : 'FREE',
'L' : '\\Lambda',
'M' : '\\int',
'N' : '\\sum',
'O' : '\\emptyset',
'P' : '\\Pi',
'Q' : '\\Theta',
'R' : 'FREE',
'S' : '\\Sigma',
'T' : '\\times',
'U' : '\\bigcup',
'V' : '\\Psi',
'W' : '\\Omega',
'X' : '\\Xi',
'Y' : '\\Upsilon',
'Z' : '\\sum',
'ge' : '\\geq',
'le' : '\\leq',
'la' : '\\leftarrow',
'ra' : '\\rightarrow',
'La' : '\\Leftarrow',
'Ra' : '\\Rightarrow',
'lra' : '\\leftrightarrow',
'up' : '\\uparrow',
'dn' : '\\downarrow',
'iff' : '\\Leftrightarrow',
'raa' : '\\rangle',
'laa' : '\\langle',
'lp' : '\\left(',
'rp' : '\\right)',
'lbk' : '\\left[',
'rbk' : '\\right]',
'lbr' : '\\left\{',
'rbr' : '\\right\}'
}

class LatextoolsTexMacroCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        currsel = self.view.sel()[0]
        currword = self.view.word(currsel)
        k = self.view.substr(currword)
        if macros.has_key(k):
            self.view.replace(edit, currword, macros[k])
        else:
            sublime.error_message("%s is not a valid TeX symbol shortcut" % (k,))


deprecate(globals(), 'tex_macroCommand', LatextoolsTexMacroCommand)
