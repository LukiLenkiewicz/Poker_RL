from game import Game

def main():
    game = Game(4, 100000, 25, 1000, q_agent=True, q_agent_train=True)
    game.start_game()

if __name__ == "__main__":
    main()
