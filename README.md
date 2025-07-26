# se-vote-tally

Not very useful for general purpose. Stack Exchange mods get a vote history page that shows a user's voting interactions with other "top users", whatever that means. This script just tallies those for the purpose of doing more detailed stats.

Data under the `src/data` folder is gitignored, except for the `templates` folder.

## To use

1. Copy the given and/or received templates into `src/data` and name with the user ID you want to name. Keep the `-given` and `-received` suffix(es). Open these in the [Edit CSV extension](https://marketplace.visualstudio.com/items?itemName=janisdd.vscode-edit-csv).

2. Go to the vote history page for that user. Copy the whole table for given or received. (Not in one copy; must be done separately.)

3. Paste the data into the second row of the csv.

4. Remove the 5th column. Its line breaks screw things up.

5. Run the script and provide the username.

Note: Delimiters and quote characters may be different on your system. I use 64-bit Win 11 in French. ¯\\\_(ツ)_/¯ At this stage you'll have to edit the code to alter it.

Note also: Most of the stats are implied, but the model is fairly complete. Add code to run stats on it as desired. My goal here was to find out, for users such as Anne and Bristol, how many of the total downvotes Anne received were given by Bristol. This is not available from the mod page itself.
