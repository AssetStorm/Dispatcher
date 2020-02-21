import requests

if __name__ == "__main__":
    with open('example-article.md', 'rb') as eafp:
        response = requests.post(
            "http://localhost:8084/convert/markdown/markdown",
            files={"example-article.md": eafp})
        print(response.text)
