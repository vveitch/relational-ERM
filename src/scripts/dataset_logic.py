import numpy as np
import tensorflow as tf

from collections import namedtuple

from relational_sgd.graph_ops.representations import create_packed_adjacency_list, edge_list_to_adj_list
from relational_sgd.graph_ops.representations import PackedAdjacencyList


GraphData = namedtuple('GraphData', ['edge_list',
                                     'weights',
                                     'labels',
                                     'adjacency_list',
                                     'num_vertices',
                                     'num_labels'])


def load_data_node2vec(data_path=None):
    """ Loads any of
    1. homo sapiens
    2. wikipedia parts of speech
    3. blog catalog 3
    assumed to be preprocessed as undirected graphs according to scripts in data_processing

    Parameters
    ----------
    data_path: The path to the node 2 vec data file to load.

    Returns
    -------
    An instance of GraphData containing the parsed graph data for the dataset.
    """
    if data_path is None:
        data_path = '../data/homo_sapiens/homo_sapiens.npz'

    # data_path = '../data/blog_catalog_3/blog_catalog.npz'
    # data_path = '../../data/wikipedia_word_coocurr/wiki_pos.npz'

    # use tensorflow loading to support loading from
    # cloud providers
    with tf.gfile.Open(data_path, mode='rb') as f:
        loaded = np.load(f, allow_pickle=False)

    edge_list = loaded['edge_list'].astype(np.int32)

    if 'weights' in loaded:
        weights = loaded['weights'].astype(np.float32)
    else:
        weights = np.ones(edge_list.shape[0], dtype=np.float32)
    labels = loaded['group'].astype(np.float32)

    # Remove self-edges
    not_self_edge = edge_list[:, 0] != edge_list[:, 1]
    edge_list = edge_list[not_self_edge, :]
    weights = weights[not_self_edge]

    adjacency_list = edge_list_to_adj_list(edge_list, weights)

    num_vertices = len(adjacency_list)
    adjacency_list = create_packed_adjacency_list(adjacency_list)
    num_labels = labels.shape[1]

    return GraphData(edge_list, weights, labels, adjacency_list, num_vertices, num_labels)


def load_data_wikipedia_hyperlink(data_path=None):
    """ Load the wikipedia hyperlink data.

    Parameters
    ----------
    data_path: the path to the preprocessed dataset.
    """
    if data_path is None:
        data_path = '../data/wikipedia_hlink/wikipedia_hlink_preprocessed.npz'

    with tf.gfile.Open(data_path, mode='rb') as f:
        loaded = np.load(f, allow_pickle=True)

    neighbours = loaded['neighbours']
    lengths = loaded['lengths']

    offsets = np.empty_like(lengths)
    np.cumsum(lengths[:-1], out=offsets[1:])
    offsets[0] = 0

    adjacency_list = PackedAdjacencyList(neighbours, None, offsets, lengths, np.arange(len(lengths)))
    labels_sparse = loaded['sparse_labels'].astype(np.int32, copy=False)

    return {
        'adjacency_list': adjacency_list,
        'labels_sparse': labels_sparse
    }
