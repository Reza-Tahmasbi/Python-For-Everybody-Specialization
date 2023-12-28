import sqlite3
conn = sqlite3.connect('p2.sqlite')
cur = conn.cursor()
cur = cur.execute("DROP TABLE IF EXISTS Counts")

cur.execute("CREATE TABLE Counts(org TEXT, count INTEGER)")
fh = open(r'C:\Users\reza\Desktop\mbox-short.txt', 'r')

for line in fh:
    if not line.startswith("From "): continue
    pieces = line.split()
    email = pieces[1]
    (email_name, organization) = email.split("@")
    cur.execute('SELECT count FROM Counts WHERE org = ?', (organization,))
    row = cur.fetchone()
    if row is None:
        cur.execute('''INSERT INTO Counts (org, count)
                    VALUES (?,1)''', (organization,))
    else:
        cur.execute('''UPDATE Counts SET count = count + 1 WHERE org = ?''', (organization, ))
    conn.commit()
sqlstr = 'SELECT org, count FROM Counts ORDER BY count DESC LIMIT 10'

for row in cur.execute(sqlstr):
    print(str(row[0]), row[1])
    
cur.close()