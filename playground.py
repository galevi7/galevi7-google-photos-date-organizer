

if __name__ == '__main__':
    text = "תמונה – לרוחב – 25 במאי 2024, 14:33:10"
    text = text.replace('\u200F', '')
    # Split the text into an array by spaces
    split_array = text.split()
    date_as_array = [word.replace(',', '') for word in split_array]



    # Print the split array
    for word in split_array:
        print(word)
    print(split_array)
