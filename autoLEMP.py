#!/usr/bin/env python

#here is where we import the subprocess package
from subprocess import Popen, PIPE,check_output #docs -- https://docs.python.org/2/library/subprocess.html
import webbrowser #for checking to see if our website has installed Nginx
import os #pretty standard import for operating system

#now that we loaded the package
#lets define a function that we can send terminal commands to run
def runCommand(someCommand):
    """test function just to show we can work with the terminal"""
    print "Opening a terminal to execute: ",someCommand
    proc = Popen(someCommand,stdout=PIPE,shell=True) #True opens a terminal instance using a string input
    
def runLocalCommand(someCommand):
    """this function opens a terminal instance and executes 'someCommand' but only does it locally """
    print "Opening the terminal and using: ",someCommand
    #proc = Popen(someCommand,stdout=PIPE,shell=True) #True opens its own terminal
    proc = Popen(someCommand,shell=True)
    proc_stdout = proc.communicate()
    
    print proc_stdout

def runServerCommand(someCommand,user,whatIP):
    """this function adds the ssh user@server in front of the command to run instances on a server"""
    someCommand = "ssh -t "+user+"@"+whatIP+" '"+someCommand+"'"
    print "Opening the Server running: ",someCommand
    #proc = Popen(someCommand,stdout=PIPE,shell=True) #True opens its own terminal
    proc = Popen(someCommand,shell=True)
    proc_stdout = proc.communicate()[0]
    print proc_stdout


#################Now explode the simple use to the make our LEMP Stack automation

"""
HERE is the process --
#DISCLAIMER(s) -- if there are config files to edit -- which there are -- you are still going to have to refer to the tutorials
#to make sure you edit them correctly.  This is just automating the bash commands for you
#also, this tutorial is meant for LINUX/UNIX only and is not made for Windows

0. Obtain a VPS through Digital Ocean by making a Droplet - know your IP (you can also purchase a URL if you want)
1. Connect to your Digital Ocean server from the terminal using SSH
    -Tut = https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04
    -skip = steps Four (and Five) could be skipped but that means you will have to enter your server passwd 2X more
    
2. Now we try and install LEMP 
    -Tut = https://www.digitalocean.com/community/tutorials/how-to-install-linux-nginx-mysql-php-lemp-stack-in-ubuntu-16-04
    -skip =

3. Install Wordpress -- you 
    -Tut = https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-lemp-on-ubuntu-16-04
4. Do LetsEncrypt
    -Tut = https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04

"""

def connectToServer(userAccount,whatIP):
    bashCommand = 'ssh '+userAccount+'@'+whatIP+''
    runLocalCommand(bashCommand)

def doServerUpdates(user,whatIP):
    """Good practice to always update your Linux when you first login"""
    bash = 'sudo apt-get update && sudo apt-get upgrade'
    runServerCommand(bash,user,whatIP)
    

def doUpdates():
    """this can do local linux updates"""
    bash = 'sudo apt-get update && sudo apt-get upgrade'
    runLocalCommand(bash)
    
    
def makeSudoUser(newUserName,whatIP):
    """adds the new user and gives them Sudo permission"""
    makeNewUser = "adduser "+newUserName+""
    runServerCommand(makeNewUser,'root',whatIP)
    giveSudoPriv ="usermod -aG sudo "+newUserName+""
    runServerCommand(giveSudoPriv,'root',whatIP)


def generateKeys(user,whatIP):
    """ONLY DO THIS ONCE!!"""
    b0 = "ssh-keygen -R "+whatIP+""
    runLocalCommand(b0)
    
    b1 = 'ssh-keygen'
    runLocalCommand(b1)
    b2 = 'ssh-copy-id '+user+'@'+whatIP+''
    runLocalCommand(b2)
    
def setupFirewall(user,whatIP):
    bash1 = 'sudo ufw app list' #just shows an an app list
    bash2 = 'sudo ufw allow OpenSSH'
    bash3 = 'sudo ufw enable'
    bash4 = 'sudo ufw status'
    bashes = [bash1,bash2,bash3,bash4]

    for b in bashes:
        runServerCommand(b,user,whatIP) #run b run!!

def installNginx(user,whatIP):
    b1 = 'sudo apt-get update && sudo apt-get upgrade'
    b2 = 'sudo apt-get install nginx'
    b3 = "sudo ufw allow \'Nginx HTTP\'"
    b4 = 'sudo ufw status'
    #we know our domain IP -- so skip the icanhazip and the other one
    bashes = [b1,b2,b3,b4]
    for b in bashes:
        runServerCommand(b,user,whatIP) #run b run!!

    ###at this point you should be up and running
    ##you can test by going to http://yourIP_or_domainName
    b5 = "python -m webbrowser -t 'http://"+whatIP+"'"
    runLocalCommand(b5)
    
    
def installMySQL(user,whatIP):
    b1 = "sudo apt-get install mysql-server"
    b2 = "sudo mysql_secure_installation"
    ##enter "Y" and enter 0 for a low security password...
    ##enter "Y" to the rest of the questions
    bashes = [b1,b2]
    for b in bashes:
        runServerCommand(b,user,whatIP)

    
def installPHP(user,whatIP):
    """this takes some manual labor"""
    b1 = "sudo apt-get install php-fpm php-mysql"
    runServerCommand(b1,user,whatIP)
    b2 = "sudo apt-get install php-fpm php-mysql"
    runServerCommand(b2,user,whatIP)
    
    ##we need to configure the php.ini file manually by following
    ##Digital Ocean tutorial for /etc/php/7.0/fpm/php.ini
    b3 = "sudo nano /etc/php/7.0/fpm/php.ini"
    runServerCommand(b3,user,whatIP)

    b4 = "sudo systemctl restart php7.0-fpm"
    runServerCommand(b4,user,whatIP)


def configNginxPHP(user,whatIP):
    """this takes some manual labor"""
    b1 = "sudo nano /etc/nginx/sites-available/default"
    runServerCommand(b1,user,whatIP) #make the manual changes to config file

    #test Nginx to see if you did it right
    b2 = "sudo nano /etc/nginx/sites-available/default"
    runServerCommand(b2,user,whatIP)

    #restart Nginx
    b3 = "sudo systemctl reload nginx"
    runServerCommand(b3,user,whatIP)

def testInfoPHP(user,whatIP):
    b1 = "sudo nano /var/www/html/info.php"
    runServerCommand(b1,user,whatIP) #put in the PHP stuff from the tut

def checkForInfoPHP(user,whatIP):
    b1 = "python -m webbrowser -t 'http://"+whatIP+"/info.php'"
    runLocalCommand(b1)

def removeInfoPHP(user,whatIP):
    b1 = "sudo rm /var/www/html/info.php"
    runServerCommand(b1,user,whatIP)

def makeDBuser(user,whatIP):
    b1="mysql -u root -p"
    #db access stuff
    runServerCommand(b1,user,whatIP)

def nginxAndWP(user,whatIP):
    b1="sudo nano /etc/nginx/sites-available/default"
    #change the sever block
    runServerCommand(b1,user,whatIP)
    
    b2="sudo nginx -t"
    runServerCommand(b2,user,whatIP)
    b3="sudo systemctl reload nginx"
    runServerCommand(b3,user,whatIP)

    
def installPHPext(user,whatIP):
    b1 = "sudo apt-get update && sudo apt-get install php-curl php-gd php-mbstring php-mcrypt php-xml php-xmlrpc"
    runServerCommand(b1,user,whatIP)
    #restart php
    b2="sudo systemctl restart php7.0-fpm"
    runServerCommand(b2,user,whatIP)

def downloadWP(user,whatIP):
    b1 = "cd /tmp"
    b2 = "curl -O https://wordpress.org/latest.tar.gz"
    b3 = "tar xzvf latest.tar.gz"
    b4 = "cp /tmp/wordpress/wp-config-sample.php /tmp/wordpress/wp-config.php"
    b5 = "mkdir /tmp/wordpress/wp-content/upgrade"
    b6 = "sudo cp -a /tmp/wordpress/. /var/www/html"
    bashes = [b1,b2,b3,b4,b5,b6]
    for b in bashes:
        runServerCommand(b,user,whatIP)

def configWP(user,whatIP):
    b1 = "sudo chown -R sammy:www-data /var/www/html"
    b2 = "sudo find /var/www/html -type d -exec chmod g+s {} \;"
    b3 = "sudo chmod g+w /var/www/html/wp-content"
    b4 = "sudo chmod -R g+w /var/www/html/wp-content/themes"
    b5 = "sudo chmod -R g+w /var/www/html/wp-content/plugins"
    bashes = [b1,b2,b3,b4,b5]
    for b in bashes:
        runServerCommand(b,user,whatIP)
        
    b6 = "curl -s https://api.wordpress.org/secret-key/1.1/salt/"
    runServerCommand(b6,user,whatIP)
    #this is where you have to copy the keys
    b7 = "nano /var/www/html/wp-config.php"
    runServerCommand(b7,user,whatIP)

def finishWP(user,whatIP):
    b1 = "python -m webbrowser -t 'http://"+whatIP+""
    runLocalCommand(b1)

def runOnce(newUser,myIP):
    #first, we want to connect through SSH
    connectToServer('root',myIP)

    ###make a new user name and give them SUDO permissions
    newUser = newUser
    makeSudoUser(newUser,myIP)
    #generateKeys(newUser,myIP)
    
    ###test your sudo users access
    connectToServer(newUser,myIP) #try and login as superuser

    ##generate a key
    generateKeys(newUser,myIP)
    
    
def makeLEMP(newUser):
    """AUTOMATE MY LEMP install!!"""
    
    ###update the server
    doServerUpdates(newUser,myIP)
    
    ###make sure to setup the firewall
    setupFirewall(newUser,myIP)
    
    #second, we want to install all the requirements following the tut
    installNginx(newUser,myIP)
    installMySQL(newUser,myIP)
    installPHP(newUser,myIP) #you will need to do a manual part here for cgi.fix_pathinfo=0
    configNginxPHP(newUser,myIP) #some more manual entering
    testInfoPHP(newUser,myIP) #another manual enter for php
    checkForInfoPHP(newUser,myIP) #shows the info page
    removeInfoPHP(newUser,myIP) #dont forget to remove it

    #third, now we go for Wordpress and make a database user
    makeDBuser(newUser,myIP)
    nginxAndWP(newUser,myIP)
    installPHPext(newUser,myIP)
    downloadWP(newUser,myIP)
    configWP(newUser,myIP)
    finishWP(newUser,myIP)
    
    #if you are successful to this point -- this should work
    b1 = "python -m webbrowser -t 'http://"+myIP+"'"
    runLocalCommand(b1)


###first test
runCommand('cd ~/Desktop; ls; cd')
#if this worked you should see a list of whatever is on your desktop

    
###Globals
global myIP
global newUser
myIP = "YOUR IP ADD HERE"
newUser = "YOUR NEW USER NAME"

###Main Loop

#runOnce(newUser,myIP)

makeLEMP(newUser)
