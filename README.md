# Austen

Nested telemetry logger.
Perfect for printing algorithms. Dumps into `json` file.

## Features

Core idea behind `Austen` is to have algorithm call stack logged with exact arguments.These are stored in a dictionary and dumped into `json`.
Additionally `Austen` handles dumps of some additional file types. These include:

- objects (using `joblib`)
- plots
- sheets
- dictionaries
- images
- GIFs

All files will be dumped in a folder structure, that corresponds to your algorithm (folder per branch).

## Getting started

```shell
pip install austen
```

## How to use

### Manual entries

We'll start by importing `Logger` class from the library.

```py
from austen import Logger
```

Now we can instantiate `Logger` object.

```py
logger = Logger(output='logs')
```

By `output` argument you can specify base directory for subsequent dumps.
It will dump to your current working directory (relative path). If you want to dump it somewhere else, just put absolute path in there. Now it'll dump to `./logs/`.

Now let's add some entry to our logger.

```py
logger.add_entry('foo', 'bar')
```

You can also add multiple entries at once.

```py
entries = [
    ('a', 1),
    ('b', 2),
    ('c', 5)
]

logger.add_entries(entries)
```

Entries are stored in a dictionary. This means that key has to be hashable.
If you think something is appropriate for `json` format, just push it to logger.

### Wrapping function calls

Let's log some functions.

```py
def add(x, y):
    return x + y

def foo(logger:Logger, x, y):
    return logger.log_func(
        func=add,
        kwargs={'x': x, 'y': y}
    )
```

### Other file types

Now let's see how we can dump files.

#### Objects

```py
logger.save_obj(logger, name='logger')
```

- `name` denotes name of your file. File extensions are handled automatically.

Objects are serialized using `joblib`.

#### Plots, figures

```py
logger.save_fig(figure, name='foo')
```

Your figure should implement `savefig` interfaces from `matplotlib`.
It's de facto standard for plots in Python.

```shell
logs/foo.png
```

#### Sheets

```py
with open('foo.csv') as csv:
    frame = pd.read_csv(csv)
    logger.save_csv(frame, name='foo')
```

Your frame should implement `to_csv` interface from `pandas`.
I guess everyone's just using `pandas` nowadays to handle sheets.

```shell
logs/foo.csv
```

#### Dictionaries

Dictionaries are saved in `json` format.

```py
logger.save_json(dictionary, name='dictionary')
```

#### Images

```py
logger.save_image(image, name='astronaut')
logger.save_image(image, name='coffee')
```

We use `skimage.io.imsave` to handle images. Images are saved as `png`.

```shell
logs/astronaut.png
logs/coffee.png
```

```py
logger.save_image(image, name='astronaut', prefix_step=True)
logger.save_image(image, name='coffee', prefix_step=True)
```

You can also use `prefix_step` parameter to append some ordering prefix.
Guess now it's time to talk about `steps`. It's a private counter inside your logger, that's incremented each time you use `log_func`. So later, when you're viewing your files, you can order them by name (which is default for most OS). It'll result in following structure:

```shell
logs/01_astronaut.png
logs/02_coffee.png
```

#### GIFs

```py
logger.save_gif(images, 'your-sequence')
```

GIFs are dumped using `PIL`.

### Time to get a bit crazy (nesting)

```py
with Logger(logs_dir) as logger:
    logger.add_entry('x', 0)

    with logger.get_child('bar') as child_logger:
        child_logger.add_entry('y', 1)
```

You can nest your loggers using `get_child` method. We recommend you wrap your loggers with scopes, so they're easier to manage.

- once logger is disposed, it'll merge to the parent logger.
- once root logger is disposed, it'll dump all your telemetry in `json` file

Another tip would be to write code in 'scope per branch' fashion - you do single method, where you use only single logger. You can pass parent logger with an argument.

## Author

- Piotr Rarus piotr.rarus@gmail.com
