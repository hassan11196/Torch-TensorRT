import torch
import torch_tensorrt.fx.tracer.acc_tracer.acc_ops as acc_ops
from parameterized import param, parameterized
from torch.testing._internal.common_fx2trt import AccTestCase, InputTensorSpec
from torch.testing._internal.common_utils import run_tests


class TestConvolutionConverter(AccTestCase):
    @parameterized.expand(
        [
            ("default", 1),
            param("no_bias", 1, bias=False),
            ("tuple_parameters", 1, (1), (1)),
            param("non_zero_padding", 1, padding=1),
            param("dilation", 1, dilation=2),
            param("groups", 1, groups=3),
        ]
    )
    def test_conv1d(
        self,
        _,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        bias=True,
    ):
        class TestModule(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = torch.nn.Conv1d(
                    3, 6, kernel_size, stride, padding, dilation, groups, bias
                )

            def forward(self, x):
                return self.conv(x)

        inputs = [torch.randn(1, 3, 32)]
        self.run_test(
            TestModule(),
            inputs,
            expected_ops={acc_ops.conv1d},
            test_explicit_precision=True,
        )

    @parameterized.expand(
        [
            ("default", 1),
            param("no_bias", 1, bias=False),
            ("tuple_parameters", 1, (1, 1), (1, 1)),
            param("non_zero_padding", 1, padding=1),
            param("dilation", 1, dilation=2),
            param("groups", 1, groups=3),
        ]
    )
    def test_conv2d(
        self,
        _,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        bias=True,
    ):
        class TestModule(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = torch.nn.Conv2d(
                    3, 6, kernel_size, stride, padding, dilation, groups, bias
                )

            def forward(self, x):
                return self.conv(x)

        inputs = [torch.randn(1, 3, 32, 32)]
        self.run_test(TestModule(), inputs, expected_ops={acc_ops.conv2d})

    def test_conv2d_with_dynamic_shape(self):
        class TestModule(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = torch.nn.Conv2d(3, 6, 1)

            def forward(self, x):
                return self.conv(x)

        input_specs = [
            InputTensorSpec(
                shape=(-1, 3, -1, -1),
                dtype=torch.float32,
                shape_ranges=[((1, 3, 1, 1), (1, 3, 4, 4), (32, 3, 128, 128))],
            ),
        ]
        self.run_test_with_dynamic_shape(
            TestModule(), input_specs, expected_ops={acc_ops.conv2d}
        )

    @parameterized.expand(
        [
            ("default", 1),
            param("no_bias", 1, bias=False),
            ("tuple_parameters", 1, (1, 1, 1), (1, 1, 1)),
            param("non_zero_padding", 1, padding=1),
            param("dilation", 1, dilation=2),
            param("groups", 1, groups=3),
        ]
    )
    def test_conv3d(
        self,
        _,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        bias=True,
    ):
        class TestModule(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = torch.nn.Conv3d(
                    3, 6, kernel_size, stride, padding, dilation, groups, bias
                )

            def forward(self, x):
                return self.conv(x)

        inputs = [torch.randn(1, 3, 32, 32, 32)]
        self.run_test(TestModule(), inputs, expected_ops={acc_ops.conv3d})

    def test_conv3d_with_dynamic_shape(self):
        class TestModule(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = torch.nn.Conv3d(3, 6, 1)

            def forward(self, x):
                return self.conv(x)

        input_specs = [
            InputTensorSpec(
                shape=(-1, 3, -1, -1, -1),
                dtype=torch.float32,
                shape_ranges=[((1, 3, 1, 1, 1), (1, 3, 4, 4, 4), (8, 3, 32, 32, 32))],
            ),
        ]
        self.run_test_with_dynamic_shape(
            TestModule(), input_specs, expected_ops={acc_ops.conv3d}
        )


if __name__ == "__main__":
    run_tests()
