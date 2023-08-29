import discord
import data_management
import check_user

# Select menus for choosing your role preferences
class RolePreferenceSelect(discord.ui.View):


    test_list = []

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
        test_value = interaction.message.id
        self.test_list.append(interaction.message.id)
        if self.test_list.count(test_value) == 5:
            print(test_value)
            await interaction.response.defer()
            await interaction.followup.edit_message(test_value,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
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
        test_value = interaction.message.id
        self.test_list.append(interaction.message.id)
        if self.test_list.count(test_value) == 5:
            print(test_value)
            [i for i in self.test_list if i == 5]
            user_data = data_management.view_user_data(interaction.user.id)
            await interaction.response.defer()
            await interaction.followup.edit_message(test_value,
                                                    content="Thank you for updating your preferences", view=None,
                                                    embed=check_user.user_embed(user_data, interaction.user, interaction.guild))
        else:
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
        test_value = interaction.message.id
        self.test_list.append(interaction.message.id)
        if self.test_list.count(test_value) == 5:
            print(test_value)
            [i for i in self.test_list if i == 5]
            user_data = data_management.view_user_data(interaction.user.id)
            await interaction.response.defer()
            await interaction.followup.edit_message(test_value,
                                                    content="Thank you for updating your preferences", view=None,
                                                    embed=check_user.user_embed(user_data, interaction.user, interaction.guild))
        else:
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
        test_value = interaction.message.id
        self.test_list.append(interaction.message.id)
        if self.test_list.count(test_value) == 5:
            print(test_value)
            [i for i in self.test_list if i == 5]
            user_data = data_management.view_user_data(interaction.user.id)
            await interaction.response.defer()
            await interaction.followup.edit_message(test_value,
                                                    content="Thank you for updating your preferences", view=None,
                                                    embed=check_user.user_embed(user_data, interaction.user, interaction.guild))
        else:
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
        test_value = interaction.message.id
        self.test_list.append(interaction.message.id)
        if self.test_list.count(test_value) == 5:
            print(test_value)
            [i for i in self.test_list if i == 5]
            user_data = data_management.view_user_data(interaction.user.id)
            await interaction.response.defer()
            await interaction.followup.edit_message(test_value,
                                                    content="Thank you for updating your preferences", view=None,
                                                    embed=check_user.user_embed(user_data, interaction.user, interaction.guild))
        else:
            await interaction.response.defer()
