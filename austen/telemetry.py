"""
Logger module is used to gather telemetry from algorithm's
function call graph. This includes function's name, parameters,
and delta time. Each logger can be enclosed in scope using
`with` statement. When exiting scope, the module will
merge it's telemetry dictionary up to the parent.

"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from timeit import default_timer as timer
from typing import Dict, List, Tuple, Any, Callable

import joblib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from numpy import ndarray
from pandas import DataFrame
from PIL import Image
from skimage import img_as_ubyte
from skimage.io import imsave

from .encoders import NumpyEncoder


class Logger:

    """
    Through this object, you'll be able to dump logs.

    Parameters
    ----------
    output : Path
        Initial base directory for logger output.
    scope : str, optional
        Scope's name. Files will be dumped under the folder with this name.
    parent : Logger, optional
        Parent logger denotes, where telemetry dictionary should
        be merged up to. (the default is None, meaning logger is the root)
    clear_dir : bool, optional
        Denotes whether specified log dir should be cleared upon start.
    """

    def __init__(
        self,
        output: Path,
        scope='',
        parent: Logger = None,
        clear_dir=False
    ):

        self.OUTPUT = output
        self.__SCOPE = scope
        self.__PARENT = parent

        self.__logs = {}
        self.__START = timer()
        self.__TIMESTAMP = datetime.today()

        self.__step_counter = 1

        if self.__SCOPE:
            self.OUTPUT = self.OUTPUT.joinpath(self.__SCOPE)

        if clear_dir:
            rmtree(str(self.OUTPUT), ignore_errors=True)

        self.OUTPUT.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.add_entry('start', str(self.__TIMESTAMP))
        self.add_entry('end', str(datetime.today()))
        self.add_entry('dt', timer() - self.__START)

        if self.__PARENT:
            self.__PARENT.__merge(self.__SCOPE, self.__logs)
        else:
            # TODO: why dumping log so implicitly?
            self.save_json(self.__logs, 'telemetry')

    def __merge(self, scope: str, log: Dict):
        if scope:
            self.__logs = {
                **self.__logs,
                scope: log
            }
        else:
            self.__logs = {
                **self.__logs,
                **log
            }

    def __step_counter_to_string(self) -> str:

        step_counter = ''

        if self.__step_counter < 10:
            step_counter = '0'

        step_counter += str(self.__step_counter)

        return step_counter

    def __get_next_key(self, key: str) -> str:
        i = 1
        temp_key = key
        while temp_key in self.__logs:
            temp_key = key + '-' + str(i)
            i += 1

        return temp_key

    def get_logs(self) -> Dict:
        """
        Returns
        -------
        Dict
            Retrieves internal dictionary of log entries.
        """

        return self.__logs

    def get_child(self, scope: str) -> Logger:
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

    def add_entry(self, key: str, value: Any):
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
        self.__logs[next_key] = value

    def add_entries(self, entries: List[Tuple[str, Any]]):
        """
        Registers new entries in the log dictionary.

        Parameters
        ----------
        entries : List[Tuple[str, Any]]
            List of keys and their values,
            that will be added to the log dictionary.
        """

        for key, value in entries:
            self.add_entry(key, value)

    def log_func(
        self,
        func: Callable,
        args: list = None,
        kwargs: dict = None
    ) -> Any:

        """
        Wrapper for a function call. Calls function, logs
        its parameters and result in the log dictionary.

        Parameters
        ----------
        func : Callable
            A function to be ran.
        args : list, optional
            List of arguments, that will be applied to function call.
        kwargs : dict, optional
            List of keyword arguments, that will be applied to function call.

        Returns
        -------
        Any
            Results from function call.
        """

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        start = timer()
        result = func(*args, **kwargs)
        end = timer()

        log = {}
        log['dt'] = end - start
        log['params'] = kwargs

        self.add_entry(func.__name__, log)

        self.__step_counter += 1

        return result

    def save_obj(self, obj: Any, name: str, prefix_step=False):
        """
        Dumps an object using joblib.
        File will be logged under logger's scope.

        Parameters
        ----------
        obj : Any
        name : str
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name + '.joblib'
        path = self.OUTPUT.joinpath(filepath)

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
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        """

        plt.figure(clear=True)

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name + '.png'
        path = self.OUTPUT.joinpath(filepath)

        figure.savefig(path)

        plt.close('all')

    def save_csv(
        self,
        data: DataFrame,
        name: str,
        prefix_step=False,
        index=True
    ):
        """
        Dumps data frame to `.csv` file.
        File will be logged under logger's scope.

        Parameters
        ----------
        data : DataFrame
        name : str
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        index: bool, optional
            Write row names (index).
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name + '.csv'
        path = self.OUTPUT.joinpath(filepath)

        data.to_csv(path, index=index)

    def save_json(self, dictionary: Dict, name: str, prefix_step=False):
        """
        Dumps dictionary onto hard drive.
        File will be logged under logger's scope.

        Parameters
        ----------
        dictionary : Dict
        name : str
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name + '.json'
        path = self.OUTPUT.joinpath(filepath)

        with open(path, 'w') as file:
            json.dump(dictionary, file, cls=NumpyEncoder)

    def save_image(
        self,
        image: ndarray,
        name: str,
        prefix_step=False,
        filetype='png'
    ):
        """
        Dumps image onto hard drive.
        File will be logged under logger's scope.

        Parameters
        ----------
        image : ndarray
        name : str
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        filetype : str, optional
            See skimage for supported filetypes.
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name
        filepath += '.' + filetype

        path = self.OUTPUT.joinpath(filepath)

        image = img_as_ubyte(image)
        imsave(path, image)

    def save_gif(
        self,
        images: List[ndarray],
        name: str,
        prefix_step=False,
        duration=100,
        loop=0
    ):
        """
        Dumps sequence of images onto hard drive as gif.
        File will be logged under logger's scope.

        Parameters
        ----------
        images : List[ndarray]
        name : str
        prefix_step : bool, optional
            Whether to append step prefix, by default False
        duration : int, optional
            Duration of a single frame in gif, by default 100 [ms]
        loop : int, optional
            How many times gif should be looped, by default 0, which means
            looping forever.
        """

        filepath = ''

        if prefix_step:
            filepath += self.__step_counter_to_string() + '-'

        filepath += name
        filepath += '.gif'

        path = self.OUTPUT.joinpath(filepath)

        images = [img_as_ubyte(image) for image in images]
        images = [Image.fromarray(image) for image in images]

        gif = images[0]

        gif.save(
            path,
            format='GIF',
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop
        )
