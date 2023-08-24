import discord
import data_management


class RolePreferenceSelect(discord.ui.View):
    # Select menu for choosing your role preferences

    @discord.ui.select(
        custom_id="CarryPref", placeholder="Carry Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_carry_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, [3], select_item.values[0])
        await interaction.user.send(content=f'{select_item.placeholder} has been updated')
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="MidPref", placeholder="Midlane Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_mid_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, [4], select_item.values[0])
        await interaction.user.send(content=f'{select_item.placeholder} has been updated')
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="OffPref", placeholder="Offlane Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_off_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, [5], select_item.values[0])
        await interaction.user.send(content=f'{select_item.placeholder} has been updated')
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="SoftPref", placeholder="Soft Support Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_soft_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, [6], select_item.values[0])
        await interaction.user.send(content=f'{select_item.placeholder} has been updated')
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="HardPref", placeholder="Hard Support Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_hard_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, [7], select_item.values[0])
        await interaction.user.send(content=f'{select_item.placeholder} has been updated')
        await interaction.response.defer()
