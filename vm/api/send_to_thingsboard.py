import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from vm.api.mqtt_client import send_telemetry


class PredictionHandler(FileSystemEventHandler):
    def on_created(self, event):
        # ignore directories
        if event.is_directory:
            return

        src = Path(event.src_path)
        if src.suffix.lower() != '.json':
            return

        # small delay to ensure file is fully written
        time.sleep(0.2)
        try:
            with open(src, 'r') as f:
                data = json.load(f)
            send_telemetry(data)
            print(f"Sent telemetry for {src.name}")
        except Exception as e:
            print(f"Failed to send telemetry for {src}: {e}")


def watch_predictions(directory: str = "logs/predictions"):
    p = Path(directory)
    p.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    handler = PredictionHandler()
    observer.schedule(handler, str(p), recursive=False)
    observer.start()
    print(f"Watching {p} for new prediction JSON files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='logs/predictions', help='Directory to watch')
    args = parser.parse_args()

    watch_predictions(args.dir)
