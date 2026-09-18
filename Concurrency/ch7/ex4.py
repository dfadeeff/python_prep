import time
import requests

from concurrent.futures import ThreadPoolExecutor


def get_status_code(url: str) -> int:
    response = requests.get(url)
    return response.status_code


if __name__ == "__main__":
    start = time.time()

    with ThreadPoolExecutor() as pool:
        urls = ['https://www.example.com' for _ in range(1000)]
        results = pool.map(get_status_code, urls)
        for result in results:
            print(result)

    end = time.time()
    print(f'finished async requests in {end - start:.4f} second(s)')

    print("Now sync")

    start = time.time()
    urls = ['https://www.example.com' for _ in range(1000)]
    for url in urls:
        print(get_status_code(url))
    end = time.time()
    print(f'finished requests in {end - start:.4f} second(s)')
