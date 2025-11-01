text = input("Enter a string:").lower().replace(" ","")
freq = {}

for char in text:
    freq[char] = freq.get(char, 0) + 1

print("\nCharacter Frequency:")
for char, count in freq.items():
    print(f"{char}: {count}")