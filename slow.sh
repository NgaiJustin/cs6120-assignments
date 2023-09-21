#!/bin/bash

# first argument is the number of times to repeat each frame
REPEATS=$1

# second argument is the input file
INPUT_FILE=$2

# output file name is the input_file name with "-slow" appended before the extension
OUTPUT_FILE=$(echo $INPUT_FILE | sed 's/\(.*\)\.\(.*\)/\1-slow.\2/')

# 1. get input frame count (note two spaces after the "\")
count=$(gifsicle --info < $INPUT_FILE | grep "<stdin>" | cut -d\  -f 3)

# 2. define how many times to repeat frames
repeats=$REPEATS

# 3. construct new frame list
frames=$(for i in $(seq 0 $((count - 1)))
    do 
        for j in $(seq $((repeats)))
            do echo "#$i"
        done
    done
)

# 4. use gifsicle to duplicate frames (note no quotes around $frames)
gifsicle < $INPUT_FILE $frames > $OUTPUT_FILE


# Source: https://graphicdesign.stackexchange.com/questions/137443/duplicate-frames-in-animated-gif