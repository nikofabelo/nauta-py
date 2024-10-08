#!/usr/bin/env python3

from getpass import getpass
import httpx, sys, time

def die(s): print(s); exit()

def fetch_user_time():
	query_url = "https://secure.etecsa.net:8443/EtecsaQueryServlet"

	data = {
		"op": "getLeftTime",
		"username": user,
		"ATTRIBUTE_UUID": ATTRIBUTE_UUID
	}

	try:
		response = httpx.post(
			query_url, data=data
		)

		if response.status_code == 200:
			return response.text
	except:
		return "couldn't fetch user time"

def format_time(t):
	t = str(t)
	return {1: "0", 2: ""}[len(t)] + t
def get_formatted_time(t):
	return "{}:{}:{}".format(
		format_time(t[3]),
		format_time(t[4]),
		format_time(t[5]))

if __name__ == "__main__":
	if len(sys.argv) == 1:
		die(
			"nauta: missing operand\n"
			+ "Please try 'nauta -h' for more information."
		)

	if sys.argv[1] in ["-h", "--help"]:
		die(
			"Usage: python3 nauta.py [USERNAME] (PASSWORD)\n"
			+ "Simple routine helping use of cuban Nauta Wi-Fi service.\n\n"
			+ "With no PASSWORD, prompts for it with echo turned off.\n\n"
			+ "  -h, --help       Display this help and exit.\n"
			+ "  -V, --version    Output version information and exit.\n\n"
			+ "Examples of usage:\n"
			+ "  python3 nauta.py axolotl7@nauta.com.cu Agr3atPWD\n"
			+ "  python3 nauta.py axolotl7 Agr3atPWD\n"
			+ "  python3 nauta.py axolotl7"
		)

	elif sys.argv[1] in ["-V", "--version"]:
		die(
			"Nauta v2.1, made in Cuba with Linux-GNU.\n\n"
			+ "Copyright © 2021- Yoel N. Fabelo.\n"
			+ "License GPLv3+: GNU GPL version 3 or later\n"
			+ "<https://gnu.org/licenses/gpl.html>.\n"
			+ "This is free software: you are free to change and redistribute it.\n"
			+ "There is NO WARRANTY, to the extent permitted by law.\n\n"
			+ "Written by Yoel N. Fabelo <human.x7e6@gmail.com>."
		)

	user = sys.argv[1].replace("@nauta.com.cu", "") + "@nauta.com.cu"
	if len(sys.argv) == 2:
		password = getpass(
			"Password for {}: ".format(
				user[:user.find("@")]
			)
		)
	else:
		password = sys.argv[2]

	connected = False
	for i in range(30):
		login_url = "https://secure.etecsa.net:8443/LoginServlet"

		data = {
			"username": user,
			"password": password
		}

		try:
			response = httpx.post(
				login_url, data=data,
				follow_redirects=True
			)

			if response.status_code == 200:
				response = response.text
				connected = True
				break
		except:
			time.sleep(2)

	if not connected:
		die(
			"nauta: couldn't open connection to secure.etecsa.net at port 8443\n"
			+ "Please check in your settings that you're connected to hotspot WIFI_ETECSA."
		)

	if "no tiene saldo" in response:
		die(
			f"nauta: no time left for user {user[:user.find('@')]}\n"
			+ "Please load credit on your Nauta account first."
		)

	elif "ya est" in response:
		die(
			f"nauta: user {user[:user.find('@')]} already connected\n"
			+ "Please disconnect first, in case online person isn't you, call 118."
		)

	elif "correctos" in response:
		die(
			"nauta: couldn't login with provided credentials\n"
			+ "Please ensure yourself of entering the correct username and password."
		)

	for line in response.split("\n"):
		if "var urlParam = " in line:
			ATTRIBUTE_UUID = line[
				line.find("ATTRIBUTE_UUID") + 15
				:line.find("&CSRFHW")
			]

	input(
		f" Logged in with user {user[:user.find('@')]}.\n"
		+ f"  local time: {get_formatted_time(time.localtime())}\n"
		+ f"  remaining time: {fetch_user_time()}\n"
		+ "  Send RETURN to disconnect.\n... "
	)

	connected = False
	for i in range(30):
		logout_url = "https://secure.etecsa.net:8443/LogoutServlet"

		data = {
			"username": user,
			"ATTRIBUTE_UUID": ATTRIBUTE_UUID
		}

		try:
			response = httpx.post(
				logout_url, data=data
			)

			if response.status_code == 200:
				response = response.text
				connected = True
				break
		except:
			time.sleep(2)

	if not connected:
		die(
			"nauta: couldn't open connection to secure.etecsa.net at port 8443\n"
			+ "Couldn't logout in a minute, please disconnect from WIFI_ETECSA."
		)

	if "SUCCESS" in response:
		print(
			" Logged out.\n"
			+ f"  local time: {get_formatted_time(time.localtime())}\n"
			+ f"  remaining time: {fetch_user_time()}"
		)
	else:
		print(
			"nauta: couldn't logout properly\n"
			+ "This happened because provided Nauta account's credit ran out."
		)