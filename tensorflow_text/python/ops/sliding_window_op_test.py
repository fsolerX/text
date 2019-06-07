# coding=utf-8
# Copyright 2019 TF.Text Authors.
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

"""Tests for sliding_window_op."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import tensorflow as tf  # tf
import tensorflow_text as text

from tensorflow.python.framework import test_util
from tensorflow.python.ops.ragged import ragged_test_util
from tensorflow.python.platform import test


@test_util.run_all_in_graph_and_eager_modes
class SlidingWindowOpTest(ragged_test_util.RaggedTensorTestCase,
                          parameterized.TestCase):

  # TODO(b/122967006): Update this to include *all* docstring examples.
  def testDocStringExamples(self):
    # Sliding window (width=3) across a sequence of tokens
    data = tf.constant(['one', 'two', 'three', 'four', 'five', 'six'])
    output = text.sliding_window(data=data, width=3, axis=0)
    self.assertRaggedEqual(output,
                           [['one', 'two', 'three'], ['two', 'three', 'four'],
                            ['three', 'four', 'five'], ['four', 'five', 'six']])
    self.assertEqual('Shape: %s -> %s' % (data.shape, output.shape),
                     'Shape: (6,) -> (4, 3)')

    # Sliding window (width=2) across the inner dimension of a ragged matrix
    # containing a batch of token sequences
    data = tf.ragged.constant([['Up', 'high', 'in', 'the', 'air'],
                               ['Down', 'under', 'water'],
                               ['Away', 'to', 'outer', 'space']])
    output = text.sliding_window(data, width=2, axis=-1)
    self.assertRaggedEqual(output, [
        [['Up', 'high'], ['high', 'in'], ['in', 'the'], ['the', 'air']],
        [['Down', 'under'], ['under', 'water']],
        [['Away', 'to'], ['to', 'outer'], ['outer', 'space']]
    ])  # pyformat: disable
    self.assertEqual(
        'Shape: %s -> %s' % (data.shape.as_list(), output.shape.as_list()),
        'Shape: [3, None] -> [3, None, 2]')

    # Sliding window across the second dimension of a 3-D tensor containing
    # batches of sequences of embedding vectors:
    data = tf.constant([[[1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1], [5, 5, 1]],
                        [[1, 1, 2], [2, 2, 2], [3, 3, 2], [4, 4, 2], [5, 5,
                                                                      2]]])
    output = text.sliding_window(data=data, width=2, axis=1)
    self.assertRaggedEqual(output,
                           [[[[1, 1, 1], [2, 2, 1]], [[2, 2, 1], [3, 3, 1]],
                             [[3, 3, 1], [4, 4, 1]], [[4, 4, 1], [5, 5, 1]]],
                            [[[1, 1, 2], [2, 2, 2]], [[2, 2, 2], [3, 3, 2]],
                             [[3, 3, 2], [4, 4, 2]], [[4, 4, 2], [5, 5, 2]]]])
    self.assertEqual('Shape: %s -> %s' % (data.shape, output.shape),
                     'Shape: (2, 5, 3) -> (2, 4, 2, 3)')

  def _test_sliding_window_op(self, expected_result, data, width, axis):
    result = text.sliding_window(data, width, axis)
    self.assertAllEqual(expected_result, result)

  def test_sliding_window_for_one_dimensional_data(self):
    """Test sliding_window when data is a 1 dimensional tensor.

    data_shape: [5]
    total_dimensions: 1
    outer_dimensions: 0
    inner_dimensions: 0
    axis_dimension: 1

    result_shape: [3, 3]
    """
    data = tf.constant([1, 2, 3, 4, 5])
    width = 3
    axis = -1

    expected_result = tf.constant([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_sliding_window_for_data_with_outer_dimensions(self):
    """Test sliding_window when data has outer dimensions.

    data_shape: [5,3]
    axis_dimension: 1

    result_shape: [4, 2, 3]
    """
    data = tf.constant([[1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1], [5, 5, 1]])

    width = 2
    axis = -2

    expected_result = tf.constant(
        [[[1, 1, 1], [2, 2, 1]], [[2, 2, 1], [3, 3, 1]], [[3, 3, 1], [4, 4, 1]],
         [[4, 4, 1], [5, 5, 1]]])
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_sliding_window_for_data_with_zero_axis(self):
    """Test sliding_window when axis is 0.

    data_shape: [5, 3]

    result_shape: [4, 2, 3]
    """
    data = tf.constant([[1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1], [5, 5, 1]])

    width = 2
    axis = 0

    expected_result = tf.constant(
        [[[1, 1, 1], [2, 2, 1]], [[2, 2, 1], [3, 3, 1]], [[3, 3, 1], [4, 4, 1]],
         [[4, 4, 1], [5, 5, 1]]])
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_sliding_window_for_multi_dimensional_data(self):
    """Test sliding_window when data has both inner and outer dimensions.

    data_shape: [2, 4, 3]
    total_dimensions: 3
    outer_dimensions: 1
    inner_dimensions: 1
    axis_dimension: 1

    result_shape: [2, 3, 2, 3]
    """
    data = tf.constant([[[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]],
                        [[5, 5, 5], [6, 6, 6], [7, 7, 7], [8, 8, 8]]])
    width = 2
    axis = -2

    expected_result = tf.constant(
        [[[[1, 1, 1], [2, 2, 2]], [[2, 2, 2], [3, 3, 3]], [[3, 3, 3], [4, 4,
                                                                       4]]],
         [[[5, 5, 5], [6, 6, 6]], [[6, 6, 6], [7, 7, 7]],
          [[7, 7, 7], [8, 8, 8]]]])  # pyformat: disable
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_sliding_window_op_invalid_width(self):
    data = tf.constant([1, 2, 3, 4, 5])
    axis = -1
    error_message = 'width must be an integer greater than 0'

    with self.assertRaisesRegexp(tf.errors.InvalidArgumentError, error_message):
      self._test_sliding_window_op(data, data, 0, axis)
    with self.assertRaisesRegexp(tf.errors.InvalidArgumentError, error_message):
      self._test_sliding_window_op(data, data, -1, axis)

  def test_sliding_window_op_invalid_axis(self):
    data = tf.constant([1, 2, 3, 4, 5])
    width = 3
    error_message = 'axis must be between -k <= axis <= -1 OR 0 <= axis < k'

    with self.assertRaisesRegexp(tf.errors.InvalidArgumentError, error_message):
      self._test_sliding_window_op(data, data, width, -2)
    with self.assertRaisesRegexp(tf.errors.InvalidArgumentError, error_message):
      self._test_sliding_window_op(data, data, width, 1)

  def test_sliding_window_op_invalid_data_types(self):
    data = tf.constant([1, 2, 3, 4, 5])
    width = 3
    bad_width = tf.constant([width])
    axis = -1
    bad_axis = tf.constant([axis])

    with self.assertRaisesRegexp(TypeError, 'width must be an int'):
      self._test_sliding_window_op(data, data, bad_width, axis)
    with self.assertRaisesRegexp(TypeError, 'axis must be an int'):
      self._test_sliding_window_op(data, data, width, bad_axis)

  def test_docstring_example_1d_tensor(self):
    """Test the 1D example in the sliding_window docstring."""
    data = tf.constant(['one', 'two', 'three', 'four', 'five'])
    width = 3
    axis = -1

    expected_result = tf.constant(
        [['one', 'two', 'three'], ['two', 'three', 'four'],
         ['three', 'four', 'five']])  # pyformat: disable
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_docstring_example_inner_dimension_tensor(self):
    """Test the inner-dimension example in the sliding_window docstring."""
    data = tf.constant([[1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1], [5, 5, 1]])
    width = 2
    axis = -1

    expected_result = tf.constant([[[1, 1], [1, 1]], [[2, 2], [2, 1]],
                                   [[3, 3], [3, 1]], [[4, 4], [4, 1]],
                                   [[5, 5], [5, 1]]])  # pyformat: disable
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_docstring_example_multi_dimension_tensor(self):
    """Test the multi-dimension example in the sliding_window docstring."""
    data = tf.constant([[[1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1], [5, 5, 1]],
                        [[1, 1, 2], [2, 2, 2], [3, 3, 2], [4, 4, 2],
                         [5, 5, 2]]])  # pyformat: disable
    width = 2
    axis = -2

    expected_result = tf.constant([[[[1, 1, 1], [2, 2, 1]],
                                    [[2, 2, 1], [3, 3, 1]],
                                    [[3, 3, 1], [4, 4, 1]],
                                    [[4, 4, 1], [5, 5, 1]]],
                                   [[[1, 1, 2], [2, 2, 2]],
                                    [[2, 2, 2], [3, 3, 2]],
                                    [[3, 3, 2], [4, 4, 2]],
                                    [[4, 4, 2], [5, 5, 2]]]])
    self._test_sliding_window_op(expected_result, data, width, axis)

  def test_with_unknown_shape_tensor(self):
    """Vaalidate that the op still works with a tensor of unknown shape."""
    data = tf.placeholder_with_default(tf.constant([1, 2, 3, 4, 5]), shape=None)
    width = 3
    axis = -1

    expected_result = tf.constant([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    self._test_sliding_window_op(expected_result, data, width, axis)

  @parameterized.parameters([
      dict(
          descr='2-D data, width=1',
          data=[['See', 'Spot', 'run'], ['Hello'], [], ['Go', 'Giants'],
                ['a', 'b', 'c', 'd', 'e', 'f']],
          width=1,
          expected=[
              [['See'], ['Spot'], ['run']],
              [['Hello']],
              [],
              [['Go'], ['Giants']],
              [['a'], ['b'], ['c'], ['d'], ['e'], ['f']]]),
      dict(
          descr='2-D data, width=2',
          data=[['See', 'Spot', 'run'], ['Hello'], [], ['Go', 'Giants'],
                ['a', 'b', 'c', 'd', 'e', 'f']],
          width=2,
          expected=[
              [['See', 'Spot'], ['Spot', 'run']],
              [],
              [],
              [['Go', 'Giants']],
              [['a', 'b'], ['b', 'c'], ['c', 'd'], ['d', 'e'], ['e', 'f']]]),
      dict(
          descr='2-D data, width=3',
          data=[['See', 'Spot', 'run'], ['Hello'], [], ['Go', 'Giants'],
                ['a', 'b', 'c', 'd', 'e']],
          width=3,
          expected=[
              [['See', 'Spot', 'run']],
              [],
              [],
              [],
              [['a', 'b', 'c'], ['b', 'c', 'd'], ['c', 'd', 'e']]]),

      dict(
          descr='3-D data, ragged_rank=1, width=2, axis=1',
          data=[
              [[0, 0], [0, 1], [0, 2]],
              [],
              [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4]]],
          ragged_rank=1,
          width=2,
          axis=1,
          expected=[
              [[[0, 0], [0, 1]],
               [[0, 1], [0, 2]]],
              [],
              [[[1, 0], [1, 1]],
               [[1, 1], [1, 2]],
               [[1, 2], [1, 3]],
               [[1, 3], [1, 4]]]]),
      dict(
          descr='3-D data, ragged_rank=2, width=2, axis=2',
          data=[[[1, 2, 3, 4],
                 [5, 6]],
                [],
                [[7, 8, 9]]],
          width=2,
          axis=2,
          expected=[[[[1, 2], [2, 3], [3, 4]],
                     [[5, 6]]],
                    [],
                    [[[7, 8], [8, 9]]]]),
      dict(
          descr='2-D data, width=2, axis=0',
          data=[[1, 2], [3, 4, 5], [], [6, 7]],
          width=2,
          axis=0,
          expected=[
              [[1, 2], [3, 4, 5]],
              [[3, 4, 5], []],
              [[], [6, 7]]]),
      dict(
          descr='3-D data, ragged_rank=1, width=2, axis=2',
          data=[[[0, 1, 2, 3],
                 [4, 5, 6, 7]],
                [],
                [[8, 9, 10, 11]]],
          width=2,
          axis=2,
          expected=[[[[0, 1], [1, 2], [2, 3]],
                     [[4, 5], [5, 6], [6, 7]]],
                    [],
                    [[[8, 9], [9, 10], [10, 11]]]]),
      dict(
          descr='empty data',
          data=[],
          ragged_rank=1,
          width=2,
          expected=[]),
  ])  # pyformat: disable
  def testRaggedInputs(self,
                       descr,
                       data,
                       width,
                       expected,
                       axis=-1,
                       ragged_rank=None):
    data = tf.ragged.constant(data, ragged_rank=ragged_rank)
    result = text.sliding_window(data, width, axis)
    self.assertRaggedEqual(result, expected)


if __name__ == '__main__':
  test.main()