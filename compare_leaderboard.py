
import re
import json
import os

# Function to normalize model names for comparison
def normalize_name(name):
    # Remove 'w-sub', 'sub', 'wo-audio', 'wo_audio' suffix variants for matching base model name
    # Also ignore case, hyphens, underscores
    
    # First, handle the suffix to determine sub/no-sub
    # But for name matching, we want the base name.
    
    base = name.lower()
    base = base.replace('_', '-').replace('.', '')
    
    # Common replacements to match index.html
    base = base.replace('videollama3', 'videollama3') 
    base = base.replace('internvl3-5', 'internvl3-5')
    base = base.replace('internvl-3-5', 'internvl3-5')
    
    # Remove specific suffixes
    # Do NOT remove wo-audio as it distinguishes models in index
    suffixes = ['-sub', '-w-sub'] # , '-wo-audio', '-wo_audio']
    for s in suffixes:
        if base.endswith(s):
            base = base[:-len(s)]
            
    # Remove -instruct, -think if they are part of the base name in index.html but maybe not consistently used?
    # Actually index.html names usually include Instruct/Think.
    # Let's just remove special chars and lowercase
    
    # Clean up
    base = re.sub(r'[^a-z0-9]', '', base)
    
    # Special mappings based on inspection
    if 'glm46flash' in base: return 'glm46flash'
    if 'glm45vthink' in base: return 'glm45vthink'
    if 'glm41vthink' in base: return 'glm41vthink'
    if 'kimivl16ba3bthink' in base: return 'kimivl16ba3bthink'
    if 'kimivl16ba3binstruct' in base: return 'kimivl16ba3binstruct'
    if 'qwen25vl7binstruct' in base: return 'qwen25vl7binstruct'
    if 'qwen25vl72binstruct' in base: return 'qwen25vl72binstruct'
    if 'internvl354binstruct' in base: return 'internvl354binstruct'
    
    return base

def parse_table_data(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    models = []
    current_model = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip headers or irrelevant lines
        if line in ["模型", "评测参数", "Frame", "结果", "逻辑链Acc", "相关性Acc", "总Acc", "Level 1", "Level 2", "Level 3", "备注", "Instruct Model", "Thinking Model"]:
            i += 1
            continue
            
        # Heuristic: Model name usually starts with letter, contains numbers/dashes, no '='
        # And subsequent lines look like params or numbers
        if '=' not in line and ':' not in line and not line.replace('.', '').isdigit():
            # This is likely a model name
            model_name = line
            
            # Look ahead for data
            # Skip params (lines with = or :)
            j = i + 1
            while j < len(lines) and ('=' in lines[j] or ':' in lines[j] or 'tokens' in lines[j]):
                j += 1
            
            if j < len(lines) and lines[j].isdigit(): # Frame number
                frame = lines[j]
                
                # Now read the metrics
                # Expected order: Result(Overall), Logic, Relevance, Total(Avg), L1, L2, L3
                try:
                    metrics = {
                        'name': model_name,
                        'frame': frame,
                        'overall': float(lines[j+1]),
                        'logic': float(lines[j+2]),
                        'relevance': float(lines[j+3]),
                        'avg_acc': float(lines[j+4]),
                        'level1': float(lines[j+5]),
                        'level2': float(lines[j+6]),
                        'level3': float(lines[j+7])
                    }
                    models.append(metrics)
                    i = j + 8 # Move past this block
                except (IndexError, ValueError) as e:
                    # print(f"Error parsing metrics for {model_name}: {e}")
                    i += 1
            else:
                i += 1
        else:
            i += 1
            
    return models

def extract_index_data(html_path):
    with open(html_path, 'r') as f:
        content = f.read()
        
    # Extract the leaderboardDataRaw array content
    match = re.search(r'const leaderboardDataRaw = \[\s*(\{.*?\})\s*\];', content, re.DOTALL)
    if not match:
        # Try to find the list content if the regex failed on boundaries
        start = content.find('const leaderboardDataRaw = [')
        if start != -1:
            end = content.find('];', start)
            js_array = content[start + 27 : end + 1] # include closing bracket
        else:
            print("Could not find leaderboardDataRaw")
            return []
    else:
        # This regex might only catch the first item if not careful with greedy matching
        # Let's use the find method approach which is safer for nested structures
        start = content.find('const leaderboardDataRaw = [')
        end = content.find('];', start)
        js_array = content[start + 27 : end + 1]

    # Convert JS object literals to JSON
    # 1. Quote keys
    js_array = re.sub(r'(\s)([a-zA-Z0-9_]+):', r'\1"\2":', js_array)
    # 2. Handle null/undefined (though null is valid JSON)
    # 3. Handle trailing commas
    js_array = re.sub(r',\s*\}', '}', js_array)
    js_array = re.sub(r',\s*\]', ']', js_array)
    
    try:
        data = json.loads(js_array)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        # fallback manual parsing if needed
        return []

def compare_data(table_models, index_data):
    # Map index data by normalized name
    index_map = {}
    for item in index_data:
        norm_name = normalize_name(item['name'])
        frames = str(item.get('frames', '64'))
        # Create key with frames to distinguish same-name models
        key = f"{norm_name}_{frames}"
        index_map[key] = item

    mismatches = []
    
    for tm in table_models:
        tm_name = tm['name']
        is_sub = '-sub' in tm_name or '-w-sub' in tm_name
        
        array_idx = 0 if is_sub else 1
        
        norm_name = normalize_name(tm_name)
        frames = str(tm.get('frame', '64'))
        
        # Try finding with frames
        key = f"{norm_name}_{frames}"
        matched_item = index_map.get(key)
        
        # If not found, try fallback without frames (maybe user omitted or index default)
        if not matched_item:
             # Try other frame variants? Or just name if unique
             # Let's try to find any key starting with norm_name_
             candidates = [k for k in index_map if k.startswith(f"{norm_name}_")]
             if len(candidates) == 1:
                 matched_item = index_map[candidates[0]]
             elif not candidates:
                 # Try approximate name match?
                 # e.g. "internvl35" vs "internvl35"
                 pass
        
        if not matched_item:
            # print(f"Warning: Could not find match for table model '{tm_name}' (key: {key})")
            continue

        # Compare fields
        # Table: Overall, Logic, Relevance, AvgAcc, L1, L2, L3
        # Index keys: overall, logic, relevance, avg_acc, level1, level2, level3
        
        fields = [
            ('overall', 'overall'),
            ('logic', 'logic'),
            ('relevance', 'relevance'),
            ('avg_acc', 'avg_acc'),
            ('level1', 'level1'),
            ('level2', 'level2'),
            ('level3', 'level3')
        ]
        
        model_mismatches = []
        
        for table_key, index_key in fields:
            table_val = tm[table_key]
            
            index_val_arr = matched_item.get(index_key)
            if not index_val_arr or len(index_val_arr) < 2:
                # print(f"Data missing in index for {tm_name} field {index_key}")
                continue
                
            index_val = index_val_arr[array_idx]
            
            if index_val is None:
                 # Some models might not have data for a specific mode
                 # But table has data?
                 model_mismatches.append(f"{table_key}: Table={table_val}, Index=None")
                 continue
                 
            # Comparison with tolerance
            if abs(table_val - index_val) > 0.1:
                model_mismatches.append(f"{table_key}: Table={table_val}, Index={index_val}")
        
        if model_mismatches:
            mismatches.append({
                'model': tm_name,
                'matched_index_model': matched_item['name'],
                'mode': 'With Subtitle' if is_sub else 'No Subtitle',
                'diffs': model_mismatches
            })
            
    return mismatches

def main():
    table_models = parse_table_data('table_data.txt')
    # print(f"Parsed {len(table_models)} models from table.")
    
    index_data = extract_index_data('index.html')
    # print(f"Parsed {len(index_data)} models from index.html.")
    
    mismatches = compare_data(table_models, index_data)
    
    if not mismatches:
        print("All data matches perfectly!")
    else:
        print(f"Found mismatches in {len(mismatches)} entries:")
        for m in mismatches:
            print(f"\nModel: {m['model']} ({m['mode']})")
            print(f"Matched Index Model: {m['matched_index_model']}")
            for d in m['diffs']:
                print(f"  - {d}")

if __name__ == "__main__":
    main()
