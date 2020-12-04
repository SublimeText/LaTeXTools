import sublime
import sublime_plugin

class SetFileAsProjectTexrootCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		variables = self.view.window().extract_variables()
		current_file_name = sublime.expand_variables("$file_name",variables)
		current_project_name = sublime.expand_variables("$project_name",variables)

		project_data = self.view.window().project_data()

		#print("current file's name: ", current_file_name)
		#print("current project's name: ", current_project_name)
		#print("project data previously:", project_data)
		
		project_data.update({'settings': {'TEXroot': current_file_name} })
		self.view.window().set_project_data(project_data)

		#print("project data currently:", self.view.window().project_data())

# Test in console:
# view.run_command("set_as_project_texroot")