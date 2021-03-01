from typing import TypeVar, Generic

from model.Connection import Connection
from model.ExtResource import ExtResource
from model.Node import Node
from model.Value import Value

T = TypeVar("T")


class DiffResult(Generic[T]):
    def __init__(self, same: list[T], different: list[T], only_in_mine: list[T], only_in_theirs: list[T]):
        self.same: list[tuple[T, T]] = same
        self.different: list[tuple[T, T]] = different
        self.only_in_mine: list[T] = only_in_mine
        self.only_in_theirs: list[T] = only_in_theirs
        pass


class NodePartition:
    def __init__(self, nodes: list[tuple[Node or None, Node or None]], is_only_mine: bool, is_only_theirs: bool):
        assert len(nodes) > 0
        self.nodes: list[tuple[Node or None, Node or None]] = nodes
        self.is_only_mine: bool = is_only_mine
        self.is_only_theirs: bool = is_only_theirs


def diff_ext_resources(mine: list[ExtResource], theirs: list[ExtResource]) -> DiffResult[ExtResource]:
    # filter all in mine that have no match with the same path in theirs
    only_in_mine: list[ExtResource] = \
        list(filter(lambda it: next(filter(lambda it2: it2.path.is_same(it.path), theirs), None) is None, mine))
    # same thing, just reversed
    only_in_theirs: list[ExtResource] = \
        list(filter(lambda it: next(filter(lambda it2: it2.path.is_same(it.path), mine), None) is None, theirs))

    def mapping_function(from_mine: ExtResource) -> tuple[ExtResource, ExtResource] or None:
        from_theirs: ExtResource = next(filter(lambda it: it.path.is_same(from_mine.path), theirs), None)
        if from_theirs is not None:
            return from_mine, from_theirs
        return None

    # now repeat again to find things that are in both and build tuples out of them
    # each tuple has mine in the first spot and theirs in the second
    in_both: list[tuple[ExtResource, ExtResource]] = list(
        filter(lambda it: it is not None, map(mapping_function, mine)))

    # for the ones in both we need to see if they differ
    same: list[tuple[ExtResource, ExtResource]] = []
    different: list[tuple[ExtResource, ExtResource]] = []

    for pair in in_both:
        if pair[0].is_same(pair[1]):
            same.append(pair)
        else:
            different.append(pair)

    return DiffResult[ExtResource](same, different, only_in_mine, only_in_theirs)


def diff_node_properties(mine: Node, theirs: Node) -> DiffResult[tuple[str, Value]]:
    only_in_mine: list[tuple[str, Value]] = list(map(lambda key: (key, mine.get(key)),
                                                     mine.properties.keys() - theirs.properties.keys()))
    only_in_theirs: list[tuple[str, Value]] = list(map(lambda key: (key, theirs.get(key)),
                                                       theirs.properties.keys() - mine.properties.keys()))

    in_both: list[tuple[tuple[str, Value], tuple[str, Value]]] = \
        list(map(lambda key: ((key, mine.get(key)), (key, theirs.get(key))),
                 mine.properties.keys() & theirs.properties.keys()))

    same: list[tuple[tuple[str, Value], tuple[str, Value]]] = []
    different: list[tuple[tuple[str, Value], tuple[str, Value]]] = []

    for pair in in_both:
        if pair[0][1].is_same(pair[1][1]):
            same.append(pair)
        else:
            different.append(pair)

    return DiffResult[tuple[str, Value]](same, different, only_in_mine, only_in_theirs)


def diff_connections(mine: list[Connection], theirs: list[Connection]) -> DiffResult[Connection]:
    only_in_mine: list[Connection] = list(filter(lambda it: next(filter(lambda it2: it.is_same(it2),
                                                                        theirs), None) is None, mine))

    only_in_theirs: list[Connection] = list(filter(lambda it: next(filter(lambda it2: it.is_same(it2),
                                                                          mine), None) is None, theirs))

    def mapping_function(from_mine: Connection) -> tuple[Connection, Connection] or None:
        from_theirs: Connection = next(filter(lambda it: it.is_same(from_mine), theirs), None)
        if from_theirs is not None:
            return from_mine, from_theirs
        return None

    in_both: list[tuple[Connection, Connection]] = list(filter(lambda it: it is not None, map(mapping_function, mine)))

    # for connections it is special that connections that are in both are always identical, therefore we do not need
    # to filter the in_both list anymore.
    return DiffResult[Connection](in_both, [], only_in_mine, only_in_theirs)


def partition_nodes(mine: list[Node], theirs: list[Node]) -> list[NodePartition]:
    result: list[NodePartition] = []

    # We build ourselves a lookup table so we can quickly find out if a node exists on their side
    their_node_positions: dict[str, int] = {}

    for index, node in enumerate(theirs):
        their_node_positions[node.full_path_reference().to_string()] = index

    # Now we can walk the list and build partitions of nodes
    my_index = 0
    their_index = 0

    current_partition: list[tuple[Node or None, Node or None]] = []

    while True:
        assert len(current_partition) == 0

        if their_index >= len(theirs):
            # only nodes left on my side
            while my_index < len(mine):
                current_partition.append((mine[my_index], None))
                my_index += 1
            if len(current_partition) > 0:
                result.append(NodePartition(current_partition, True, False))
            # and no more nodes to do, so return here
            return result

        if my_index >= len(mine):
            # only nodes left on their side
            while their_index < len(mine):
                current_partition.append((None, theirs[their_index]))
                their_index += 1
            if len(current_partition) > 0:
                result.append(NodePartition(current_partition, False, True))
            # and no more nodes to do, so return here
            return result

        assert my_index < len(mine) and their_index < len(theirs)
        assert len(current_partition) == 0

        while mine[my_index].full_path_reference().is_same(theirs[their_index].full_path_reference()):
            # While the nodes we look at represent the same path, group them together
            current_partition.append((mine[my_index], theirs[their_index]))
            my_index += 1
            their_index += 1
            if my_index >= len(mine) or their_index >= len(theirs):
                break

        # once we exit from the previous loop, there may be a partition of matching nodes which we add
        if len(current_partition) > 0:
            result.append(NodePartition(current_partition, False, False))
            current_partition = []

        assert len(current_partition) == 0

        # Check if we still have a valid index on both sides
        if my_index < len(mine) and their_index < len(theirs):
            # Nodes do not match anymore. So we need to find out which side to advance.

            node_index_on_their_side = their_node_positions.get(mine[my_index].full_path_reference().to_string(), None)
            while node_index_on_their_side is None:
                # the node on my side is unique and has no equivalent in their tree, so we add it
                # and keep adding nodes until we have found a node that has a counterpart on their side
                current_partition.append((mine[my_index], None))
                my_index += 1
                if my_index >= len(mine):
                    break

                node_index_on_their_side = \
                    their_node_positions.get(mine[my_index].full_path_reference().to_string(), None)

            # Finish the partition of nodes only on my side, if it exists
            if len(current_partition) > 0:
                result.append(NodePartition(current_partition, True, False))
                current_partition = []

            if node_index_on_their_side is not None:
                assert node_index_on_their_side > their_index
                # we have a matching node on their side, so now make a partition with all nodes
                # on their side until we hit the matching index.
                while their_index < node_index_on_their_side:
                    current_partition.append((None, theirs[their_index]))
                    their_index += 1
                    assert their_index < len(theirs)

                result.append(NodePartition(current_partition, False, True))
                current_partition = []

            # at this point either my side has run out of nodes or the indices point to two matching nodes
            assert my_index >= len(mine) or \
                   mine[my_index].full_path_reference().is_same(theirs[their_index].full_path_reference())
