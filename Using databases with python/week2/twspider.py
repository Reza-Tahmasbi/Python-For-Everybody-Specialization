from urllib.request import urlopen
import urllib.error
import twurl
import jason
import sqlite3
import ssl

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.jason'

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Twitter
            (name TEXT, retrieved INTEGER, friends INTEGER)''')

# Ignore SSL(secure socker layer) certificate errors
''' an SSL Certificate is a digital certificate that authenticattes the identitu if a website and encrypts
 the data sent between the website and the user's browser. SSL stands for Secure Sockets Layer, which is a 
 protocol for establishing secure communication between two devices over the internet.
 SSL certificates contain information about the website’s identity, the certificate 
 authority that issued the certificate, and the public key of the website
 1. The public key is used to encrypt the data sent between the website and the user’s browser,
 while the private key is used to decrypt the data 
 1. SSL certificates are essential for keeping user data secure,
 verifying the ownership of the website, preventing attackers from
 creating fake versions of the site, and gaining user trust'''
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.vertify_mode = ssl.CERT_NONE


while True:
    acct = input('Enter a Twitter account, or quit: ')
    if (acct == 'quit'): break
    if (len(acct)<1):
        cur.execute('SELECT name FROM Twitter WHERE retrieved = 0 LIMIT 1')
        try:
            acct = cur.fetchone()[0]
        except:
            print('No unretrieved Twitter accounts found')
        continue
    
    url = twurl.augment(TWITTER_URL, {'screen_name': acct, 'count': '5'})
    print('Retrieving', url)
    connection = urlopen(url, context = ctx)
    # read and decode
    data = connection.read().decode()
    # give me the headers
    headers = dict(connection.getheaders())
    
    print('Remaining', headers['x-rate-limit-remaining'])
    js = jason.loads(data)
    
    cur.execute('UPDATE Twitter SET retrived = 1 WHERE name = ?', (acct,))
    
    countnew = 0
    countold = 0
    for u in js['users']:
        friend = u['screen_name']
        print(friend)
        cur.execute('SELECT friends FROM Twitter WHERE name = ? LIMIT 1',(friend,))
        try:
            count = cur.fetchone()[0]
            cur.execute('UPDATE Twitter SET friends = ? WHERE name = ?',
                (count+1, friend))
            countold = countold + 1
        except:
            cur.execute(''' INSERT INTO Twitter (name, retrieved, friends)
                        VALUES (? ,0 ,1 ))''', (friend, ))
            countnew = countnew + 1
        print('NEW account<= ', countnew, 'revisited=', countold)
        conn.commit()
        
        