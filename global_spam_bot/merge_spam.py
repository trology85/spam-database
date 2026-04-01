import requests
import csv
import re

CSV_URL = "https://raw.githubusercontent.com/symbuzzer/Turkish-Spam-Numbers/main/SpamBlocker.csv"
GIST_URL = "https://gist.githubusercontent.com/antichown/8219c5c3afd410dc7d6776fb0de334c0/raw"

OUTPUT_FILE = "combined_spam_list.csv"

def main():
    final_rules = set() # Store tuples of (pattern, is_exact)

    # 1. Fetch exact CSV
    print("Fetching CSV...")
    try:
        r1 = requests.get(CSV_URL)
        r1.raise_for_status()
        csv_lines = r1.text.splitlines()
        for idx, line in enumerate(csv_lines):
            line = line.strip()
            if idx == 0 and line.lower() == "number":
                continue # Skip header
            if line:
                final_rules.add((line, 1))
        print(f"Added {len(final_rules)} rules from CSV.")
    except Exception as e:
        print(f"Error fetching CSV: {e}")

    # 2. Fetch patterned GIST
    print("Fetching Gist...")
    try:
        r2 = requests.get(GIST_URL)
        r2.raise_for_status()
        gist_lines = r2.text.splitlines()
        
        parsed_count = 0
        for line in gist_lines:
            line = line.strip()
            if line.startswith("Telefon:"):
                tel = line.replace("Telefon:", "").strip()
                if tel:
                    # Convert any generic masking asterisks to SQLite LIKE %
                    tel = tel.replace("*", "%")
                    
                    if "%" in tel:
                        final_rules.add((tel, 0)) # is_exact = 0
                    else:
                        final_rules.add((tel, 1)) # is_exact = 1
                    parsed_count += 1
        print(f"Added {parsed_count} rules from Gist. Total unique rules: {len(final_rules)}")
    except Exception as e:
        print(f"Error fetching Gist: {e}")

    # 3. Write to combined CSV
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["pattern", "is_exact"])
        # Sort so output is consistent and clean (first exact, then patterns)
        for pattern, is_exact in sorted(final_rules, key=lambda x: (x[1], x[0])):
            writer.writerow([pattern, is_exact])
            
    print("Done!")

if __name__ == "__main__":
    main()
