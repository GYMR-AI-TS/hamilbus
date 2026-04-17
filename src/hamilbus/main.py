from .web import run_server


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
