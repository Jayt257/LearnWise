import os
import json

directory = "/home/jeel/Downloads/learnwise-react_till_now_6/learnwise-react/backend/data/languages"
changed_count = 0

def clean_dict(d):
    changed = False
    for k, v in d.items():
        if isinstance(v, dict):
            if clean_dict(v):
                changed = True
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    if clean_dict(item):
                        changed = True
        else:
            # If the key implies an audio file/path (contains audio) and is not metadata
            if "audio" in k.lower():
                ignore_keys = ["audiolanguage", "audiotranscript", "audioduration", "audiorepeatallowed"]
                if k.lower() not in ignore_keys:
                    if v is not None:
                        # Set audio file string to null
                        d[k] = None
                        changed = True
    return changed

for root, dirs, files in os.walk(directory):
    for file in files:
        # Edit all json files EXCEPT listening activities and meta files
        if file.endswith(".json") and not file.endswith("_listening.json") and not file.endswith("meta.json"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
                    continue
            
            if clean_dict(data):
                # Write back the corrected JSON
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                changed_count += 1
                
print(f"Total files updated: {changed_count}")
