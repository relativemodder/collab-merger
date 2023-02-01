import os
import pywintypes
from typing import Any, Union, List, Optional, Tuple
from win32gui import GetDesktopWindow, GetOpenFileNameW, GetSaveFileNameW, FindWindowEx
from win32con import OFN_EXPLORER, OFN_ALLOWMULTISELECT

def open_file_dialog(
    hWnd: Any = None,
    title: str = None,
    directory: str = os.getcwd(),
    default_name: str = "",
    default_ext: str = "",
    ext: List[Tuple[str, str]] = None,
    multiselect: bool = False,
) -> Union[str, List[str], None]:
    """Open a file open dialog at a specified directory.

    :param title: Dialog title.
    :param directory: Directory to open file dialog in.
    :param default_name: Default file name.
    :param default_ext: Default file extension. Only letters, no dot.
    :param ext: List of available extension description + name tuples,
                e.g. [(JPEG Image, jpg), (PNG Image, png)].
    :param multiselect: Allow multiple files to be selected.
    :return: Path to a file to open if multiselect=False.
             List of the paths to files which should be opened if multiselect=True.
             None if file open dialog canceled.
    :raises IOError: File open dialog failed.
    """

    # https://programtalk.com/python-examples/win32gui.GetOpenFileNameW/

    flags = OFN_EXPLORER
    if multiselect:
        flags = flags | OFN_ALLOWMULTISELECT

    if ext is None:
        ext = "All Files\0*.*\0"
    else:
        ext = "".join([f"{name}\0*.{extension}\0" for name, extension in ext])

    try:
        file_path, _, _ = GetOpenFileNameW(
            hwndOwner=hWnd,
            InitialDir=directory,
            File=default_name,
            Flags=flags,
            Title=title,
            MaxFile=2 ** 16,
            Filter=ext,
            DefExt=default_ext,
        )

        paths = file_path.split("\0")

        if len(paths) == 1:
            return paths[0]
        else:
            for i in range(1, len(paths)):
                paths[i] = os.path.join(paths[0], paths[i])
            paths.pop(0)

        return paths

    except pywintypes.error as e:  # noqa
        if e.winerror == 0:
            return
        else:
            raise IOError()