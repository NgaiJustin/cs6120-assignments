# Converts a .bril file to a .json file with `bril2json < NAME.bril > NAME.json`
# Usage: ./bril2json.sh NAME.bril

# If no argument is given, more than one argument is given, or argument is 
# not a .bril file print usage message
if [ $# -ne 1 ] || [ ! -f $1 ] || [ ${1: -5} != ".bril" ]; then
    echo "Usage: ./bril2json.sh NAME.bril"
    exit 1
fi

# Remove the .bril extension from the file name
NAME=${1%.bril}
bril2json < $1 > $NAME.json