# Iterate over all json files and run test on them
for f in *.json; do
    echo "Running 'turnt $f'"
    turnt $f
done