
# get config and create agents
todd, frank, conversation_starters = Agent.get_config()
    
for topic in conversation_starters:
    
    print(f"\nNew topic: {topic}")
    print("=" * 75)
    
    # Todd starts
    response = todd.respond(topic)
    print(f"Todd >>>>>: \n {response}")
    print("-" * 75)
    sleep(1)  # Add delay for readability
    
    # Frank responds to Todd
    response = frank.respond(f"Frank >>>>>: \n {response}")
    print("-" * 75)

    sleep(1)
    
    # Todd responds to Frank
    response = todd.respond(f"Todd >>>>>: \n {response}")
    print(f"Todd >>>>>:\n  {response}")
    print("-" * 75)
    sleep(1)