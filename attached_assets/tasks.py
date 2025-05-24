from .celery_app import celery_app

@celery_app.task
def example_task(x, y):
    # This is a simple example task
    # In a real scenario, this could be an LLM call, a complex calculation,
    # or interaction with your game's database or other services.
    result = x + y
    print(f"Task example_task executed: {x} + {y} = {result}")
    return result

@celery_app.task
def long_running_npc_simulation_update(npc_id):
    # Simulate a long-running task for an NPC
    import time
    print(f"Starting simulation update for NPC {npc_id}...")
    time.sleep(10) # Simulate work
    # Here you would interact with your NPC models, database, potentially other services
    # For example, update NPC state, needs, or trigger an LLM call for complex behavior
    print(f"Finished simulation update for NPC {npc_id}.")
    return f"NPC {npc_id} updated successfully"

# You will add more tasks here as your application grows.
# For example:
# @celery_app.task
# def process_llm_dialogue_request(npc_id, player_input, context):
#     # ... logic to call LLM and store result ...
#     pass

# @celery_app.task
# def run_economic_tick():
#     # ... logic for your economy system ...
#     pass
