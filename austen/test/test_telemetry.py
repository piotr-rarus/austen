from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

from ..telemetry import Logger

sns.set()


def test_logger(logs_dir: Path):
    with Logger(logs_dir) as logger:
        logger.add_entry('foo', 'bar')

        entries = [
                ('a', 1),
                ('b', 2),
                ('c', 5)
        ]

        logger.add_entries(entries)

        expected_logs = {
            'foo': 'bar',
            'a': 1,
            'b': 2,
            'c': 5
        }

        assert expected_logs == logger.get_logs()


def test_pre_clear(logs_dir: Path):
    with Logger(logs_dir, clear_dir=True):

        # has new dir been created
        assert logs_dir.is_dir()

        # is this new dir completely empty
        assert not tuple(logs_dir.iterdir())


def test_child(logs_dir: Path):
    with Logger(logs_dir) as logger:
        logger.add_entry('foo', 'bar')
        with logger.get_child('child') as child_logger:
            child_logger.add_entry('foo-child', 'bar-child')

        child_dir = logs_dir.joinpath('child')

        # has new dir for child logger been created
        assert child_dir.exists()
        assert 'child' in logger.get_logs()


def test_log_func(logs_dir: Path):
    with Logger(logs_dir) as logger:
        logger.log_func(__add, kwargs={'x': 1, 'y': 2})

        assert '__add' in logger.get_logs()


def __add(x, y):
    return x + y


def test_save_obj(logs_dir: Path):
    with Logger(logs_dir) as logger:
        logger.save_obj(logger, 'logger')

        logger_path = logs_dir.joinpath('logger.joblib')
        assert logger_path.exists()

        logger.save_obj(logger, 'logger', prefix_step=True)

        logger_path = logs_dir.joinpath('01-logger.joblib')
        assert logger_path.exists()


def test_save_fig(logs_dir: Path, people: pd.DataFrame):
    with Logger(logs_dir) as logger:
        plt.figure(clear=True)

        figure = sns.barplot(
            x='name',
            y='height',
            data=people
        ).get_figure()

        plt.title('Height')

        logger.save_fig(figure, 'height', dpi=200)
        plt.close('all')

        plot_path = logs_dir.joinpath('height.png')
        assert plot_path.exists()


def test_save_csv(logs_dir: Path, people: pd.DataFrame):
    with Logger(logs_dir) as logger:
        logger.save_csv(people, 'people')

        people_path = logs_dir.joinpath('people.csv')
        assert people_path.exists()


def test_save_json(logs_dir: Path):
    with Logger(logs_dir) as logger:

        dictionary = {
            'foo': 'bar'
        }

        logger.save_json(dictionary, 'dictionary')

        path = logs_dir.joinpath('dictionary.json')
        assert path.exists()


def test_save_image(logs_dir: Path, astronaut: np.ndarray):
    with Logger(logs_dir) as logger:
        logger.save_image(astronaut, 'astronaut')

        astronaut_path = logs_dir.joinpath('astronaut.png')
        assert astronaut_path.exists()

        logger.save_image(astronaut, 'astronaut', prefix_step=True)

        astronaut_path = logs_dir.joinpath('01-astronaut.png')
        assert astronaut_path.exists()


def test_save_gif(logs_dir: Path, astronaut: np.ndarray):
    with Logger(logs_dir) as logger:
        images = []
        images.append(astronaut)

        for i in range(19):
            darker = images[i] * 0.9
            darker = darker.astype(np.uint8)
            images.append(darker)

        logger.save_gif(images, 'astronaut')

        astronaut_path = logs_dir.joinpath('astronaut.gif')
        assert astronaut_path.exists()

        logger.save_gif(images, 'astronaut', prefix_step=True)

        astronaut_path = logs_dir.joinpath('01-astronaut.gif')
        assert astronaut_path.exists()
