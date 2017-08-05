#!/usr/bin/env python3

import re
import socket
import winsound
from threading import Thread
import tkinter as tk

keyFile = open('keywords.txt', 'r')
keyFile = keyFile.read()

bannedFile = open('bannedwords.txt', 'r')
bannedFile = bannedFile.read()

global senderName
senderName = ""
global lastMsg
lastMsg = ""

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.twitch.tv"                          # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
CHAN = ""                                       # Channelname = #{Nickname}
NICK = ""                                       # Nickname = Twitch username
PASS = ""                                       # www.twitchapps.com/tmi/ will help to retrieve the required authkey
# --------------------------------------------- End Settings -------------------------------------------------------


# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))

def beep():
    winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))
# --------------------------------------------- End Functions ------------------------------------------------------



# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def parse_message(sender, msg):
    if len(msg) >= 1:
        message = msg
        msg = msg.lower()
        check_words = keyFile
        check_list= check_words.split()
        check_bannedwords = bannedFile
        check_bannedlist= check_bannedwords.split()
        for word in check_list:
            if word in msg:
                global lastMsg
                lastMsg = sender + ": " + message
                label.config(text=lastMsg)

                t3 = Thread(target=beepFunction)
                t3.start()

                print(sender + ": " + message)
                global senderName
                senderName = sender

                return
        for word in check_bannedlist:
            if word in msg:
                send_message(CHAN, '/timeout '+ sender)
                print("Gave "+ sender+ " timeout for saying '"+msg+"'")
                return




# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Command Functions --------------------------------------------
def command_1():
    send_message(CHAN, '/timeout ')


def onKeyPress():
    if(senderName!=""):
        send_message(CHAN, '!permit '+senderName)

# --------------------------------------------- End Command Functions ----------------------------------------------

con = socket.socket()
con.connect((HOST, PORT))

send_pass(PASS)
send_nick(NICK)
join_channel(CHAN)

def beepFunction():
    beep()

def firstFunction():
    root = tk.Tk()
    root.title("Permit Button")
    global label
    label = tk.Label(root, fg="dark green")
    label.pack()
    button = tk.Button(root, text='Permit', width=25, command=onKeyPress)
    button.pack()
    root.mainloop()

def secondFunction():
    data = ""

    while True:
        try:

            data = data+con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", data)
            data = data_split.pop()

            for line in data_split:
                line = str.rstrip(line)
                line = str.split(line)

                if len(line) >= 1:
                    if line[0] == 'PING':
                        send_pong(line[1])
                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message)



        except socket.error:
            print("Socket died")

        except socket.timeout:
            print("Socket timeout")




t1 = Thread(target=firstFunction)
t2 = Thread(target=secondFunction)

t1.start()
t2.start()

