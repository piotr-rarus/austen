from pathlib import Path
from shutil import rmtree
from typing import Generator

import pandas as pd
from numpy import ndarray
from pytest import fixture
from skimage.io import imread

__LOGS_DIR = Path('logs')
__ASTRONAUT_PNG_PATH = Path('austen/test/astronaut.png')
__PEOPLE_CSV_PATH = Path('austen/test/people.csv')


def __reset_dir(path: Path):
    if path.is_dir:
        rmtree(str(path), ignore_errors=True)


@fixture()
def logs_dir() -> Generator[Path, None, None]:
    yield __LOGS_DIR
    __reset_dir(__LOGS_DIR)


@fixture(scope='session')
def astronaut() -> ndarray:
    astronaut = imread(__ASTRONAUT_PNG_PATH)
    return astronaut


@fixture(scope='session')
def people() -> pd.DataFrame:
    with open(__PEOPLE_CSV_PATH) as csv:
        people = pd.read_csv(csv)
        return people
