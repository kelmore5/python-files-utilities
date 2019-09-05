# Files

Files is a small library of file utility functions compiled for personal needs. There's 
nothing too fancy nor anything you can't find from another library, but Files consists of
smaller functions to be used rather than relying on larger packages.

The function include things like exists, copy, read, overwrite, delete, delete recursive, get 
all files in a folder, word count, line count, etc.

## Personal Note

Files is only on Github because I reference it in other projects. I don't have any plans 
to maintain this project, but I will update it from time to time. 

# Install

You can install this project directly from Github via:

```bash
$ pip3.7 install git+https://github.com/kelmore5/python-file-utilities.git
```

## Dependencies

- Python 3.7

# Usage

Once installed, you can import the main class like so:

    >>> from kelmore_files import FileTools as Files
    >>>
    >>> x = '/home/username/Downloads'                          # Some folder
    >>> y = '/home/username/Downloads/download.txt'             # Some file
    >>>
    >>> Files.check.exists(x)                                   # True
    >>> Files.check.is_directory(x)                             # True
    >>> Files.check.is_file(y)                                  # True
    >>> Files.directories.children(y)                           # ['download.txt']
    >>> Files.io_.copy(y, '/home/username/Downloads/copy.txt')  # None
    >>> Files.io_.delete('/home/username/Downloads/copy.txt')   # None
    >>> Files.io_.text(y)                                       # "hey look I'm a download"
    .
    .
    .

# Documentation

To be updated
