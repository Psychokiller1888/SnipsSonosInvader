# SnipsSonosInvader

Welcome!

This demo script will show you how to use your Sonos installation as Snips speakers

I have been asked many time how it works, so you have here a full working exemple.

Snips will try, if instructed to, to speak through a Sonos player if one is detected in the room you are having the conversation. If no Sonos detected or not instructed to use Sonos it will use its internal speaker.


## Installation
```
sudo pip install soco
sudo pip install paho-mqtt
sudo apt-get install samba samba-common-bin
sudo mkdir -m 1777 /share
sudo nano /etc/samba/smb.conf
```

Check that Samba did configure correctly in

```/etc/samba/smb.conf```

If not here's a valid Samba config:

```
#==================== Share Definitions =======================
[global]
   ntlm auth=yes

[homes]
   comment = Home Directories
   browseable = no

# By default, the home directories are exported read-only. Change the
# next parameter to 'no' if you want to be able to write to them.
   read only = yes

# File creation mask is set to 0700 for security reasons. If you want to
# create files with group=rw permissions, set next parameter to 0775.
   create mask = 0700

# Directory creation mask is set to 0700 for security reasons. If you want to
# create dirs. with group=rw permissions, set next parameter to 0775.
   directory mask = 0700

# By default, \\server\username shares can be connected to by anyone
# with access to the samba server.
# The following parameter makes sure that only "username" can connect
# to \\server\username
# This might need tweaking when using external authentication schemes
   valid users = %S

# Un-comment the following and create the netlogon directory for Domain Logons
# (you need to configure Samba to act as a domain controller too.)
;[netlogon]
;   comment = Network Logon Service
;   path = /home/samba/netlogon
;   guest ok = yes
;   read only = yes

# Un-comment the following and create the profiles directory to store
# users profiles (see the "logon path" option above)
# (you need to configure Samba to act as a domain controller too.)
# The path below should be writable by all users so that their
# profile directory may be created the first time they log on
;[profiles]
;   comment = Users profiles
;   path = /home/samba/profiles
;   guest ok = no
;   browseable = no
;   create mask = 0600
;   directory mask = 0700

[share]
   comment = Sonos Invader SMB
   path = /share
   browseable = yes
   writeable = Yes
   only guest = no
   create mask = 0777
   directory mask = 0777
   public = yes
   guest ok = yes
```

```
sudo smbpasswd -a pi
sudo /etc/init.d/samba restart
```

Clone this repo
```git clone https://github.com/Psychokiller1888/SnipsSonosInvader.git```

This project includes an assistant. I also shared the bundle Snips in case you want it for your already working assistant

```
sudo rm -r /usr/share/snips/assistant
sudo mv /home/pi/SnipsSonosInvader/assistant /usr/share/snips/assistant
sudo systemctl restart "snips*"
```

## Sonos configuration
On every player you have to add a library that points to your Raspberry. If your raspberry ip is "**192.168.1.150**" add a library on Sonos that points to "**//192.168.1.150/share**"


**!! Make sure that you name the sonos players the same as you name your Snips satellites !!**


## Let's start the demo script

Edit _sonosInvader.py_ and change

* On line 16: Set 'office' to 'the place this satellite is'. Exemple, my Snips device is running in my bedroom. My sonos unit there is also called bedroom, i'd set this to 'bedroom'

* On line 17: The language to use. Check pico2wave for available language. For french you'd use "fr-FR"

```
cd /home/pi/SnipsSonosInvader
sudo chmod +x snipsTalk.sh
python sonosInvader.py
```

At the begining Snips will talk to you through your internal speaker. Ask it for the time!

If you want it to use your Sonos when available, ask it to! "Hey Snips! Use my sonos!"

If you want it to stop using your Sonos, ask it! "Hey Snips! Stop using my sonos!"


## Troubleshooting

Make sure SnipsSonosInvader/snipsTalk.sh, after cloning the repo, has line endings set to LF
