"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This module contains a few functions for manipulating and extracting information
from consituent parse trees.
"""

import os
from nltk.tree import ParentedTree

def add_depth(tree):
    """Adds a depth attribute to each node in the given tree, which is equal to
    the number of ancestors that node has.

    Args:
        tree: A ParentedTree object.
    """
    if not isinstance(tree, str):
        if tree.parent() is None:
            tree.depth = 0
        else:
            tree.depth = tree.parent().depth + 1
        for child in tree[:]:
            add_depth(child)

def get_path(i, j, tree, prune=True):
    """Retrieves the shortest path from leaf i to leaf j in the given tree.

    Nodes encountered while ascending the tree are given a suffix of '1', while
    nodes encounted while descending are given a suffix of '2'. The lowest
    common ancestor is given a suffix of '3'.
    
    If 'prune' is True, then any sequence of two or more of the same label will
    be collapsed into a single label.

    Args:
        i: The leaf-index of the first node.
        j: The leaf-index of the second node.
        tree: The ParentedTree to traverse.
        prune: If true, collapses sequences of the same label.
    Returns:
        The path from leaf i to leaf j, as a list.
        
    """
    i_tree_pos = tree.leaf_treeposition(i)
    j_tree_pos = tree.leaf_treeposition(j)
    i_node = tree[i_tree_pos[:-1]]
    j_node = tree[j_tree_pos[:-1]]
    i_path = []
    j_path = []

    # Move up from nodes i and j until the lowest common ancestor is reached.
    while i_node != j_node:
        if i_node.depth < j_node.depth:
            j_path.append(j_node.label() + '2')
            j_node = j_node.parent()
        elif i_node.depth > j_node.depth:
            i_path.append(i_node.label() + '1' )
            i_node = i_node.parent()
        else:
            i_path.append(i_node.label() + '1')
            i_node = i_node.parent()
            j_path.append(j_node.label() + '2')
            j_node = j_node.parent()
    i_path.append(i_node.label() + '0')
    j_path.reverse()
    full_path = i_path + j_path
    
    if prune:
        pruned_path = []
        for node in full_path:
            if pruned_path == []:
                pruned_path.append(node)
            elif not pruned_path[-1] == node:
                pruned_path.append(node)
        full_path = pruned_path

    return full_path
