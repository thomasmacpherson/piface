import gtk

import game
import gui


def begin(question_file=None):
	gtk.gdk.threads_init() # init the gdk threads
	the_gui = gui.RacingPiGUI()
	the_game = game.RacingPiGame(the_gui, question_file)
	the_gui.the_game = the_game

	the_game.start()
	the_gui.main()

	the_game.join()
