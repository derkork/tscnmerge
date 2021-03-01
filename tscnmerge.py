import os

from click import command, option, Path, Choice

from merging import merge_external_resources, merge_nodes, merge_connections
from model.TscnFile import TscnFile
from parsing import parse
from resolving import interactive, always_mine, always_theirs


@command()
@option('--local', '-l', type=Path(exists=True, file_okay=True, dir_okay=False, readable=True),
        help='The local file (aka MINE).', envvar='LOCAL', required=True)
@option('--remote', '-r', type=Path(exists=True, file_okay=True, dir_okay=False, readable=True),
        help='The remote file (aka THEIRS).', envvar='REMOTE', required=True)
@option('--merged', '-m', type=Path(writable=True), help='The path where to output the merged result.',
        envvar='MERGED')
@option('--print-only', '-p', help='Only print merged result to stdout.')
@option('--conflict-resolution', '-c', type=Choice(['mine', 'theirs', 'interactive']),
        default='interactive', show_default=True, help='Which version should be used in case of a conflict?')
def run(local, remote, merged, print_only, conflict_resolution):
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
    merge_external_resources(mine, theirs, result)
    # Step 3: Merge the node trees
    merge_nodes(mine, theirs, result, interactive)
    # Step 4: Merge connections
    merge_connections(mine, theirs, result)

    if print_only:
        print(result.to_string())


if __name__ == '__main__':
    run()
