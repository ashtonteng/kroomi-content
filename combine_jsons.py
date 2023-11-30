import json
import os


def main():
    # looks combines all jsons in the directory '4_final_json' into one json
    # looks for jsons in the directory '4_final_json'
    # writes the combined json to 'combined.json'
    protocols = []
    for filename in os.listdir('4_final_json'):
        if filename.endswith('.json'):
            this_json = json.load(open(f'4_final_json/{filename}', 'r'))
            protocol = this_json['protocols'][0]
            protocols.append(protocol)
    combined_json = {'protocols': protocols}
    with open('combined.json', 'w') as f:
        f.write(json.dumps(combined_json, indent=4))


if __name__ == "__main__":
    main()
