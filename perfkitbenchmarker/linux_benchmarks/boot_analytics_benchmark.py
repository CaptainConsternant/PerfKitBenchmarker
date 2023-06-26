# Copyright 2019 PerfKitBenchmarker Authors. All rights reserved.
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
"""Collects analytics on vm boot process.
"""

from perfkitbenchmarker import sample
import re

BENCHMARK_NAME = 'boot_analytics'
BENCHMARK_CONFIG = """
boot_analytics:
  description: Retrieves boot process metrics
  vm_groups:
    default:
      vm_spec: *default_single_core
"""

def _ParseSystemdAnalyze(vm):
  """Parses systemd-analyze results as metrics. 

  Args:
      vm: The vm to run the command on 

  Returns:
      a list of sample objects
  """  
  output, _ = vm.RemoteCommand('systemd-analyze')
  # eg  'Startup finished in 15.741s (userspace) \ngraphical.target reached after 14.919s in userspace\n'
  metadata  = {
    "summary": "systemd-analyze",
    "cmd": "systemd-analyze",
  }
  graphical_target = (re.findall(r"graphical.target reached after (\d+\.\d+)s", 
    output, 
    re.IGNORECASE) or ['']
  )[0]
  
  startup = (re.findall(r"Startup finished in (\d+\.\d+)s", output, re.IGNORECASE) or [''])[0]
  metrics = []
  metrics.append(sample.Sample("startup_time",startup,'s',metadata))
  metrics.append(sample.Sample("graphical_target_time",graphical_target,'s',metadata))
  return metrics

def _CloudInitBoot(vm):
  """Parses 'cloud-init analyze boot' results as metrics. 

  Args:
      vm: The vm to run the command on 

  Returns:
      a list of sample objects
  """  
  output, _ = vm.RemoteCommand('cloud-init analyze boot')
  # eg '-- Most Recent Container Boot Record --\n    Container started at: 2023-06-09 07:19:51.631616\n    Cloud-init activated by systemd at: 2023-06-09 07:19:53.544404\n    Cloud-init start: 2023-06-09 07:19:56.043000\n'
  metrics = []
  return metrics

def _CloudInitShow(vm):
  """Parses 'cloud-init analyze show' results as metrics. 

  Args:
      vm: The vm to run the command on 

  Returns:
      a list of sample objects
  """    

  output, _ = vm.RemoteCommand('cloud-init analyze show')
  data=output.split('-- Boot Record ')[-1].split('\n')

  """example

  ['15 --',
  'The total time elapsed since completing an event is printed after the "@" character.',
  'The time the event takes is printed after the "+" character.',
  '',
  'Starting stage: init-local',
  '|`->restored from checked cache: DataSourceLXD @00.03300s +00.05400s',
  'Finished stage: (init-local) 00.17600 seconds',
  '',
  'Starting stage: init-network',
  '|`->restored from cache with run check: DataSourceLXD @01.19100s +00.00400s',
  '|`->setting up datasource @01.26400s +00.00000s',
  '|`->reading and applying user-data @01.27000s +00.00400s',
  '|`->reading and applying vendor-data @01.27400s +00.00000s',
  '|`->reading and applying vendor-data2 @01.27400s +00.00000s',
  '|`->activating datasource @01.32300s +00.00200s',
  '|`->config-migrator ran successfully @01.49900s +00.00200s',
  '|`->config-seed_random previously ran @01.50100s +00.00100s',
  '|`->config-growpart ran successfully @01.50200s +00.01100s',
  '|`->config-resizefs ran successfully @01.51400s +00.00100s',
  '|`->config-mounts previously ran @01.51500s +00.00000s',
  '|`->config-set_hostname previously ran @01.51500s +00.00100s',
  '|`->config-update_hostname ran successfully @01.51600s +00.01000s',
  '|`->config-users-groups previously ran @01.52600s +00.00000s',
  '|`->config-ssh previously ran @01.52700s +00.00000s',
  'Finished stage: (init-network) 00.42100 seconds',
  '',
  'Starting stage: modules-config',
  '|`->config-ssh-import-id previously ran @09.37100s +00.00100s',
  '|`->config-locale previously ran @09.37200s +00.00100s',
  '|`->config-set-passwords previously ran @09.37300s +00.00000s',
  '|`->config-grub-dpkg previously ran @09.37400s +00.00000s',
  '|`->config-apt-configure previously ran @09.37500s +00.00000s',
  '|`->config-byobu previously ran @09.37600s +00.00000s',
  'Finished stage: (modules-config) 00.21300 seconds',
  '',
  'Starting stage: modules-final',
  '|`->config-reset_rmc previously ran @11.14900s +00.00100s',
  '|`->config-refresh_rmc_and_interface ran successfully @11.15000s +00.00100s',
  '|`->config-rightscale_userdata previously ran @11.15100s +00.00100s',
  '|`->config-scripts-vendor previously ran @11.15200s +00.00100s',
  '|`->config-scripts-per-once previously ran @11.15300s +00.00000s',
  '|`->config-scripts-per-boot ran successfully @11.15400s +00.00000s',
  '|`->config-scripts-per-instance previously ran @11.15500s +00.00000s',
  '|`->config-scripts-user previously ran @11.15600s +00.00000s',
  '|`->config-ssh-authkey-fingerprints previously ran @11.15600s +00.00100s',
  '|`->config-keys-to-console previously ran @11.15700s +00.00100s',
  '|`->config-install-hotplug previously ran @11.15800s +00.00000s',
  '|`->config-final-message ran successfully @11.15900s +00.02000s',
  'Finished stage: (modules-final) 00.24900 seconds',
  '',
  'Total Time: 1.05900 seconds',
  '',
  '15 boot records analyzed',
  '']
  """
  metadata  = {
    "summary": "cloud-init",
    "cmd": "cloud-init analyze show",
  }
  metrics = []
  for line in data :
    lres= re.findall(r"\(([\w\-_]+)\)\s+(\d+\.\d+)\s", line, re.IGNORECASE)
    if lres:
      metrics.append(sample.Sample(lres[0],lres[1],'s',metadata))
  return metrics

def Run(benchmark_spec):
  """Runs boot analytics on the VM.


  Args:
    benchmark_spec: The benchmark specification.

  Returns:
    A list of sample.Sample objects with the performance results.

  Raises:
    Benchmarks.RunError: If correct operation is not validated.
  """
  metrics = []
  vm = benchmark_spec.vms[0]
  metrics += _ParseSystemdAnalyze(vm)
  metrics += _CloudInitBoot(vm)
  metrics += _CloudInitShow(vm)


  return metrics

