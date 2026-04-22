import re

class AmharicNumberConverter:
    def __init__(self):
        # Mappings for word-to-number conversion
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
        
        # Lists for number-to-word generation
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
        try:
            num = int(number)
        except (ValueError, TypeError):
            return str(number)

        if num == 0: return "ዜሮ"
        
        is_negative = num < 0
        num = abs(num)
        result_parts = []
        scale_idx = 0

        while num > 0:
            chunk = num % 1000
            if chunk > 0:
                chunk_text = self._convert_below_thousand(chunk)
                if scale_idx == 0:
                    result_parts.insert(0, chunk_text)
                elif scale_idx == 1:
                    label = "ሺህ"
                    result_parts.insert(0, f"አንድ {label}" if chunk == 1 else f"{chunk_text} {label}")
                else:
                    label = self.scales[scale_idx + 1]
                    result_parts.insert(0, f"{chunk_text} {label}")
            num //= 1000
            scale_idx += 1

        text = " ".join(result_parts).strip()
        return f"ከዜሮ በታች {text}" if is_negative else text

    def process_sentence_to_text(self, text: str) -> str:
        """Replaces all digits in a sentence with their Amharic word equivalents."""
        if not text: return "ዜሮ"
        return re.sub(r'-?\d+', lambda m: self.convert_to_text(int(m.group(0))), text)

    def is_number_word(self, word: str) -> bool:
        """Checks if a word is part of the Amharic number system."""
        if not word: return False
        if word in self.ones_map or word in self.tens_map or word in self.scales_map:
            return True
        if word in ["ከዜሮ", "በታች"]:
            return True
        if any(word.endswith(s) for s in ["መቶ", "ሺህ", "ሚሊዮን", "ቢሊዮን"]):
            return True
        for t_word in self.tens_map:
            if t_word and word.startswith(t_word):
                return True
        return False

    def convert_to_number(self, text: str) -> int:
        """Internal logic to parse a string of Amharic number words into an integer."""
        if not text or text.strip() == "": return 0
        clean_text = text.strip()
        if clean_text == "ዜሮ": return 0
        
        is_negative = False
        if "ከዜሮ በታች" in clean_text:
            is_negative = True
            clean_text = clean_text.replace("ከዜሮ በታች", "").strip()

        words = clean_text.split()
        total = 0
        current_chunk = 0
        
        for word in words:
            if word in self.ones_map:
                current_chunk += self.ones_map[word]
            elif word in self.tens_map:
                current_chunk += self.tens_map[word]
            elif word == "መቶ":
                if current_chunk == 0: current_chunk = 1
                current_chunk *= 100
            elif word.endswith("መቶ"):
                prefix = word.replace("መቶ", "")
                val = self.ones_map.get(prefix, 1)
                current_chunk += val * 100
            elif word in self.scales_map:
                if current_chunk == 0: current_chunk = 1
                total += current_chunk * self.scales_map[word]
                current_chunk = 0
            else:
                # Check for concatenated Tens + Ones (e.g., ሃያአምስት)
                matched = False
                for t_word, t_val in self.tens_map.items():
                    if t_word and word.startswith(t_word):
                        current_chunk += t_val
                        rem = word.replace(t_word, "")
                        current_chunk += self.ones_map.get(rem, 0)
                        matched = True
                        break
                
                # Check for concatenated scales (e.g., አምስትሺህ)
                if not matched:
                    for s_word, s_val in self.scales_map.items():
                        if word.endswith(s_word):
                            prefix = word.replace(s_word, "")
                            p_val = self.ones_map.get(prefix, 1)
                            current_chunk += p_val * s_val
                            total += current_chunk
                            current_chunk = 0
                            break
        
        total += current_chunk
        return -total if is_negative else total

    def process_sentence_to_number(self, text: str) -> str:
        """Replaces Amharic number word sequences in a sentence with formatted integers."""
        if not text: return "0"
        
        # Tokenize preserving spaces and punctuation
        tokens = re.split(r'(\s+|[.,!?;:])', text)
        result = []
        buffer = []

        def flush_buffer():
            if buffer:
                num_text = "".join(buffer).strip()
                if num_text:
                    # Format with commas for readability
                    result.append(f"{self.convert_to_number(num_text):,}")
                buffer.clear()

        for token in tokens:
            if not token: continue
            
            clean_token = re.sub(r'[.,!?;:]', '', token.strip())
            
            if self.is_number_word(clean_token):
                buffer.append(token)
            elif token.isspace() and buffer:
                buffer.append(token)
            else:
                flush_buffer()
                result.append(token)
        
        flush_buffer()
        return "".join(result)

# --- Demo Usage ---
if __name__ == "__main__":
    converter = AmharicNumberConverter()
    
    print("--- 1. Numeral to Amharic Words ---")
    sentence_1 = "The price is ሰላም ሰላም ሰላም ሰላም ሰላም ሰላም  123456789 birr."
    print(f"Input:  {sentence_1}")
    print(f"Output: {converter.process_sentence_to_text(sentence_1)}\n")

    print("--- 2. Amharic Words to Numeral ---")
    sentence_2 = "ሰላም መቶ ሃያ ሶስት ሚሊዮን አራትመቶ ሃምሳ ስድስት ሺህ ሰባትመቶ ሰማንያ ዘጠኝ ብር ስጠኝ"
    print(f"Input:  {sentence_2}")
    print(f"Output: {converter.process_sentence_to_number(sentence_2)}")