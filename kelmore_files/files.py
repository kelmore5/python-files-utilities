from __future__ import annotations

import datetime
import os
import shutil
import typing
from typing import Union, Any, IO, Type, Optional, List, Tuple

import dill


class FileCheck:

    @staticmethod
    def exists(full_path: str) -> bool:
        return os.path.exists(full_path)

    @staticmethod
    def has_quarry(full_path: str, quarry: str) -> bool:
        """ prec: file is a valid path, quarry is a string
                    postc: returns True if the quarry is in the file, false otherwise"""
        text: Optional[str] = FileIO.read(full_path)
        if text:
            return quarry in text

        return False

    @staticmethod
    def is_directory(full_path: str) -> bool:
        return os.path.isdir(full_path)

    @staticmethod
    def is_file(full_path: str) -> bool:
        return os.path.isfile(full_path)

    @staticmethod
    def is_link(full_path: str) -> bool:
        return os.path.islink(full_path)


class FileCount:

    @staticmethod
    def characters(full_path: str) -> Optional[int]:
        if FileCheck.exists(full_path):
            count: int = 0
            with FileIO.open(full_path) as file:
                for line in file:
                    count += len(line)

            return count

        return None

    @staticmethod
    def lines(full_path: str) -> Optional[int]:
        lines: Optional[List[str]] = FileTransform.lines(full_path)
        return len(lines) if lines else None

    @staticmethod
    def words(full_path: str) -> Optional[int]:
        words: Optional[List[str]] = FileTransform.words(full_path)
        return len(words) if words else None


class FileDirectories:

    @staticmethod
    def clear_all(directory: str) -> None:
        FileDirectories._raise_error_if_file(directory)
        FileDirectories.clear(directory, recursive=True)

    @staticmethod
    def clear(directory: str, recursive: bool = False) -> None:
        FileDirectories._raise_error_if_file(directory)
        if not FileCheck.exists(directory):
            return

        if recursive:
            children: typing.List[str] = FileDirectories.children(directory, include_full_path=True)
            for full_path in children:
                if FileCheck.is_link(full_path):
                    FileIO.unlink(full_path)
                elif FileCheck.is_file(full_path):
                    FileIO.delete(full_path)
                else:
                    FileDirectories.delete(full_path, recursive=True)
        else:
            files: List[str] = FileDirectories.files(directory)
            for file_name in files:
                full_path: str = FileTools.concat(directory, file_name)
                FileIO.delete(full_path)

    @staticmethod
    def clear_files(directory: str) -> None:
        FileDirectories._raise_error_if_file(directory)
        FileDirectories.clear(directory)

    @staticmethod
    def children(directory: str,
                 recursive: bool = False,
                 include_full_path: bool = False,
                 extension: str = None) -> List[str]:
        FileDirectories._raise_error_if_file(directory)

        children: List[str] = []
        for (current_directory, directories, file_names) in os.walk(directory):
            if include_full_path:
                directories = [FileTools.concat(current_directory, x) for x in directories]
                file_names = [FileTools.concat(current_directory, x) for x in file_names]

            if extension:
                file_names = FileTransform.filter_by_extension(file_names, extension)

            children.extend(directories)
            children.extend(file_names)

            if not recursive:
                break

        return children

    @staticmethod
    def create(full_path: str) -> Optional[str]:
        """
        Checks for existence of a file path and if it does not exist, creates it.
            Returns the created path
        :param full_path: (str) The path to be checked and/or created. If path is None,
            Files will check for an internal path to use.
            If none is found, a ValueError will be raised
        :return: The confirmed path
        """
        if not FileCheck.exists(full_path):
            os.makedirs(full_path)
        elif os.path.isfile(full_path):
            return None

        return full_path

    @staticmethod
    def delete(directory: str, recursive: bool = False) -> None:
        if FileCheck.is_link(directory):
            FileIO.unlink(directory)
        elif FileCheck.is_file(directory):
            FileIO.delete(directory)

        if recursive:
            shutil.rmtree(directory, ignore_errors=True)
        else:
            os.rmdir(directory)

    @staticmethod
    def directories(directory: str,
                    recursive: bool = False,
                    include_full_path: bool = False) -> List[str]:
        FileDirectories._raise_error_if_file(directory)

        directories: List[str] = []
        for root in os.walk(directory):
            child_directories: List[str] = root[1]
            if include_full_path:
                parent: str = root[0]
                child_directories = [FileTools.concat(parent, x) for x in child_directories]

            directories.extend(child_directories)
            if not recursive:
                break

        return directories

    @staticmethod
    def files(directory: str,
              recursive: bool = False,
              include_full_path: bool = False,
              extension: str = None) -> List[str]:
        FileDirectories._raise_error_if_file(directory)

        files: List[str] = []
        for root in os.walk(directory):
            child_files: List[str] = root[2]
            if include_full_path:
                parent: str = root[0]
                child_files = [FileTools.concat(parent, x) for x in child_files]

            if extension:
                child_files = FileTransform.filter_by_extension(child_files, extension)

            files.extend(child_files)
            if not recursive:
                break

        return files

    @staticmethod
    def parent(full_path: str, depth: int = 1) -> Optional[str]:
        if not FileCheck.exists(full_path):
            return None

        while depth > 0:
            full_path = os.path.dirname(full_path)
            depth -= 1

        return full_path

    @staticmethod
    def _raise_error_if_file(full_path: str) -> None:
        if FileCheck.is_file(full_path):
            raise ValueError('Given path must be a directory, not a file')


class FileFind:

    @staticmethod
    def line_number(full_path: str, word: str) -> Optional[int]:
        """ prec: file is a valid path, word is a string
                    postc: returns the line number of the word in the file"""
        if FileCheck.is_file(full_path):
            in_pipe: IO = open(full_path, "r")

            line_number: int = 0
            for line in in_pipe:
                line_number += 1
                if word in line.split():
                    return line_number

            return -1

        return None


class FileIO:

    @staticmethod
    def copy(donor_path: str,
             recipient_path: str,
             overwrite: bool = False) -> bool:
        if FileCheck.is_directory(donor_path):
            raise ValueError('The donor path cannot be a folder')

        if FileCheck.is_directory(recipient_path):
            raise ValueError('The recipient path cannot be a folder')

        if not FileCheck.exists(donor_path):
            raise IOError('The given donor path does not exist')

        if not overwrite and FileCheck.exists(recipient_path):
            raise IOError('The given recipient path already exists')

        donor: str = FileIO.read(donor_path)
        FileIO.save(recipient_path, donor, overwrite=overwrite)

        return True

    @staticmethod
    def delete(full_path: str) -> None:
        FileIO._raise_error_if_directory(full_path)
        if FileCheck.exists(full_path):
            os.remove(full_path)

    @staticmethod
    def open(full_path: str,
             write: bool = False,
             append: bool = False,
             binary: bool = False,
             **kwargs: Any) -> Union[IO, None]:
        FileIO._raise_error_if_directory(full_path)

        if write:
            command: str = 'wb' if binary else 'w'
        elif append:
            command = 'ab' if binary else 'a+'
        else:
            command = 'rb' if binary else 'r'

        return open(full_path, command, **kwargs)

    @staticmethod
    def read(full_path: str) -> Optional[str]:
        if FileCheck.is_file(full_path):
            with FileIO.open(full_path) as file:
                return file.read()

        return None

    @staticmethod
    def read_object(full_path: str) -> Union[Any, None]:
        """ prec: filename is a string
                    postc: returns the Python object saved in the file"""
        FileIO._raise_error_if_directory(full_path)
        if not os.path.isfile(full_path):
            return None

        with FileIO.open(full_path, binary=True) as file:
            return dill.load(file)

    @staticmethod
    def save(full_path: str,
             text: str,
             overwrite: bool = False) -> None:
        if not overwrite and FileCheck.exists(full_path):
            raise IOError('The given file path already exists')

        with FileIO.open(full_path, write=True) as file:
            file.write(text)

    @staticmethod
    def save_object(full_path: str,
                    obj: Any,
                    overwrite: bool = False) -> None:
        """ prec: obj is any python variable and filename is a string
                    postc: saves the object to a file"""
        FileIO._raise_error_if_directory(full_path)

        if not overwrite and FileCheck.exists(full_path):
            raise IOError('The given file path already exists')

        with FileIO.open(full_path, write=True, binary=True) as file:
            dill.dump(obj, file)

    @staticmethod
    def text(full_path: str) -> Optional[str]:
        return FileIO.read(full_path)

    @staticmethod
    def touch(full_path: str, overwrite: bool = False) -> None:
        FileIO.save(full_path, '', overwrite=overwrite)

    @staticmethod
    def unlink(full_path: str) -> None:
        os.unlink(full_path)

    @staticmethod
    def _raise_error_if_directory(full_path: str) -> None:
        if FileCheck.is_directory(full_path):
            raise ValueError('Given path cannot be a directory')


class FileNames:

    @staticmethod
    def stamp(file_path: str) -> str:
        split_file: Tuple[str] = os.path.splitext(file_path)
        return f'{split_file[0]} {FileTools.timestamp()}{split_file[1]}'


class FileTransform:

    @staticmethod
    def filter_by_extension(file_paths: List[str], extension: str) -> List[str]:
        if not extension.startswith('.'):
            extension = f'.{extension}'

        filtered_file_names: List[str] = []
        for file_path in file_paths:
            split_file: Tuple[str, str] = os.path.splitext(file_path)
            if split_file[1] == extension:
                filtered_file_names.append(file_path)

        return filtered_file_names

    @staticmethod
    def lines(full_path: str) -> Optional[List[str]]:
        if FileCheck.exists(full_path):
            with FileIO.open(full_path) as file:
                return [line for line in file]

        return None

    @staticmethod
    def words(full_path: str) -> Optional[List[str]]:
        if FileCheck.exists(full_path):
            with FileIO.open(full_path) as file:
                output: List[str] = []
                for line in file:
                    output.extend(line.split(' '))

                return output

        return None


class FileTools:
    check: Type[FileCheck] = FileCheck
    count: Type[FileCount] = FileCount
    directories: Type[FileDirectories] = FileDirectories
    find: Type[FileFind] = FileFind
    io_: Type[FileIO] = FileIO
    names: Type[FileNames] = FileNames
    transform: Type[FileTransform] = FileTransform

    @staticmethod
    def concat(*paths: str) -> str:
        return os.path.join(*paths)

    @staticmethod
    def timestamp() -> str:
        return datetime.datetime.today().strftime('%Y-%m-%d %H.%M.%S')


class DirectoryWrapper:
    directory: str

    def __init__(self, full_path: str):
        if FileTools.check.exists(full_path) and not FileTools.check.is_directory(full_path):
            raise ValueError('Give path must be a path to a directory')

    def clear_all(self) -> None:
        FileDirectories.clear_all(self.directory)

    def clear(self, recursive: bool = False) -> None:
        FileDirectories.clear(self.directory, recursive=recursive)

    def clear_files(self) -> None:
        FileDirectories.clear_files(self.directory)

    def children(self,
                 recursive: bool = False,
                 include_full_path: bool = False) -> List[str]:
        return FileDirectories.children(self.directory,
                                        recursive=recursive,
                                        include_full_path=include_full_path)

    def concat(self, *paths: str) -> Union[FileWrapper, DirectoryWrapper]:
        full_path: str = os.path.join(self.directory, *paths)
        if FileTools.check.is_directory(full_path):
            return DirectoryWrapper(full_path)
        else:
            return FileWrapper(full_path)

    def create(self) -> Optional[str]:
        """
        Checks for existence of a file path and if it does not exist, creates it.
            Returns the created path
        :return: The confirmed path
        """
        return FileDirectories.create(self.directory)

    def delete(self, recursive: bool = False) -> None:
        FileDirectories.delete(self.directory, recursive=recursive)

    def directories(self,
                    recursive: bool = False,
                    include_full_path: bool = False) -> List[str]:
        return FileDirectories.directories(self.directory,
                                           recursive=recursive,
                                           include_full_path=include_full_path)

    def files(self,
              recursive: bool = False,
              include_full_path: bool = False) -> List[str]:
        return FileDirectories.files(self.directory,
                                     recursive=recursive,
                                     include_full_path=include_full_path)

    def parent(self, depth: int = 1) -> Optional[str]:
        return FileDirectories.parent(self.directory, depth=depth)


class FileWrapperContainerBase:
    _wrapper: FileWrapper

    def __init__(self, wrapper: FileWrapper):
        self._wrapper = wrapper

    def full_path(self) -> str:
        return self._wrapper.full_path

    def name(self) -> str:
        return self._wrapper.name

    def path(self) -> str:
        return self._wrapper.path


class FileWrapperCheck(FileWrapperContainerBase):

    def exists(self) -> bool:
        return FileCheck.exists(self.full_path())

    def has_quarry(self, quarry: str) -> bool:
        """ prec: file is a valid path, quarry is a string
                    postc: returns True if the quarry is in the file, false otherwise"""
        return FileCheck.has_quarry(self.full_path(), quarry)


class FileWrapperCount(FileWrapperContainerBase):

    def characters(self) -> Optional[int]:
        return FileCount.characters(self.full_path())

    def lines(self) -> Optional[int]:
        return FileCount.lines(self.full_path())

    def words(self) -> Optional[int]:
        return FileCount.words(self.full_path())


class FileWrapperFind(FileWrapperContainerBase):

    def line_number(self, word: str) -> Optional[int]:
        return FileTools.find.line_number(self.full_path(), word)


class FileWrapperIO(FileWrapperContainerBase):

    def copy(self, recipient_path: str, overwrite: bool = False) -> bool:
        return FileTools.io_.copy(self.full_path(), recipient_path, overwrite=overwrite)

    def delete(self) -> None:
        FileTools.io_.delete(self.full_path())

    def open(self,
             write: bool = False,
             append: bool = False,
             binary: bool = False,
             **kwargs: Any) -> Union[IO, None]:
        return FileTools.io_.open(self.full_path(),
                                  write=write,
                                  append=append,
                                  binary=binary,
                                  **kwargs)

    def overwrite(self, text: str) -> None:
        with self.open(write=True) as file:
            file.write(text)

    def overwrite_by_file(self, donor_path: str) -> None:
        FileTools.io_.copy(donor_path, self.full_path(), overwrite=True)

    def read(self) -> Optional[str]:
        return FileTools.io_.read(self.full_path())

    def read_object(self) -> Union[Any, None]:
        return FileTools.io_.read_object(self.full_path())

    def save(self,
             text: str,
             overwrite: bool = False) -> None:
        FileTools.io_.save(self.full_path(), text, overwrite=overwrite)

    def save_object(self,
                    obj: Any,
                    overwrite: bool = False) -> None:
        """ prec: obj is any python variable and filename is a string
                    postc: saves the object to a file"""
        FileTools.io_.save_object(self.full_path(), obj, overwrite=overwrite)

    def text(self) -> Optional[str]:
        return FileTools.io_.text(self.full_path())

    def touch(self, overwrite: bool = False) -> None:
        FileTools.io_.touch(self.full_path(), overwrite=overwrite)

    def unlink(self) -> None:
        FileTools.io_.unlink(self.full_path())


class FileWrapperNames(FileWrapperContainerBase):

    def stamp(self) -> FileWrapper:
        return FileWrapper(FileTools.names.stamp(self.full_path()))


class FileWrapperTransform(FileWrapperContainerBase):

    def lines(self) -> Optional[List[str]]:
        return FileTransform.lines(self.full_path())

    def words(self) -> Optional[List[str]]:
        return FileTransform.words(self.full_path())


class FileWrapper:
    full_path: str

    path: str
    name: str

    check: FileWrapperCheck
    count: FileWrapperCount
    find: FileWrapperFind
    io_: FileWrapperIO
    names: FileWrapperNames
    transform: FileWrapperTransform

    def __init__(self, full_path: str):
        if FileCheck.exists(full_path) and not FileTools.check.is_file(full_path):
            raise ValueError('Give path must be a path to a file')

        self.full_path = full_path

        self.path = os.path.dirname(self.full_path)
        self.name = os.path.basename(self.full_path)

        self.check = FileWrapperCheck(self)
        self.count = FileWrapperCount(self)
        self.find = FileWrapperFind(self)
        self.io_ = FileWrapperIO(self)
        self.names = FileWrapperNames(self)
        self.transform = FileWrapperTransform(self)

    def __copy__(self) -> FileWrapper:
        return FileWrapper(self.full_path)

    def parent(self, depth: int = 1) -> Optional[str]:
        return FileDirectories.parent(self.full_path, depth=depth)
