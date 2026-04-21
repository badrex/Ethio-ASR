class AmharicNumberConverter:
    def __init__(self):
        self.ones = ["", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"]
        self.tens = ["", "አስር", "ሃያ", "ሰላሳ", "አርባ", "ሃምሳ", "ስድሳ", "ሰባ", "ሰማንያ", "ዘጠና"]
        # In modern Amharic, scales usually follow the international 10^3 system
        self.scales = ["", "መቶ", "ሺህ", "ሚሊዮን", "ቢሊዮን", "ትሪሊዮን"]

    def _convert_below_thousand(self, num: int) -> str:
        """Helper to process chunks of up to 3 digits."""
        parts = []
        
        # Hundreds
        if num >= 100:
            hundred_digit = num // 100
            # Usually just "መቶ" (Meto) for 100, not "አንድ መቶ"
            prefix = "" if hundred_digit == 1 else self.ones[hundred_digit]
            parts.append(f"{prefix}{self.scales[1]}")
            num %= 100

        # Tens
        if num >= 10:
            ten_digit = num // 10
            parts.append(self.tens[ten_digit])
            num %= 10

        # Ones
        if num > 0:
            parts.append(self.ones[num])

        return " ".join(parts).strip()

    def convert(self, number: int) -> str:
        """Main conversion method."""
        if not isinstance(number, int):
            try:
                number = int(number)
            except (ValueError, TypeError):
                return "እባክዎን ትክክለኛ ቁጥር ያስገቡ" # "Please enter a valid number"

        if number == 0:
            return "ዜሮ"

        is_negative = number < 0
        num = abs(number)
        
        result_parts = []
        scale_idx = 0

        # Process in chunks of 1000
        while num > 0:
            chunk = num % 1000
            if chunk > 0:
                chunk_text = self._convert_below_thousand(chunk)
                
                # Determine the scale label (Thousand, Million, etc.)
                if scale_idx == 0:
                    # No scale label for the last 3 digits
                    current_segment = chunk_text
                elif scale_idx == 1:
                    # Special case for Thousand: "አንድ ሺህ" is standard vs just "ሺህ"
                    label = self.scales[2] # "ሺህ"
                    if chunk == 1:
                        current_segment = f"አንድ {label}"
                    else:
                        current_segment = f"{chunk_text} {label}"
                else:
                    # Millions, Billions, etc.
                    label = self.scales[scale_idx + 1]
                    current_segment = f"{chunk_text} {label}"
                
                result_parts.insert(0, current_segment)
            
            num //= 1000
            scale_idx += 1

        text = " ".join(result_parts).strip()
        return f"ከዜሮ በታች {text}" if is_negative else text

# --- Test Suite ---
if __name__ == "__main__":
    converter = AmharicNumberConverter()
    
    test_cases = [
        (0, "ዜሮ"),
        (5, "አምስት"),
        (25, "ሃያ አምስት"),
        (100, "መቶ"),
        (125, "መቶ ሃያ አምስት"),
        (1000, "አንድ ሺህ"),
        (1001, "አንድ ሺህ አንድ"),
        (500000, "አምስት መቶ ሺህ"),
        (1234567, "አንድ ሚሊዮን ሁለት መቶ ሰላሳ አራት ሺህ አምስት መቶ ስድስት ሰባት"),
        (-42, "ከዜሮ በታች አርባ ሁለት")
    ]

    print(f"{'Input':<12} | {'Amharic Text'}")
    print("-" * 50)
    for num, expected in test_cases:
        print(f"{num:<12} | {converter.convert(num)}")