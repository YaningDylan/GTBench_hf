seed=0
output_root="./experiments"
exp_name='test'
num_matches=20 # number of matches
num_workers=5 # run 20 matches in parallel
threshold_matches=100 # maximum number of matches, stop criteria for low completion rate, e.g., LLM agents always generate illegal actions.
# suports all the games listed in ./gamingbench/configs/game_configs/*.yaml
game_name='liars_dice'
# supports all the llms defined in ./gamingbench/configs/model_configs/*.yaml
model_config_root='gamingbench/configs/model_configs'
llm_name='Llama-2-7b-chat-hf'
opponent_llm_name='Llama-2-7b-chat-hf'
# supports all the reasoning methods defined in ./gamingbench/agent_configs/*.yaml
agent_config_root='gamingbench/configs/agent_configs'
agent_name='prompt_agent'
opponent_agent_name='cot_agent'
declare -a api_keys=("<YOUR-OPENAIAPI-KEY>" "<YOUR_DEEPINFRA_KEY>")

python3 -m gamingbench.main \
    --num-matches ${num_matches} \
    --exp-root ${output_root}/${exp_name}/${llm_name} \
    --seed ${seed} \
    --game-name ${game_name} \
    --agent-configs ${agent_config_root}/${agent_name}.yaml ${agent_config_root}/${opponent_agent_name}.yaml \
    --model-configs ${model_config_root}/${llm_name}.yaml ${model_config_root}/${opponent_llm_name}.yaml \
    --api-keys ${api_keys[@]} \
    --exchange-first-player \
    --num-workers ${num_workers} \
    --threshold-matches ${threshold_matches}
