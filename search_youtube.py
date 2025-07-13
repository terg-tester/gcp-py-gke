from playwright.sync_api import sync_playwright

def search_youtube(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Run in headless mode
        page = browser.new_page()
        try:
            page.goto("https://www.youtube.com", timeout=60000) # Increased timeout to 60 seconds
            page.wait_for_selector("input#search, [name=\"search_query\"]", timeout=60000) # Wait for either selector
            page.fill("input#search, [name=\"search_query\"]", query, timeout=60000)
            page.press("input#search, [name=\"search_query\"]", "Enter")
            page.wait_for_selector("ytd-video-renderer", timeout=60000)

            videos = page.query_selector_all("ytd-video-renderer")
            results = []
            for i, video in enumerate(videos):
                if i >= 5:  # Limit to 5 results
                    break
                title_element = video.query_selector("#video-title")
                url_element = video.query_selector("#video-title")
                if title_element and url_element:
                    title = title_element.text_content().strip()
                    url = url_element.get_attribute("href")
                    results.append({"title": title, "url": f"https://www.youtube.com{url}"})
            browser.close()
            return results
        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="error_screenshot.png")
            browser.close()
            return []

if __name__ == "__main__":
    print("Searching for new popular Russian pop music...")
    russian_pop_results = search_youtube("new popular russian pop music 2024 2025")
    for item in russian_pop_results:
        print(f"Title: {item['title']}\nURL: {item['url']}\n")

    print("Searching for Vladivostok Customs Outpost new music...")
    vladivostok_results = search_youtube("Vladivostok Customs Outpost new music")
    for item in vladivostok_results:
        print(f"Title: {item['title']}\nURL: {item['url']}\n")