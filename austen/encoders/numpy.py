import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """
    This class helps with converting numpy arrays into JSON format.

    Parameters
    ----------
    json : JSONEncoder
        Encoder object to handle JSON conversion.

    Returns
    -------
    NumpyEncoder
        New instance for numpy array JSON conversion.
    """

    def default(self, obj):
        """
        Converts numpy array into JSON dictionary.

        Parameters
        ----------
        obj : nd.array
            Numpy array to be converted into JSON.

        Returns
        -------
        dict
            Converted numpy array.
        """

        if isinstance(obj, np.ndarray):
            if obj.size < 20:
                return obj.tolist()
            else:
                return 'shape:' + str(obj.shape)

        if isinstance(obj, (np.int, np.float)):
            return str(obj)

        if type(obj) in [np.int8, np.int16, np.int32, np.int64]:
            return str(obj)

        if hasattr(obj, '__name__'):
            return obj.__name__

        return json.JSONEncoder.default(self, obj)
