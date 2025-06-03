import requests
import csv
import time

API_KEY = "ec114db0fac06fc1a5493c720bf6ac75"
DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def fetch_posters(total_pages=1000, delay=0.25):
    """
    total_pages: kaç sayfa çekeceğin (max 1000 sayfa * 20 film = 20k film)
    delay: her istekte bekleme süresi (rate limit için)
    """
    posters = []
    for page in range(1, total_pages+1):
        params = {
            "api_key": API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": page
        }
        resp = requests.get(DISCOVER_URL, params=params)
        data = resp.json()
        for movie in data.get("results", []):
            path = movie.get("poster_path")
            if path:
                posters.append(IMAGE_BASE + path)
        print(f"Fetched page {page}/{total_pages}, collected {len(posters)} posters so far")
        time.sleep(delay)
        if page >= data.get("total_pages", 0):
            break
    return posters

def save_csv(posters, filename="posters.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["poster_url"])
        for url in posters:
            writer.writerow([url])
    print(f"Saved {len(posters)} URLs to {filename}")

if __name__ == "__main__":
    # TMDB API maksimumda 1000 sayfa (20k film) dönmeye izin veriyor
    posters = fetch_posters(total_pages=1000, delay=0.25)
    save_csv(posters)
