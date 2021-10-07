#!/usr/bin/env python
from getpass import getpass
from http.cookiejar import CookieJar
from sys import argv
from time import localtime, sleep
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, urlopen

def die(s): print(s); exit()

def fetch_user_time():
	try:
		return urlopen(
			"https://secure.etecsa.net:8443/EtecsaQueryServlet?op=getLeftTime&username={}&ATTRIBUTE_UUID={}".format(
				usr, ATTRIBUTE_UUID)).read().decode()
	except: return "couldn't fetch user time"

def format_time(t):
	t = str(t)
	return {1: "0", 2: ""}[len(t)]+t
def get_formatted_time(t):
	return "{}:{}:{}".format(
		format_time(t[3]),
		format_time(t[4]),
		format_time(t[5]))

if __name__ == "__main__":
	if len(argv) == 1:
		die("nauta: missing operand\nPlease try 'nauta -h' for more information.")
	if argv[1] in ["-h", "--help"]:
		die("Usage: python3 nauta.py [USERNAME] (PASSWORD)\n"
		+ "Simple routine helping use of cuban Nauta Wi-Fi service.\n\n"
		+ "With no PASSWORD, prompts for it with echo turned off.\n\n"
		+ "  -h, --help       Display this help and exit.\n"
		+ "  -V, --version    Output version information and exit.\n\n"
		+ "Examples of usage:\n"
		+ "  python3 nauta.py axolotl7@nauta.com.cu Agr3atPWD\n"
		+ "  python3 nauta.py axolotl7 Agr3atPWD\n"
		+ "  python3 nauta.py axolotl7")
	elif argv[1] in ["-V", "--version"]:
		die("Nauta v1.2, made in Cuba with Linux-GNU.\n\n"
		+ "Copyright © 2021- Yoel N. Fabelo.\n"
		+ "License GPLv3+: GNU GPL version 3 or later\n"
		+ "<https://gnu.org/licenses/gpl.html>.\n"
		+ "This is free software: you are free to change and redistribute it.\n"
		+ "There is NO WARRANTY, to the extent permitted by law.\n\n"
		+ "Written by Yoel N. Fabelo <human.x7e6@gmail.com>.")

	usr = argv[1].replace("@nauta.com.cu", "")+"@nauta.com.cu"
	if len(argv) == 2: pwd = getpass("Password for {}: ".format(usr[:usr.find("@")]))
	else: pwd = argv[2]

	connectionStablished = False
	for i in range(30):
		try:
			response = build_opener(HTTPCookieProcessor(CookieJar())).open(
				"https://secure.etecsa.net:8443/LoginServlet",
				urlencode({"username": usr, "password": pwd}).encode()).read().decode()
			connectionStablished = True
			break
		except: sleep(2)
	if connectionStablished is False:
		die("nauta: couldn't open connection to secure.etecsa.net at port 8443\n"
		+ "Please check in your settings that you're connected to WIFI_ETECSA hotspot.")

	if "no tiene saldo" in response:
		die("nauta: no time left for user {}\n".format(usr[:usr.find("@")])
		+ "Please load credit on your Nauta account first.")
	elif "ya est" in response:
		die("nauta: user {} already connected\n".format(usr[:usr.find("@")])
		+ "Please disconnect first, in case online person isn't you, call 118.")
	elif "correctos" in response:
		die("nauta: couldn't login with provided credentials\n"
		+ "Please ensure yourself of entering the correct username and password.")

	for line in response.split("\n"):
		if "var urlParam = " in line:
			ATTRIBUTE_UUID = line[line.find("ATTRIBUTE_UUID")+15:line.find("&CSRFHW")]

	input(" Logged in with user {}.\n".format(usr[:usr.find("@")])
	+ "  local time: {}\n".format(get_formatted_time(localtime()))
	+ "  remaining time: {}\n".format(fetch_user_time())
	+ "  Send RETURN to disconnect.\n"
	+ "... ")

	connectionStablished = False
	for i in range(30):
		try:
			response = urlopen(
				"https://secure.etecsa.net:8443/LogoutServlet?username={}&ATTRIBUTE_UUID={}".format(
					usr, ATTRIBUTE_UUID)).read().decode()
			connectionStablished = True
			break
		except: sleep(2)
	if connectionStablished is False:
		die("nauta: couldn't open connection to secure.etecsa.net at port 8443\n"
		+ "Couldn't logout in a minute, please disconnect from WIFI_ETECSA.")

	if "SUCCESS" in response:
		print(" Logged out.\n"
		+ "  local time: {}\n".format(get_formatted_time(localtime()))
		+ "  remaining time: {}".format(fetch_user_time()))
	else:
		print("nauta: couldn't logout properly\n"
		+ "This happened because provided Nauta account credit ran out.")