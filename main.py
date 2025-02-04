from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Set
import subprocess

app = FastAPI()

class BotStatus(BaseModel):
    running: bool
    enabled_cogs: Set[str]

# État initial du bot
bot_status = BotStatus(running=False, enabled_cogs=set())

@app.get("/api/status")
def get_status():
    return bot_status

@app.post("/api/toggle-bot")
def toggle_bot():
    bot_status.running = not bot_status.running
    if bot_status.running:
        subprocess.Popen(["python", "bot.py"])
    else:
        subprocess.run(["pkill", "-f", "bot.py"])
    return {"message": f"Bot {'démarré' if bot_status.running else 'arrêté'}"}

class CogUpdate(BaseModel):
    cog: str

@app.post("/api/toggle-cog")
def toggle_cog(update: CogUpdate):
    if update.cog in bot_status.enabled_cogs:
        bot_status.enabled_cogs.remove(update.cog)
        # Désactiver le cog
        subprocess.run(["python", "-c", f"from bot import bot; bot.unload_extension('cogs.{update.cog}')"])
    else:
        bot_status.enabled_cogs.add(update.cog)
        # Activer le cog
        subprocess.run(["python", "-c", f"from bot import bot; bot.load_extension('cogs.{update.cog}')"])

    return {"message": f"Cog {update.cog} {'activé' if update.cog in bot_status.enabled_cogs else 'désactivé'}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
