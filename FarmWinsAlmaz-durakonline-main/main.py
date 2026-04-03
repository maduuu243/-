import os
import time
import multiprocessing
from durakonline import durakonline
from datetime import datetime

MAIN_TOKEN = os.environ.get("MAIN_TOKEN")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not MAIN_TOKEN or not BOT_TOKEN:
    raise RuntimeError("Environment variables MAIN_TOKEN and BOT_TOKEN must be set.")

COUNT: int = 2100
DEBUG_MODE: bool = False

SERVERS = ["u1", "u2", "u3"]


class Almaz:

    def start_game(self, server_id: str, count: int = 1000):
        self.log("Start process", server_id)

        main = durakonline.Client(MAIN_TOKEN, server_id=server_id, tag="[MAIN]", debug=DEBUG_MODE)
        bot = durakonline.Client(BOT_TOKEN, server_id=server_id, tag="[BOT]", debug=DEBUG_MODE)

        game = bot.game.create(100, "1", 2, 52)
        main.game.join("1", game.id)
        main._get_data("game")

        for i in range(count):
            self.log(f"{i+1} game", server_id)

            main.game.ready()
            bot.game.ready()

            for _ in range(4):
                try:
                    main_cards = main._get_data("hand")["cards"]
                except:
                    main_cards = []

                try:
                    bot_cards = bot._get_data("hand")["cards"]
                except:
                    bot_cards = []

                mode = bot._get_data("mode")

                if mode["0"] == 1:
                    if bot_cards:
                        bot.game.turn(bot_cards[0])
                    time.sleep(.1)
                    main.game.take()
                    time.sleep(.1)
                    bot.game._pass()
                else:
                    if main_cards:
                        main.game.turn(main_cards[0])
                    time.sleep(.1)
                    bot.game.take()
                    time.sleep(.1)
                    main.game._pass()

            bot.game.surrender()
            bot._get_data("game_over")

        main.game.leave(game.id)
        self.log("Leave", server_id)

        data = main._get_data("uu")
        while data["k"] != "points":
            data = main._get_data("uu")

        self.log(f"Balance: {data.get('v')}", server_id)

    def log(self, message: str, tag: str):
        print(f">> [{tag}] [{datetime.now().strftime('%H:%M:%S')}] {message}")


def run_process(server_id):
    bot = Almaz()
    bot.start_game(server_id, COUNT)


if __name__ == "__main__":
    processes = []

    for server in SERVERS:
        p = multiprocessing.Process(target=run_process, args=(server,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
