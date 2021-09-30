#!/bin/bash

poetry build
zipfile=$(aga gen "$1")

docker run --rm -it                                             \
  -v "$PWD"/"$zipfile":/tmp/autograder.zip                      \
  -v "$PWD"/dist/aga-0.2.0.tar.gz:/autograder/aga/aga.tar.gz    \
  -v "$PWD"/"$2":/autograder/submission/"$1".py                 \
  gradescope/auto-builds bash -c "
bash -c '
set -e

apt-get update

apt-get install -y curl unzip dos2unix 

mkdir -p /autograder/source /autograder/results 

unzip -n -d /autograder/source /tmp/autograder.zip 

cp /autograder/source/run_autograder /autograder/run_autograder 

dos2unix /autograder/run_autograder /autograder/source/setup.sh 

chmod +x /autograder/run_autograder 
apt-get update 

bash /autograder/source/setup.sh 
apt-get clean 
rm -rf /var/lib/apt/lists/* /var/tmp/* 

/autograder/run_autograder 
cat /autograder/results/results.json
'
bash
"
