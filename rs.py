import requests
import re
import getpass

loginurl = "https://ssl.reddit.com/api/login/{}"
url = "http://www.reddit.com/r/{}"
voteurl = "http://www.reddit.com/api/vote"
credentials = {
   "op":"login-main",
   "user":raw_input("USERNAME: "),
   "passwd":getpass.getpass("PASSWORD: "),
   "api_type":"json"}

def scrape(s):
    return s.get(url).text

def login(s):
    r = s.post(loginurl.format(credentials["user"]),
            params=credentials)

def vote(s, direct, iden):
    vote_data = {
       "id":iden,
       "dir":direct,
       "vh":get_vote_hash(s),
       "r":re.findall("/r/(.*)$",url)[0],
       "uh":get_mod_hash(s)}
    return s.post(voteurl, params=vote_data)

def get_data_fullnames(s):
    return re.findall("data-fullname=\"(.*?)\"",scrape(s))

def get_vote_hash(s):
    return re.findall("\"vote_hash\": \"(.*?)\",",scrape(s))[0]

def get_mod_hash(s):
    return re.findall("\"modhash\": \"(.*?)\",",scrape(s))[0]

def find_titles(s):
    return re.findall("<a class=\"title [^>]*>(.*?)</a>",scrape(s))

def re_quote(deQuote):
    escape_table = {"&quot;" : "\"",
                    "&amp;" : "&",
                    "&lt;" : "<",
                    "&gt;" : ">",
                    "&#39;" : "'"}
    for escape_code in escape_table.keys():
        deQuote=deQuote.replace(escape_code,escape_table[escape_code])
    return deQuote

def find_content(s, postid):
    comurl = s.get(url+"/comments/"+postid[3:]).text
    pat = re.compile('<div class=\"md\">([\S\s]*?)</div>')
    fix = re.compile('</?\w+?>')
    print re_quote(re.sub(fix,'',re.findall(pat,comurl)[1]))

def boat_all(s, direct):
    for names in get_data_fullnames(s):
        vote(s, direct, names)
def formatting(s):
    form = re_quote("SPLITMEHERE".join(find_titles(s))).encode("utf-8")
    form = str(form)
    form = re.split('SPLITMEHERE',form)
    form = list(enumerate(form,start=1))
    for n in range(len(form)):
        print str(form[n][0]) + ".  " + str(form[n][1]) + "\n"

def process_input(s, inp):
    if len(re.findall('content', inp,flags=re.IGNORECASE))>0:
        find_content(s,
        get_data_fullnames(s)[int(re.findall('\d+',inp)[0])-1])
        return
    command = re.sub('up','1', inp, flags=re.IGNORECASE)
    command = re.sub('down','-1', command, flags=re.IGNORECASE)
    command = re.findall('-?\d+',command)
    vote(s, int(command[1]),\
get_data_fullnames(s)[int(command[0])-1])
    print 'voted'

if __name__ == "__main__":
    url = url.format(raw_input("SUBREDDIT: "))
    user = requests.session()
    login(user)
    formatting(user)
while True:
    inp = raw_input("COMMAND: ")
    if len(re.findall('quit',inp,flags=re.IGNORECASE))>0:
        break
    process_input(user,inp)
