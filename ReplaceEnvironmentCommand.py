import sublime, sublime_plugin  
import re

# Based on which environment of the form
# \begin{this}
# . . .
# \end{this}
# you are prompted to change "this" to any string desired.

def levels_into_latex(beginning_pts, ending_pts, pt):
	# This function returns how many levels deep you are in nested 
	# \begin{X...} ....\end{...Y}
	# It counts the cursor positions labeled X and Y as in the environment 
	# and out of the environment respectively.
	if len(beginning_pts) == len(ending_pts):
		ups = sum(a <= pt for a in beginning_pts)
		downs = sum(z <= pt for z in ending_pts)
		return ups - downs
	else:
		sublime.error_message("Error parsing buffer: Not every \\begin{...} has a matching \\end{...}.")


class Level_Distance_Region:
	# Dummy class to keep things organized in "ChangeEnvironmentCommand" below.
	pass

class ReplaceEnvironmentCommand(sublime_plugin.WindowCommand):  
	# This prompts the user to enter what she wants to change the environment to
    def run(self):
    	self.window.show_input_panel("New Environment:","",self.on_done, None, None)
    	pass

    def on_done(self,text):
    # If the user doesn't enter anything, nothing is changed
    	if text and self.window.active_view():
    	   	self.window.active_view().run_command("change_environment",{"environmentname": text} )
    	else:
    		pass

class ChangeEnvironmentCommand(sublime_plugin.TextCommand):
	# This is where the bulk of the work is done
	# Accepting "environmentname" as a variable, this command searches
	# throughout the document for all instances of \begin{...} and \end{...}
	# storing, and using that to compute how deeply nested the user is in
	# "\begin{...}"s and "\end{...}"s. From there it finds which instances of \begin{...}
	# or "\end{...}" are at the same nesting level and closest to the cursor.
	# Those are the ones that are replaced.
	def run(self, edit, environmentname):

		for a_selection in self.view.sel():
			# Find all instances of \begin{...}
			beginnings = self.view.find_all(r"(?<=\\begin\{)[a-zA-Z0-9]+(?=\})")
			beginning_pts = [a.begin() for a in beginnings]
			# Find all instances of \end{...}
			endings = self.view.find_all(r"(?<=\\end\{)[a-zA-Z0-9]+(?=\})")
			ending_pts = [z.end() for z in endings]

			# Where the start of the cursor is determines which environments will be replaced
			pt = a_selection.begin()
			# Compute the cursor's nesting level
			level = levels_into_latex(beginning_pts, ending_pts, a_selection.begin())
			print "Levels deep: ", level


			beginning_items = []
			ending_items = []

			for a in beginnings:
				# Cycling through all \begin{...} items, we find the ones at the same nesting level
				# as the cursor (and above the cursor), and store those as potential candidates for
				# replacement
				n = levels_into_latex(beginning_pts, ending_pts, a.begin())
				if n == level and pt - a.begin() > 0:
					q = Level_Distance_Region()
					#q.level = n
					q.distance = pt - a.begin()
					q.region = a
					beginning_items.append(q)

			for z in endings:
				# Cycling through all \end{...} items, we find the ones at the same nesting level
				# as the cursor - 1 (and below the cursor), and store those as potential candidates for
				# replacement
				n = levels_into_latex(beginning_pts, ending_pts, z.end())
				if n + 1 == level and z.end() - pt > 0:
					q = Level_Distance_Region()
					#q.level = n
					q.distance = z.end() - pt
					q.region = z
					ending_items.append(q)

			# We minimize the above stored regions over the distance from the cursor, the closest
			# then gets replaced.
			beginning = min(beginning_items, key = lambda q:q.distance)
			ending = min(ending_items, key = lambda q:q.distance)

			self.view.replace(edit, ending.region, environmentname)
			self.view.replace(edit, beginning.region, environmentname)
			### Offset (code listed below) not needed since we do the replacements back to front
			# offset = beginning.region.end() - beginning.region.begin() + len(environmentname)
			# new_ending_region = sublime.Region(ending.region.begin() + offset, ending.region.end() + offset)
			# self.view.replace(edit, new_ending_region, environmentname)
			###

