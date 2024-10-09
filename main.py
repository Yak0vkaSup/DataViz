import requests
import json
import plotly.express as px

# List of major crypto exchange domains
exchange_domains = [
    "binance.com",
    "coinbase.com",
    "kraken.com",
    "bybit.com",
    "bitfinex.com",
    "bitstamp.net",
    "huobi.com",
    "kucoin.com",
    "gemini.com",
    "okx.com",
    "upbit.com",
    "gate.io",
    "mexc.com",
    "bitget.com",
    "crypto.com",
    "bingx.com",
    "bitmart.com",
    "bithumb.com",
    "lbank.info",
    "tokocrypto.com",
    "bitflyer.com",
    "binance.us"
]


# Function to get the IP address using Google's DNS-over-HTTPS API
def get_ip_google_dns(domain):
    try:
        response = requests.get(f"https://dns.google/resolve?name={domain}&type=A")
        if response.status_code == 200:
            answer = response.json().get("Answer", [])
            if answer:
                return answer[0]["data"]
    except Exception as e:
        print(f"Error occurred during DNS resolution for {domain}: {e}")
    return None


# Function to get geolocation information using ipinfo.io API
def get_geolocation(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Unable to get geolocation for {ip}, Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred during geolocation fetch: {e}")
    return None


# Main function to collect geolocation data for each exchange
def main():
    exchanges_data = []  # List to store data for plotting

    for domain in exchange_domains:
        print(f"Resolving domain: {domain}")

        # Get the IP address for the domain
        ip_address = get_ip_google_dns(domain)

        if ip_address:
            print(f"IP address for {domain}: {ip_address}")

            # Get geolocation information for the IP address
            geolocation = get_geolocation(ip_address)
            if geolocation and 'loc' in geolocation:
                loc = geolocation['loc'].split(',')
                latitude, longitude = float(loc[0]), float(loc[1])

                # Collect the data
                exchanges_data.append({
                    'exchange': domain,
                    'latitude': latitude,
                    'longitude': longitude,
                    'city': geolocation.get('city', 'Unknown'),
                    'country': geolocation.get('country', 'Unknown')
                })

                print(json.dumps(geolocation, indent=4))
        else:
            print(f"Could not resolve domain: {domain}")
        print("-" * 50)

    # Plot the data on a world map
    plot_exchanges_on_map(exchanges_data)


# Function to plot the exchanges on a map using Plotly
def plot_exchanges_on_map(data):
    if not data:
        print("No data to plot.")
        return

    # Create a DataFrame using pandas for easier plotting
    import pandas as pd
    df = pd.DataFrame(data)

    # Create the scatter_geo plot using Plotly Express
    fig = px.scatter_geo(
        df,
        lat='latitude',
        lon='longitude',
        text='exchange',
        hover_name='exchange',
        hover_data={'city': True, 'country': True},
        title='Geolocation of Major Cryptocurrency Exchanges',
        template='plotly_dark'
    )

    # Update layout for better visualization
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='rgb(217, 217, 217)',
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Show the map
    fig.show()


if __name__ == "__main__":
    main()
