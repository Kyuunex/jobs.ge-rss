#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, make_response, redirect
from feedgen.feed import FeedGenerator

app = Flask(__name__)


def get_url_contents(urle):
    try:
        response = requests.get(urle)
        response.raise_for_status()  # Raise an exception for any HTTP error
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching data from the URL:", e)
        return None


def parse_data(html_content):
    if not html_content:
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    temp_table = soup.find('table', {'id': 'temp_table'})
    if not temp_table:
        print("Table with ID 'temp_table' not found.")
        return None

    table_datae = []
    for rowe in temp_table.find_all('tr'):
        row_data = []
        for cell in rowe.find_all(['td', 'th']):
            for href in cell.find_all(['a']):
                if "?view=jobs&id=" in href.get('href'):
                    row_data.append("https://jobs.ge" + href.get('href'))
                    break
            data = cell.get_text().strip()
            if len(data) != 0:
                row_data.append(data)
        table_datae.append(row_data)

    return table_datae


@app.route('/')
@app.route('/<path:endpoint>')
def gen_rss(endpoint=None):
    if not endpoint:
        endpoint = request.full_path

    if endpoint[0] != "/":
        endpoint = "/" + endpoint

    if not endpoint.endswith("&for_scroll=yes"):
        endpoint += "&for_scroll=yes"

    url = f"https://jobs.ge{endpoint}"
    print(url)
    content = get_url_contents(url)
    table_data = parse_data(content)

    feed = FeedGenerator()
    feed.title("ჯობს.გე - ვაკანსიები")
    feed.description("საქართველოში სამუშაოს ძიება აქ იწყება")
    feed.link(href=request.host_url)

    if table_data:
        for row in table_data:
            feed_entry = feed.add_entry()
            feed_entry.link(href=row[0])
            feed_entry.title(row[1])
            feed_entry.author(name=row[2])
            feed_entry.description(row[3] + " - " + row[4])
            # feed_entry.pubDate()
            feed_entry.guid(row[0])

    response = make_response(feed.rss_str())
    response.headers.set("Content-Type", "application/rss+xml; charset=utf-8")
    return response


@app.route('/favicon.ico')
def favicon():
    return redirect("https://jobs.ge/favicon.ico", code=302)


if __name__ == '__main__':
    app.run()





