#!/usr/bin/python

# Copyright 2015 Huawei Devices Inc. All rights reserved.
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

""" Interval:  Represents an interval of time defined by two timestamps.
    IntervalList: List with objects with interval, sorted/sliceable by interval.
"""
from bisect import bisect, insort, bisect_left
from .common import memoize

class Interval(object):
    """
    Represents an interval of time defined by two timestamps.

    Parameters:
    -----------

    start: float.
        Starting value.
    end : float
        Ending value.
    """

    __slots__ = ("start", "end")

    def __init__(self, start, end):
        if end < start:
            raise ValueError("End timestamp:{end} cannot be less than start timestamp:{start}".format(start=start, end=end))
        self.start, self.end = float(start), float(end)

    def __repr__(self):
        return "Interval(start={:.3f}ms, end={:.3f}ms, duration={:.3f}ms)".format(
            self.start * 1000, self.end * 1000, self.duration * 1000)

    @property
    def duration(self):
        """Returns float"""
        return self.end - self.start

    @memoize
    def within(self, timestamp):
        """Returns true if timestamp falls within interval"""
        return True if (timestamp >= self.start) and \
            (timestamp <= self.end) else False


class IntervalList(list):
    """
    List with objects with intervals, sorted and sliceable by interval.
    """
    
    def __init__(self, iterable=None):
        self._intervals = []
        self._start_timestamps = []
        self._end_timestamps = []
        if iterable:
            for item in iterable:
                if hasattr(item, 'interval'):
                    self.append(item)
                else:
                    raise AttributeError('{} object has no attribute `interval`'.format(type(item)))

    def __repr__(self):
        return '\n'.join([item.__repr__() for item in self])

    @property
    def _start_times(self):
        return self._start_timestamps

    @property
    def _end_times(self):
        return self._end_timestamps

    @property
    def duration(self):
        """Duration of events in seconds"""
        return sum(interval.duration for interval in self._intervals)

    def __add_interval(self, obj):
        """Add interval to (sorted) intervals list"""
        start, end = obj.interval.start, obj.interval.end
        idx = bisect(self._start_timestamps, start)
        insort(self._end_timestamps, end)
        self._start_timestamps.insert(idx, start) # insert into self based on start
        self._intervals.insert(idx, obj.interval)
        return idx

    def append(self, obj):
        """Append new event to list"""
        try:
            obj.interval
        except AttributeError:
            raise TypeError("Must have interval attribute")
        super(self.__class__, self).insert(self.__add_interval(obj), obj)

    def slice(self, interval, trimmed=True):
        """
        Caution: the slice must not overlap
        Returns list of objects whose interval fall
        between the specified interval.

        Parameters:
        -----------
        trimmed : bool, default True
            Trim interval of returned list of objects to fall within specified
            interval
        """
        if interval is None:
            return self

        start, end = interval.start, interval.end
        '''
        don't use -1 because
                             0              1
        interval        [  A   ]       [  B   ]
                                    [         C      ] 
        will get wrong index 1 - 1 = 0, we want B
        
        idx_left = bisect(self._start_timestamps, start) - 1
        if idx_left == -1:
            idx_left = 0
        '''

        idx_left = bisect_left(self._start_timestamps, start)
        log_left = -1
        log_right = -1
        if start >= log_left and start <= log_right:
            print("original idx_left : {}".format(idx_left))
            if idx_left != len(self._start_timestamps):
                print("start left: {} ".format(self._start_timestamps[idx_left]))
            if idx_left != 0:
                print("start left - 1: {} ".format(self._start_timestamps[idx_left - 1]))
            if idx_left != len(self._start_timestamps):
                print("end left: {} ".format(self._end_timestamps[idx_left]))
            if idx_left != 0:
                print("end left - 1: {} ".format(self._end_timestamps[idx_left - 1]))
            print("len : {}".format(len(self._start_timestamps)))
        #if idx_left != 0 and idx_left != len(self._start_timestamps):
        '''
                             0              1
        interval        [  A   ]       [  B   ]
                                [             C      ] 
        we want (0, 2)

                             0              1
        interval        [  A   ]       [  B   ]
                                             [] 
                                           [ C ] 
        we want (1, 2)
        '''
        if idx_left != 0:
            if self._end_timestamps[idx_left - 1] > start:
                idx_left = idx_left - 1

        idx_right = bisect(self._start_timestamps, end)

        if start >=  log_left and start <= log_right:
            print("after idx_left : {}".format(idx_left))
            print("after idx_right : {}".format(idx_right))

#       idx_right = None if idx_right > len(self) else idx_right
        #idx = slice(idx_left, idx_right) if idx_left != idx_right else slice(idx_left - 1, idx_left)
        idx = slice(idx_left, idx_right)

        ll = self[idx]
        rv = IntervalList()

        if start >= log_left and start <= log_right:
            print(idx)
            print(ll)

        if trimmed and len(ll):
            for item in ll:
                trim = False
                item_start, item_end = item.interval.start, item.interval.end
                if item_start < start:
                    trim, item_start = True, start
                if item_end > end:
                    trim, item_end = True, end
                if trim:
                    rv.append(item._replace(interval=Interval(item_start, item_end)))
                else:
                    rv.append(item)
        else:
            for item in ll:
                rv.append(item)

        return rv
