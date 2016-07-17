#!/usr/local/env python 
# Author: currentsea 
# Program: validate_signature.py 
# Validates a GPG signature upon code commit 
# Usage is intended for that within a Jenkins environment 

import gnupg 
import os

DEFAULT_SIGINING_KEY_ID = "0xBE3623B2" 
DEFAULT_SIGINING_KEY_SERVER = "hkps://pgp.mit.edu:11371" 

class Codeshield: 

	def __init__(self): 
		print "INITIALIZING CODESHIELD"
		self.gpg = gnupg.GPG('/Users/lightranger51')
		print (self.gpg.list_keys())
		# self.pgpConfig = self.getPgpConfig()  
		# print self.pgpConfig
		self.importResult =  self.gpg.recv_keys('pgp.mit.edu', '0x609BE7A5')
		print str(self.importResult.summary())


	def getPgpConfig(self): 
		pgpConfig = {}
		try: 
			signingKeyServer = os.environ["SIGNING_KEY_SERVER"]
		except: 
			signingKeyServer = DEFAULT_SIGINING_KEY_SERVER
		try: 
			signingKeyId = os.environ["SIGNING_KEY_ID"]
		except: 
			signingKeyId = DEFAULT_SIGINING_KEY_ID
		pgpConfig["trust_key_server"] = signingKeyServer
		pgpConfig["trust_key_id"] = signingKeyId
		return pgpConfig

if __name__ == "__main__": 
	shield = Codeshield()

	# pgpConfig = getPgpConfig()
# curDir = os.getcwd() 
# gpg = gnupg.GPG() 
# import_result = gpg.import_keys(key_data)
