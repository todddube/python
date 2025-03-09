import random
random.seed()

# First, the `Person` object. All each person needs is a birthday.

class Person:
    def __init__( self ):
        self.birthday = random.randint( 1, 365 )

# After that we need a Party object, which must be able to
# contain a bunch of people and check to see whether any
# of them have the same birthday.

class Party:
    def __init__( self, partiers ):
        self.members   = [ Person() for p in range(partiers) ]
        self.birthdays = [ member.birthday for member in self.members ]
        self.check_matching_birthdays()

    def check_matching_birthdays( self ):
        birthday_frequencies = { b:0 for b in self.birthdays }
        for b in self.birthdays: birthday_frequencies[b] += 1
        for b in self.birthdays:
            if birthday_frequencies[b] < 2:
                del birthday_frequencies[b]
        self.matching_dates = len(birthday_frequencies)

# Finally, we need the _**main()**_ function
# allowing the user to choose the number of parties and attendees.

def main():
    while True:
        parties  = int(input("Number of parties:  "))
        partiers = int(input("Number of partiers: "))
        parties_with_matching_birthdays = 0

        for party in range( parties ):
            party = Party( partiers )
            if party.matching_dates:
                parties_with_matching_birthdays += 1

        print( 'Fraction of parties having at least one match:' )
        print( '   ', parties_with_matching_birthdays / parties )

main()