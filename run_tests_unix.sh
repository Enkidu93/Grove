#!/bin/bash

set -u

py="python3"
$py check_errors.py
totalPoints=$?

echo "Checking results from single-line expressions..."
possiblePoints=0
points=0
while read -u 6 -r theInput && read -u 7 -r correctOutput; do

    (( possiblePoints++ ))
    
    echo -e "$theInput\nquit\n" | $py grove.py >& output.txt
    output=$(cat output.txt | sed -e "s/Grove>>[[:space:]]\+//g")
    if [[ "$output" != "$correctOutput" ]]
    then
	echo "Incorrect output; details follow..."
	echo "      Input was:          $theInput"
        echo "      Correct output was: $correctOutput"
        echo "      Your output was:    $output"
        echo ""
        diff  <(echo "$output" ) <(echo "$correctOutput")
    else
	(( points++ ))
    fi
    
done 6<singles.txt  7<singles_answers.txt

echo -e "\n*** EARNED $points out of $possiblePoints for the single-line expressions\n\n"

(( totalPoints += points ))



echo "Checking results from single-line statements..."
possiblePoints=0
points=0
while read -u 6 -r theInput; do

    (( possiblePoints++ ))
    
    echo -e "$theInput\nquit\n" | $py grove.py >& output.txt

    output=$(cat output.txt | sed -e "s/Grove>>[[:space:]]\+//g")
    if [[ "$output" != "" ]]
    then
	echo "There should be no output for the statement ${theInput}"
        echo "but your output was: $output"
    else
	(( points++ ))
    fi
    
done 6<single_stmts.txt

echo -e "\n*** EARNED $points out of $possiblePoints for the single-line statements\n\n"
(( totalPoints += points ))


for i in 1 2 3 4 5 6
do
    inFile=test${i}.txt
    echo "Checking ${inFile}..."
    
    cat ${inFile} | $py grove.py >& output.txt

    cat output.txt | sed -e "s/Grove>>[[:space:]]\+//g" > cleanOutput.txt

    echo "(correct answer on left, yours on the right)"
    diff -b -y answer${i}.txt cleanOutput.txt
    res=$?

    possiblePoints=6
    if (( res == 0 ))
    then
	points=${possiblePoints}
    else
	points=0
    fi
    
    echo -e "\n*** EARNED $points out of $possiblePoints for ${inFile}\n\n"
    (( totalPoints += points ))
    
done

echo "$totalPoints total points"

echo "{\"scores\" : {\"all\": ${totalPoints} } }"
