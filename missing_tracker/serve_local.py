from pathlib import Path
import traceback

LOG_PATH = Path(__file__).resolve().parent / "local_server.log"


def write_log(message: str) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


try:
    write_log("Starting local server bootstrap")
    from app import create_app

    app = create_app()
    write_log("App created successfully")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
except Exception:
    write_log(traceback.format_exc())
    raise
