import argparse as ap
import random

dictionary_filename = "data/500-worst-passwords-processed.txt"
password_frequency_filename = "data/rockyou-withcount-processed.txt"


# Method to pick a key from a dictionary based on the frequency of the key
# (frequency of a key is the key's value in the dict)
def weighted_pick(passwords):
	r = random.uniform(0, sum(passwords.itervalues()))
	s = 0.0
	for k, v in passwords.iteritems():
		s += v
		if r < s: return k
	return k

def match(password, guess):
	if len(password)==0:
		return len(guess)==0

	for a in range(0,3):

		x = random.randint(0, len(password)-3)
		try:
			if password[x]!=guess[x]:
				return False
		except IndexError:
			print password, len(password)
			print guess, len(guess)
			print x
			raise IndexError
	return True

def matchfull(password, guess):
	return password == guess


# Class to store passwords for guesses
class Password_attack_list(object):
	passwords = []
	# Create using file with line-seperated passwords
	def __init__(self, filename):
		f = open(dictionary_filename, 'r')
		line = f.readline()
		while line:
			self.passwords.append(line.rstrip())
			line = f.readline()
		f.close()

	# Method to randomly pick a password/passcode of valid lengths from the list of common passwords
	def pick_password_passcode(self, n1, n2):
		NOT WORKING, PASSWORDS ARE TOO SHORT
		valid_passwords = filter(lambda x: len(x)>=n1, self.passwords)
		valid_passcodes = filter(lambda x: len(x)==n2, self.passwords)
		if len(valid_passwords)==0:
			raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
		if len(valid_passcodes)==0:
			raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')
		return random.choice(valid_passwords), random.choice(valid_passcodes)


# Class to store passwords to be guessed
class Password_picker(object):
	password_dict = dict()

	# Create using file with frequency / password tuples on each line
	def __init__(self, filename):
		f = open(filename, 'r')
		line = f.readline()
		while line:
			try:
				v, k = line.strip().split(' ', 1)
			except ValueError:
				v = line.strip()
				k = ''
			v = v.strip()
			k = k.strip()
			self.password_dict[k] =  int(v)
			line = f.readline()
		f.close()

	# Method to randomly pick a password/passcode combination from the list
	def pick_password_passcode(self, n1, n2):
		valid_passwords = dict((k, self.password_dict[k]) for k in self.password_dict.keys() if len(k)>=n1)
		valid_passcodes = dict((k, self.password_dict[k]) for k in self.password_dict.keys() if len(k)==n2)
		if len(valid_passwords)==0:
			raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
		if len(valid_passcodes)==0:
			raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')
		return weighted_pick(valid_passwords), weighted_pick(valid_passcodes)



def main():
	# Parse program arguments
	parser = ap.ArgumentParser(description="Calculate probability of dictionary attack for each authentication system")
	parser.add_argument("m", metavar="M", help="Number of guesses", type=int)
	parser.add_argument("n1", metavar="N1", help="Min password length", type=int)
	parser.add_argument("n2", metavar="N2", help="Exact passcode length", type=int)

	args = parser.parse_args()

	if args.n2<3:
		raise ap.ArgumentTypeError("N2 minimum value is 3")

	# Initialise list of passwords to sample from during attack
	password_list = Password_attack_list(dictionary_filename)

	# Pick user password/passcode (to be guessed)
	password_distrib = Password_picker(password_frequency_filename)
	password, passcode = password_distrib.pick_password_passcode(args.n1, args.n2)

	print "Things to guess: "
	print "PASSWORD | PASSCODE"
	print password, passcode

	full_guesses = 0
	char_guesses = 0
	for x in range(0, args.m):
		guess_password, guess_passcode = password_list.pick_password_passcode(args.n1, args.n2)
		
		if match(passcode, guess_passcode):
			if matchfull(password, guess_password):
				print "FULL"
				full_guesses+=1
			if match(password, guess_password):
				print "CHAR"
				char_guesses+=1
		if x%10000==0:
			print x
	print "Full guesses: " + str(full_guesses)
	print "Partial guesses: " + str(char_guesses)

if __name__ == "__main__":
	main()