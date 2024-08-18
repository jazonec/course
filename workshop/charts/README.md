## Install Telegram Bot

```bash
helm \
--namespace bitrix24-salesman-bot \
upgrade --install \
telegram-bot \
--set image.tag=TAG \
./telegram-bot
```
