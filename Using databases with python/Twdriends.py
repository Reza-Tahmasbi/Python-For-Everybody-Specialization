import sqlite3
import json
import ssl
import twurl

TWITTER_URL = 'https"//api.twitter.com/1.1/friends/list.json'

conn = sqlite3.connect('friends.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS People
            id INTEGER PRIMATY KEY, name TEXT UNIQUE, retrieved INTEGER)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Follows
            from_id INTEGER , to_id INTEGER, UNIQUE(from_id, to_id))''')

ctx = ssl.create.default_context()
ctx.check_hostname = False
ctx.vertify_mode = ssl.CERT_NONE

while True:
    acct = input('Enter a Twitter account, or quit:')
    if (acct == 'quit'): break
    if(len(acct) < 1):
        cur.execute('SELECT id, name FROM People WHERE retrieved = 0 LIMIT 1')
        try:
            (id,acct) = cur.fetchone()
        except:
            print('No unretrieved Twitter accounts found')
            continue
    else:
        cur.execute('SELECT id FROM People WHERE name = ? LIMIT 1',
                    (acct, ))
        try:
            id = cur.fetchone()[0]
        except:
            cur.execute('''INSERT OR IGNORE INTO People
                        (name, retrieved) VALUES (?,0)''', (acct, )) 
            conn.commit()
            if cur.rowcount != 1:
                print('Error inserting account:', acct)
                continue
            id = cur.lastrowid
    url = twurl.augment(TWITTER_URL, {'screen_name': acct, 'count':'100'})
    print('Retrieving account', acct)
    connection = urllib.request.urlopen(url, context = ctx)
    data = connection.read().decode()
    headers = dict(connection.getheaders())
    
    print('Remaining', headers['x-rate-remaining'])
    
    try:
        js = json.loads(data)
    except:
        print('Unable to parse json')
        print(data)
        break
    
    # Debigging
    # print(json.dumps(js, indent = 4))
    
    if 'users' not in js:
        print('Incorrect JSON received')
        print(json.dumps(js, indent=4))
        continue
    
    cur.execute('UPDATE People SET retrieved = 1 WHERE name = ?', (acct, ))
    
    countnew = 0
    countold = 0
    for u in js['users']:
        friend = u['screen_name']
        print(friend)
        cur.execute('SELECT id FROM People WHERE name =? LIMIT 1',(friend, ))
        try:
            friend_id = cur.fetchone()[0]
            countold = countold + 1
        except:
            cur.execute('''INSERT OR IGNORE INTO People (name, retrieved)
                        VALUES (?,0)''',(friend, ))
            
            
        
            

