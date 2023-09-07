# Converts a .bril file to a .json file with `bril2json < NAME.bril > NAME.json`
# Usage: ./bril2json.sh NAME.bril

# Remove the .bril extension from the file name
NAME=${1%.bril}
bril2json < $1 > $NAME.json