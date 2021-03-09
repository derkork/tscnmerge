# tscnmerge

This is a utility to merge scene files of the Godot game engine. It can be used manually and as a merge tool for Git.

## How does it merge?
The utility tries to preserve as much information from both scenes as possible. Only if the scene structures conflict with each other you will need to make a decision which version you want. So in a sense you will always get the _union_ of both scenes. Later versions may support a three-way merge, so the tool can make a better decision about what changed and give you more options to control the merge process. 

## How to use it
You can either use it directly on the command line or as a git merge tool. First download the latest version from the releases and place it somewhere on your computer.

### Using tscnmerge as a command line tool
```
tscnmerge --local path/to/your_version.tscn 
          --remote path/to/their_version.tscn
          --merged path/to/where_the_result_should_be_written.tscn
```

You can also call 

```
tscnmerge --help
```
to get information about all the parameters.

### Using tscnmerge as a git merge tool

If you want to use it as a git merge tool simply add the following to your `.git/config` file. The path will differ depending on your operating system. So e.g. on Windows you would add something like this:
```
[mergetool "tscnmerge"]
  cmd = d:/tools/tscnmerge/tscnmerge.exe -l \"$LOCAL\" -r \"$REMOTE\" -m \"$MERGED\"
```

While on Linux or OSX you would add something like that:
```
[mergetool "tscnmerge"]
  cmd = /Users/derkork/tools/tscnmerge/tscnmerge -l \"$LOCAL\" -r \"$REMOTE\" -m \"$MERGED\"
```

Then you can merge a file with conflicts quite simply using:

```
git mergetool --tool=tscnmerge scene_with_conflicts.tscn
```

This will start an interactive merge process using tscnmerge.


## What works
- Two-way merge using two scene files.
- Merges of referenced external resources.
- Fixing references to external resources in the resulting merge file.
- Merges of node trees.
- Merges of node properties.
- Interactive merging.
- Merges of signal connections.
- Merges of internal resources.

## What doesn't work
- Three-way merge using a common base.