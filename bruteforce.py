import argparse as ap
import random
import multiprocessing
import itertools
from tqdm import tqdm

dictionary_filename = "data/500-worst-passwords-processed.txt"
password_frequency_filename = "data/rockyou-withcount-processed.txt"

results_file = "data.csv"


# Method to pick a key from a dictionary based on the frequency of the key
# (frequency of a key is the key's value in the dict)
def weighted_pick(passwords, maxkey):
    r = random.randint(0, maxkey - 1)
    return passwords[r].v

# Method to match password and guess using specified indeces
def match(indeces, password, guess):
    if len(password) == 0:
        return len(guess) == 0

    for x in indeces:
        try:
            if password[x] != guess[x]:
                return False
        except IndexError:
            return False
    return True

# Method to fully match password and guess
def matchfull(password, guess):
    return password == guess


# Class to store passwords for guesses
class PasswordAttackList(object):
    # Create using file with line-seperated passwords
    def __init__(self, filename, n1):
        self.valid_passwords = []
        # Read and filter passwords according to policy
        f = open(filename, 'r')
        line = f.readline().strip()
        while line:
            if len(line)>=n1:
                self.valid_passwords.append(line)
            line = f.readline()
        f.close()


        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
        print "Valid attack passwords: ", n1, len(self.valid_passwords)
    # Method to randomly pick a password/passcode of valid lengths from the list of common passwords


    def get_dict(self):
        return self.valid_passwords

class Value:
    def __init__(self, v=None):
        self.v = v


# Class to store passwords to be guessed
class PasswordPicker(object):
    # Create using file with frequency / password tuples on each line
    def __init__(self, filename, n1):
        self.valid_passwords = dict()
        self.totalpasswords = 0
        f = open(filename, 'r')
        line = f.readline()

        # Read and filter passwords according to policy
        while line:
            try:
                v, k = line.strip().split(' ', 1)
            except ValueError:
                v = line.strip()
                k = ''
            obj = Value(k)
            v = int(v)
            if len(k) >= n1:
                self.valid_passwords[k] = v
            line = f.readline()
        f.close()
        print "Valid victim passwords: ", n1, len(set(self.valid_passwords))
        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
    # Method to randomly pick a password/passcode combination from the list
    def get_dict(self):
        return self.valid_passwords

def main():
    parser = ap.ArgumentParser(description="Brute force the number of password collisions in attack/victim dictionaries")
    parser.add_argument("n1", metavar="n1", help="Minimum password length", type=int)

    args = parser.parse_args()
    password_len = args.n1
    # Pick user password/passcode (to be guessed)
    print "Loading passwords"
    victim_passwords = PasswordPicker(password_frequency_filename, password_len).get_dict()
    attack_passwords = PasswordAttackList(dictionary_filename, password_len).get_dict()
    indeces = list(itertools.combinations(range(password_len), 3))

    partial_guesses = 0.0
    partial_attempts = 0.0

    total_guesses = 0.0
    total_attempts = 0.0

    total = len(victim_passwords) * len(attack_passwords)
    print total, "iterations coming through!"
    i = 0
    # Use progress bar
    with tqdm(total=total) as pbar:
        # Iterate over every combination of victim and attack passwords
        for vk,vv in tqdm(victim_passwords.iteritems()):
            for guess in attack_passwords:
                # Sum succesful matches according to the number of users using that password
                if matchfull(guess, vk):
                    total_guesses+=vv
                # Verify across all combinations of indeces
                for inds in indeces:
                    if match(inds, guess, vk):
                        partial_guesses+=vv
                    partial_attempts+=vv
                total_attempts+=vv
                # Increment progress bar
                i+=1
                if i==1000:
                    i = 0
                    pbar.update(1000)
    # Store results
    print partial_guesses, partial_attempts, total_guesses, total_attempts
    row = (partial_guesses, partial_attempts, total_guesses, total_attempts, "\r")
    fd = open("results/" + str(password_len), 'a+')
    fd.write(",".join(map(str, row)))
    fd.close()

if __name__ == "__main__":
    main()
