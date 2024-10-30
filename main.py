import discord.ext
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import bot

import keys
from keys import gpt_key
from keys import discord_key

import os
import json

from difflib import get_close_matches

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/',intents=intents, help_command=None)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

@bot.event
async def on_ready():
    print("Moo Deng is ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="chat", description="Chat with Moo Deng.")
async def chat(interaction, message: str):
    knowledge_base: dict = load_knowledge_base("knowledge_base.json")

    best_match: str | None = find_best_match(message, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer: str = get_answer_for_question(best_match, knowledge_base)
    else:
        answer: str = "idk dat. can u teach me using `/teach`?"

    message_to_send = f"<@{interaction.user.id}>: {message}\n**Me**: {answer}"

    await interaction.response.send_message(message_to_send)

class TeachUI(discord.ui.Modal, title="Teach Moo Deng"):
    # Ensure knowledge_base.json exists and is properly formatted before loading
    try:
        knowledge_base: dict = load_knowledge_base("knowledge_base.json")
    except json.JSONDecodeError:
        # Initialize the file with an empty structure if it fails to load
        knowledge_base = {"questions": []}
        save_knowledge_base("knowledge_base.json", knowledge_base)

    new_question = discord.ui.TextInput(label="Question", style=discord.TextStyle.paragraph, placeholder="Enter question here.", required=True)
    new_answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.paragraph, placeholder="Enter answer here.", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # Append the new question and answer
        self.knowledge_base["questions"].append({
            "question": self.new_question.value,
            "answer": self.new_answer.value
        })
        save_knowledge_base("knowledge_base.json", self.knowledge_base)

        embed = discord.Embed(
            title=f"look what {interaction.user.name} taught me",
            description=f"Question: {self.new_question.value}\nAnswer: {self.new_answer.value}",  # Corrected escape sequence
            colour=0xe63b7a
        )

        embed.set_author(name="Moo Deng")
        embed.set_thumbnail(url="https://images.lifestyleasia.com/wp-content/uploads/sites/2/2024/09/24163013/460338167_543284354878326_8062202962983340092_n-1.jpeg")

        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="teach", description="Teach Moo Deng.")
async def teach(interaction: discord.Interaction):
    await interaction.response.send_modal(TeachUI())

bot.run(discord_key)