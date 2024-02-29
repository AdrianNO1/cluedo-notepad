This is a simple notepad sheet thing for the game cluedo. I got the idea when playing a game with my distracted family, who often give out wrong information and I am unable to erase the notes I already made using my ballpoint pen. Sharpening my pencil was too much effort, so instead i made this program. It's 100% reusable too!

Controls:
- Left click to select a person, weapon, room, or player, Right click to deselect
- Left click on a tile to toggle it between X and O, Right click to remove the mark
- Press a number to add it to the hovered tile
- Press the same number again to remove it
- Press 'v' to mark a tile as shown to a player
- Press 'n' to mark that the selected player does not have the selected person, weapon and room
- Press 'h' to mark that the selected player has at least one of the selected person, weapon and room
- Press 'r' to randomize the board to confuse the players (is not stored in the redo/undo array, so redo to undo)
- Press 'u' to hide the entire board (is not stored in the redo/undo array, so redo to undo)
- Press 'a' to fill in more information on the board
- Press 's' to force save the board to the file
- Press 'l' to load the board from the file (is done automatically on startup so idk why I made a keybind for this)
- Ctrl + Z to undo
- Ctrl + Y to redo

Note: If you play cluedo way too much, delete rows.pkl occasionally so it doesnt take up much space as it stores the entire history of the board since its creation.