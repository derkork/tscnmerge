from collections import Callable

from diffing import DiffResult, diff_ext_resources, diff_node_properties, NodePartition, partition_nodes, \
    diff_connections
from model.Connection import Connection
from model.ExtResource import ExtResource
from model.ExtResourceReference import ExtResourceReference
from model.Node import Node
from model.NumericValue import NumericValue
from model.Printable import Printable
from model.TscnFile import TscnFile
from model.Value import Value
from resolving import Resolution


def merge_external_resources(mine: TscnFile, theirs: TscnFile, result: TscnFile):
    # IDs do not need to be contiguous, they just need to be unique, so we try to
    # reuse as many IDs as we can and then give new IDs.
    max_known_resource_id = 1

    resource_diff: DiffResult[ExtResource] = diff_ext_resources(mine.ext_resources, theirs.ext_resources)

    # first, all resources that are identical, can keep their resource ids
    # this way we will not  make this more confusing than it needs to be.
    for my_resource, _ in resource_diff.same:
        # since my_resource and their_resource are identical we just use my_resource
        item_id = my_resource.id.to_int()
        if item_id > max_known_resource_id:
            max_known_resource_id = item_id
        result.ext_resources.append(my_resource)

    # All other items that are somehow different will get new resource ids
    # assigned.

    # noinspection PyShadowingNames
    def make_new_resource_and_reference(old: ExtResource, id: int) -> tuple[ExtResource, ExtResourceReference]:
        new_resource_id = NumericValue(str(id))
        new_resource_reference = ExtResourceReference(new_resource_id)
        new_resource = ExtResource(old.type, new_resource_id, old.path)
        return new_resource, new_resource_reference

    # First the ones that exist in both but have gotten different ids
    for my_resource, their_resource in resource_diff.different:
        assert my_resource.type.is_same(their_resource.type), "Cannot merge resources with same path and different type"

        # We need to fix the references in both files to a new id
        max_known_resource_id += 1
        new_resource, new_resource_reference = make_new_resource_and_reference(my_resource, max_known_resource_id)

        mine.refactor_external_reference(ExtResourceReference(my_resource.id), new_resource_reference)
        theirs.refactor_external_reference(ExtResourceReference(their_resource.id), new_resource_reference)

        # Now build a new resource with the path and type, but use the new id
        # And add that to the result
        result.ext_resources.append(new_resource)

    # Now the ones that only exist in mine
    for my_resource in resource_diff.only_in_mine:
        max_known_resource_id += 1
        new_resource, new_resource_reference = make_new_resource_and_reference(my_resource, max_known_resource_id)

        mine.refactor_external_reference(ExtResourceReference(my_resource.id), new_resource_reference)
        result.ext_resources.append(new_resource)

    # And the ones that only exist in theirs
    for their_resource in resource_diff.only_in_theirs:
        max_known_resource_id += 1
        new_resource, new_resource_reference = make_new_resource_and_reference(their_resource, max_known_resource_id)

        theirs.refactor_external_reference(ExtResourceReference(their_resource.id), new_resource_reference)
        result.ext_resources.append(new_resource)


def merge_nodes(mine: TscnFile, theirs: TscnFile, result: TscnFile,
                resolution: Callable[[str, Printable, Printable], Resolution]):
    # We start at the root node and work down the tree of each file
    # we tree to keep node order as is as far as possible.

    assert len(mine.nodes) > 0, "MINE file has no node. This is invalid."
    assert len(theirs.nodes) > 0, "THEIRS file has no node. This is invalid."

    # Now we need to partition up the nodes so we can do a comparison between them and start the merging
    partitions: list[NodePartition] = partition_nodes(mine.nodes, theirs.nodes)

    # Now we can walk the partitions and merge if necessary
    for partition in partitions:
        if partition.is_only_mine:
            # node exists only on my side, so we can just add it to the result
            for my_node, _ in partition.nodes:
                result.nodes.append(my_node)

        elif partition.is_only_theirs:
            # node exists only on their side, so we can just add it to the result
            for _, their_node in partition.nodes:
                result.nodes.append(their_node)

        else:
            # node exists on both sides and we need to merge it
            for my_node, their_node in partition.nodes:
                if not my_node.represents_same_thing(their_node):
                    # If the two nodes represent different things, there is no way to merge them as the properties are
                    # dependent on the type of the node and therefore merging properties of two different
                    # types together just makes not any sense. Therefore in this case the only thing
                    # we can do is ask which of the both nodes we would like to have.

                    decision = resolution("The same node has different types/scripts. "
                                          "This cannot be merged. Which node should I take?", my_node, their_node)

                    if decision == Resolution.MINE:
                        result.nodes.append(my_node)
                    elif decision == Resolution.THEIRS:
                        result.nodes.append(their_node)
                    else:
                        assert False, "Unexpected input."
                else:
                    # The nodes represent the same thing. Now we can compare their properties and build a result node.
                    result_node = Node(my_node.type, my_node.name, my_node.parent, my_node.instance)

                    properties: DiffResult[tuple[str, Value]] = diff_node_properties(my_node, their_node)

                    # Stuff that is same in both nodes, goes to the result
                    for (key, value), _ in properties.same:
                        result_node.set(key, value)

                    # Stuff that is in my node only, also goes into the result
                    for key, value in properties.only_in_mine:
                        result_node.set(key, value)

                    # Stuff that is in their node only, also goes into the result
                    for key, value in properties.only_in_theirs:
                        result_node.set(key, value)

                    # Stuff that is different in both needs to be decided upon
                    for (key, my_value), (_, their_value) in properties.different:
                        decision = resolution(f"Node {result_node.full_path_reference().to_string()} -> "
                                              f"Property \"{key}\" is different in both sides. "
                                              f"Which one should I take?",
                                              my_value, their_value)

                        if decision == Resolution.MINE:
                            result_node.set(key, my_value)
                        elif decision == Resolution.THEIRS:
                            result_node.set(key, their_value)
                        else:
                            assert False, "Unexpected input."

                    result.nodes.append(result_node)


def merge_connections(mine: TscnFile, theirs: TscnFile, result: TscnFile):
    connection_diff: DiffResult[Connection] = diff_connections(mine.connections, theirs.connections)

    assert len(connection_diff.different) == 0

    # connections is really easy, we basically just need to avoid having duplicates, which the diffing process
    # solves already, so we can just insert mine, theirs and both

    for connection, _ in connection_diff.same:
        result.connections.append(connection)

    for connection in connection_diff.only_in_mine:
        result.connections.append(connection)

    for connection in connection_diff.only_in_theirs:
        result.connections.append(connection)


