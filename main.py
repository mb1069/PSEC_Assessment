import argparse as ap
import random
from tqdm import tqdm, trange

# Paths to victim list and attack dictionary
dictionary_filename = "data/500-worst-passwords-processed.txt"
password_frequency_filename = "data/rockyou-withcount-processed.txt"

# Path to file in which results are optionally stored
results_file = "data.csv"


# Method to pick a key from a dictionary based on the frequency of the key
# (frequency of a key is the key's value in the dict)
def weighted_pick(passwords, maxkey):
    r = random.randint(0, maxkey - 1)
    return passwords[r].v

# Method to validate passwords using 3 random indeces in the password's range
def match(password, guess):
    # Edge case where the password is blank
    if len(password) == 0:
        return len(guess) == 0

    # Randomly select 3 individual indeces for which the passwords/passcodes will need to match
    indices = random.sample(range(0, len(password)), 3)
    for a in range(0, 3):
        x = indices[a]
        try:
            if password[x] != guess[x]:
                return False
        except IndexError:
            return False
    return True

# Method to match full passwords
def matchfull(password, guess):
    return password == guess


# Class to store passwords for guesses
class AttackPasswords(object):
    # Create using file with line-seperated passwords
    def __init__(self, filename, n1, n2):
        self.valid_passwords = []
        self.valid_passcodes = []
        # Retrieve passwords from file
        f = open(filename, 'r')
        line = f.readline()
        while line:
            line = line.strip() # Remove whitespace
            # Append to either/both/neither list depending on current policy
            if len(line)>=n1:
                self.valid_passwords.append(line)
            if len(line)==n2:
                self.valid_passcodes.append(line)
            line = f.readline()
        f.close()

        # Validating the compatibility of the data sets with arguments to ensure bulk guessing can be conducted
        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
        if len(self.valid_passcodes) == 0:
            raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')

    # Method to randomly pick a password/passcode of valid lengths from the list of common passwords
    def pick_password_passcode(self):
        password = random.choice(self.valid_passwords)
        passcode = random.choice(self.valid_passcodes)
        return password, passcode

# Value wrapping class to avoid duplicating values in memory
class Value:
    def __init__(self, v=None):
        self.v = v


# Class to store passwords to be guessed
class VictimPasswords(object):
    # Create using file with frequency / password tuples on each line
    def __init__(self, filename, n1, n2):
        self.valid_passwords = []
        self.valid_passcodes = []
        self.totalpasswords = 0
        self.totalpasscodes = 0

        # Reading password distribution from file
        f = open(filename, 'r')
        line = f.readline()
        while line:
            # Error catching for blank passwords
            try:
                v, k = line.strip().split(' ', 1)
            except ValueError:
                v = line.strip()
                k = ''
            # Wrap value in object to avoid duplicating string in memory
            obj = Value(k)
            v = int(v)
            # Conditionally add to either passwords or passcodes
            if len(k) >= n1:
                for x in range(0, v):
                    self.valid_passwords.append(obj)
                self.totalpasswords += v
            if len(k) == n2:
                for x in range(0, v):
                    self.valid_passcodes.append(obj)
                self.totalpasscodes += v
            line = f.readline()
        f.close()

        self.totalpasswords = len(self.valid_passwords)
        self.totalpasscodes = len(self.valid_passcodes)

        # Validating the compatibility of the data sets with arguments to ensure bulk guessing can be conducted
        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
        if len(self.valid_passcodes) == 0:
            raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')

    # Method to randomly pick a password/passcode combination from the list
    def pick_password_passcode(self):
        return weighted_pick(self.valid_passwords, self.totalpasswords), weighted_pick(self.valid_passcodes,
                                                                                       self.totalpasscodes)


def main():
    random.seed()
    # Parse program arguments
    parser = ap.ArgumentParser(description="Calculate probability of dictionary attack for each authentication system")
    parser.add_argument("m", metavar="M", help="Number of guesses", type=int)
    parser.add_argument("n1", metavar="N1", help="Min password length", type=int)
    parser.add_argument("n2", metavar="N2", help="Exact passcode length", type=int)
    parser.add_argument("-its", help="Number of times to run the program", default=1, type=int)
    parser.add_argument("--save_file", help="Saves results to data/"+results_file+"or a specified filename in data/", action='store_true')

    args = parser.parse_args()

    if args.n2 < 3:
        raise ap.ArgumentTypeError("N2 minimum value is 3")

    print "Loading guess credentials"
    # Initialise list of passwords to sample from during attack
    password_list = AttackPasswords(dictionary_filename, args.n1, args.n2)

    # Pick user password/passcode (to be guessed)
    print "Loading victim credentials"
    password_distrib = VictimPasswords(password_frequency_filename, args.n1, args.n2)

    print "Loaded passwords, beginning bulk guessing"
    for i in trange(0, args.its):
        full_guesses = 0
        char_guesses = 0
        for x in trange(0, args.m):
            guess_password, guess_passcode = password_list.pick_password_passcode()
            password, passcode = password_distrib.pick_password_passcode()
            # If passcodes match at indeces, evaluate further, else skip to save computational time
            if match(passcode, guess_passcode):
                # Evaluate full password (Auth system 1)
                if matchfull(password, guess_password):
                    full_guesses += 1
                # Evaluate partial password (Auth system 2)
                if match(password, guess_password):
                    char_guesses += 1

        # Save data to file
        if args.save_file is not None:
            row = (full_guesses, char_guesses, "\r")
            fd = open("results/" + results_file, 'a+')
            fd.write(",".join(map(str, row)))
            fd.close()
    print "Ran bulk guessing "+str(args.m)+" times"
    print "Password/passcode length of: ", args.n1, "/", args.n2 
    print "Successful guesses using a full password: ", full_guesses
    print "Successful guesses using a sub-sampled password: ", char_guesses
    if args.save_file is not None:
        print "Data was saved at data/"+results_file


if __name__ == "__main__":
    main()
