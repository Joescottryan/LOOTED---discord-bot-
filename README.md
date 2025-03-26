# 💼 LOOTED – A Discord Extraction-Style Raid Bot

LOOTED is a fast-paced, text-based Discord bot where players dive into dangerous raids, fight enemies, collect loot, equip gear, and try to extract safely — inspired by games like Escape from Tarkov.

---

## ⚙️ Features

- 🎯 `!raid` – Solo raids with risk & reward
- 🧪 `!raidlabs` – High-risk, high-reward raids (Keycard required)
- 🎒 `!inventory` – View your stash
- 💰 `!sell`, `!buy`, `!value` – Full player economy
- 🛡️ Gear system – Equip weapons, armor, and utilities
- 🧠 XP and leveling
- 🤝 Player trading (`!trade`, `!accept`)
- 🌐 **Global raids** (`!startraid`, `!joinraid`) – Raid as a squad and survive together
- 🧔 Igor – Your personal loot gremlin, roasts you when you die 😤

---




### . Set up your environment
Create a `.env` file in the root folder:

```
DISCORD_BOT_TOKEN=your_bot_token_here
```

### . Install requirements
```bash
pip install -r requirements.txt
```

> (Make sure you have Python 3.10+ installed)

### . Run the bot
```bash
python Looted_bot.py
```

---

## 📂 File Structure

```
/looted-bot/
├── Looted_bot.py          # Main bot logic
├── inventory.json         # Player data (auto-generated)
├── .env                   # Your bot token (DO NOT COMMIT THIS)
├── .gitignore             # Keeps secrets and cache out of Git
└── README.md              # You're here!
```

---

## 🔐 Important: Keep Your Bot Token Safe

- NEVER hardcode your token in the Python file
- Always use `.env` + `os.getenv("DISCORD_BOT_TOKEN")`
- Your `.env` should be listed in `.gitignore`



---













---

## 🧔 Igor Says

> “Loot is temporary. Humiliation is forever.”
