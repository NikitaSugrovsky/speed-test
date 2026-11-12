import argparse
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

REQUESTS_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT_SECONDS = 30


def parse_args():
    parser = argparse.ArgumentParser(
        description="Замер скорости скачивания по адресу: 10 последовательных запросов."
    )
    parser.add_argument("url", help="адрес файла, например https://example.com/big.jpg")
    return parser.parse_args()


def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"некорректный адрес: {url}")


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "speedtest/1.0"})
    size = 0
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
    elapsed = time.perf_counter() - started
    return size, elapsed


def main():
    args = parse_args()

    try:
        validate_url(args.url)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    total_bytes = 0
    total_time = 0.0

    for number in range(1, REQUESTS_COUNT + 1):
        try:
            size, elapsed = download(args.url)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            print(f"Запрос {number} завершился ошибкой: {error}", file=sys.stderr)
            return 1

        total_bytes += size
        total_time += elapsed
        print(f"Запрос {number:>2}: {size / 1024 / 1024:.2f} МБ за {elapsed:.3f} с")

    if total_bytes == 0 or total_time == 0:
        print("Сервер не вернул данных, скорость посчитать нельзя", file=sys.stderr)
        return 1

    average_time = total_time / REQUESTS_COUNT
    speed_mbit = total_bytes * 8 / total_time / 1_000_000

    print()
    print(f"Среднее время запроса: {average_time:.3f} с")
    print(f"Скачано всего: {total_bytes / 1024 / 1024:.2f} МБ")
    print(f"Скорость скачивания: {speed_mbit:.2f} Мбит/с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
