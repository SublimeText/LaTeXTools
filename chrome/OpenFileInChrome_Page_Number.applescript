on run argv
	set finalDestination to item 1 of argv
	set quotedPDFName to item 2 of argv
	set defaultCmd to item 3 of argv
	log quotedPDFName
	tell application "Google Chrome"
		set found to false
		set windowList to every window
		repeat with aWindow in windowList
			if found then
				exit repeat
			end if
			set tabList to every tab of aWindow
			set tabIndex to 0
			repeat with atab in tabList
				set tabIndex to tabIndex + 1
				if (URL of atab contains quotedPDFName) then
					set found to true
					set aWindow's active tab index to tabIndex
					set index of aWindow to 1
					set URL of atab to finalDestination
					delay 0.05 -- makes it not fail
					delay 0.05 -- makes it not fail
					tell atab to reload
					exit repeat
				end if
			end repeat
		end repeat
	end tell
	if not found then
		do shell script defaultCmd
	end if
end run
