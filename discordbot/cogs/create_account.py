import discord
from discord.ext import tasks, commands
import os, json
import aiohttp
from urllib.parse import urlencode
from utils import log

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Create_account(bot))

JSON_FILE = "button_message.json"
VERIFY_CHANNEL_ID = 1419358816876625980

SECRET_KEY = os.environ.get("SECRET_KEY")
FRONTEND = os.environ["FRONTEND"].rstrip('/')
BACKEND = os.environ["BACKEND"].rstrip('/')

HEADERS = {
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json"
}

class SignupButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def check_user_exists(self, user: discord.User) -> bool:
        """Asynchronous request to check if user exists."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BACKEND}/discord/user",
                    headers=HEADERS,
                    params={"discord_id": str(user.id)},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return bool(data)
                    return False
        except Exception as e:
            log(f"Error checking user existence: {e}")
            return False
    
    async def create_verify(self, user: discord.User) -> str:
        """Asynchronous request to create verification token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND}/discord/create",
                headers=HEADERS,
                json={"discord_id": str(user.id)},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return str(data)
    
    async def process_verification(self, interaction: discord.Interaction, action_type: str):
        """Generates link and sends the followup message."""
        try:
            secret = await self.create_verify(interaction.user)
            params = urlencode({"type": action_type, "secret": secret})
            link = f"{FRONTEND}/discord?{params}"

            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Xác thực tài khoản", 
                url=link, 
                style=discord.ButtonStyle.link
            ))

            await interaction.followup.send(
                "Nhấn nút dưới đây để tiếp tục xử lý tài khoản (liên kết hết hạn sau 5 phút).", 
                view=view, 
                ephemeral=True
            )
        except Exception as e:
            log(f"Failed to create verify link for {interaction.user.id}: {e}")
            await interaction.followup.send(
                "Có lỗi khi tạo link xác thực, vui lòng thử lại sau.", 
                ephemeral=True
            )

    @discord.ui.button(label="Sign up", style=discord.ButtonStyle.green, custom_id="signup_click")
    async def signup_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Defer ONLY ONCE at the start, with ephemeral=True
        await interaction.response.defer(ephemeral=True)

        # 2. Perform async check
        if await self.check_user_exists(interaction.user):
            return await interaction.followup.send("Bạn đã có tài khoản trên hệ thống.", ephemeral=True)

        # 3. Process link creation
        await self.process_verification(interaction, "create_account")

    @discord.ui.button(label="Forgot password", style=discord.ButtonStyle.danger, custom_id="forgotpassword_click")
    async def forgotpassword_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if not await self.check_user_exists(interaction.user):
            return await interaction.followup.send("Tài khoản của bạn không tồn tại để khôi phục mật khẩu. Vui lòng Sign up trước.", ephemeral=True)

        await self.process_verification(interaction, "change_password")
    
    @discord.ui.button(label="Quick Login", style=discord.ButtonStyle.primary, custom_id="quicklogin_click")
    async def quicklogin_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if not await self.check_user_exists(interaction.user):
            return await interaction.followup.send("Tài khoản của bạn không tồn tại. Vui lòng Sign up trước.", ephemeral=True)

        await self.process_verification(interaction, "quick_login")


class Create_account(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def cog_load(self):
        # Register persistent view
        self.bot.add_view(SignupButton())
        self.check_button.start()
        
    def cog_unload(self): 
        self.check_button.cancel()

    def load_message_id(self):
        if not os.path.exists(JSON_FILE):
            return None
        try:
            with open(JSON_FILE, "r") as f:
                return json.load(f).get("message_id")
        except Exception:
            return None
            
    def save_message_id(self, msg_id: int):
        with open(JSON_FILE, "w") as f:
            json.dump({"message_id": msg_id}, f)

    @tasks.loop(minutes=5)
    async def check_button(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(VERIFY_CHANNEL_ID)
        if channel is None:
            log("⚠ Channel not found")
            return

        msg_id = self.load_message_id()
        if msg_id:
            try:
                await channel.fetch_message(msg_id)
                log("🧕 Button message still exists")
                return
            except discord.NotFound:
                log("❌ Button message not found, re-sending...")

        view = SignupButton()
        msg = await channel.send(view=view)
        self.save_message_id(msg.id)
        log(f"✅ Sent new button message with id {msg.id}")