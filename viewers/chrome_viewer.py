from urllib.parse import quote
import subprocess as sp
import os


from base_viewer import BaseViewer
from latextools_utils import get_setting
from latextools_utils.output_directory import get_output_directory
from latextools_utils.external_command import external_command, check_output
# from delete_temp_files import DeleteTempFilesCommand
## TODO: remove defaultCmd from applescript - just return True or False, then run that default command from Python.
## TODO: GET CHROME PATH
## TODO: GET CURRENT FOLDER PATH (for osascript command)

class ChromeViewer(BaseViewer):


    def _get_applescript_folder(self):
        return os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'chrome'
            )
        )
    def _get_chrome_dir(self,escaped=False):
        viewer_location = check_output([
            'osascript',
            '-e',
            'POSIX path of '
            '(path to app id "com.google.Chrome")'
        ], use_texpath=False)
        viewer_location = viewer_location.replace(" ","\\ ")
        if escaped:
            return "{viewer_location}Contents/MacOS/Google\\ Chrome".format(viewer_location=viewer_location)
        return "{viewer_location}Contents/MacOS/Google Chrome".format(viewer_location=viewer_location)


    def _get_browser_filepath(self,tex_line_no,tex_col_no,tex_filename,pdf_filename,zoom=100):
        try:
            relative_outputdir = os.path.relpath(get_output_directory(tex_filename),os.path.dirname(tex_filename))
            outputdir_command = ['-d',relative_outputdir]
        except Exception as e:
            print("ERROR GETTING 'output_directory'")
            print(e)
            outputdir_command = []
        synctex_loc = '{tex_line_no}:{tex_col_no}:{tex_filename}'.format(tex_line_no=tex_line_no,tex_col_no=tex_col_no,tex_filename=tex_filename)
        cmd = ['/Library/TeX/texbin/synctex', 'view', '-i', synctex_loc, '-o', pdf_filename] + outputdir_command
        try:
            stdout = check_output(cmd)
            with open('/Users/zach/Desktop/latexoutput','w') as f:
                f.write(stdout)
            output_text = stdout.split("\n")
            page_no = next((e.lstrip('Page:') for e in output_text if e.startswith('Page:')), 1)
            # page_no = int(page_no) + 1 #offset, see `synctex view help`
            col_no = next((e.lstrip('x:') for e in output_text if e.startswith('x:')), 1)
            line_no = next((e.lstrip('y:') for e in output_text if e.startswith('y:')), 1)
        except Exception as e:
            print("ERROR IN SYNCTEX")
            print(e)
            page_no = 1
            line_no = 1
            col_no = 0
        return "file://{pdf_filename}#page={page_no}&view=FitH,{line_no}".format(pdf_filename=pdf_filename,page_no=page_no,line_no=line_no)


    def _get_run_command(self,pdf_filename,tex_filename=None,tex_line_no=None,tex_col_no=None,zoom=100):
        if tex_filename is None:
            chrome_dir = self._get_chrome_dir()
            basic_cmd =  [chrome_dir,pdf_filename]
            return basic_cmd
        pdf_filename = tex_filename.rsplit(".",1)[0] + ".pdf"

        finalDestination = self._get_browser_filepath(tex_line_no,tex_col_no,tex_filename,pdf_filename)
        quotedPDFName = quote(pdf_filename)
        scriptName= "{}/OpenFileInChrome_Page_Number.applescript".format(self._get_applescript_folder())
        chrome_dir = self._get_chrome_dir(escaped=True)
        defaultCmd = "{chrome_dir} '{finalDestination}'".format(chrome_dir=chrome_dir,finalDestination=finalDestination)
        # defaultCmd = "{chrome_dir} {quotedPDFName}".format(chrome_dir=chrome_dir,finalDestination=finalDestination)
        cmd = ['osascript', scriptName, finalDestination,quotedPDFName,defaultCmd]
        return cmd

        # osascript '/Users/zach/Library/Application Support/Sublime Text/Packages/LaTeXTools/chrome/OpenFileInChrome_Page_Number.applescript' 'file:///Users/zach/Documents/UCLA_classes/stats203/project/presentation/presentation.pdf#page=33&view=FitH,28.346443' '/Users/zach/Documents/UCLA_classes/stats203/project/presentation/presentation.pdf' '/Applications/Google Chrome.app/Contents/MacOS/Google\ Chrome file:///Users/zach/Documents/UCLA_classes/stats203/project/presentation/presentation.pdf#page=33&view=FitH,28.346443'

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        cmd = self._get_run_command(pdf_file,tex_file,line,col)
        print("FORWARD SYNCING CHROME COMMAND IS:")
        print(cmd)
        external_command(cmd, use_texpath=True)
        # df = DeleteTempFilesCommand()
        # df.run()

    def view_file(self, pdf_file, **kwargs):
        tex_filename = pdf_file.rsplit(".",1)[0] + ".pdf"
        cmd = self._get_run_command(pdf_file,tex_filename=tex_filename,tex_line_no=1,tex_col_no=1)
        print("BASIC VIEWING CHROME")
        external_command(cmd, use_texpath=False)
