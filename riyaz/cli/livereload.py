import contextlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@contextlib.contextmanager
def live_reload(loader, path):

    def callback(event):
        if event.is_directory:
            return

        loader.load()

    observer = get_observer(callback, path)

    observer.start()
    try:
        yield observer
    finally:
        observer.stop()
        observer.join()


def get_observer(callback, path):
    observer = Observer()
    handler = FileSystemEventHandler()

    handler.on_any_event = callback
    observer.schedule(handler, path, recursive=True)

    return observer
