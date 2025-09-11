async def get_commands(driver, emp_id):
    commands = await pymongo_management.get_commands(emp_id)
    for command in commands:
        if command['type'] == 'post_to_group':
            params = command.get("params", {})
            await post_to_group(driver, command['_id'], params.get("group_link", ""), params.get("content", ""), params.get("files", []))
        if command['type'] == 'join_group':
            params = command.get("params", {})
            await join_group(driver, command['user_id'], params.get("group_link", ""))
        await asyncio.sleep(random.uniform(4, 6))