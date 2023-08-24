import discord
import numpy as np
import data_management

class RolePreferenceSelect(discord.ui.View):
    # Select menu for choosing your role preferences
    role_pref = np.empty(5, dtype=int)
    role_pref.fill(5)
    selected = []

    def update_roles(self, number, role_choice, custom_id, user):
        check = False
        self.role_pref[number] = role_choice
        if custom_id not in self.selected:
            self.selected.append(custom_id)
        print(self.selected)
        print(len(self.selected))
        if len(self.selected) == 5:
            data_management.update_user_data(user.id, [3, 4, 5, 6, 7], self.role_pref)
            check = True
            self.selected.clear()
        return check

    @discord.ui.select(
        custom_id="CarryPref", placeholder="Carry Preference", max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_carry_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        role_check = self.update_roles(0, select_item.values[0], select_item.custom_id, interaction.user)
        if role_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id)

    @discord.ui.select(
        custom_id="MidPref", placeholder="Midlane Preference", max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_mid_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        role_check = self.update_roles(1, select_item.values[0], select_item.custom_id, interaction.user)
        if role_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id)

    @discord.ui.select(
        custom_id="OffPref", placeholder="Offlane Preference", max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_off_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        role_check = self.update_roles(2, select_item.values[0], select_item.custom_id, interaction.user)
        if role_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id)

    @discord.ui.select(
        custom_id="SoftPref", placeholder="Soft Support Preference", max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_soft_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        role_check = self.update_roles(3, select_item.values[0], select_item.custom_id, interaction.user)
        if role_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id)

    @discord.ui.select(
        custom_id="HardPref", placeholder="Hard Support Preference", max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_hard_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        role_check = self.update_roles(4, select_item.values[0], select_item.custom_id, interaction.user)
        if role_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id)
