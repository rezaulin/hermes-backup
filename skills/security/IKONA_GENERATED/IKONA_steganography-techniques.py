#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/steganography-techniques

Skill: SKILL: Steganography Techniques — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-steganography-techniques.py --help
      python hack-skills-steganography-techniques.py --list
      python hack-skills-steganography-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/steganography-techniques'
TITLE = 'SKILL: Steganography Techniques — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: steganography-techniques", "description: >-", "Steganography detection and extraction playbook. Use when analyzing images (LSB, PNG chunks, JPEG DCT, EXIF), audio (spectrogram, DTMF), files (polyglots, appended data, ADS), and text (whitespace, zero-width, homoglyphs) for hidden data."],
    'skill-steganography-techniques-expert-analysis-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md) for extracting files from network captures before stego analysis", "- [memory-forensics-volatility](../memory-forensics-volatility/SKILL.md) for extracting files from memory dumps", "- [classical-cipher-analysis](../classical-cipher-analysis/SKILL.md) if extracted hidden data is further encrypted/encoded"],
    'tool-reference': ["Also load [STEGO_TOOLS_GUIDE.md](./STEGO_TOOLS_GUIDE.md) when you need:", "- Tool installation instructions and dependencies", "- Detailed command reference for each stego tool", "- Workflow patterns for specific file types"],
    '1-image-steganography': [],
    'lsb-least-significant-bit': ["LSB embeds data in the least significant bits of pixel color channels.", "```bash"],
    'zsteg-lsb-analysis-for-png-bmp': ["zsteg image.png                       # auto-detect all LSB patterns", "zsteg image.png -a                    # try all known methods", "zsteg image.png -b 1                  # extract bit plane 1", "zsteg image.png -E \"b1,rgb,lsb,xy\"   # specific extraction pattern"],
    'stegsolve-java-gui': ["java -jar StegSolve.jar"],
    'navigate-color-planes-red-0-green-0-blue-0-look-for-hidden-image-text': [],
    'data-extractor-specify-bit-planes-byte-order': [],
    'stegoveritas-comprehensive-automated-analysis': ["stegoveritas image.png"],
    'runs-exiftool-binwalk-zsteg-foremost-color-plane-extraction': [],
    'png-specific': ["```bash"],
    'pngcheck-validate-structure-find-hidden-chunks': ["pngcheck -v image.png"],
    'hidden-chunks-text-ztxt-compressed-text-itxt-international-text': [],
    'custom-private-chunks-may-contain-hidden-data': [],
    'crc-vs-dimensions-trick': [],
    'if-crc-doesn-t-match-declared-dimensions-image-was-cropped': [],
    'fix-brute-force-correct-width-height-reveals-hidden-rows-columns': ["python3 -c \"", "import struct, zlib", "with open('image.png','rb') as f:", "data = f.read()"],
    'check-ihdr-crc-at-offset-29': ["ihdr = data[12:29]", "for h in range(1,2000):", "for w in range(1,2000):", "new_ihdr = struct.pack('>II',w,h) + ihdr[8:]", "if zlib.crc32(b'IHDR'+new_ihdr) & 0xffffffff == struct.unpack('>I',data[29:33])[0]:", "print(f'Width: {w}, Height: {h}')"],
    'apng-animated-png-hidden-frames': [],
    'use-apngdis-to-extract-all-frames-apngdis-image-png': [],
    'jpeg-specific': ["```bash"],
    'steghide-embed-extract-from-jpeg-dct-coefficient-modification': ["steghide extract -sf image.jpg                 # extract (no passphrase)", "steghide extract -sf image.jpg -p PASSWORD     # extract with passphrase", "steghide info image.jpg                        # check if data is embedded"],
    'stegcracker-brute-force-steghide-passphrase': ["stegcracker image.jpg wordlist.txt"],
    'jsteg-jpeg-lsb-steganography': ["jsteg reveal image.jpg output.txt"],
    'jpeg-structure-analysis': ["exiftool -v3 image.jpg       # verbose metadata + structure", "jpegdump image.jpg           # raw JPEG marker analysis"],
    'exif-metadata': ["```bash"],
    'exiftool-comprehensive-metadata-extraction': ["exiftool image.jpg", "exiftool -b -ThumbnailImage image.jpg > thumb.jpg   # extract thumbnail", "exiftool -all= image.jpg                             # strip all metadata"],
    'hidden-data-in-exif-fields-comment-artist-copyright-etc': ["exiftool -Comment image.jpg", "exiftool -UserComment image.jpg", "strings image.jpg | grep -i \"flag\\|key\\|secret\""],
    'palette-based-gif': ["```bash"],
    'gif-color-table-manipulation-data-in-color-palette-order': ["gifsicle -I image.gif                    # info", "gifsicle --color-info image.gif          # palette details"],
    'check-for-animation-frames-convert-coalesce-image-gif-frame-d-png': [],
    '2-audio-steganography': [],
    'spectrogram-analysis': ["```bash"],
    'sonic-visualiser-best-for-spectrogram-viewing': [],
    'layer-add-spectrogram-look-for-visual-patterns-text-images': [],
    'audacity': [],
    'analyze-plot-spectrum': [],
    'select-audio-change-view-to-spectrogram': [],
    'sox-for-command-line-spectrogram-generation': ["sox audio.wav -n spectrogram -o spectro.png"],
    'audio-lsb': ["```bash"],
    'deepsound-hide-extract-files-in-audio-windows': [],
    'gui-tool-open-audio-file-extract-hidden-files': [],
    'wavsteg-lsb-in-wav-files': ["python3 WavSteg.py -r -i audio.wav -o output.txt -n 1   # extract 1 LSB", "python3 WavSteg.py -r -i audio.wav -o output.txt -n 2   # extract 2 LSBs"],
    'dtmf-morse-code': ["```bash"],
    'dtmf-decoder-phone-tones': ["multimon-ng -t wav -a DTMF audio.wav"],
    'morse-code': [],
    'audacity-visual-inspection-of-on-off-pattern': [],
    'online-decoder-or-manual-a-b-etc': [],
    'sstv-slow-scan-television-image-in-audio': ["qsstv                    # GUI decoder"],
    'or-rx-sstv-windows': [],
    'wav-header-manipulation': ["```bash"],
    'check-for-data-appended-after-wav-audio-data': [],
    'wav-data-chunk-size-vs-actual-file-size': ["python3 -c \"", "import wave", "w = wave.open('audio.wav','rb')", "print(f'Frames: {w.getnframes()}, Channels: {w.getnchannels()}, Width: {w.getsampwidth()}')", "expected = w.getnframes() * w.getnchannels() * w.getsampwidth() + 44  # 44 = WAV header", "import os", "actual = os.path.getsize('audio.wav')", "if actual > expected:", "print(f'Extra data: {actual - expected} bytes appended')"],
    '3-file-steganography': [],
    'polyglot-files': ["A single file that is valid in two or more formats simultaneously.", "```bash"],
    'detection-check-file-with-multiple-tools': ["file suspicious_file", "xxd suspicious_file | head          # check magic bytes", "binwalk suspicious_file             # find embedded files"],
    'common-polyglots-pdf-zip-jpeg-zip-jpeg-rar-png-zip': [],
    'try-unzip-on-image-files': ["unzip image.jpg -d extracted/", "7z x image.jpg -oextracted/"],
    'appended-embedded-data': ["```bash"],
    'binwalk-scan-for-embedded-files-and-data': ["binwalk image.png                   # scan", "binwalk -e image.png                # extract embedded files", "binwalk --dd='.*' image.png         # extract everything"],
    'foremost-file-carving': ["foremost -i suspicious_file -o output_dir/"],
    'dd-manual-extraction': [],
    'if-binwalk-shows-embedded-zip-at-offset-0x1234': ["dd if=suspicious_file bs=1 skip=$((0x1234)) of=extracted.zip"],
    'ntfs-alternate-data-streams-ads': ["```cmd", ":: List ADS (Windows)", "dir /r file.txt", "Get-Item file.txt -Stream *", ":: Read hidden stream", "more < file.txt:hidden_stream", "Get-Content file.txt -Stream hidden_stream", ":: Create ADS (for testing)", "echo \"hidden data\" > file.txt:secret"],
    'steghide-brute-force': ["```bash"],
    'stegcracker-wordlist-attack-on-steghide-passphrase': ["stegcracker image.jpg /usr/share/wordlists/rockyou.txt"],
    'stegseek-faster-alternative': ["stegseek image.jpg /usr/share/wordlists/rockyou.txt"],
    'stegseek-is-10000x-faster-than-stegcracker': [],
    '4-text-steganography': [],
    'whitespace-encoding': ["```bash"],
    'tabs-and-spaces-encode-binary-tab-1-space-0-or-vice-versa': [],
    'stegsnow-whitespace-steganography': ["stegsnow -C message.txt                # extract hidden message", "stegsnow -C -p PASSWORD message.txt    # extract with password"],
    'manual-detection': ["cat -A file.txt | head     # show tabs (^I) and line endings ($)", "xxd file.txt | grep \"09 20\\|20 09\"    # look for tab/space patterns"],
    'zero-width-characters': ["```bash"],
    'unicode-invisible-characters-used-for-encoding': [],
    'u-200b-zero-width-space-u-200c-zwnj-u-200d-zwj-u-feff-bom': [],
    'detection': ["python3 -c \"", "text = open('message.txt','r').read()", "hidden = [c for c in text if ord(c) in [0x200b, 0x200c, 0x200d, 0xfeff]]", "print(f'Found {len(hidden)} zero-width characters')", "binary = ''.join('0' if ord(c)==0x200b else '1' for c in hidden)"],
    'convert-binary-to-ascii': [],
    'online-tools-holloway-nz-steg-unicode-steganography-decoders': [],
    'homoglyph-substitution': ["```bash"],
    'visually-identical-characters-from-different-unicode-blocks': [],
    'e-g-latin-a-u-0061-vs-cyrillic-u-0430': [],
    'detection': ["python3 -c \"", "text = open('message.txt','r').read()", "for i, c in enumerate(text):", "if ord(c) > 127:", "print(f'Position {i}: char={c} ord={ord(c)} name={__import__(\\\"unicodedata\\\").name(c,\\\"?\\\")}')"],
    '5-decision-tree': ["Suspect hidden data \u2014 what file type?", "\u251c\u2500\u2500 Image (PNG/BMP)?", "\u2502   \u251c\u2500\u2500 Check metadata: exiftool (\u00a71 EXIF)", "\u2502   \u251c\u2500\u2500 Check structure: pngcheck, binwalk (\u00a71 PNG)", "\u2502   \u251c\u2500\u2500 LSB analysis: zsteg, StegSolve (\u00a71 LSB)", "\u2502   \u251c\u2500\u2500 Check dimensions vs CRC: height/width brute force (\u00a71 PNG)", "\u2502   \u251c\u2500\u2500 Check for appended data: binwalk -e (\u00a73)", "\u2502   \u2514\u2500\u2500 Try as polyglot: unzip/7z (\u00a73)", "\u251c\u2500\u2500 Image (JPEG)?", "\u2502   \u251c\u2500\u2500 Check metadata: exiftool (\u00a71 EXIF)", "\u2502   \u251c\u2500\u2500 Try steghide: steghide extract (\u00a71 JPEG)", "\u2502   \u2502   \u2514\u2500\u2500 Password protected? \u2192 stegseek brute force (\u00a73)", "\u2502   \u251c\u2500\u2500 Try jsteg: jsteg reveal (\u00a71 JPEG)", "\u2502   \u251c\u2500\u2500 Check for appended data: binwalk -e (\u00a73)", "\u2502   \u2514\u2500\u2500 Check thumbnail: exiftool -b -ThumbnailImage (\u00a71 EXIF)", "\u251c\u2500\u2500 Image (GIF)?", "\u2502   \u251c\u2500\u2500 Check frames: extract all animation frames (\u00a71 Palette)", "\u2502   \u251c\u2500\u2500 Check palette: gifsicle --color-info (\u00a71 Palette)", "\u2502   \u2514\u2500\u2500 Check for appended data: binwalk -e (\u00a73)", "\u251c\u2500\u2500 Audio (WAV/MP3/FLAC)?", "\u2502   \u251c\u2500\u2500 Spectrogram: Sonic Visualiser / Audacity (\u00a72)", "\u2502   \u251c\u2500\u2500 LSB: WavSteg (\u00a72)", "\u2502   \u251c\u2500\u2500 DTMF tones: multimon-ng (\u00a72)", "\u2502   \u251c\u2500\u2500 Morse code: manual or decoder (\u00a72)", "\u2502   \u251c\u2500\u2500 SSTV: qsstv (\u00a72)", "\u2502   \u2514\u2500\u2500 Check file size vs expected: header analysis (\u00a72)", "\u251c\u2500\u2500 Text file?", "\u2502   \u251c\u2500\u2500 Check whitespace: cat -A, stegsnow (\u00a74)", "\u2502   \u251c\u2500\u2500 Check zero-width chars: Unicode analysis (\u00a74)", "\u2502   \u251c\u2500\u2500 Check homoglyphs: non-ASCII detection (\u00a74)", "\u2502   \u2514\u2500\u2500 Check encoding: multiple base decodings", "\u251c\u2500\u2500 Any file type?", "\u2502   \u251c\u2500\u2500 strings: strings -n 8 file | grep -i \"flag\\|key\\|pass\"", "\u2502   \u251c\u2500\u2500 binwalk: binwalk -e file (embedded files) (\u00a73)", "\u2502   \u251c\u2500\u2500 file: file suspicious_file (true type)", "\u2502   \u251c\u2500\u2500 xxd: check magic bytes, compare headers", "\u2502   \u2514\u2500\u2500 NTFS? \u2192 check ADS: dir /r (\u00a73)", "\u2514\u2500\u2500 Password/passphrase needed?", "\u251c\u2500\u2500 steghide \u2192 stegseek / stegcracker (\u00a73)", "\u251c\u2500\u2500 Check challenge description for hints", "\u2514\u2500\u2500 Try common passwords: password, file name, challenge name"],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()