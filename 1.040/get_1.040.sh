#!/bin/bash
LAB=1.040
cd /Users/teacher/PycharmProjects/untitled/$LAB 
/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list -m 0 --query " name contains '2018' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  " |grep $LAB\.py |awk '{print $1}' > /tmp/blah.$$
/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list -m 0 --query " name contains '2019' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  " |grep $LAB\.py |awk '{print $1}' > /tmp/blah.$$

while IFS= read -r line;
do
   $HOME/bin/gdrive_download.sh $line
   sleep 2
done < "/tmp/blah.$$"
