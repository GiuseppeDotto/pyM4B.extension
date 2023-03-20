
import webbrowser
from pyrevit import forms

user_input = forms.alert("Thanks for using our scripts!", warn_icon=False, options=['Go to website', 'Share ideas.', 'Ciao!'])
if user_input == 'Go to website':
	webbrowser.open('https://www.macro4bim.com')
elif user_input == 'Share ideas.':
	webbrowser.open("https://www.macro4bim.com/#custom-solutions")