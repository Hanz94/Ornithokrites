# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 21:33:27 2013

@author: Lukasz Tracewski

Module for handling recordings' input and output.
"""

from __future__ import division
import os
import numpy as np
import scipy.io.wavfile as wav


def read(path):
    """ Read wave file from the given path """
    (rate, sample) = wav.read(path)
    sample = sample.astype('float32')
    sample /= np.max(np.abs(sample), axis=0)  # Normalize sample
    return rate, sample


def write(path, rate, sample, dB=30.0, output_dir="", segments=[]):
    """
    Write signal to disc as wave file

    Parameters
    ----------
    path : string
        Absolute or relative path.
    rate : int
        Sample rate in Hz.
    sample : 1-d array
        Single-channel audio sample.
    dB : float (default = 30)
        Optional number of decibels to which audio will be amplified or reduced.
        Largest value in sample will be scaled to given number of dB.
    output_dir : string (default = "")
        Optional output directory. If provided, this directory will be created
        (if not yet existing) and concatenated with path.
    segments : list of touples (int, int) (default = no segmentation)
        Optional list of segments. If provided only parts indicated by segments
        will be saved to disc.

    Returns
    -------
    Nothing
    """
    if segments:
        total_length = sum([end - start for start, end in segments])
        new_sample = np.zeros(total_length)
        idx = 0
        for start, end in segments:
            length = end - start
            new_sample[idx:idx+length] = sample[start:end]
            idx += length
        sample = new_sample

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = os.path.basename(path)
        path = os.path.join(output_dir, filename)

    max_sample = np.max(sample)
    desired_dB_log = 10**(dB / 10)
    sample *= desired_dB_log / max_sample

    wav.write(path, rate, sample.astype('int16'))


class Walker(object):
    """ Walk the directory structure and find all wave files """

    def __init__(self, recordings_location):
        """
        From the given location we will traverse all nodes and
        find wave files
        """
        self._recordings = []

        if os.path.isfile(recordings_location) and recordings_location.endswith('.wav'):
            self._recordings.append(recordings_location)

        for dirpath, dirnames, filenames in os.walk(recordings_location):
            for filename in [f for f in filenames if f.endswith('.wav')]:
                self._recordings.append(os.path.join(dirpath, filename))

    def read_wave(self):
        """
        Generator for reading of wave files.
        Generators are iterators, but you can only iterate over them once.
        It's because they do not store all the values in memory,
        they generate the values on the fly. It means that all wave files will
        not be read at once, but on as-required basis.

        Parameters
        ----------
        None

        Returns
        -------
        samplerate : int
            Rate of the sample in Hz
        sample : 1-d array
            Wave file read as numpy array of int16
        name : string
            Name of a wave file
        """
        for name in self._recordings:
            (samplerate, sample) = wav.read(name)
            yield samplerate, sample, name

    def get_recordings_list(self):
        """ Returns list of all recordings """
        return self._recordings

    def count(self):
        """ Total number of recordings """
        return len(self._recordings)


""" Test """
if __name__ == '__main__':
    recordings_walker = Walker("./Recordings")
    print recordings_walker.count()
