# Provided contexts

LaTeXTools provides contexts to improve the creation for your keybindings.

The general structure of a keybinding contains a context fields and LaTeXTools adds context you can use inside LaTeX. The key is prefixed with `latextools.` followed by a key, which is described in this section. It may be followed by additional specifiers, used by the context.
For example in the context key `latextools.setting.setting_name` you have
- the prefix `latextools` is used to have a unique name-space
- the key `setting` is used to specify the context
- the additional specifier `setting_name` my be used to provide additional arguments to the context


```js
    {
        "keys": ["ctrl+l", "ctrl+x"],
        "command": "insert", "args": {"characters": "my_input"},
        "context":
        [
            { "key": "selector", "operand": "text.tex.latex" },
            { "key": "latextools.the_context", "operator": "equal", "operand": "The operand" },
        ],
    },
```


## `setting`

You can use the key `latextools.setting.setting_name` to check for a setting set in the LaTeXTools settings. You can change `setting_name` to specify the name of the setting and the `"operand"` to specify the value.


## `st_version`

This can be used to check the version of Sublime Text in the `"operand"`, e.g. `"<=3114"`. This is mainly internally used to keep backward compatibility.


## `documentclass`

You can use the documentclass context to check the for the documentclass of your current document. You can pass the class as the `"operand"`. However if you want to check for different classes you can also use regular expressions.
E.g. `"operator": "regex_match"` and `"operand": "^(scrartcl|article)$"` to have either the class scrartcl or article.


## `usepackage`

The usepackage context can be used to check for the used packages in the document. Just use the package name as operand, e.g. `"operand": "amsmath"`. If you want to check several packages at once you can just use a regex, e.g. `"operator": "regex_contains"` and `"operand": "\\b(amsmath|mathtools)\\b"` to check for either the package amsmath or mathtools.


## `env_selector`

Have you ever thought: "The scope selectors are nice, but I would like to have the same for arbitrary LaTeX environment"? With the `latextools.env_selector` context you can use the same syntax for environment. As with `selector` you can define the environment (instead of the scopes) in the operand and combine them with operators (increasing precedence):

- `,` "or". The caret must be inside the left *or* the right environment/selector
- `|` same as `,`
- `&` "and" The caret must be inside both the left *and* the right environment/selector
- `-` "without" The caret must be inside the left, but not inside the right environment/selector
- ` ` (whitespace) "nested and" The caret must be inside the left and the right environment with the same order. For technical reasons you must use environment as lhs and rhs and can't use parens at that position

You can add a `*` to an environment to indicate that the star must be present and a `!` to indicate, that it must not be present. In addition you can add an `^` anchor to indicate that an environment should be the closest one.

E.g. You can create a keybinding, which is valid inside a `list` or `mylist` environment, but not if there is an additional surrounding `enumerate` environment close to the caret: `(list, mylist) - enumerate^`

## `command_selector`

This is the same as `env_selector`, but for commands. So you can create a keybinding, which is only valid inside the `\graphicspath` command. The selector syntax is the same as in env_selector. You can also add `*` to ensure it is a star-command or `!` to ensure it is not a star command. In addition you can ensure the command is the neared one with the `^` anchor.
E.g. you can use `ensuremath!^` to ensure you are directly inside an `\ensuremath` command and it does not have a star (as in `\ensuremath*`).
