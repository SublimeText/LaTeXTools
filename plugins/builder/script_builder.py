import os
import re
import sublime
import subprocess

from shlex import quote
from string import Template

from LaTeXTools.latextools.utils.external_command import external_command
from LaTeXTools.latextools.utils.external_command import get_texpath
from LaTeXTools.latextools.utils.external_command import update_env

from pdf_builder import PdfBuilder


class ScriptBuilder(PdfBuilder):
    """
    ScriptBuilder class

    Launch a user-specified script
    """

    FILE_VARIABLES = r"file|file_path|file_name|file_ext|file_base_name"

    CONTAINS_VARIABLE = re.compile(
        r"\$\{?(?:" + FILE_VARIABLES + r"|output_directory|aux_directory|jobname)\}?\b",
        re.IGNORECASE | re.UNICODE,
    )

    def __init__(self, *args):
        # Sets the file name parts, plus internal stuff
        super(ScriptBuilder, self).__init__(*args)
        # Now do our own initialization: set our name
        self.name = "Script Builder"
        # Display output?
        self.display_log = self.builder_settings.get("display_log", False)
        plat = sublime.platform()
        self.cmd = self.builder_settings.get(plat, {}).get("script_commands", None)
        self.env = self.builder_settings.get(plat, {}).get("env", None)
        # Loaded here so it is calculated on the main thread
        self.texpath = get_texpath() or os.environ["PATH"]

    # Very simple here: we yield a single command
    # Also add environment variables
    def commands(self):
        # Print greeting
        self.display("\n\nScriptBuilder: ")

        # create an environment to be used for all subprocesses
        # adds any settings from the `env` dict to the current
        # environment
        env = dict(os.environ)
        env["PATH"] = self.texpath
        if self.env is not None and isinstance(self.env, dict):
            update_env(env, self.env)

        if self.cmd is None:
            sublime.error_message(
                "You MUST set a command in your LaTeXTools.sublime-settings "
                + "file before launching the script builder."
            )
            # I'm not sure this is the best way to handle things...
            raise StopIteration()

        if isinstance(self.cmd, str):
            self.cmd = [self.cmd]

        for cmd in self.cmd:
            replaced_var = False
            if isinstance(cmd, str):
                cmd, replaced_var = self.substitute(cmd)
            else:
                for i, component in enumerate(cmd):
                    cmd[i], replaced = self.substitute(component)
                    replaced_var = replaced_var or replaced

            if not replaced_var:
                if isinstance(cmd, str):
                    cmd += " " + self.base_name
                else:
                    cmd.append(self.base_name)

            if not isinstance(cmd, str):
                self.display("Invoking '{0}'... ".format(" ".join([quote(s) for s in cmd])))
            else:
                self.display("Invoking '{0}'... ".format(cmd))

            yield (
                # run with use_texpath=False as we have already configured
                # the environment above, including the texpath
                external_command(
                    cmd,
                    env=env,
                    cwd=self.tex_dir,
                    use_texpath=False,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                ),
                "",
            )

            self.display("done.\n")

            # This is for debugging purposes
            if self.display_log and self.out is not None:
                self.display("\nCommand results:\n")
                self.display(self.out)
                self.display("\n\n")

    def substitute(self, command):
        replaced_var = False
        if self.CONTAINS_VARIABLE.search(command):
            replaced_var = True

            template = Template(command)
            command = template.safe_substitute(
                file=self.tex_root,
                file_path=self.tex_dir,
                file_name=self.tex_name,
                file_ext=self.tex_ext,
                file_base_name=self.base_name,
                output_directory=self.output_directory_full or self.tex_dir,
                aux_directory=self.aux_directory_full or self.tex_dir,
                jobname=self.job_name,
            )

        return (command, replaced_var)
