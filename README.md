# Thanks

A Discord bot that rewards helpful members. When someone thanks another member by mentioning them, that member earns a point.

## How it works

Send a message that contains a thank word and **mention** (or **reply to**) the member you want to thank:

> "Thanks @someone for the help!"

The bot will confirm the point with a message in the channel. Supported thank words include: `thanks`, `ty`, `merci`, `gracias`, `danke`, `спасибо`, and more.

**Limits:**
- You can give points once every **60 minutes**
- A member can receive at most **5 points per day**

## Server setup

### Required bot permissions

Make sure the bot's role has the following permissions in your server (or in the specific channels you want it to monitor):

| Permission | Why |
|---|---|
| **View Channels** | See channels and read messages to detect thank words |
| **Send Messages** | Post the point confirmation |
| **Embed Links** | Send the confirmation as an embed |
| **Manage Roles** | Assign autoroles when members hit a points threshold |

### Role position for autoroles

If you use the `/add_autorole` command, the bot's role must be **above** the roles it is supposed to assign in your server's role list (**Server Settings → Roles**). Roles below the bot's role cannot be assigned by it.

> Note: the bot will refuse to assign a role that has sensitive permissions (Administrator, Manage Roles, Manage Channels, Moderate Members).


## Commands

| Command | Who | Description |
|---|---|---|
| `/help` | Everyone | Show all available commands |
| `/stats_thanks` | Everyone | Check your points and how many times you've thanked others |
| `/stats_thanks @user` | Everyone | Check another member's stats |
| `/leaderboard` | Everyone | View the server points leaderboard |
| `/channel_blacklist #channel` | Admin | Stop the bot from tracking thanks in a channel |
| `/channel_whitelist #channel` | Admin | Re-enable tracking in a blacklisted channel |
| `/add_autorole @role <points>` | Admin | Assign a role automatically when a member reaches a points threshold |
| `/remove_autorole @role` | Admin | Remove an autorole assignment |
| `/show_autoroles` | Admin | Show all autoroles for the server |
