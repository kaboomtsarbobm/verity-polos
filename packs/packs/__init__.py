async def setup(bot):
    from .cog import AdminPacksCog
    await bot.add_cog(AdminPacksCog(bot))