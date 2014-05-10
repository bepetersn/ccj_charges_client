from pysqlite2 import dbapi2 as sqlite3
from pprint import pprint
import re


SQLITE_DB = 'charges.db'

CHARGE_REGEX = \
        ('(\d{1,4})'                 # - Chapter
        ' ILCS '                     #  
        '(\d{1,4})'                  # - Act
        '[ |/]'                      # 
        '(\d{1,4}'                   # - Section
        '(?:[ |-]\d{1,4}\w?)?'       # - Section, cont. 
        '(?:\.\d)?)'                 # - Section, cont.
        '((?:\([\w|\-|.]\)){0,4})?'  # - optional sub-sections
        '.*')                        # 


def normalize():

    """ Returns a 3-tuple:

        - a list of normalized charge objects, 
        - a list of unqiue citations that couldn't be handled, 
        - a tuple containing: 
            1) the percent of the entire input table that couldn't be handled 
            2) the percent of the unique citations that couldn't be handled

    """

    CHARGE_PATTERN = re.compile(CHARGE_REGEX)

    charges = []

    conn = sqlite3.connect(SQLITE_DB)
    conn.enable_load_extension(True)
    conn.load_extension("/usr/lib/sqlite3/pcre.so")
    c = conn.cursor()

    # get the size of the table
    c.execute('SELECT COUNT(*) FROM chargeshistory')
    for result in c:
        size = float(result[0])

    c.execute("SELECT citation FROM chargeshistory WHERE "
              "citation REGEXP '{0}'".format(CHARGE_REGEX))

    count = 0
    fail = 0
    miss = set([])
    for row in c:

        charge = row[0]
        if charge.startswith('38'):
            print charge
            raw_input()
        match = CHARGE_PATTERN.match(charge)

        if match:

            chapter = match.group(1)
            act = match.group(2)
            section = match.group(3)
            subsection = match.group(4)

            # ignore id creation until we know it's a new charge
            citation = "{0} {1} {2}{3}".format(chapter, act, section, subsection)
            if citation not in [c[1] for c in charges]:
                charges.append((count, citation))

            # increment if a new charge was added
            if len(charges) > count:
                count += 1

        else:
            fail += 1
            miss.add(charge) 

    return charges, miss, (round((fail / size), 3), round(len(miss) / float(len(charges)), 3))


def write(charges=None):

    conn = sqlite3.connect(SQLITE_DB)

    if not charges:
        charges = normalize()

    query_str = 'INSERT INTO charges VALUES (?, ?)'
    conn.executemany(query_str, charges)
    conn.commit()

    print "{0} citations added to the charges table".format(len(charges))


