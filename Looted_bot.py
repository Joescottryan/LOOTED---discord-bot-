import discord
from discord.ext import commands
import random
import asyncio
from discord.ext.commands import has_permissions
import os
from dotenv import load_dotenv

load_dotenv()


import json
import os


pending_trades = {}  # key = receiver_id, value = trade data

igor_roasts = [
    "‘You call *that* a raid? My babushka could do better.’",
    "‘Did you trip on your own loot again?’",
    "‘You die more than my plants, and I forget to water them.’",
    "‘I warned you. But nooo, you had to be the hero.’",
    "‘What did you expect bringing a spoon to a firefight?’",
    "‘Next time try not blinking so hard, maybe you’ll survive.’",
    "‘LOOTED? More like LOST IT.’",
    "‘That was the worst raid I’ve seen. Impressive, in a sad way.’"
]


# Loot table with values
loot_values = {
    "AK-74U": 2500,
    "Bandages": 100,
    "$400": 400,
    "Painkillers": 200,
    "Sniper Rifle": 5000,
    "Empty Backpack": 0,
    "Keycard": 10000,
    "Nothing": 0,
    
    # 🔫 NEW GUNS
    "M4A1": 3500,
    "Glock-17": 1200,
    "MP5": 3000,
    "RPK": 4000,
    "Desert Eagle": 3800,
    "Sawed-Off Shotgun": 2800,
    "SCAR-L": 4500,
    "Crossbow": 1500,
    "Flare Gun": 1000
}

enemies = [
    {"name": "Scav", "danger": 20, "reward": 1},
    {"name": "Raider", "danger": 40, "reward": 2},
    {"name": "PMC", "danger": 60, "reward": 3},
    {"name": "Sniper", "danger": 80, "reward": 3},
    {"name": "Boss", "danger": 95, "reward": 5}
]



global_raid = {
    "active": False,
    "players": [],
    "started_by": None
}








# Temporary gear loadouts (in-memory only for now)
loadouts = {}





inventory_file = "inventory.json"


# Load player data (inventory + cash + xp)
if os.path.exists(inventory_file):
    with open(inventory_file, "r") as f:
        player_data = json.load(f)
else:
    player_data = {}



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"LOOTED is online as {bot.user}")

@bot.command()
async def loot(ctx):
    await ctx.send(f"💼 {ctx.author.name} found a bunch of loot!")

#RAID COMMAND
@bot.command()
async def raid(ctx):
    player_id = str(ctx.author.id)
    player_name = ctx.author.name
    await ctx.send(f"🎯 {player_name} is entering the raid...")

    await asyncio.sleep(2)

    # Base loot roll
    loot_pool = list(loot_values.keys())
    loot = random.sample(loot_pool, k=2)

    # --- GEAR LOGIC ---
    gear = loadouts.get(player_id, [])

    extraction_bonus = 0
    extra_loot = 0
    medkit_revive = False
    silencer_bonus = False

    if "Armor" in gear:
        extraction_bonus += 20
    if "Medkit" in gear:
        medkit_revive = True
    if "Backpack" in gear:
        extra_loot += 1
    if "Silencer" in gear:
        silencer_bonus = True  # Placeholder

    # ENEMY ENCOUNTER SYSTEM
    enemies = [
        {"name": "Scav", "danger": 20, "reward": 1},
        {"name": "Raider", "danger": 40, "reward": 2},
        {"name": "PMC", "danger": 60, "reward": 3},
        {"name": "Sniper", "danger": 80, "reward": 3},
        {"name": "Boss", "danger": 95, "reward": 5}
    ]

    enemy = random.choice(enemies)
    await ctx.send(f"👀 You encounter a **{enemy['name']}**...")

    await asyncio.sleep(2)

    danger_roll = enemy["danger"]
    if "Armor" in gear:
        danger_roll -= 10
    if "Silencer" in gear:
        danger_roll -= 5

    fight_result = random.randint(1, 100)

    if fight_result <= danger_roll:
      if medkit_revive and random.randint(1, 100) <= 10:
        await ctx.send("🩹 Your Medkit saved you during the fight!")
    else:
        loadouts[player_id] = []  # Lose gear on death
        roast = random.choice(igor_roasts)
        await ctx.send(f"💀 The **{enemy['name']}** killed you.\n🧔 Igor: {roast}")
        return


    await ctx.send(f"✅ You took down the **{enemy['name']}**!")
    extra_loot += enemy["reward"]

    await ctx.send("🧰 Searching for loot...")
    await asyncio.sleep(2)

    # Extraction chance with gear bonuses
    base_chance = 70 + extraction_bonus
    extracted = random.choices(["extracted", "died"], weights=[base_chance, 100 - base_chance])[0]

    # Auto-create player profile
    if player_id not in player_data:
        player_data[player_id] = {
            "inventory": [],
            "cash": 0,
            "xp": 0,
            "level": 1
        }

    if extracted == "extracted":
        if extra_loot > 0:
            loot += random.sample(loot_pool, k=extra_loot)

        player_data[player_id]["inventory"].extend(loot)
        player_data[player_id]["xp"] += 10

        with open(inventory_file, "w") as f:
            json.dump(player_data, f, indent=2)

        await ctx.send(f"🛫 You extracted safely with: " + ", ".join(f"**{item}**" for item in loot))
    else:
        if medkit_revive and random.randint(1, 100) <= 10:
            player_data[player_id]["inventory"].extend(loot)
            player_data[player_id]["xp"] += 10

            with open(inventory_file, "w") as f:
                json.dump(player_data, f, indent=2)

            await ctx.send("🩹 Your Medkit kept you alive! Barely.")
            await ctx.send(f"🛫 You extracted with: " + ", ".join(f"**{item}**" for item in loot))
        else:
            loadouts[player_id] = []  # Wipe gear on failed extraction
            roast = random.choice(igor_roasts)
            await ctx.send(f"💀 You died and lost everything in this run.\n🧔 Igor: {roast}")

#RAID LABS
@bot.command(aliases=["raidlabs"])
async def raid_labs(ctx):
    player_id = str(ctx.author.id)
    player_name = ctx.author.name
    gear = loadouts.get(player_id, [])

    # Require Keycard to raid Labs
    if "Keycard" not in gear:
        await ctx.send("🔐 You need to equip a **Keycard** to access Labs. Use `!equip Keycard`.")
        return

    await ctx.send(f"🧪 {player_name} is infiltrating **The Labs**...")

    await asyncio.sleep(2)

    # Labs-specific loot pool
    loot_pool = [
        "High-End AK", "M4A1", "Labs Intel", "Rare Key", "Bitcoin", "Armor Plates",
        "Advanced Medkit", "Encrypted Drive", "Tactical Rig"
    ]
    loot = random.sample(loot_pool, k=2)

    # Gear bonuses
    extraction_bonus = 0
    extra_loot = 0
    medkit_revive = False
    silencer_bonus = False

    if "Armor" in gear:
        extraction_bonus += 10  # Less than normal raid
    if "Medkit" in gear:
        medkit_revive = True
    if "Backpack" in gear:
        extra_loot += 1
    if "Silencer" in gear:
        silencer_bonus = True

    # Labs enemies: harder
    enemies = [
        {"name": "Labs Guard", "danger": 50, "reward": 1},
        {"name": "Security Drone", "danger": 65, "reward": 2},
        {"name": "PMC Elite", "danger": 80, "reward": 2},
        {"name": "KILLA", "danger": 90, "reward": 3},
        {"name": "Labs Boss", "danger": 99, "reward": 4}
    ]

    enemy = random.choice(enemies)
    await ctx.send(f"🚨 You encounter **{enemy['name']}** inside Labs...")

    await asyncio.sleep(2)

    # Adjust danger based on gear
    danger_roll = enemy["danger"]
    if "Armor" in gear:
        danger_roll -= 10
    if "Silencer" in gear:
        danger_roll -= 5

    fight_result = random.randint(1, 100)

    if fight_result <= danger_roll:
        roast = random.choice(igor_roasts)
        await ctx.send(f"💀 The **{enemy['name']}** smoked you in Labs.\n🧔 Igor: {roast}")
        return

    await ctx.send(f"✅ You took down the **{enemy['name']}**!")
    extra_loot += enemy["reward"]

    await ctx.send("🧰 Searching for rare loot...")
    await asyncio.sleep(2)

    # Extraction chance (harder)
    base_chance = 50 + extraction_bonus
    extracted = random.choices(["extracted", "died"], weights=[base_chance, 100 - base_chance])[0]

    # Make sure profile exists
    if player_id not in player_data:
        player_data[player_id] = {
            "inventory": [],
            "cash": 0,
            "xp": 0,
            "level": 1
        }

    if extracted == "extracted":
        if extra_loot > 0:
            loot += random.sample(loot_pool, k=extra_loot)

        player_data[player_id]["inventory"].extend(loot)
        player_data[player_id]["xp"] += 20  # Labs = more XP

        with open(inventory_file, "w") as f:
            json.dump(player_data, f, indent=2)

        await ctx.send(f"🛫 You escaped Labs with: " + ", ".join(f"**{item}**" for item in loot))
    else:
        if medkit_revive and random.randint(1, 100) <= 10:
            player_data[player_id]["inventory"].extend(loot)
            player_data[player_id]["xp"] += 20

            with open(inventory_file, "w") as f:
                json.dump(player_data, f, indent=2)

            await ctx.send("🩹 Your Medkit kept you alive — barely made it out of Labs!")
            await ctx.send(f"🛫 You extracted with: " + ", ".join(f"**{item}**" for item in loot))
        else:
            roast = random.choice(igor_roasts)
            await ctx.send(f"💀 You died in Labs and lost everything.\n🧔 Igor: {roast}")



 #SELL COMMAND
@bot.command()
async def sell(ctx, *, input_text: str = None):
    player_id = str(ctx.author.id)

    # Make sure the player exists
    if player_id not in player_data:
        await ctx.send("🧔‍♂️ General Borovich stares blankly. 'You don't even have a bag, rookie.'")
        return

    inventory = player_data[player_id]["inventory"]

    # Sell all items if no input
    if not input_text:
        if not inventory:
            await ctx.send("🧔‍♂️ Borovich grunts. 'You got nothing. Don’t waste my time.'")
            return

        total = sum(loot_values.get(item, 0) for item in inventory)
        count = len(inventory)

        player_data[player_id]["cash"] += total
        player_data[player_id]["inventory"] = []

        with open(inventory_file, "w") as f:
            json.dump(player_data, f, indent=2)

        await ctx.send(f"🧔‍♂️ Borovich tosses you ${total} for {count} items. 'Now get outta here.'")
        return

    # Sell a specific item (with optional amount)
    parts = input_text.strip().split()
    if len(parts) == 0:
        await ctx.send("🧔‍♂️ Borovich: 'Use `!sell [item name] [amount]`. Or just `!sell` to dump it all.'")
        return

    # Get item and amount
    if parts[-1].isdigit():
        amount = int(parts[-1])
        item_name = " ".join(parts[:-1])
    else:
        amount = 1
        item_name = " ".join(parts)

    item = item_name.title()
    inv_items = player_data[player_id]["inventory"]

    if item not in inv_items:
        await ctx.send(f"🧔‍♂️ Borovich: 'You don't have any **{item}**, rookie.'")
        return

    item_count = inv_items.count(item)

    if amount > item_count:
        await ctx.send(f"🧔‍♂️ Borovich: 'You only got **{item_count}x {item}**. Don’t try to scam me.'")
        return

    # Calculate value and remove items
    value = loot_values.get(item, 0) * amount
    for _ in range(amount):
        inv_items.remove(item)

    player_data[player_id]["cash"] += value

    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send(f"🧔‍♂️ Borovich buys {amount}x **{item}** for ${value}. 'Good deal... for me.'")




#INVENTORY
@bot.command(aliases=["inv"])
async def inventory(ctx, member: discord.Member = None):
    target = member or ctx.author
    player_id = str(target.id)

    # Make sure the player exists in the system
    if player_id not in player_data:
        player_data[player_id] = {
            "inventory": [],
            "cash": 0,
            "xp": 0,
            "level": 1
        }

    items = player_data[player_id]["inventory"]
    cash = player_data[player_id]["cash"]

    if not items:
        if target == ctx.author:
            await ctx.send(f"🎒 Your inventory is empty.\n💰 **Cash:** ${cash}")
        else:
            await ctx.send(f"📦 {target.display_name}'s inventory is empty.\n💰 **Cash:** ${cash}")
        return

    # Count each item
    item_counts = {}
    for item in items:
        item_counts[item] = item_counts.get(item, 0) + 1

    # Build the message
    msg = f"**🧾 {target.display_name}'s Inventory:**\n"
    for item, count in item_counts.items():
        msg += f"- {item} x{count}\n"

    msg += f"\n💰 **Cash:** ${cash}"

    await ctx.send(msg)



#VALUE OF INV
@bot.command()
async def value(ctx):
    player_id = str(ctx.author.id)

    if player_id not in player_data:
        await ctx.send("🧾 You don't have an inventory yet.")
        return

    items = player_data[player_id]["inventory"]
    if not items:
        await ctx.send("📭 Your inventory is empty.")
        return

    total_value = 0
    item_totals = {}

    for item in items:
        item_totals[item] = item_totals.get(item, 0) + loot_values.get(item, 0)
        total_value += loot_values.get(item, 0)

    msg = "**💰 Loot Value Breakdown:**\n"
    for item, val in item_totals.items():
        msg += f"- {item}: ${val}\n"
    msg += f"\n**Total: ${total_value}**"

    await ctx.send(msg)


#GEAR SHOP
gear_shop = {
    "Armor": 1500,
    "Medkit": 500,
    "Silencer": 1000,
    "Ammo": 500,
}




#BUY COMMAND
@bot.command()
async def buy(ctx, *, input_text: str = None):
    player_id = str(ctx.author.id)

    if input_text is None:
        # Show Igor's shop
        shop_msg = "🧔 **Igor's Gear Shop**\nHere's what I've got for you today:\n\n"
        for item, price in gear_shop.items():
            shop_msg += f"🛒 {item} — ${price}\n"
        shop_msg += "\nUse `!buy [item name] [amount]` to purchase. Example: `!buy medkit 2`"
        await ctx.send(shop_msg)
        return

    # Split input into item and amount
    parts = input_text.strip().split()
    if len(parts) == 0:
        await ctx.send("🧔 Igor says: 'Say what you want, rookie.'")
        return

    # Try to get item name and optional amount
    if parts[-1].isdigit():
        amount = int(parts[-1])
        item_name = " ".join(parts[:-1])
    else:
        amount = 1
        item_name = " ".join(parts)

    item = item_name.title()

    if item not in gear_shop:
        await ctx.send(f"🧔 Igor frowns. 'Ain’t got no **{item}**. Try again.'")
        return

    cost = gear_shop[item] * amount

    # Make sure player exists
    if player_id not in player_data:
        player_data[player_id] = {
            "inventory": [],
            "cash": 0,
            "xp": 0,
            "level": 1
        }

    if player_data[player_id]["cash"] < cost:
        await ctx.send(f"🧔 Igor snorts. 'You need **${cost}** for that. Come back richer.'")
        return

    # Process purchase
    player_data[player_id]["cash"] -= cost
    player_data[player_id]["inventory"].extend([item] * amount)

    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send(f"🧔 Igor hands you **{amount}x {item}**. 'Don’t waste it, yeah?'")





#XP SYSTEM
@bot.command()
async def xp(ctx):
    player_id = str(ctx.author.id)
    data = player_data.get(player_id, {"xp": 0, "level": 1})
    xp = data["xp"]
    level = data["level"]

    await ctx.send(f"🏅 XP: {xp} | Level: {level}")


#TRADE SYSTEM
@bot.command()
async def trade(ctx, member: discord.Member = None, *, trade_text: str = None):
    if member is None or trade_text is None:
        await ctx.send("🧾 Usage: `!trade @user item1 amount1 for item2 amount2`")
        return

    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)

    if sender_id == receiver_id:
        await ctx.send("🧔 Igor: 'Trying to trade with yourself again? Rookie mistake.'")
        return

    if receiver_id in pending_trades:
        await ctx.send("🧔 Igor: 'That player already has a pending trade request.'")
        return

    # Parse trade string (e.g. "medkit 2 for silencer 1")
    try:
        parts = trade_text.lower().split(" for ")
        give_part = parts[0].rsplit(" ", 1)
        take_part = parts[1].rsplit(" ", 1)

        give_item = give_part[0].title()
        give_amount = int(give_part[1])

        take_item = take_part[0].title()
        take_amount = int(take_part[1])
    except:
        await ctx.send("❌ Invalid format. Try `!trade @user medkit 2 for silencer 1`")
        return

    # Check sender inventory
    if sender_id not in player_data or player_data[sender_id]["inventory"].count(give_item) < give_amount:
        await ctx.send(f"🧔 Igor: 'You don’t have enough **{give_item}**.'")
        return

    # Save the pending trade
    pending_trades[receiver_id] = {
        "from": sender_id,
        "give_item": give_item,
        "give_amount": give_amount,
        "take_item": take_item,
        "take_amount": take_amount
    }

    await ctx.send(f"📨 {member.mention}, {ctx.author.mention} wants to trade:\n"
                   f"**{give_amount}x {give_item}** for **{take_amount}x {take_item}**\n"
                   f"Respond with `!accept` or `!decline`.")


#!accept COMMAND
@bot.command()
async def accept(ctx):
    receiver_id = str(ctx.author.id)

    if receiver_id not in pending_trades:
        await ctx.send("📭 You have no pending trade requests.")
        return

    trade = pending_trades[receiver_id]
    sender_id = trade["from"]

    # Check both players have what they need
    if player_data[sender_id]["inventory"].count(trade["give_item"]) < trade["give_amount"]:
        await ctx.send("❌ Trade failed. The sender no longer has the item.")
        del pending_trades[receiver_id]
        return

    if player_data[receiver_id]["inventory"].count(trade["take_item"]) < trade["take_amount"]:
        await ctx.send("❌ Trade failed. You no longer have the item.")
        del pending_trades[receiver_id]
        return

    # Swap items
    for _ in range(trade["give_amount"]):
        player_data[sender_id]["inventory"].remove(trade["give_item"])
        player_data[receiver_id]["inventory"].append(trade["give_item"])

    for _ in range(trade["take_amount"]):
        player_data[receiver_id]["inventory"].remove(trade["take_item"])
        player_data[sender_id]["inventory"].append(trade["take_item"])

    # Save
    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send(f"✅ Trade complete between <@{sender_id}> and <@{receiver_id}>.")
    del pending_trades[receiver_id]

#!decline COMMAND
@bot.command()
async def decline(ctx):
    receiver_id = str(ctx.author.id)

    if receiver_id not in pending_trades:
        await ctx.send("📭 You have no pending trade requests.")
        return

    del pending_trades[receiver_id]
    await ctx.send("❌ Trade declined. Igor nods silently.")

#EQUIP LOADOUT
@bot.command(aliases=["e"])
async def equip(ctx, *, item: str = None):
    player_id = str(ctx.author.id)

    if item is None:
        await ctx.send("Usage: `!equip [item name]`")
        return

    item = item.strip()

    if player_id not in player_data or not player_data[player_id]["inventory"]:
        await ctx.send("🧔 Igor: 'You don’t have any gear at all, rookie.'")
        return

    # Case-insensitive match
    matched_item = None
    for inv_item in player_data[player_id]["inventory"]:
        if inv_item.lower() == item.lower():
            matched_item = inv_item
            break

    if not matched_item:
        await ctx.send("🧔 Igor: 'You don't have that gear, rookie.'")
        return

    # Initialize loadout if needed
    if player_id not in loadouts:
        loadouts[player_id] = []

    if matched_item in loadouts[player_id]:
        await ctx.send(f"🧔 Igor: 'You're already wearing **{matched_item}**.'")
        return

    # Remove from inventory and add to loadout
    player_data[player_id]["inventory"].remove(matched_item)
    loadouts[player_id].append(matched_item)

    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send(f"✅ Equipped **{matched_item}**.")




#!LOADOUT

@bot.command()
async def loadout(ctx):
    player_id = str(ctx.author.id)
    gear = loadouts.get(player_id, [])

    if not gear:
        await ctx.send("🧍 You have no gear equipped.")
    else:
        msg = "**🛡️ Current Loadout:**\n"
        for g in gear:
            msg += f"- {g}\n"
        await ctx.send(msg)

#!UNEQUIP
@bot.command(aliases=["u"])
async def unequip(ctx, *, item: str = None):
    player_id = str(ctx.author.id)

    if item is None:
        await ctx.send("Usage: `!unequip [item name]`")
        return

    item = item.strip()

    if player_id not in loadouts or not loadouts[player_id]:
        await ctx.send("🧍 You have nothing equipped.")
        return

    # Case-insensitive match
    matched_item = None
    for equipped in loadouts[player_id]:
        if equipped.lower() == item.lower():
            matched_item = equipped
            break

    if not matched_item:
        await ctx.send(f"🧍 You're not wearing **{item}**.")
        return

    # Remove from loadout and return to inventory
    loadouts[player_id].remove(matched_item)

    if player_id not in player_data:
        player_data[player_id] = {
            "inventory": [],
            "cash": 0,
            "xp": 0,
            "level": 1
        }

    player_data[player_id]["inventory"].append(matched_item)

    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send(f"🧍 Unequipped **{matched_item}** and returned it to your inventory.")



#!COMMANDS
@bot.command(aliases=["com"])
async def commands(ctx):
    msg = (
        "**📜 LOOTED Commands:**\n"
        "🎯 `!raid` – Enter a raid\n"
        "🎒 `!inventory` / `!inv` – View your stash\n"
        "💰 `!value` – See loot worth\n"
        "💵 `!sell [item] [amount]` – Sell items or use `!sell` to sell all\n"
        "🛒 `!buy [item] [amount]` – Buy gear from Igor\n"
        "🧍 `!equip [item]` – Equip gear before raids\n"
        "🧾 `!loadout` – View equipped gear\n"
        "🛑 `!unequip [item]` – Remove gear\n"
        "📈 `!xp` – Check XP and level\n"
        "🔁 `!trade @user item1 amount1 for item2 amount2` – Trade with players\n"
        "✅ `!accept` / ❌ `!decline` – Respond to trade offers\n"
        "🧾 `!commands` / `!com` – Show this command list"
    )
    await ctx.send(msg)





#!JOIN RAID
@bot.command()
async def joinraid(ctx):
    player_id = str(ctx.author.id)

    if not global_raid["active"]:
        await ctx.send("❌ There's no active global raid. Wait for one to be started.")
        return

    if player_id in global_raid["players"]:
        await ctx.send("⚠️ You're already in this raid.")
        return

    global_raid["players"].append(player_id)
    await ctx.send(f"✅ {ctx.author.display_name} has joined the global raid!")


#!START RAID
@has_permissions(administrator=True)
@bot.command()
async def startraid(ctx):
    if global_raid["active"]:
        await ctx.send("⚠️ A global raid is already active.")
        return

    global_raid["active"] = True
    global_raid["players"] = []
    global_raid["started_by"] = str(ctx.author.id)

    await ctx.send("🌐 A global raid has been launched! Type `!joinraid` to enter.\nStarts in 30 seconds...")

    await asyncio.sleep(30)

    if len(global_raid["players"]) == 0:
        await ctx.send("⏹️ No one joined the raid. It was cancelled.")
        global_raid["active"] = False
        return

    await ctx.send(f"🔫 {len(global_raid['players'])} players are entering the global raid!")

    raid_results = []

    for pid in global_raid["players"]:
        member = ctx.guild.get_member(int(pid))
        if not member:
            continue

        await ctx.send(f"──────────\n🎮 **{member.display_name}**'s Raid\n──────────")

        loot_pool = list(loot_values.keys())
        loot = random.sample(loot_pool, k=2)

        if pid not in player_data:
            player_data[pid] = {
                "inventory": [],
                "cash": 0,
                "xp": 0,
                "level": 1
            }

        gear = loadouts.get(pid, [])
        extraction_bonus = 10  # Global raids are 10% easier
        extra_loot = 0
        medkit_revive = False

        if "Armor" in gear:
            extraction_bonus += 20
        if "Backpack" in gear:
            extra_loot += 1
        if "Medkit" in gear:
            medkit_revive = True

        # ENEMY ENCOUNTER
        enemies = [
            {"name": "Scav", "danger": 20, "reward": 1},
            {"name": "Raider", "danger": 40, "reward": 2},
            {"name": "PMC", "danger": 60, "reward": 3},
            {"name": "Sniper", "danger": 80, "reward": 3},
            {"name": "Boss", "danger": 95, "reward": 5}
        ]

        enemy = random.choice(enemies)
        await ctx.send(f"👀 {member.display_name} encounters a **{enemy['name']}**...")

        await asyncio.sleep(1.5)

        danger_roll = enemy["danger"] - 10
        if "Armor" in gear:
            danger_roll -= 10

        if random.randint(1, 100) <= danger_roll:
            if medkit_revive and random.randint(1, 100) <= 10:
                await ctx.send(f"🩹 {member.display_name}'s Medkit saved them from the **{enemy['name']}**!")
                raid_results.append(f"🩹 **{member.display_name}** – Medkit saved them from **{enemy['name']}**")
            else:
                loadouts[pid] = []
                roast = random.choice(igor_roasts)
                await ctx.send(f"💀 {member.display_name} was killed by the **{enemy['name']}**.\n🧔 Igor: {roast}")
                raid_results.append(f"💀 **{member.display_name}** – Killed by **{enemy['name']}**")
                continue
        else:
            await ctx.send(f"✅ {member.display_name} defeated the **{enemy['name']}**!")
            extra_loot += enemy["reward"]

        await asyncio.sleep(1.5)

        # EXTRACTION
        extract_chance = 70 + extraction_bonus
        if random.randint(1, 100) > extract_chance:
            if medkit_revive and random.randint(1, 100) <= 10:
                await ctx.send(f"🩹 {member.display_name}'s Medkit saved them during extraction!")
                raid_results.append(f"🩹 **{member.display_name}** – Medkit saved them during extraction")
            else:
                loadouts[pid] = []
                roast = random.choice(igor_roasts)
                await ctx.send(f"💀 {member.display_name} failed to extract.\n🧔 Igor: {roast}")
                raid_results.append(f"💀 **{member.display_name}** – Failed extraction")
                continue

        if extra_loot > 0:
            loot += random.sample(loot_pool, k=extra_loot)

        player_data[pid]["inventory"].extend(loot)
        player_data[pid]["xp"] += 10

        await ctx.send(f"🛫 {member.display_name} extracted with: " + ", ".join(f"**{item}**" for item in loot))
        raid_results.append(f"✅ **{member.display_name}** – Extracted with {len(loot)} loot, +10 XP")

        await asyncio.sleep(1)

    # Save progress
    with open(inventory_file, "w") as f:
        json.dump(player_data, f, indent=2)

    await ctx.send("✅ Global raid complete! GG.")

    if raid_results:
        summary = "**📊 Global Raid Summary:**\n" + "\n".join(raid_results)
    else:
        summary = "📊 Global Raid Summary:\nNo survivors. Igor is disappointed."

    await ctx.send(summary)

    global_raid["active"] = False














bot.run(os.getenv("DISCORD_BOT_TOKEN"))
