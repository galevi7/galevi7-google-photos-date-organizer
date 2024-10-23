import speedtest

if __name__ == '__main__':
    text = "תמונה – לרוחב – 25 במאי 2024, 14:33:10"
    text = text.replace('\u200F', '')

    # Split the text into an array by spaces
    split_array = text.split()
    date_as_array = [word.replace(',', '') for word in split_array]

    # Initialize the Speedtest object
    st = speedtest.Speedtest()

    # Testing the internet download speed
    print("Testing internet speed...", st.download() / 1000000, "Mbps")

    # Print the length of the photo API prefix
    print("Photo API prefix len", len('https://photos.google.com/'))
