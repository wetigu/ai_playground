#!/bin/bash
if [ $# -ne 3 ];then
 echo "$0 user pass dbname"
 exit 99
fi
username=$1
password=$2
db=$3
sql=$(cat<<eof
CREATE USER '$username'@'%' IDENTIFIED BY '$password';
GRANT ALL PRIVILEGES ON $db.* TO '$username'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
eof
)
echo $sql
sudo mysql mysql<<<$sql
