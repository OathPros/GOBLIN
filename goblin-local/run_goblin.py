import threading
import time
from goblin.data_store import ensure_data_files
from goblin.dictionary import ensure_wordnet
from goblin.server import run_server
from goblin.desktop import run_desktop

if __name__ == "__main__":
    ensure_data_files()
    ensure_wordnet()
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(0.8)
    run_desktop()
