"""The Mosasauraboard's main program: start the host and never return.
The behaviours are in /behaviours; what they ask to keep is in /saved. See software/README.md."""
from dino.hw_board import Board
from dino.host import Host

board = Board()
# A flat battery: do not light anything, sleep until USB arrives. Otherwise each start-up dips the
# supply, the supervisor resets the module and the board loops (NOTES.md, "For firmware").
if board.battery_volts() < 3.5 and not board.vbus.value:
    board.sleep_until_plugged_in()
Host(board, "/behaviours", "/saved").run()
