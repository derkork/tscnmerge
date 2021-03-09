import os

from click import command, option, Path, Choice, BadParameter

from merging import merge_ext_resources, merge_nodes, merge_connections, merge_sub_resources
from model.TscnFile import TscnFile
from parsing import parse
from resolving import interactive, always_mine, always_theirs


@command()
@option('--local', '-l', type=Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
        help='The local file (aka MINE).', envvar='LOCAL', required=True)
@option('--remote', '-r', type=Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
        help='The remote file (aka THEIRS).', envvar='REMOTE', required=True)
@option('--merged', '-m', type=Path(writable=True), help='The path where to output the merged result. '
                                                         'If not given, the result is printed to stdout.',
        envvar='MERGED')
@option('--conflict-resolution', '-c', type=Choice(['mine', 'theirs', 'interactive']),
        default='interactive', show_default=True, help='Which version should be used in case of a conflict?')
def run(local, remote, merged, conflict_resolution):
    print("TSCN-Merge")
    print(f"local/MINE: {local}")
    print(f"remote/THEIRS: {remote}")

    mine: TscnFile = parse(local)
    theirs: TscnFile = parse(remote)
    result: TscnFile = TscnFile()
    result.gd_scene = mine.gd_scene

    resolver = interactive
    if conflict_resolution == "mine":
        resolver = always_mine
    if conflict_resolution == "theirs":
        resolver = always_theirs

    # Step 1: Merge external resources and consolidate IDs.
    merge_ext_resources(mine, theirs, result)
    # Step 2: Merge sub resources
    merge_sub_resources(mine, theirs, result, resolver)
    # Step 3: Merge the node trees
    merge_nodes(mine, theirs, result, resolver)
    # Step 4: Merge connections
    merge_connections(mine, theirs, result)

    if not merged:
        print(result.to_string())
    else:
        absolute_path = os.path.abspath(merged)
        directory, file_name = os.path.split(absolute_path)
        os.makedirs(directory, exist_ok=True)
        out_file = open(file_name, "w")
        out_file.write(result.to_string())
        out_file.close()

        print(f"Result written to {absolute_path}.")


if __name__ == '__main__':
    run()
