# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Any

import numpy as np

from onnx import helper, numpy_helper


def bfloat16_to_float32(ival: int) -> Any:
    if ival == 0x7FC0:
        return np.float32(np.nan)

    expo = ival >> 7
    prec = ival - (expo << 7)
    sign = expo & 256
    powe = expo & 255
    fval = float(prec * 2 ** (-7) + 1) * 2.0 ** (powe - 127)
    if sign:
        fval = -fval
    return np.float32(fval)


def floate4m3_to_float32(ival: int) -> Any:
    if ival == 255:
        return np.float32(np.inf)
    if ival == 127:
        return np.float32(-np.inf)
    if ival == 0:
        return np.float32(0)

    expo = ival >> 3
    mant = ival - (expo << 3)
    sign = expo & 16
    powe = expo & 15
    if expo == 0:
        powe -= 6
        fraction = 0
    else:
        powe -= 7
        fraction = 1
    fval = float(mant * 2 ** (-3) + fraction) * 2.0**powe
    if sign:
        fval = -fval
    return np.float32(fval)


def floate5m2_to_float32(ival: int) -> Any:
    if ival == int("0111100", 2):
        return np.float32(np.inf)
    if ival == int("1111100", 2):
        return np.float32(-np.inf)
    raise NotImplementedError("not yet implemented")


class TestNumpyHelper(unittest.TestCase):
    def _test_numpy_helper_float_type(self, dtype: np.number) -> None:
        a = np.random.rand(13, 37).astype(dtype)
        tensor_def = numpy_helper.from_array(a, "test")
        self.assertEqual(tensor_def.name, "test")
        a_recover = numpy_helper.to_array(tensor_def)
        np.testing.assert_equal(a, a_recover)

    def _test_numpy_helper_int_type(self, dtype: np.number) -> None:
        a = np.random.randint(
            np.iinfo(dtype).min, np.iinfo(dtype).max, dtype=dtype, size=(13, 37)
        )
        tensor_def = numpy_helper.from_array(a, "test")
        self.assertEqual(tensor_def.name, "test")
        a_recover = numpy_helper.to_array(tensor_def)
        np.testing.assert_equal(a, a_recover)

    def test_float(self) -> None:
        self._test_numpy_helper_float_type(np.float32)

    def test_uint8(self) -> None:
        self._test_numpy_helper_int_type(np.uint8)

    def test_int8(self) -> None:
        self._test_numpy_helper_int_type(np.int8)

    def test_uint16(self) -> None:
        self._test_numpy_helper_int_type(np.uint16)

    def test_int16(self) -> None:
        self._test_numpy_helper_int_type(np.int16)

    def test_int32(self) -> None:
        self._test_numpy_helper_int_type(np.int32)

    def test_int64(self) -> None:
        self._test_numpy_helper_int_type(np.int64)

    def test_string(self) -> None:
        a = np.array(["Amy", "Billy", "Cindy", "David"]).astype(object)
        tensor_def = numpy_helper.from_array(a, "test")
        self.assertEqual(tensor_def.name, "test")
        a_recover = numpy_helper.to_array(tensor_def)
        np.testing.assert_equal(a, a_recover)

    def test_bool(self) -> None:
        a = np.random.randint(2, size=(13, 37)).astype(bool)
        tensor_def = numpy_helper.from_array(a, "test")
        self.assertEqual(tensor_def.name, "test")
        a_recover = numpy_helper.to_array(tensor_def)
        np.testing.assert_equal(a, a_recover)

    def test_float16(self) -> None:
        self._test_numpy_helper_float_type(np.float32)

    def test_complex64(self) -> None:
        self._test_numpy_helper_float_type(np.complex64)

    def test_complex128(self) -> None:
        self._test_numpy_helper_float_type(np.complex128)

    def test_bfloat16_to_float32(self):
        for f in [1, 0.100097656, 130048, 1.2993813e-5, np.nan]:
            with self.subTest(f=f):
                f32 = np.float32(f)
                bf16 = helper.float32_to_bfloat16(f32)
                assert isinstance(bf16, int)
                f32_1 = numpy_helper.bfloat16_to_float32(np.array([bf16]))[0]
                f32_2 = bfloat16_to_float32(bf16)
                if np.isnan(f32):
                    assert np.isnan(f32_1)
                    assert np.isnan(f32_2)
                else:
                    self.assertEqual(f32, f32_1)
                    self.assertEqual(f32, f32_2)

    def test_floate4m3_to_float32(self):
        self.assertEqual(floate4m3_to_float32(int("1111110", 2)), 448)
        self.assertEqual(floate4m3_to_float32(int("1000", 2)), 2 ** (-6))
        self.assertEqual(floate4m3_to_float32(int("1", 2)), 2 ** (-9))
        self.assertEqual(floate4m3_to_float32(int("111", 2)), 0.875 * 2 ** (-6))
        for f in [
            0,
            1,
            -1,
            0.5,
            -0.5,
            0.1,
            -0.1,
            2,
            3,
            -2,
            -3,
            448,
            2 ** (-6),
            2 ** (-9),
            0.875 * 2 ** (-6),
            np.nan,
        ]:
            with self.subTest(f=f):
                f32 = np.float32(f)
                f8 = helper.float32_to_floate4m3(f32)
                assert isinstance(f8, int)
                f32_1 = numpy_helper.floate4m3_to_float32(np.array([f8]))[0]
                f32_2 = floate4m3_to_float32(f8)
                # print(f"# f32={f32} f8={bin(f8)} f32_1={f32_1} f32_2={f32_2} *")
                if np.isnan(f32):
                    assert np.isnan(f32_1)
                    assert np.isnan(f32_2)
                else:
                    self.assertEqual(f32, f32_1)
                    self.assertEqual(f32, f32_2)

    def test_floate5m2_to_float32(self):
        # placeholder
        pass


if __name__ == "__main__":
    unittest.main()
