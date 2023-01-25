# SPDX-License-Identifier: Apache-2.0
# pylint: disable=W0221

from onnx.helper import np_dtype_to_tensor_dtype
from onnx.onnx_pb import TensorProto
from onnx.reference.op_run import OpRun

from .op_cast import bfloat16, floate4m3, floate5m2, cast_to


class CastLike(OpRun):
    def _run(self, x, y):  # type: ignore
        if y.dtype == bfloat16:
            to = TensorProto.BFLOAT16
        elif y.dtype == floate4m3:
            to = TensorProto.FLOATE4M3
        elif y.dtype == floate5m2:
            to = TensorProto.FLOATE5M2
        else:
            to = np_dtype_to_tensor_dtype(y.dtype)  # type: ignore
        return (cast_to(x, to),)
