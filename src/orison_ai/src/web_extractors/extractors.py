import requests
from bs4 import BeautifulSoup
from orison_ai.src.database.models import GoogleScholarDB, Publication


def get_google_scholar_info(profile_link):
    if profile_link == "":
        return None
    # # Prepare the search query
    # query = f'{name} {" ".join(keywords)} site:scholar.google.com'

    # # Fetch search results from Google
    headers = {"User-Agent": "Mozilla/5.0"}
    # url = f"https://www.google.com/search?q={query}"
    # response = requests.get(url, headers=headers)
    # soup = BeautifulSoup(response.text, "html.parser")

    # Find the link to the Google Scholar profile
    # profile_link = None
    # for link in soup.find_all("a"):
    #     href = link.get("href")
    #     if href and "scholar.google.com/citations" in href:
    #         profile_link = href
    #         break

    # if not profile_link:
    #     return None

    # profile_link = "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"
    # Fetch data from the Google Scholar profile
    response = requests.get(profile_link, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract basic information
    name = soup.find("div", {"id": "gsc_prf_in"}).text.strip()
    designation = soup.find("div", {"class": "gsc_prf_il"}).text.strip()

    # Extract number of citations
    citations = soup.find("td", {"class": "gsc_rsb_std"}).text.strip()

    # Extract publications and their citations
    publications = []
    for row in soup.find_all("tr", {"class": "gsc_a_tr"}):
        title = row.find("a", {"class": "gsc_a_at"}).text.strip()
        authors = row.find("div", {"class": "gs_gray"}).text.strip()
        cited_by = row.find("a", {"class": "gsc_a_ac"}).text.strip()
        publications.append(
            Publication(title=title, authors=authors, citations_received=cited_by)
        )

    return GoogleScholarDB(
        name=name,
        designation=designation,
        total_citations=citations,
        publications=publications,
    )


def get_portfolio_info(profile_link):
    # Make a GET request to the website
    response = requests.get(profile_link)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {profile_link}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links on the page
    links = soup.find_all("a", href=True)

    # Initialize an empty list to store the content from each page
    content_list = []

    # Iterate over each link
    for link in links:
        page_url = profile_link + link["href"]

        # Make a GET request to the page URL
        page_response = requests.get(page_url)
        if page_response.status_code != 200:
            print(f"Failed to fetch URL: {page_url}")
            continue

        # Parse the HTML content of the page
        page_soup = BeautifulSoup(page_response.content, "html.parser")

        # Extract the text content of the page
        page_content = page_soup.get_text(separator="\n")

        # Append the page content to the list
        content_list.append(page_content)

    # Join all the content from different pages into a single text separated by new lines
    website_content = "\n".join(content_list)

    return website_content


if __name__ == "__main__":
    # Example usage
    name = input("Enter the person's name: ")
    keywords = input(
        "Enter keywords to refine the search (separated by comma): "
    ).split(",")

    info = get_google_scholar_info(name, keywords)
    if info:
        print(f"Name: {info['name']}")
        print(f"Affiliation: {info['affiliation']}")
        print(f"Total Citations: {info['citations']}")
        print("Publications:")
        for publication in info["publications"]:
            print(f"  Title: {publication['title']}")
            print(f"  Authors: {publication['authors']}")
            print(f"  Citations: {publication['cited_by']}")
            print()
    else:
        print("No information found.")
