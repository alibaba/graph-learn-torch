# Copyright 2022 Alibaba Group Holding Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
import unittest

# TODO(hongyi): load data into vineyard from file

os.environ["socket"] = '/var/run/vineyard.sock'
os.environ["fid"] = '26586469478206803'

from graphlearn_torch.data import *
from graphlearn_torch.distributed import DistDataset

try:
    import vineyard
except ImportError:
    vineyard = None


@unittest.skipIf(not vineyard, "only test with vineyard")
class VineyardDatasetTest(unittest.TestCase):

  def setUp(self):
    self.sock = os.environ["socket"]
    self.fid = os.environ["fid"]
    self.homo_edges = [
      ("person", "knows", "person"),
    ]
    self.homo_edge_weights = {
      ("person", "knows", "person"): "weight",
    }
    self.homo_node_features = {
      "person": ["feat0", "feat1"],
    }
    self.homo_edge_features = {
      ("person", "knows", "person"): ["feat0", "feat1"],
    },
    self.node_labels = {
      "person": "label",
    }

    self.hetero_edges = [
      ("person", "knows", "person"),
      ("person", "created", "software"),
    ]
    self.hetero_edge_weights = {
      ("person", "knows", "person"): "weight",
      ("person", "created", "software"): "weight",
    }
    self.hetero_node_features = {
      "person": ["feat0", "feat1"],
      "software": ["feat0"],
    }
    self.hetero_edge_features = {
      ("person", "knows", "person"): ["feat0", "feat1"],
      ("person", "created", "software"): ["feat0"],
    }

  def test_homo_dataset(self):
    ds = Dataset()
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.homo_edges,
      edge_weights=self.homo_edge_weights,
      node_features=self.homo_node_features,
      edge_features=self.homo_edge_features,
      node_labels=self.node_labels,
    )
    self.assertEqual(ds.graph.row_count, 4)
    self.assertEqual(ds.graph.col_count, 2)
    self.assertEqual(ds.graph.edge_count, 2)
    self.assertEqual(ds.graph.topo.edge_weights.shape, (2,))
    self.assertEqual(ds.node_features.shape, (4, 2))
    self.assertEqual(ds.edge_features.shape, (2, 2))
    self.assertEqual(ds.node_labels.shape, (4,))

  def test_in_homo_dataset(self):
    ds = Dataset(edge_dir="in")
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.homo_edges,
    )
    self.assertEqual(ds.graph.row_count, 4)
    self.assertEqual(ds.graph.col_count, 1)
    self.assertEqual(ds.graph.edge_count, 2)

  def test_hetero_dataset(self):
    ds = Dataset()
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.hetero_edges,
      edge_weights=self.hetero_edge_weights,
      node_features=self.hetero_node_features,
      edge_features=self.hetero_edge_features,
      node_labels=self.node_labels,
    )
    graph1 = ds.graph[("person", "knows", "person")]
    graph2 = ds.graph[("person", "created", "software")]
    self.assertEqual(graph1.row_count, 4)
    self.assertEqual(graph1.col_count, 2)
    self.assertEqual(graph1.edge_count, 2)
    self.assertEqual(graph1.topo.edge_weights.shape, (2,))

    self.assertEqual(graph2.row_count, 4)
    self.assertEqual(graph2.col_count, 2)
    self.assertEqual(graph2.edge_count, 4)
    self.assertEqual(graph2.topo.edge_weights.shape, (4,))

    self.assertEqual(ds.node_features["person"].shape, (4, 2))
    self.assertEqual(ds.node_features["software"].shape, (2, 1))
    self.assertEqual(
      ds.edge_features[("person", "knows", "person")].shape, (2, 2)
    )
    self.assertEqual(
      ds.edge_features[("person", "created", "software")].shape, (4, 1)
    )
    self.assertEqual(ds.node_labels["person"].shape, (4,))

  def test_in_hetero_dataset(self):
    ds = Dataset(edge_dir="in")
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.hetero_edges,
    )
    graph1 = ds.graph[("person", "knows", "person")]
    graph2 = ds.graph[("person", "created", "software")]

    self.assertEqual(graph1.row_count, 4)
    self.assertEqual(graph1.col_count, 1)
    self.assertEqual(graph1.edge_count, 2)

    self.assertEqual(graph2.row_count, 2)
    self.assertEqual(graph2.col_count, 3)
    self.assertEqual(graph2.edge_count, 4)

  def test_homo_dist_dataset(self):
    ds = DistDataset()
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.homo_edges,
      node_features=self.homo_node_features,
      edge_features=self.homo_edge_features,
      node_labels=self.node_labels,
    )
    self.assertEqual(ds.node_pb.shape, (4,))
    self.assertEqual(ds.edge_pb.shape, (2,))
    self.assertEqual(ds.node_feat_pb.shape, (4,))
    self.assertEqual(ds.edge_feat_pb.shape, (2,))

  def test_hetero_dist_dataset(self):
    ds = DistDataset()
    ds.load_vineyard(
      self.fid,
      self.sock,
      edges=self.hetero_edges,
      node_features=self.hetero_node_features,
      edge_features=self.hetero_edge_features,
      node_labels=self.node_labels,
    )
    self.assertEqual(ds.node_pb["person"].shape, (4,))
    # self.assertEqual(ds.node_pb["software"].shape, (2,))
    
    self.assertEqual(ds.edge_pb[("person", "knows", "person")].shape, (2,))
    self.assertEqual(ds.edge_pb[("person", "created", "software")].shape, (4,))

    self.assertEqual(ds.node_feat_pb["person"].shape, (4,))
    self.assertEqual(ds.node_feat_pb["software"].shape, (2,))

    self.assertEqual(ds.edge_feat_pb[("person", "knows", "person")].shape, (2,))
    self.assertEqual(
      ds.edge_feat_pb[("person", "created", "software")].shape, (4,)
    )


if __name__ == "__main__":
  unittest.main()
