# TSCN-Merge

This is a utility to merge scene files of the Godot game engine. It can be used manually and as a merge tool for Git.

## How does it merge?
The utility tries to preserve as much information from both scenes as possible. Only if the scene structures conflict with each other you will need to make a decision which version you want. So in a sense you will always get the _union_ of both scenes. Later versions may support a three-way merge, so the tool can make a better decision about what changed and give you more options to control the merge process. 

## What works
- Two-way merge using two scene files.
- Merges of referenced external resources.
- Fixing references to external resources in the resulting merge file.
- Merges of node trees.
- Merges of node properties.
- Interactive merging.

## What doesn't work
- Merges of signal connections.
- Merges of internal resources.
- Three-way merge using a common base.