

def read_courtlocations(sqlite_db='ccj'):

    """ 
        Assumes the SQL table 'chargeshistory' exists, with at least a 
        citation column in it, basically in the format of the data found at:
        "http://cookcountyjail.recoveredfactory.net/api/1.0/chargeshistory/?format=json".

    """

    conn = sqlite3.connect(sqlite_db)
    c = conn.cursor()

    # get the size of the table
    c.execute('SELECT COUNT(*) FROM countyapi_courtlocations')
    for result in c:
        size = float(result[0])

    c.execute("SELECT charges_citation FROM countyapi_chargeshistory;")

    charges = []

    for row in c:
        if row[0] is not None:
            charges.append(row[0])

    return charges