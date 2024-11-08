import json

def jsonl_to_json(input_jsonl, output_json):
    try:
        with open(input_jsonl, 'r', encoding='utf-8') as jsonl_file:
            json_list = [json.loads(line.strip()) for line in jsonl_file]
        
        if len(json_list) == 1:
            json_data = json_list[0]
        else:
            json_data = {
                "game_config": json_list[0]["game_config"],
                "agents_config": json_list[0]["agents_config"],
                "models_config": json_list[0]["models_config"],
                "win_rate": {}, 
                "matches": json_list,
                "token_size": sum(item.get("token_size", 0) for item in json_list)
            }
        
        with open(output_json, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)
            
        print(f"Successfully converted {input_jsonl} to {output_json}")
        
    except Exception as e:
        print(f"Error converting file: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = "input.jsonl"
        output_file = "output.json"
    
    jsonl_to_json(input_file, output_file)