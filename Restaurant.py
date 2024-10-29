import time
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_restaurants():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('https://www.google.com/maps/search/best+restaurants+near+me+nagpur')

        try:
            page.wait_for_selector('div.lv7K9c', timeout=5000)
            page.click('div.lv7K9c')  
            print("Clicked on 'Use precise location' button")
        except Exception as e:
            print(f"Error clicking 'Use precise location': {e}")

        try:
            page.context.grant_permissions(["geolocation"])
            page.set_geolocation({"latitude": 21.155702, "longitude": 79.085236})  
            print("Location permissions granted")
        except Exception as e:
            print(f"Error with location permissions: {e}")

        page.wait_for_selector('.Nv2PK')
        time.sleep(2) 

        # Extract restaurant data
        restaurants = extract_restaurant_data(page)
        
        # Save the restaurant data to a CSV file
        save_to_csv(restaurants)

        browser.close()

# Function to extract restaurant data
def extract_restaurant_data(page):
    restaurants = []
    
    # Locate restaurant cards
    restaurant_cards = page.query_selector_all('.Nv2PK')

    for card in restaurant_cards:
        # Extract restaurant details
        name = card.query_selector('.qBF1Pd').inner_text() if card.query_selector('.qBF1Pd') else 'N/A'
        rating = card.query_selector('.MW4etd').inner_text() if card.query_selector('.MW4etd') else 'N/A'
        
        price_element = card.query_selector('span[aria-label^="Price"]')
        price = price_element.inner_text() if price_element else 'No Price Available'
        

        location = page.evaluate('''() => {
            const locationElement = document.querySelector('div.AeaXub div.Io6YTe');
            return locationElement ? locationElement.innerText : 'N/A';
        }''')

        card.click()
        time.sleep(2)  # Delay to ensure page loads

        review_texts = page.evaluate('''() => {
            const reviews = [];
            document.querySelectorAll('div.OXD3gb div[role="text"]').forEach(div => {
                reviews.push(div.innerText);
            });
            return reviews;
        }''')

        restaurants.append({
            'Name': name,
            'Rating': rating,
            'Price': price,
            'Location': location,
            'Reviews': '; '.join(review_texts)
        })

        page.go_back()
        page.wait_for_selector('.Nv2PK')

    return restaurants

def save_to_csv(restaurants):
    df = pd.DataFrame(restaurants)
    df.to_csv('restaurants.csv', index=True,encoding='utf-8-sig')
    print("Data saved to restaurants.csv")

if __name__ == "__main__":
    scrape_restaurants()
