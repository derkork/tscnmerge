from collections import Callable

from diffing import DiffResult, diff_ext_resources, diff_bag_properties, NodePartition, partition_nodes, \
    diff_connections, diff_sub_resources
from model.Connection import Connection
from model.ExtResource import ExtResource
from model.ExtResourceReference import ExtResourceReference
from model.Node import Node
from model.NumericValue import NumericValue
from model.Printable import Printable
from model.SubResource import SubResource
from model.SubResourceReference import SubResourceReference
from model.TscnFile import TscnFile
from model.Value import Value
from resolving import Resolution


def merge_ext_resources(mine: TscnFile, theirs: TscnFile, result: TscnFile):

    resource_diff: DiffResult[ExtResource] = diff_ext_resources(mine.ext_resources, theirs.ext_resources)

    # first, all resources that are identical, can keep their resource ids
    # this way we will not  make this more confusing than it needs to be.
    for my_resource, _ in resource_diff.same:
        # since my_resource and their_resource are identical we just use my_resource
        result.ext_resources.append(my_resource)

    # Now we need a safe new id range so we don't get clashes between ids in the old and new file.
    max_known_resource_id = max(map(lambda it: it.id.to_int(), mine.ext_resources + theirs.ext_resources))

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

        mine.refactor_ext_resource_reference(my_resource.to_reference(), new_resource_reference)
        theirs.refactor_ext_resource_reference(their_resource.to_reference(), new_resource_reference)

        # Now build a new resource with the path and type, but use the new id
        # And add that to the result
        result.ext_resources.append(new_resource)

    # Now the ones that only exist in mine
    for my_resource in resource_diff.only_in_mine:
        max_known_resource_id += 1
        new_resource, new_resource_reference = make_new_resource_and_reference(my_resource, max_known_resource_id)

        mine.refactor_ext_resource_reference(my_resource.to_reference(), new_resource_reference)
        result.ext_resources.append(new_resource)

    # And the ones that only exist in theirs
    for their_resource in resource_diff.only_in_theirs:
        max_known_resource_id += 1
        new_resource, new_resource_reference = make_new_resource_and_reference(their_resource, max_known_resource_id)

        theirs.refactor_ext_resource_reference(their_resource.to_reference(), new_resource_reference)
        result.ext_resources.append(new_resource)


def merge_sub_resources(mine: TscnFile, theirs: TscnFile, result: TscnFile,
                        resolution: Callable[[str, Printable, Printable], Resolution]):
    # We'll start by giving all resources unique ids across files, as this makes our life a lot easier.
    resource_id: int = 1
    for resource in mine.sub_resources:
        mine.refactor_sub_resource_reference(resource.to_reference(),
                                             SubResourceReference(NumericValue(str(resource_id))))
        resource_id += 1

    for resource in theirs.sub_resources:
        theirs.refactor_sub_resource_reference(resource.to_reference(),
                                               SubResourceReference(NumericValue(str(resource_id))))
        resource_id += 1

    resource_diff: DiffResult[SubResource] = diff_sub_resources(mine, theirs)

    # Stuff that is only in mine, can be simply copied over (and since IDs are unique now we don't have to fix anything)
    for my_resource in resource_diff.only_in_mine:
        result.sub_resources.append(my_resource)

    # Same for stuff that is only in theirs.
    for my_resource in resource_diff.only_in_theirs:
        result.sub_resources.append(my_resource)

    # Stuff that is in both, can be copied over however we need to replace the losing ID.
    for my_resource, their_resource in resource_diff.same:
        result.sub_resources.append(my_resource)

        # and we need to fix up the losing id in their file
        # AND the result file (as we may have references copied over there)
        theirs.refactor_sub_resource_reference(their_resource.to_reference(), my_resource.to_reference())
        result.refactor_sub_resource_reference(their_resource.to_reference(), my_resource.to_reference())

    # Now to resources that are different
    for my_resource, their_resource in resource_diff.different:
        if not my_resource.represents_same_thing(their_resource):
            # If the two resources represent different things, there is no way to merge them as the properties are
            # dependent on the type of the resource and therefore merging properties of two different
            # types together just makes not any sense. Therefore in this case the only thing
            # we can do is ask which of the both resources we would like to have.

            decision = resolution("The same resource has different types. "
                                  "This cannot be merged. Which node should I take?", my_resource, their_resource)
            if decision == Resolution.MINE:
                result.sub_resources.append(my_resource)
                theirs.refactor_sub_resource_reference(their_resource.to_reference(), my_resource.to_reference())
                result.refactor_sub_resource_reference(their_resource.to_reference(), my_resource.to_reference())
            elif decision == Resolution.THEIRS:
                result.sub_resources.append(their_resource)
                mine.refactor_sub_resource_reference(my_resource.to_reference(), their_resource.to_reference())
                result.refactor_sub_resource_reference(my_resource.to_reference(), their_resource.to_reference())
            else:
                assert False, "Unexpected input."

        else:
            # The resources represent the same thing. Now we can compare their properties and build a result resource.
            result_resource = SubResource(my_resource.type, NumericValue(str(resource_id)))
            resource_id += 1
            properties: DiffResult[tuple[str, Value]] = diff_bag_properties(my_resource, their_resource)

            # Stuff that is same in both resources, goes to the result
            for (key, value), _ in properties.same:
                result_resource.set_property(key, value)

            # Stuff that is in my node only, also goes into the result
            for key, value in properties.only_in_mine:
                result_resource.set_property(key, value)

            # Stuff that is in their node only, also goes into the result
            for key, value in properties.only_in_theirs:
                result_resource.set_property(key, value)

            # Stuff that is different in both needs to be decided upon
            for (key, my_value), (_, their_value) in properties.different:
                decision = resolution(f"SubResource {result_resource.type.to_string()} -> "
                                      f"Property \"{key}\" is different in both sides. "
                                      f"Which one should I take?",
                                      my_value, their_value)

                if decision == Resolution.MINE:
                    result_resource.set_property(key, my_value)
                elif decision == Resolution.THEIRS:
                    result_resource.set_property(key, their_value)
                else:
                    assert False, "Unexpected input."

            result.sub_resources.append(result_resource)
            # since we dropped both resources, we need to fix up the resource everywhere
            mine.refactor_sub_resource_reference(my_resource.to_reference(), result_resource.to_reference())
            theirs.refactor_sub_resource_reference(their_resource.to_reference(), result_resource.to_reference())
            result.refactor_sub_resource_reference(my_resource.to_reference(), result_resource.to_reference())
            result.refactor_sub_resource_reference(their_resource.to_reference(), result_resource.to_reference())

    # finally, the resources must be ordered such that we have no forward references
    available_resources: set[SubResourceReference] = set()
    sorted_resources: list[SubResource] = []
    remaining_resources: list[SubResource] = list(result.sub_resources)

    while len(remaining_resources) > 0:
        had_progress = False
        index = 0
        while index < len(remaining_resources):
            references: set[SubResourceReference] = set()
            remaining_resources[index].find_all_sub_resource_references(references)
            if available_resources.issuperset(references):
                # all the referenced resources are known, so we can put
                # this into sorted
                sorted_resources.append(remaining_resources[index])
                del (remaining_resources[index])
                had_progress = True
            else:
                index += 1
        assert had_progress, "Either we have a circular reference or this is buggy."

    result.sub_resources = sorted_resources


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
                    result_node = Node(my_node.type, my_node.name, my_node.parent, my_node.instance,
                                       my_node.instance_placeholder)

                    properties: DiffResult[tuple[str, Value]] = diff_bag_properties(my_node, their_node)

                    # Stuff that is same in both nodes, goes to the result
                    for (key, value), _ in properties.same:
                        result_node.set_property(key, value)

                    # Stuff that is in my node only, also goes into the result
                    for key, value in properties.only_in_mine:
                        result_node.set_property(key, value)

                    # Stuff that is in their node only, also goes into the result
                    for key, value in properties.only_in_theirs:
                        result_node.set_property(key, value)

                    # Stuff that is different in both needs to be decided upon
                    for (key, my_value), (_, their_value) in properties.different:
                        decision = resolution(f"Node {result_node.full_path_reference().to_string()} -> "
                                              f"Property \"{key}\" is different in both sides. "
                                              f"Which one should I take?",
                                              my_value, their_value)

                        if decision == Resolution.MINE:
                            result_node.set_property(key, my_value)
                        elif decision == Resolution.THEIRS:
                            result_node.set_property(key, their_value)
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
