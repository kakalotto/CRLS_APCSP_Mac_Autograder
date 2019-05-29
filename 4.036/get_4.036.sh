#!/bin/bash
LAB=4.036
#cd /home/ewu/PycharmProjects/untitled/$LAB
cd /Users/teacher/PycharmProjects/untitled/$LAB
#/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list -m 0 --query " name contains '2018' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  " |grep $LAB\.py |awk '{print $1}' > /tmp/blah.$$
/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list -m 0 --query " name contains '2019' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  and 'me' in owners " |grep $LAB\.py |awk '{print $1}' > /tmp/blah.$$


if [ $# -eq 0 ]
then
/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list  -m 0 --query " name contains '2019' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  and 'me' in owners " |grep $LAB\.py |awk '{print $1}' > /tmp/blah.$$
else
/usr/local/Cellar/gdrive/2.1.0/bin/gdrive  list -m 0 --query " name contains '2019' and modifiedTime > '2018-09-01T00:00:00' and fullText contains '.py'  and 'me' in owners " |grep $LAB\.py |grep $1| awk '{print $1}' > /tmp/blah.$$    
fi

while IFS= read -r line;
do
    /usr/local/Cellar/gdrive/2.1.0/bin/gdrive  download $line
done < "/tmp/blah.$$"
