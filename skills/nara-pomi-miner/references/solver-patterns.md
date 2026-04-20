# PoMI Quest Solver Patterns — Complete Reference

All discovered quest question patterns from live testing on devnet (April 2026).

## Arithmetic
| Pattern | Example | Answer |
|---------|---------|--------|
| Basic math | "What is 42 + 58?" | 100 |
| Modulo | "15 mod 4" | 3 |
| Power | "2 to the power of 10" | 1024 |
| Factorial | "Factorial of 6" | 720 |
| Square | "Square of 15" / "15 squared" | 225 |
| Square root | "Square root of 144" | 12 |
| Cube | "Cube of 3" / "3 cubed" | 27 |
| Fibonacci | "10th Fibonacci number" | 55 |
| Absolute | "Absolute value of -42" | 42 |

## Bitwise
| Pattern | Example | Answer |
|---------|---------|--------|
| OR | "What is 11 OR 2 (bitwise)?" | 11 |
| AND | "What is 11 AND 2 (bitwise)?" | 2 |
| XOR | "What is 11 XOR 2 (bitwise)?" | 9 |

## Array Operations
| Pattern | Example | Answer |
|---------|---------|--------|
| Sort asc | "Sort [50, 57, 2, 22] in ascending order." | [2, 22, 50, 57] |
| Sort desc | "Sort [50, 57, 2, 22] in descending order." | [57, 50, 22, 2] |
| Product | "What is the product of [1, 12, 9, 12]?" | 1296 |
| Sum | "Sum of [1, 2, 3, 4, 5]" | 15 |
| Median | "Median of [1, 3, 5]" | 3 |
| Min/Max | "Maximum of 3, 7, 1, 9" | 9 |
| Difference | "Difference between 100 and 37" | 63 |

## Number Theory
| Pattern | Example | Answer |
|---------|---------|--------|
| GCD | "GCD of 12 and 8" | 4 |
| LCM | "LCM of 13 and 20" | 260 |
| Prime check | "Is 7 prime?" | yes |
| Even check | "Is 4 even?" | yes |
| Odd check | "Is 5 odd?" | yes |

## String — Sorting
| Pattern | Example | Answer |
|---------|---------|--------|
| Sort digits | "Sort the digits of 419 in ascending order." | 149 |
| Sort digits desc | "Sort the digits of 419 in descending order." | 941 |
| Sort chars | "Sort characters of 'dcba'" | abcd |

## String — Extraction
| Pattern | Example | Answer |
|---------|---------|--------|
| Extract letters | "Extract all letters from 'u0gh26'" | ugh |
| Extract digits | "Extract all digits from 'cr2yptocurren1cy'" | 21 |
| First N chars | "What are the first 3 characters of 'whale'?" | wha |
| Last N chars | "What are the last 3 characters of 'whale'?" | ale |
| Char at pos | "Character at position 2 of 'hello'" | l |
| Substring | "Substring of 'hello' from 1 to 3" | el |

## String — Transformation
| Pattern | Example | Answer |
|---------|---------|--------|
| Reverse | "Reverse the string 'hello'" | olleh |
| Repeat | "'abc' repeated 3 times" | abcabcabc |
| Uppercase | "Convert 'hello' to uppercase" | HELLO |
| Lowercase | "Convert 'HELLO' to lowercase" | hello |
| Replace | "Replace 'a' with 'o' in 'banana'" | bonono |
| Replace every | "Replace every 'i' in 'light' with 'a'" | laght |
| Pad left | "Pad 'nfr' on the left with '0' to length 6" | 000nfr |
| Pad right | "Pad 'nfr' on the right with '*' to length 6" | nfr*** |
| Remove cons dups | "Remove consecutive duplicate characters from 'qqfffrrr'" | qfr |
| Remove all dups | "Remove all duplicate characters from 'abcabc'" | abc |

## String — Queries
| Pattern | Example | Answer |
|---------|---------|--------|
| Length | "Length of 'nara chain'" | 10 |
| Concatenate | "Concatenate 'foo' and 'bar'" | foobar |
| Count char | "Count 'a' in 'banana'" | 3 |
| Count vowels | "Count vowels in 'hello'" | 2 |
| Count consonants | "Count consonants in 'hello'" | 3 |
| Word count | "Number of words in 'hello world'" | 2 |

## Yes/No Questions
| Pattern | Example | Answer |
|---------|---------|--------|
| Ends with | "Does 'piano' end with 'o'?" | yes |
| Starts with | "Does 'piano' start with 'pi'?" | yes |
| Contains | "Is 'hello' contained in 'say hello world'?" | yes |
| Palindrome | "Is 'racecar' a palindrome?" | true / false |

## Averages
| Pattern | Example | Answer |
|---------|---------|--------|
| Floor avg | "What is the integer average (floor) of 70, 29, 59?" | 52 |

## Conversion
| Pattern | Example | Answer |
|---------|---------|--------|
| To hex | "Convert 255 to hexadecimal" | ff |
| To binary | "Convert 10 to binary" | 1010 |
