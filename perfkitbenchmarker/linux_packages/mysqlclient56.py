# Copyright 2014 PerfKitBenchmarker Authors. All rights reserved.
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


"""Module containing mysqlclient installation and cleanup functions."""


def YumInstall(vm):
  """Installs the mysql package on the VM."""
  del vm
  raise NotImplementedError('mysqlclient56 not implemented for yum')


def AptInstall(vm):
  """Installs the mysql package on the VM."""
  vm.RemoteCommand(
      'sudo add-apt-repository '
      "'deb http://archive.ubuntu.com/ubuntu trusty universe'"
  )
  vm.RemoteCommand('sudo apt-get update')
  vm.RemoteCommand('sudo apt-get -y install mysql-client-5.6')


def YumGetPathToConfig(vm):
  """Returns the path to the mysql config file."""
  del vm
  return '/etc/my.cnf'


def AptGetPathToConfig(vm):
  """Returns the path to the mysql config file."""
  del vm
  return '/etc/mysql/conf.d/mysql.cnf'
