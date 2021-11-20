board = [
	[7,8,0,4,0,0,1,2,0],
	[6,0,0,0,7,5,0,0,9],
	[0,0,0,6,0,1,0,7,8],
	[0,0,7,0,4,0,2,6,0],
	[0,0,1,0,5,0,9,3,0],
	[9,0,4,0,6,0,0,0,5],
	[0,7,0,3,0,0,0,1,2],
	[1,2,0,0,0,7,4,0,0],
	[0,4,9,2,0,6,0,0,7]
]

def solve(db):
	counter = empty_space(db)
	if not counter:
		return True
	else:
		row, col = counter

	for i in range(1,10):
		if check(db, i, (row, col)):
			db[row][col] = i

			if solve(db):
				return True

			db[row][col] = 0

	return False

def check(db, n, pos):

	#checking x-axis and y-axis

	for i in range(len(db[0])):
		if db[pos[0]][i] == n and pos[1] != i:
			return False

	for i in range(len(db)):
		if db[i][pos[1]] == n and pos[0] != i:
			return False

	#checking per box on the board

	x = pos[1] // 3
	y = pos[0] // 3

	for i in range(y*3, y*3 + 3):
		for j in range(x*3, x*3 + 3):
			if db[i][j] == n and (i,j) != pos:
				return False

	return True

def default_board(db):
	for i in range(len(db)):
		if i % 3 == 0 and i != 0:
			print("---------------------")
		for j in range(len(db[0])):
			if j % 3 == 0 and j != 0:
				print("| ", end="")

			if j == 8:
				print(db[i][j])
			else:
				print(str(db[i][j]) + " ", end="")

def empty_space(db):
	for i in range(len(db)):
		for j in range(len(db[0])):
			if db[i][j] == 0:
				return (i, j) # y-axis(row), x-axis(column)
	return None

default_board(board)
print("\n=====================\n")
solve(board)
default_board(board)