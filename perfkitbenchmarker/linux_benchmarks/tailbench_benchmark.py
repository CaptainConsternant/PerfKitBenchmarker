# Copyright 2021 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Records the latencies generated by the tailbench suite of tests."""

from absl import flags
from perfkitbenchmarker import configs
from perfkitbenchmarker import vm_util
from perfkitbenchmarker.linux_packages import tailbench

FLAGS = flags.FLAGS

BENCHMARK_NAME = 'tailbench'
BENCHMARK_CONFIG = """
tailbench:
  description: >
      Run the tailbench suite of benchmark tests. Get information about the
      latency of running certain applications on the VM.
  vm_groups:
    default:
      vm_spec:
        AWS:
          machine_type: m5.large
          zone: us-east-1
        Azure:
          machine_type: STANDARD_D2_V3
          zone: westus2
          boot_disk_type: StandardSSD_LRS
        GCP:
          machine_type: n1-standard-2
          zone: us-central1-a
          boot_disk_type: pd-ssd
      disk_spec:
        GCP:
          disk_size: 2000
          disk_type: pd-ssd
          mount_point: /scratch_ts
        AWS:
          disk_size: 2000
          disk_type: gp2
          mount_point: /scratch_ts
        Azure:
          disk_size: 2000
          disk_type: StandardSSD_LRS
          mount_point: /scratch_ts
  flags:
    openjdk_version: 8
"""

_TESTS = flags.DEFINE_multi_enum(
    'tailbench_tests',
    ['img-dnn', 'specjbb', 'masstree'],
    ['img-dnn', 'specjbb', 'masstree'],
    'Which tailbench tests to run, all by default',
)

INSTALL_DIR = '/scratch_ts'


def GetConfig(user_config):
  return configs.LoadConfig(BENCHMARK_CONFIG, user_config, BENCHMARK_NAME)


def Prepare(benchmark_spec):
  vm = benchmark_spec.vms[0]
  tailbench.Install(vm)
  tailbench.PrepareTailBench(vm)


def CheckFlag(value: str):
  return any(
      substring in value for substring in ['img-dnn', 'specjbb', 'masstree']
  )


def Run(benchmark_spec):
  """Run tailbench and return the latency values as a list of histograms.

  Args:
    benchmark_spec: allows us to access the vm

  Returns:
    A list sample.Sample objects
  """
  samples = []
  vm = benchmark_spec.vms[0]
  tailbench.RunTailbench(vm, _TESTS.value)
  for test in _TESTS.value:
    vm.PullFile(vm_util.GetTempDir(), f'{INSTALL_DIR}/results/{test}.txt')
    samples += tailbench.BuildHistogramSamples(
        f'{vm_util.GetTempDir()}/{test}.txt', test, 'latency'
    )
  return samples


def Cleanup(benchmark_spec):
  del benchmark_spec
