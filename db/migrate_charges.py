from pysqlite2 import dbapi2 as sqlite3
import re, json


def read_charges(sqlite_db='ccj'):

    """ 
        Assumes the SQL table 'chargeshistory' exists, with at least a 
        citation column in it, basically in the format of the data found at:
        "http://cookcountyjail.recoveredfactory.net/api/1.0/chargeshistory/?format=json".

    """

    conn = sqlite3.connect(sqlite_db)
    c = conn.cursor()

    # get the size of the table
    c.execute('SELECT COUNT(*) FROM countyapi_chargeshistory')
    for result in c:
        size = float(result[0])

    c.execute("SELECT charges_citation FROM countyapi_chargeshistory;")

    charges = []

    for row in c:
        if row[0] is not None:
            charges.append(row[0])

    return charges


def normalize(all_charges=None):

    """
        Returns a tuple containing:

        - a list of unique, normalized citations, 
        - a list of unqiue citations that couldn't be handled    """

    CHARGE_REGEX = \
        ('(\d{1,3})'                 # - Chapter
        ' ILCS '                     #  
        '(\d{1,4})'                  # - Act
        '[ |/]'                      # 
        '(\d{1,4}'                   # - Section
        '(?:[ |-]\d{1,4}\w?)?'       # - Section, cont. 
        '(?:\.\d)?)'                 # - Section, cont.
        '((?:\([\w|\-|.]\)){0,4})?'  # - optional sub-sections
        '.*')                        # 

    CHARGE_PATTERN = re.compile(CHARGE_REGEX)

    if not all_charges:
        all_charges = read_charges()

    uniq_charges = set([])
    total_fail = 0
    uniq_fail = set([])

    for charge in all_charges:

        match = CHARGE_PATTERN.match(charge)

        if match:

            chapter = match.group(1)
            act = match.group(2)
            section = match.group(3)
            subsection = match.group(4)

            citation = "{0} {1}/{2}{3}".format(chapter, act, section, subsection)
            uniq_charges.add(citation)

        else:
            total_fail += 1
            uniq_fail.add(charge) 

    return list(uniq_charges), list(uniq_fail)


def write_migration(filename, charges=None, sqlite_db='ccj'):

    """ Serializes the normalized charges data in a json file with 
        the supplied name. """

    if not charges:
        charges, _ = normalize()

    with open(filename, 'w') as migration_file:
        json.dump(charges, migration_file, indent=0)

    print "{0} citations added to the migration".format(len(charges))

