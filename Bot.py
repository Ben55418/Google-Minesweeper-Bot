import cv2
import numpy as np
import pyautogui
import time

pyautogui.PAUSE = 0.01

# inquire the user about some data
flag_total = -1
width = -1
height = -1

# variables that will be handy later
surrounding_tiles = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
surrounding_tiles_cross = [[-1, 0], [1, 0], [0, -1], [0, 1]]
surrounding_tiles_large = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1], [-2, -1], [-2, 0], [-2, 1], [2, -1], [2, 0], [2, 1], [-1, -2], [0, -2], [1, -2], [-1, 2], [0, 2], [1, 2]]

start_delay = 0
enable_prints = True

while True:
	i = input("current diffuculty setting / command: ")
	if i == "exit":
		quit()
	elif i == "delay":
		start_delay = float(input("set delay: "))
	elif i == "prints":
		enable_prints = not enable_prints
		print("prints are now set to: ", enable_prints)
	elif i == "hard":
		flag_total = 99
		width = 24
		height = 20
		break
	elif i == "medium":
		flag_total = 40
		width = 18
		height = 14
		break
	elif i == "easy":
		flag_total = 10
		width = 10
		height = 8
		break
	else:
		print("invalid")

time.sleep(start_delay)

# take the screenshot
image = pyautogui.screenshot()
image = np.array(image)


# save the normal screenshot
# cv2.imwrite("screenshot.png", cv2.cvtColor(image, cv2.COLOR_BGR2RGB));


# identify the play area
img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

hsv_color1 = np.asarray([79, 156, 206])
hsv_color2 = np.asarray([81, 166, 216])

mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)


# show the mask
# cv2.imwrite("mask.png", mask);


# get the location and size of the box
contours, hierarchy = cv2.findContours(mask.copy(), 1, 1)
x,y,w,h = cv2.boundingRect(contours[0])


# calculate where each click should be
box_size = w / width

base_x = x + box_size/2
base_y = y + box_size/2



# -------------------------------actually solving the puzzle--------------------------------#

#function for image processing

lower_tan = np.array([100, 70, 204])
upper_tan = np.array([110, 80, 244])
lower_green = np.array([79, 155, 205])
upper_green = np.array([81, 170, 220])
def identify_number(tile_img):
	tile_img = tile_img[int(box_size*0.15):int(box_size*0.85), int(box_size*0.15):int(box_size*0.85)]

	mask_tan = cv2.inRange(tile_img, lower_tan, upper_tan)
	mask_green = cv2.inRange(tile_img, lower_green, upper_green)

	mask = cv2.bitwise_not(cv2.bitwise_or(mask_tan, mask_green))

	mask_total = np.sum(mask != 0)

	if mask_total < box_size:
		return identify_number_by_color(tile_img[0][0])

	color = [0, 0, 0]

	masked_image = cv2.bitwise_or(tile_img, tile_img, mask=mask)

	# remove the failed mask outliers (especially for the 3s)
	if any(masked_image[0][0]):
		#cv2.imwrite("mask_failed.jpg", masked_image)
		return -9

	for row in masked_image:
		for pxl in row:
			if any(pxl):
				for i in range(3):
					color[i] += pxl[i]

	for i in range(3):
		color[i] = int(color[i] / mask_total)

	c = identify_number_by_color(color)
	if c == -9:
		#cv2.imwrite("masked_{}_{}_{}.jpg".format(color[0], color[1], color[2]), masked_image)
		pass

	return c

def identify_number_by_color(color):
	if 20 <= color[0] <= 50 and 120 <= color[1] <= 170 and 190 <= color[2] <= 210:
		return 1
	elif 60 <= color[0] <= 100 and 110 <= color[1] <= 145 and 140 <= color[2] <= 170:
		return 2
	elif 100 <= color[0] <= 130 and 120 <= color[1] <= 180 and 150 <= color[2] <= 240:
		return 3
	elif 100 <= color[0] <= 160 and 125 <= color[1] <= 160 and 160 <= color[2] <= 185:
		return 4
	elif 90 <= color[0] <= 115 and 190 <= color[1] <= 225 and 130 <= color[2] <= 255:
		return 5
	elif 30 <= color[0] <= 60 and 140 <= color[1] <= 185 and 160 <= color[2] <= 185:
		return 6
	elif 55 <= color[0] <= 80 and 15 <= color[1] <= 50 and 0 <= color[2] <= 25:
		return 7
	elif 0 <= color[0] <= 0 and 0 <= color[1] <= 0 and 0 <= color[2] <= 0:
		return 8
	elif 75 <= color[0] <= 85 and 155 <= color[1] <= 170 and 200 <= color[2] <= 220:
		return -1
	elif 100 <= color[0] <= 110 and 70 <= color[1] <= 80 and 204 <= color[2] <= 243:
		return 0

	#print("returned -9 for:", color)
	return -9

def print_board(board):

	for l in range(2):
		line = "     "
		for i in range(width):
			line += str("{:02d}".format(i)[l])
			line += " "
		print(line)
	print()

	for i in range(height):
		line = "{:02d}   ".format(i)
		for j in range(width):
			char = str(board[j][i]);
			if char == "0":
				line += " "
			elif char == "-1": 
				line += "?"
			elif char == "-2":
				line += "X"
			elif char == "-9":
				line += "E"
			else: 
				line += char
			line += " "
		print(line)



#functions for solving

def get_mines_and_empty(board, i, j):
	total_mines = 0
	total_empty = 0
	for offset in surrounding_tiles:
		tile_x = i + offset[0]
		tile_y = j + offset[1]
		if 0 <= tile_x < width and 0 <= tile_y < height:
			v = board[tile_x][tile_y]
			if v == -9:
				return (-999, -999)
			elif v == -2:
				total_mines += 1
			elif v == -1:
				total_empty += 1
	return (total_mines, total_empty)

def get_mines(board, i, j):
	total_mines = 0
	for offset in surrounding_tiles:
		tile_x = i + offset[0]
		tile_y = j + offset[1]
		if 0 <= tile_x < width and 0 <= tile_y < height:
			v = board[tile_x][tile_y]
			if v == -9:
				return -999
			elif v == -2:
				total_mines += 1
	return total_mines

def get_empty(board, i, j):
	total_empty = 0
	for offset in surrounding_tiles:
		tile_x = i + offset[0]
		tile_y = j + offset[1]
		if 0 <= tile_x < width and 0 <= tile_y < height:
			v = board[tile_x][tile_y]
			if v == -9:
				return -999
			elif v == -1:
				total_empty += 1
	return total_empty

def is_known_tile(board, i, j):
	if not 0 <= i < width:
		return True
	elif not 0 <= j < height:
		return True
	elif board[i][j] == -1:
		return False
	return True

def adjacent_open_tile_postions(board, i, j):
	tiles = set()
	for offset in surrounding_tiles:
		tile_x = i + offset[0]
		tile_y = j + offset[1]
		if 0 <= tile_x < width and 0 <= tile_y < height:
			v = board[tile_x][tile_y]
			if v == -1:
				tup = (tile_x, tile_y)
				tiles.add(tup)
	return tiles

def get_effective_board(board):
	effective_board = [[-1 for i in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			if board[i][j] >= 1:
				effective_board[i][j] = board[i][j] - get_mines(board, i, j)
	return effective_board




# on start - perform the initial click
pyautogui.click(base_x + box_size*(width/2 - 1), base_y + box_size*(height/2 - 1))
time.sleep(1)


# important variables
board = [[-1 for i in range(height)] for i in range(width)]
total_loops_without_progress = 0

# the main solve loop
while True:
	# gather data about the board
	board_img = cv2.cvtColor(np.array(pyautogui.screenshot().crop((x, y, x+w, y+h))), cv2.COLOR_BGR2HSV)

	for i in range(width):
		for j in range(height):

			#cv2.imwrite("box.jpg", board_img[int(j*box_size):int((j+1)*box_size), int(i*box_size):int((i+1)*box_size)])

			number = identify_number(board_img[int(j*box_size):int((j+1)*box_size), int(i*box_size):int((i+1)*box_size)])
			#if number == -9:
				#print("pos", i, j, "returned -9")

			if board[i][j] == -1 or board[i][j] == -9:
				board[i][j] = number
	#print_board(board)

	#quit if the board contains too many errorous tiles
	if sum(row.count(-9) for row in board) > width:
		print("quit due to error overload: too many tiles failed to identify")
		break

# -----------------------------------------------solver--------------------------------------------------
	actions = set()

	# mines first ---------------------------------------------------------------------------------------

	# standard mine algorithm
	for i in range(width):
		for j in range(height):
			# only numbered tiles
			current_tile_value = board[i][j]
			if current_tile_value >= 1:
				# count the number of mines and empty squares
				total_mines, total_empty = get_mines_and_empty(board, i, j)

				#failsafe
				if total_mines == -999:
					break

				# do something with the information
				if current_tile_value == total_empty + total_mines:
					for offset in surrounding_tiles:
						tile_x = i + offset[0]
						tile_y = j + offset[1]
						if 0 <= tile_x < width and 0 <= tile_y < height:
							v = board[tile_x][tile_y]
							if v == -1:
								board[tile_x][tile_y] = -2

								if enable_prints:
									print("basic mine rules marked", tile_x, tile_y, "because", i, j, "had", total_empty, "+", total_mines, "=", current_tile_value)

	# the effective board
	effective_board = get_effective_board(board)

	# the 1-2C+ rule
	for i in range(width):
		for j in range(height):
			if effective_board[i][j] >= 2:
				current_tile_open_adjacents = adjacent_open_tile_postions(board, i, j)

				for offset in surrounding_tiles_cross:
					tile_x = i + offset[0]
					tile_y = j + offset[1]
					if 0 <= tile_x < width and 0 <= tile_y < height:
						v = effective_board[tile_x][tile_y]
						if v == 1:
							adjacent_one_tile_open_adjacents = adjacent_open_tile_postions(board, tile_x, tile_y)

							overlap = set()
							for tile in current_tile_open_adjacents:
								if tile in adjacent_one_tile_open_adjacents:
									overlap.add(tile)

							total_empty = get_empty(board, i, j)

							#failsafe
							if total_empty == -999:
								break

							if total_empty == effective_board[i][j] + (len(overlap) - 1):
								for location in current_tile_open_adjacents:
									if not location in overlap:
										board[location[0]][location[1]] = -2

										# update the effective board to avoid errors
										effective_board = get_effective_board(board)

										if enable_prints:
											print("1-2C+ rule marked", location[0], location[1], "because of", i, j, "with adjacent one tile", tile_x, tile_y)

	# open tiles second -------------------------------------------------------------

	won = False
	# every mine rule
	total_marked = 0
	for i in range(width):
		for j in range(height):
			if board[i][j] == -2:
				total_marked += 1

	if total_marked == flag_total:
		for i in range(width):
			for j in range(height):
				if board[i][j] == -1:
					tup = (i, j)
					actions.add(tup)

		# game identified as won
		if enable_prints:
			print("all mines identified: clear board")

		for action in actions:
			pyautogui.click(base_x + box_size*action[0], base_y + box_size*action[1])

		pyautogui.moveTo(base_x + box_size*width, base_y + box_size*height)

		if enable_prints:
			print()
			print_board(board)
			print()

		print("game won")
		break



	# standard "all marked" algorithm
	for i in range(width):
		for j in range(height):
			# only numbered tiles
			current_tile_value = board[i][j]
			if current_tile_value >= 1:
				# count the number of mines and empty squares
				total_mines = get_mines(board, i, j)

				#failsafe
				if total_mines == -999:
					break

				# do something with the information
				if current_tile_value == total_mines:
					for offset in surrounding_tiles:
						tile_x = i + offset[0]
						tile_y = j + offset[1]
						if 0 <= tile_x < width and 0 <= tile_y < height:
							v = board[tile_x][tile_y]
							if v == -1:
								tup = (tile_x, tile_y)
								actions.add(tup)

								if enable_prints:
									print("basic open rules opened", tile_x, tile_y, "becuase", i, j, "had", total_mines, "=", current_tile_value)

	# the 1-1+ rule
	for i in range(width):
		for j in range(height):
			if effective_board[i][j] == 1:
				current_tile_open_adjacents = adjacent_open_tile_postions(board, i, j)

				for offset in surrounding_tiles_large:
					tile_x = i + offset[0]
					tile_y = j + offset[1]
					if 0 <= tile_x < width and 0 <= tile_y < height:
						v = effective_board[tile_x][tile_y]
						if v == 1:
							adjacent_one_tile_open_adjacents = adjacent_open_tile_postions(board, tile_x, tile_y)

							overlap = set()
							for tile in current_tile_open_adjacents:
								if tile in adjacent_one_tile_open_adjacents:
									overlap.add(tile)

							if len(overlap) == len(adjacent_one_tile_open_adjacents):
								for location in current_tile_open_adjacents:
									if not location in overlap:
										tup = (location[0], location[1])
										actions.add(tup)

										if enable_prints:
											print("1-1+ rule opened", location[0], location[1], "because of", i, j, "with adjacent one tile", tile_x, tile_y)


# ----------------------------------------------solver end-------------------------------------------

	#print(actions)
	for action in actions:
		pyautogui.click(base_x + box_size*action[0], base_y + box_size*action[1])

	pyautogui.moveTo(base_x + box_size*width, base_y + box_size*height)

	if enable_prints:
		print()
		print_board(board)
		print("-" * width*2)

	if len(actions) != 0:
		total_loops_without_progress = 0
		time.sleep(0.7)
	else:
		total_loops_without_progress += 1

	if total_loops_without_progress >= 3:
		print("no progress can be made by this bot: quitting")
		break


exit()