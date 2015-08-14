sort debconf-get-selections

I wanted to tune the seed files I send to the debian pre-seed process.  

brief instructions to sort and collate debconf output:
* apt-get install debconf-utils
* debconf-get-selections --installer > seed.txt
* debconf-get-selections >> seed.txt
* cat seed.txt | python seed.sort.py

debconf-get-selections randomizes the output.  my program helps to sort the output into something meaningful.

a bit more info at:  
http://blog.raymond.burkholder.net/index.php?/archives/637-DebConf-Debian-Installer-Preseed.html
