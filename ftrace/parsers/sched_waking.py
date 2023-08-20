#!/usr/bin/python

# Copyright 2015 Huawei Devices USA Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors:
#       Chuk Orakwue <chuk.orakwue@huawei.com>

import re
from ftrace.common import ParserError
from .register import register_parser
from collections import namedtuple

TRACEPOINT = 'sched_waking'


__all__ = [TRACEPOINT]

# NOTE: 'success' is optional for some android phones and linux kernels
# comm=tfm_b6bcf800 pid=1714 prio=35 success=1 target_cpu=000

SchedWakingBase = namedtuple(TRACEPOINT,
    [
    'comm', # Task name
    'pid', # Process pid
    'prio', # Process priority
    'success', # success flag
    'target_cpu', # Target cpu
    ]
)

class SchedWaking(SchedWakingBase):
    __slots__ = ()
    def __new__(cls, comm, pid, prio, success, target_cpu):
            pid = int(pid)
            prio = int(prio)
            success = 1 if success is None else int(success)
            target_cpu = int(target_cpu)

            return super(cls, SchedWaking).__new__(
                cls,
                comm=comm,
                pid=pid,
                prio=prio,
                success=success,
                target_cpu=target_cpu,
            )

sched_waking_pattern = re.compile(
        r"""
        comm=(?P<comm>.*)\s+
        pid=(?P<pid>\d+)\s+
        prio=(?P<prio>\d+)\s+
        (success=(?P<success>\d+)\s+)?
        target_cpu=(?P<target_cpu>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_waking(payload):
    """Parser for `sched_waking` tracepoint"""
    try:
        match = re.match(sched_waking_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedWaking(**match_group_dict)
    except Exception as e:
        raise ParserError(e.message)
