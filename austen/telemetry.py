"""
Logger module is used to gather telemetry from algorithm's
function call graph. This includes function's name, parameters,
and delta time. Each logger can be enclosed in scope using
`with` statement. When exiting scope, the module will
merge it's telemetry dictionary up to the parent.

"""

from __future__ import annotations
import collections
from datetime import datetime
import json
import os
import joblib
from timeit import default_timer as timer
from typing import Dict

from pandas import DataFrame
from matplotlib.figure import Figure
from skimage.io import imsave
from skimage import img_as_ubyte

from .encoders import NumpyEncoder


class Logger:

    """
    Through this object, you'll be able to dump logs.

    Parameters
    ----------
    output : str
        Initial base directory for logger output.
    scope : str, optional
        Current scope's name.
    parent : Logger, optional
        Parent logger denotes, where telemetry dictionary should
        be merged up to. (the default is None, meaning logger is the root)

    """

    def __init__(self, output: str, scope='', parent=None):

        self.OUTPUT = output
        self.__SCOPE = scope
        self.__PARENT = parent

        self.__LOG = collections.OrderedDict()
        self.__START = timer()
        self.__TIMESTAMP = datetime.today()

        self.__step_counter = 1

        if self.__SCOPE:
            self.OUTPUT = os.path.join(self.OUTPUT, self.__SCOPE)

        if not os.path.isdir(self.OUTPUT):
            os.makedirs(self.OUTPUT)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.add_entry('start', str(self.__TIMESTAMP))
        self.add_entry('end', str(datetime.today()))
        self.add_entry('dt', timer() - self.__START)

        if self.__PARENT:
            self.__PARENT.__merge(self.__SCOPE, self.__LOG)
            return self.__PARENT
        else:
            # TODO: why dumping log so implicitly?
            self.save_json(self.__LOG, 'telemetry')

    def __merge(self, scope, log):
        if scope:
            self.__LOG = {
                **self.__LOG,
                scope: log
            }
        else:
            self.__LOG = {
                **self.__LOG,
                **log
            }

    def __step_counter_to_string(self):
        if self.__step_counter < 10:
            return '0' + str(self.__step_counter)
        else:
            return str(self.__step_counter)

    def __get_next_key(self, key):
        i = 1
        temp_key = key
        while(temp_key in self.__LOG):
            temp_key = key + '_' + str(i)
            i += 1

        return temp_key

    def get_child(self, scope) -> Logger:
        """
        Creates child logger, using current instance as a parent.

        Parameters
        ----------
        scope : str
            Every subsequent logs will be put under this scope.

        Returns
        -------
        Logger
            New child instance, where current logger is parent logger.
        """

        return Logger(
            output=self.OUTPUT,
            scope=scope,
            parent=self
        )

    def add_entry(self, key, value):
        """
        Registers new entry in the log dictionary.

        Parameters
        ----------
        key : str
            Indicates where value will be logged.
        value : str / dict
            Value to log under key.

        """

        next_key = self.__get_next_key(key)
        self.__LOG[next_key] = value

    def add_entries(self, entries):
        """
        Registers new entries in the log dictionary.

        Parameters
        ----------
        entries : list[tuple(str, any)]
            List of keys and their values,
            that will be added to the log dictionary.

        """

        for key, value in entries:
            self.add_entry(key, value)

    def log_func(self, func, args=[], kwargs={}):
        """
        Wrapper for a function call. Calls function, logs
        its parameters and result in the log dictionary.

        Parameters
        ----------
        func : callable
            A function to be ran.
        args : list, optional
            List of arguments, that will be applied to function call.
        kwargs : dict, optional
            List of keyword arguments, that will be applied to function call.

        Returns
        -------
        any
            Results from function call.
        """

        start = timer()
        result = func(*args, **kwargs)
        end = timer()

        log = {}
        log['dt'] = end - start
        log['params'] = kwargs

        self.add_entry(func.__name__, log)

        self.__step_counter += 1

        return result

    def save_obj(self, obj, name: str, prefix_step=False):
        """
        Dumps an object using joblib.
        File will be logged under logger's scope.

        Parameters
        ----------
        obj : class
        name : str
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '_'

        filepath += name + '.joblib'
        path = os.path.join(self.OUTPUT, filepath)

        joblib.dump(obj, path)

    def save_fig(self, figure: Figure, name: str, prefix_step=False):
        """
        Dumps figure.
        File will be logged under logger's scope.

        Parameters
        ----------
        figure : Figure
            Should implement `savefig(path)` interface.
        name : str
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '_'

        filepath += name + '.png'
        path = os.path.join(self.OUTPUT, filepath)

        figure.savefig(path)

    def save_csv(self, data: DataFrame, name: str, prefix_step=False):
        """
        Dumps data frame to `.csv` file.
        File will be logged under logger's scope.

        Parameters
        ----------
        data : DataFrame
        name : str
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '_'

        filepath += name + '.csv'
        path = os.path.join(self.OUTPUT, filepath)

        data.to_csv(path)

    def save_json(self, dictionary: Dict, name: str, prefix_step=False):
        """
        Dumps dictionary onto hard drive.
        File will be logged under logger's scope.

        Parameters
        ----------
        dictionary : Dict
        name : str
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '_'

        filepath += name + '.json'
        path = os.path.join(self.OUTPUT, filepath)

        with open(path, 'w') as file:
            json.dump(dictionary, file, cls=NumpyEncoder)

    def save_image(self, image, name: str, prefix_step=False):
        """
        Dumps image onto hard drive.
        File will be logged under logger's scope.

        Parameters
        ----------
        image : ndarray
        name : str
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '_'

        filepath += name + '.tiff'
        path = os.path.join(self.OUTPUT, filepath)

        image = img_as_ubyte(image)
        imsave(path, image)
