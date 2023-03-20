
import webbrowser
from pyrevit import forms

if forms.alert("Thanks for using our scripts!", warn_icon=False, options=['go to website', 'bye!']) == 'go to website':
	webbrowser.open('https://www.macro4bim.com')