import logging

from discord_webhook import DiscordWebhook, DiscordEmbed


class Discord:

    def __init__(self, webhook: str | list[str]):
        self.webhook = DiscordWebhook(url=webhook, rate_limit_retry=True)

    def set_embed(self, title: str, description: str, color: str | int):
        self.webhook.remove_embeds()  # Reset body of message

        embed = DiscordEmbed(title=title, description=description, color=color)

        embed.set_author(name="Instagramer", url="https://github.com/Koenigseder/instagramer",
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Instagram_logo_2022.svg/1200px-Instagram_logo_2022.svg.png")

        embed.set_timestamp()

        self.webhook.add_embed(embed)

    def send_message(self):
        try:
            response = self.webhook.execute()
            if response.ok:
                logging.info("Discord message sent!")
            return response

        except BaseException as e:
            logging.error(f"Message could not be sent: {e}")
