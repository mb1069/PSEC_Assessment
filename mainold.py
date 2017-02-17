import argparse as ap
import random

dictionary_filename = "data/500-worst-passwords-processed.txt"
password_frequency_filename = "data/rockyou-withcount-processed.txt"

results_file = "data.csv"


# Method to pick a key from a dictionary based on the frequency of the key
# (frequency of a key is the key's value in the dict)
def weighted_pick(passwords, maxkey):
    r = random.randint(0, maxkey-1)
    return passwords[r].v


def match(password, guess):
    if len(password) == 0:
        return len(guess) == 0

    indices = random.sample(range(0, len(password)), 3)
    for a in range(0, 3):
        x = indices[a]
        try:
            if password[x] != guess[x]:
                return False
        except IndexError:
            return False
    return True


def matchfull(password, guess):
    return password == guess


# Class to store passwords for guesses
class PasswordAttackList(object):
    # Create using file with line-seperated passwords
    def __init__(self, filename, n1, n2):
        self.passwords = []
        self.valid_passwords = []
        self.valid_passcodes = []
        f = open(filename, 'r')
        line = f.readline()
        while line:
            self.passwords.append(line.strip())
            line = f.readline()
        f.close()

        self.valid_passwords = filter(lambda x: len(x) >= n1, self.passwords)
        self.valid_passcodes = filter(lambda x: len(x) == n2, self.passwords)

        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
        if len(self.valid_passcodes) == 0:
            raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')

    # Method to randomly pick a password/passcode of valid lengths from the list of common passwords
    def pick_password_passcode(self, n1, n2):
        password = random.choice(self.valid_passwords)
        passcode = random.choice(self.valid_passcodes)
        return password, passcode


class Value:
    def __init__(self, v=None):
        self.v = v


# Class to store passwords to be guessed
class PasswordPicker(object):
    # Create using file with frequency / password tuples on each line
    def __init__(self, filename, n1, n2):
        f = open(filename, 'r')
        password_dict = dict()
        line = f.readline()

        self.valid_passwords = []
        self.valid_passcodes = []

        self.totalpasswords = 0
        self.totalpasscodes = 0
        while line:
            try:
                v, k = line.strip().split(' ', 1)
            except ValueError:
                v = line.strip()
                k = ''
            obj = Value(k)
            v = int(v)
            if len(k) >= n1:
                for x in range(0, v):
                    self.valid_passwords.append(obj)
                self.totalpasswords += v
            if len(k) == n2:
                for x in range(0, v):
                    self.valid_passcodes.append(obj)
                self.totalpasscodes += v

            password_dict[k] = int(v)
            line = f.readline()
        f.close()

        # self.valid_passwords = dict((k, password_dict[k]) for k in password_dict.keys() if len(k) >= n1)
        # self.valid_passcodes = dict((k, password_dict[k]) for k in password_dict.keys() if len(k) == n2)
        print len(self.valid_passwords), len(self.valid_passcodes)
        print self.totalpasswords, self.totalpasscodes
        if len(self.valid_passwords) == 0:
            raise ValueError('Invalid password lengths, no passwords of this length exist in the dictionary file.')
        if len(self.valid_passcodes) == 0:
            raise ValueError('Invalid passcode lengths, no passcodes of this length exist in the dictionary file.')

    # Method to randomly pick a password/passcode combination from the list
    def pick_password_passcode(self):
        return weighted_pick(self.valid_passwords, self.totalpasswords), weighted_pick(self.valid_passcodes, self.totalpasscodes)


def main():
    random.seed()
    # Parse program arguments
    parser = ap.ArgumentParser(description="Calculate probability of dictionary attack for each authentication system")
    parser.add_argument("m", metavar="M", help="Number of guesses", type=int)
    parser.add_argument("n1", metavar="N1", help="Min password length", type=int)
    parser.add_argument("n2", metavar="N2", help="Exact passcode length", type=int)
    parser.add_argument("-its", metavar="ITS", help="Number of runs to undertake", default=1, type=int)
    parser.add_argument("-save_file", metavar="F", help="Filename to save to", default=results_file)

    args = parser.parse_args()

    if args.n2 < 3:
        raise ap.ArgumentTypeError("N2 minimum value is 3")

    print "Loading guess passwords"
    # Initialise list of passwords to sample from during attack
    password_list = PasswordAttackList(dictionary_filename, args.n1, args.n2)

    # Pick user password/passcode (to be guessed)
    password_distrib = PasswordPicker(password_frequency_filename, args.n1, args.n2)


    for i in range(0, args.its):

        guess_password, guess_passcode = password_list.pick_password_passcode(args.n1, args.n2)
        print "Attempting: "
        print "PASSWORD | PASSCODE"
        print guess_password, guess_passcode
        full_guesses = 0
        char_guesses = 0
        for x in range(0, args.m):
            password, passcode = password_distrib.pick_password_passcode()
            if match(passcode, guess_passcode):
                if matchfull(password, guess_password):
                    full_guesses += 1
                if match(password, guess_password):
                    char_guesses += 1
            if x % 1000000 == 0:
                print float(x) / float(args.m), full_guesses, char_guesses
        row = (full_guesses, char_guesses, guess_password, guess_passcode, "\r")
        fd = open("results/"+args.save_file, 'a+')
        fd.write(",".join(map(str, row)))
        fd.close()


    # for x in range(0, args.m):
    #     password_distrib.pick_password_passcode()
    #     if x % 1000 == 0:
    #         print x
    #         for i in range(0, args.its):
    #             guess_password, guess_passcode = password_list.pick_password_passcode(args.n1, args.n2)
    #
    #             print guess_password, guess_passcode
    #             full_guesses = 0
    #             char_guesses = 0
    #             for x in range(0, args.m):
    #                 password, passcode = password_distrib.pick_password_passcode()
    #                 if match(passcode, guess_passcode):
    #                     if matchfull(password, guess_password):
    #                         full_guesses += 1
    #                     if match(password, guess_password):
    #                         char_guesses += 1
    #                 if x % 10000 == 0:
    #                     print float(x) / float(args.m), full_guesses, char_guesses



if __name__ == "__main__":
    main()
