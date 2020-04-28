#!/usr/bin/python3

import blocksmith
import secrets
import string
import webbrowser

# blocksmith used a seed phrase.
# instead I'll generate something using secrets library which is cryptographically secure.
alphabet = string.ascii_letters + string.digits
length = 128 + secrets.randbelow(64) # Random length greater than 128
seed_text = ''.join(secrets.choice(alphabet) for i in range(length))

print("Using random seed:")
print (seed_text, '\n')

# Generate the private key
kg = blocksmith.KeyGenerator()
kg.seed_input(seed_text)
privateKey = kg.generate_key()

# Now the corresponding address
address = blocksmith.BitcoinWallet.generate_address(privateKey)

# Output all into to terminal
print("Bitcoin Address  : \033[0;92m" , address + "\033[00m")
print("Private key      : \033[0;92m" , privateKey + "\033[00m\n")
print("Opened browser to offline bitaddress to validate the address from private key and print QR Codes")

# Going to also write into into text files
fp = open(address + ".txt", "w")
fp.write("GENERATED BITCOIN WALLET\n\n")
fp.write("Address     : " + address + "\n")
fp.write("Private Key : " + privateKey + "\n")
fp.close()

# 'cos I'm lazy
webbrowser.get('firefox').open('file:///home/iain/Crypto/Bitcoin/bitaddress.org-3.3.0/IRB_bitaddress.html')

