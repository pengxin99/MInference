# Load data
wget https://gutenberg.org/cache/epub/2600/pg2600.txt -O ./data/pg2600.txt

python examples/run_hf_streaming.py --attn_type minference
