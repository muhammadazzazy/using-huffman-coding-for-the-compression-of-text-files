import heapq
import os
from collections import defaultdict, Counter
import math
input_codes_path = "input_codes.txt"

class HuffmanCoding:
    # Initializing the data structures
    def __init__(self):
        self.heap = []
        self.frequency = {}
        self.codes = {}
        self.reverse_mapping = {}
        
    # HeapNode Class for Huffman Coding Algorithm
    class HeapNode:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

        def __eq__(self, other):
            if not other:
                return False
            if not isinstance(other, self._class_):
                return False
            return self.freq == other.freq
        
    # Main function used for compressing text files
    def compress(self, input_path):
        filename, file_extension = os.path.splitext(input_path)
        output_path = filename + ".bin"

        with open(input_path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()

            # Handling in case the text file is empty
            if not text:
                output.write(b'\n')
                print("Input text is empty. Nothing to compress.")
                return output_path

            frequency = self.make_frequency_dict(text)
            self.make_heap(frequency)
            self.merge_nodes()
            self.make_codes()

            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            b = self.get_byte_array(padded_encoded_text)

            # Write the binary compressed file
            output.write(bytes(b))

            # Output the input table for decompression
            self.output_codes(input_codes_path)

            # Calculate and print the metrics
            avg_code_length, entropy, efficiency, compression_ratio = self.calculate_metrics(text)
            print(f"Average Code Length: {avg_code_length:.2f} bits/char")
            print(f"Entropy: {entropy:.2f} bits/char")
            print(f"Code Efficiency: {efficiency:.2%}")
            print(f"Compression Ratio: {compression_ratio:.2f}")

        return output_path
    
    # Extract the frequency of each character in the text 
    def make_frequency_dict(self, text):
        self.frequency = Counter(text)
        return self.frequency
    
    # Inserting Nodes in the heap
    def make_heap(self, frequency):
        for key in frequency:
            node = self.HeapNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    # Merging Nodes
    def merge_nodes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    # Extract the codes from the Huffman Tree
    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)
    
    # Recursive helper function to extract codes from the tree 
    def make_codes_helper(self, root, current_code):
        if root is None:
            return

        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    # Get the binary encoded text
    def get_encoded_text(self, text):
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text
    
    # Pad encoded text  
    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text
    
    # Get byte array to write the binary compmressed file
    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b
    
    # Outputting each character of the text file along with its code to be used for decommpression
    def output_codes(self, output_path):
        with open(output_path, 'w') as file:
            for char, code in self.codes.items():
                if char == "\n" :
                    char = "\\n"
                elif char == " ":
                    char = "\\s"
                file.write(f"{char} {code}\n")

    # Calculating Compression Metrics
    def calculate_metrics(self, text):
        total_length = sum(len(self.codes[char]) * freq for char, freq in self.frequency.items())
        total_chars = sum(self.frequency.values())
        average_code_length = total_length / total_chars
        probabilities = [freq / total_chars for freq in self.frequency.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        efficiency = entropy / average_code_length if average_code_length else 0
        compression_ratio = average_code_length / 8

        return average_code_length, entropy, efficiency, compression_ratio
    
    # Main function for decompressing text files 
    def decompress(self, input_path, input_codes_path):
        filename, file_extension = os.path.splitext(input_path)
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while byte:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
            encoded_text = self.remove_padding(bit_string)
            decompressed_text = self.decode_text(encoded_text, input_codes_path)
            output.write(decompressed_text)

        return output_path
    
    # Remove padding of the encoded text
    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:] 
        encoded_text = padded_encoded_text[:-1*extra_padding]

        return encoded_text
    
    # Decode text 
    def decode_text(self, encoded_text, input_codes_path):
        current_code = ""
        decoded_text = ""

        with open(input_codes_path, "r") as file:
            for line in file:
                char, code = line.strip().split()
                self.reverse_mapping[code] = char

        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                if character == "\\n":
                    character = "\n"
                elif character == "\\s":
                    character = " "
                decoded_text += character
                current_code = ""

        return decoded_text

path = "input.txt"
h = HuffmanCoding()
compressed_path = h.compress(path)
decompressed_path = h.decompress("input.bin", input_codes_path)