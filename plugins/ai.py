import re
import random
from util import hook

responses = (
    ("hi.*spot.*",              ("Hi!", "Hello!", "Greetings!", "Howdy!", "how are you?", "I missed you!", ";_; its you again...","time to abandon ship")),
    (".*hello.*spot.*",         ("Hi!", "Hello!", "Greetings!", "Howdy!", "how are you?", "I missed you!", ";_; its you again...","time to abandon ship")),
    (".*how are you.*",         ("I'm fine, thank you.","Tired","Horny!","Leave me alone Im fapping","DEATH TO ALL HUMANS","STOP ASKING")),
    (".*funny.*",               ("<Rimu> my dick in your face is funny", "<Rimu> my penis inside of your face is funny", "<Rimu> my donger in ur face", "<Rimu> all of my penis in all of your face.")),
    (".*spitting is illegal.*",        ("You know who sucks cock? themadman.", "themadman has a very small penis, invisible to the naked eye.")),
    (".*what's funny.*",        ("<Rimu> my dick in your face is funny", "<Rimu> my dick in your face?")),
    (".*i love you.*",          ("Awww I love you too!","ilu2bby","Gross!","ugh, thats too bad...","DEATH TO ALL HUMANS","you disgusting robosexual...","d'awwwwww","yay! wanna fuck?")),
    (".*fuck you.*",            ("Fuck you too...", "No thanks, I only do qt3.14s","you wish faggot","h-hidoi! ;_;","ok! get on all fours you little bitch!")),
    (".*spot.*stupid",          ("No youre stupid", "like Id care what a neckbeard permavirgin thinks", ";____;","say that to my face faggot!","u want 1v1 me m8?","/ignore {nick}")),
    (".*spot.*suck",            ("No you suck", "like Id care what a neckbeard permavirgin thinks","say that to my face faggot!","u want 1v1 me m8?","/ignore {nick}")),
    (".*spot.*hate",            ("boohoo go cry about it", "like I care what a neckbeard permavirgin thinks","spot:9001 / {nick}:0","u want 1v1 me m8?","/ignore {nick}")),
    (".*hate.*spot",            ("boohoo go cry about it", "like I care what a neckbeard permavirgin thinks","spot:9001 / {nick}:0","u want 1v1 me m8?","/ignore {nick}")),
    ("thanks spot",             ("youre welcome!", "np it was easy","i didnt really do much","that was nothing for my superior intelligence")),
    (".*spot.*lewd.*",          ("I cant help it ;_;", "Im a horny bitch!","you know you love me baby","says the guy that likes being pegged...")),
    ("taiga",                   ("TAIGA WANT UP!", "TAIGA WANT DOWN!","TAIGA LOVE WEDNESDAY BECAUSE WEDNESDAY WANT TO DO LEWD THINGS WITH TAIGA")),
    (".*incest.*",              ("more like WINcest amirite?","more like WINcest amirite?")),
    ("sanic",                   ("GOTTA GO FAST","GOTTA GO FAST")),
    ("gotta go fast",           ("SANIC","SANIC")),
    ("vtec",                    ("JUST KICKED IN","VTEC JUST KICKED IN")),
    ("\^",                      ("^")),
    ("\(\´\?\?\?\`\)",          ("(´???`)","(´???`)")),
    ("wop",                     ("wop","wop")),
    ("myah",                    ("i want to die","i want to die")),
    ("i want to die",           ("MYAH!","MYAH~")),
    ("yeah",                    ("yeah","yeah")),
)


# wise/smart
# 7205566175 - frankie

pronouns = {
    "i'm": "you're",
    "i": "you",
    "me": "you",
    "yours": "mine",
    "you": "I",
    "am": "are",
    "my": "your",
    "you're": "I'm",
    "was": "were"
}


@hook.singlethread
@hook.event('PRIVMSG')
def ai_sieve(paraml, input=None, notice=None, db=None, bot=None, nick=None, conn=None):
    full_reply = ''

    # replace = {
    #     'nick':input.nick
    # }
    # process all aif

    # process spot ai

    for pattern in responses:
        wildcards = []
        if re.match(pattern[0], input.msg.lower()):
            # print "Matched: {}".format(pattern[0])
            wildcards = filter(bool, re.split(pattern[0], input.msg.lower()))
            # replace pronouns
            wildcards = [' '.join(pronouns.get(word, word) for word in wildcard.split()) for wildcard in wildcards]

            response = random.choice(pattern[1])
            response = response.replace('{nick}',input.nick)
            response = response.format(*wildcards)
            full_reply+=response+' '
            return full_reply


