from modules.states.main import MainProcessing
import os

CONTAINER_ID = os.getenv("CONTAINER_ID")
VIDEO_PATH = os.getenv(f'VIDEO_PATH_{CONTAINER_ID}')


def main():
    process = MainProcessing(
        CONTAINER_ID,
        VIDEO_PATH
    )
    process.run()

if __name__ == "__main__":
    main()


