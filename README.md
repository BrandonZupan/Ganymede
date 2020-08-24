# Ganymede
Module based Discord Bot

## Contributing
Contributions should be done through issues and pull requests. If there is a new 
feature that is desired, add it as an issue then work on it from there. 

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) when contributing 
to this repository. 

If adding features, do so through 
[discord.py cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html). 
This makes the bot more expandable and allows users to host their code in their 
own repo. 

### Adding a Cog
1. Create your cog. Pass in any required data (i.e. config values) as parameters 
for the class constructor. 
1. Add your code to the bot. 
    - If working in **Ganymede** repository: Put code in the `cogs` folder. Create 
    an issue, branch, and pull request for the new content. 
    - If working in your own repo: Create an issue, branch, and pull request and 
    add the repo as a [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules). 
    Use the following command to add it:
    ```
    git submodule add link/to/repository
    ```
    Make sure that the code can be imported into Ganymede. If it can't, it may need 
    to be restructed to be importable (make the imported module top level)
1. Import into Ganymede. 
    1. Inside `ganymede.py`, add any required config options to the 
    `config_options` list. 
    1. Import the cog at the top of the file under the `# Cogs` comment
    1. Inside `run()` under the `# Load cogs` comment, add the cog to the bot. 
    If the cog needs a function called to run, call it here. 
    ```python
    async def run():
        ...
            # Load cogs
            cog1 = Cog1(bot, db)    # Cog with initialization
            await cog1.setup()
            bot.add_cog(cog1)

            bot.add_cog(Cog2(bot))   # Cog without initialization

            