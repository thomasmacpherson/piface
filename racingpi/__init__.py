import gtk

import game
import gui


def begin():
	gtk.gdk.threads_init() # init the gdk threads
	the_gui = gui.RacingPiGUI()
	the_game = game.RacingPiGame(the_gui)

	the_game.start()
	the_gui.main()
