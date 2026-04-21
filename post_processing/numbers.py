"""
Amharic Number Converter
Converts Arabic numerals (integers) to Amharic text and vice-versa.
"""

class AmharicNumberConverter:
    def __init__(self):
        self.ones_map = {
            "": 0, "አንድ": 1, "ሁለት": 2, "ሶስት": 3, "አራት": 4, 
            "አምስት": 5, "ስድስት": 6, "ሰባት": 7, "ስምንት": 8, "ዘጠኝ": 9
        }
        self.tens_map = {
            "": 0, "አስር": 10, "ሃያ": 20, "ሰላሳ": 30, "አርባ": 40, 
            "ሃምሳ": 50, "ስድሳ": 60, "ሰባ": 70, "ሰማንያ": 80, "ዘጠና": 90
        }
        self.scales_map = {
            "መቶ": 100, "ሺህ": 1000, "ሚሊዮን": 1000000, 
            "ቢሊዮን": 1000000000, "ትሪሊዮን": 1000000000000
        }
        
        # Lists for generation (numeric to text)
        self.ones = ["", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"]
        self.tens = ["", "አስር", "ሃያ", "ሰላሳ", "አርባ", "ሃምሳ", "ስድሳ", "ሰባ", "ሰማንያ", "ዘጠና"]
        self.scales = ["", "መቶ", "ሺህ", "ሚሊዮን", "ቢሊዮን", "ትሪሊዮን"]

    def _convert_below_thousand(self, num: int) -> str:
        """Helper to process chunks of up to 3 digits into text."""
        parts = []
        if num >= 100:
            hundred_digit = num // 100
            prefix = "" if hundred_digit == 1 else self.ones[hundred_digit]
            parts.append(f"{prefix}መቶ")
            num %= 100
        if num >= 10:
            parts.append(self.tens[num // 10])
            num %= 10
        if num > 0:
            parts.append(self.ones[num])
        return " ".join(parts).strip()

    def convert_to_text(self, number: int) -> str:
        """Converts an integer to Amharic text."""
        if not isinstance(number, int):
            try:
                number = int(number)
            except (ValueError, TypeError):
                return "እባክዎን ትክክለኛ ቁጥር ያስገቡ"

        if number == 0: return "ዜሮ"
        
        is_negative = number < 0
        num = abs(number)
        result_parts = []
        scale_idx = 0

        while num > 0:
            chunk = num % 1000
            if chunk > 0:
                chunk_text = self._convert_below_thousand(chunk)
                if scale_idx == 0:
                    current_segment = chunk_text
                elif scale_idx == 1:
                    label = "ሺህ"
                    current_segment = f"አንድ {label}" if chunk == 1 else f"{chunk_text} {label}"
                else:
                    label = self.scales[scale_idx + 1]
                    current_segment = f"{chunk_text} {label}"
                result_parts.insert(0, current_segment)
            num //= 1000
            scale_idx += 1

        text = " ".join(result_parts).replace("  ", " ").strip()
        return f"ከዜሮ በታች {text}" if is_negative else text

    def convert_to_number(self, text: str) -> int:
        """Converts Amharic text back into an integer."""
        if text == "ዜሮ": return 0
        
        is_negative = False
        if text.startswith("ከዜሮ በታች"):
            is_negative = True
            text = text.replace("ከዜሮ በታች", "").strip()

        words = text.split()
        total = 0
        current_chunk = 0
        
        for word in words:
            if word in self.ones_map:
                current_chunk += self.ones_map[word]
            elif word in self.tens_map:
                current_chunk += self.tens_map[word]
            elif word == "መቶ":
                # Handle "መቶ" which might be "አንድ መቶ" or just "መቶ"
                if current_chunk == 0: current_chunk = 1
                current_chunk *= 100
            elif "መቶ" in word and word != "መቶ":
                # Handle compounds like "ሁለትመቶ"
                prefix = word.replace("መቶ", "")
                val = self.ones_map.get(prefix, 1)
                current_chunk += val * 100
            elif word in self.scales_map:
                # Scalers like Thousand, Million
                if current_chunk == 0: current_chunk = 1
                total += current_chunk * self.scales_map[word]
                current_chunk = 0
            else:
                # Support for combined words like "ሃያአምስት"
                for t_word, t_val in self.tens_map.items():
                    if t_word and word.startswith(t_word):
                        current_chunk += t_val
                        rem = word.replace(t_word, "")
                        current_chunk += self.ones_map.get(rem, 0)
                        break
        
        total += current_chunk
        return -total if is_negative else total

# --- Test Suite ---
if __name__ == "__main__":
    converter = AmharicNumberConverter()
    
    # Test cases for bidirectional conversion
    numbers = [125, 1001, 500000, 1234567, -42]
    
    print(f"{'Numeric':<10} | {'Amharic Text':<60} | {'Back to Num'}")
    print("-" * 90)
    for n in numbers:
        text = converter.convert_to_text(n)
        back = converter.convert_to_number(text)
        print(f"{n:<10} | {text:<60} | {back}")

    # Manual word to number test
    word_test = "ሁለት መቶ ሃምሳ"
    print(f"\nManual Parse: '{word_test}' -> {converter.convert_to_number(word_test)}")