import subprocess
import os

def run_command(cmd):
    print(f"\n▶️ Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        exit(result.returncode)

run_command("pip install -r requirements.txt --no-cache-dir")

run_command("python3 src/fix_emoji.py")

run_command("python3 src/bot.py")

print("\n🎉 All steps completed successfully!")
