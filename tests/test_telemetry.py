# flake8: noqa
from pathlib import Path

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from skimage.io import imread

from austen import Logger


sns.set()
logs_dir = Path('logs')


def test_logger():
    with Logger(logs_dir) as logger:
        logger.add_entry('foo', 'bar')

        entries = [
                ('a', 1),
                ('b', 2),
                ('c', 5)
        ]

        logger.add_entries(entries)
        logger.add_entry('a', 3)


def test_pre_clear():
    with Logger(logs_dir, clear_dir=True) as logger:
        image = imread(Path('tests/astronaut.png'))
        logger.save_image(image, 'astronaut')


def test_child():
    with Logger(logs_dir) as logger:
        logger.add_entry('foo', 'bar')
        with logger.get_child('bar') as child_logger:
            child_logger.add_entry('foochild', 'barchild')


def add(x, y):
    return x + y


def test_log_func():
    with Logger(logs_dir) as logger:
        logger.log_func(add, kwargs={'x': 1, 'y': 2})


def test_save_obj():
    with Logger(logs_dir) as logger:
        logger.save_obj(logger, 'logger')


def test_save_fig():
    with Logger(logs_dir) as logger:
        with open(Path('tests/people.csv')) as csv:
            frame = pd.read_csv(csv)

            plt.figure(clear=True)

            figure = sns.barplot(
                x='name',
                y='height',
                data=frame
            ).get_figure()

            plt.title('Height')

            logger.save_fig(figure, 'height')
            plt.close('all')


def test_save_csv():
    with Logger(logs_dir) as logger:
        with open(Path('tests/people.csv')) as csv:
            frame = pd.read_csv(csv)
            logger.save_csv(frame, 'people')


def test_save_image():
    with Logger(logs_dir) as logger:
        image = imread(Path('tests/astronaut.png'))
        logger.save_image(image, 'astronaut')

