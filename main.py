import random


class BoardOutException(Exception):
	pass


class Dot:
	def __init__(self,x, y):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y


class Ship:
	def __init__(self, length, start_dot, direction):
		self.length = length
		self.start_dot = start_dot
		self.direction = direction
		self.health_point = length

	def dots(self):
		ship_points = []
		x = self.start_dot.x
		y = self.start_dot.y

		for i in range(self.length):
			if self.direction == 'вертикальное':
				ship_points.append(Dot(x, y + i))
			else:
				ship_points.append(Dot(x + i, y))

		return ship_points


class Board:
	def __init__(self):
		self.board = [['0' for _ in range(6)] for _ in range(6)]
		self.ships = []
		self.hid = False
		self.live_ships = 0
		self.contoured = [[False for _ in range(6)] for _ in range(6)]
		self.missed = [[False for _ in range(6)] for _ in range(6)]
		self.destroyed = [[False for _ in range(6)] for _ in range(6)]


	def add_ship(self, ship):
		for dot in ship.dots():
			if self.out(dot) or self.board[dot.x][dot.y] == '■' or self.board[dot.x][dot.y] == '.':
				raise BoardOutException('Невозможно установить корабль')
		self.ships.append(ship)
		for dot in ship.dots():
				self.board[dot.x][dot.y] = '■'
		self.live_ships += 1
		self.contour(ship)

	def display(self):
		print('_|', end='')
		for i in range(6):
			print(f'{i+1}|', end='')
		print()
		for row in range(6):
			print(f'{row+1}|', end='')
			for col in range(6):
				if self.hid and self.board[row][col] == '■' and not any(
						[s.health_point for s in self.ships if Dot(row, col) in s.dots()]):
					print('Т|', end='')
				elif self.hid and not self.destroyed[row][col] and (
						self.board[row][col] == '■' or (self.contoured[row][col] and not self.missed[row][col])):
					print('0|', end='')
				else:
					print(f'{self.board[row][col]}|', end='')
			print()

	def contour(self, ship, destroy=False):
		for dot in ship.dots():
			for j in range(dot.y-1, dot.y + 2):
				for i in range(dot.x-1, dot.x + 2):
					if not self.out(Dot(i, j)):
						if self.board[i][j] == '0':
							self.board[i][j] = '.' if not destroy else 'Т'
							self.contoured[i][j] = True
							if destroy:
								self.destroyed[i][j] = True

	def out(self, dot):
		return dot.x < 0 or dot.x >= 6 or dot.y < 0 or dot.y >= 6

	def shot(self,dot):
		if self.out(dot):
			raise BoardOutException('Не стреляй мимо поля')
		if self.board[dot.x][dot.y] == 'X' or self.board[dot.x][dot.y] == 'Т':
			raise BoardOutException('Сюда уже стреляли')

		for ship in self.ships:
			if dot in ship.dots():
				self.board[dot.x][dot.y] = 'X'
				ship.health_point -= 1
				if ship.health_point == 0:
					self.live_ships -= 1
					self.contour(ship, True)
					for d in ship.dots():
						self.destroyed[d.x][d.y] = True
					print('Корабль уничтожен')
					return True
				else:
					print('Попал, стреляй еще')
					return True
		self.board[dot.x][dot.y] = 'Т'
		self.missed[dot.x][dot.y] = True
		print('Промахнулся...')
		return False


class Player:
	def __init__(self):
		self.own_board = Board()
		self.enemy_board = Board()

	def ask(self):
		pass

	def move(self, enemy_board):
		while True:
			try:
				dot = self.ask()
				shot_result = self.enemy_board.shot(dot)
				if shot_result is True:
					return True
				else:
					return False
			except Exception as e:
				print(f'Error: {str(e)}. Пожалуйста попробуй еще.')


class AI(Player):
	def ask(self):
		dot = Dot(random.randint(0, 5),random.randint(0, 5))
		return dot


class User(Player):
	def ask(self):
		x = int(input("Введите номер строки:"))
		y = int(input("Введите номер столбца:"))
		return Dot(x-1, y-1)


class Game:
	def __init__(self):
		self.player_user = User()
		self.user_board = Board()
		self.player_ai = AI()
		self.ai_board = Board()
		self.player_ai.own_board.hid = True
		self.random_board(self.player_user.own_board)
		self.random_board(self.player_ai.own_board)
		self.player_user.enemy_board = self.player_ai.own_board
		self.player_ai.enemy_board = self.player_user.own_board


	def random_board(self, board):
		self.ships = [3, 2, 2, 1, 1, 1]
		for i in self.ships:
			while True:
				direction = random.choice(['вертикальное', 'горизонтальное'])
				if direction == 'вертикальное':
					x, y = random.randint(0, 5), random.randint(0, 5 - i)
				else:
					x, y = random.randint(0, 5 - i), random.randint(0, 5)

				ship = Ship(i, Dot(x, y), direction)
				try:
					board.add_ship(ship)
					break
				except BoardOutException:
					continue


	def greet(self):
		print("Привет!!! Добро пожаловать в игру : МОРСКОЙ БОЙ!")
		print("В игре учавствует 6 кораблей \n"
		      "1 - трехпалубный \n"
		      "2 - двухпалубных \n"
		      "3 - однопалубных")
		print("Для осуществления выстрела необходимо ввести номер строки от 1 до 6 \n"
		      "И номер столбца в том же диапазоне.")
		print("Побеждает игрок первым уничтоживший все вражеские корабли!\n"
		      "Удачи в бою АДМИРАЛ!!!")


	def loop(self):
		while True:
			print('Ваша доска:')
			self.player_user.own_board.display()
			print('Доска противника:')
			self.player_user.enemy_board.display()
			while self.player_user.move(self.player_ai.own_board):
				print('Ваша доска:')
				self.player_user.own_board.display()
				print('Доска противника:')
				self.player_user.enemy_board.display()
			if self.player_ai.own_board.live_ships == 0:
				print("Пользователь выиграл!")
				break
			print('Доска ИИ:')
			self.player_ai.own_board.display()
			print('Ваша доска:')
			self.player_user.own_board.display()
			while self.player_ai.move(self.player_user.own_board):
				print('Доска ИИ:')
				self.player_ai.own_board.display()
				print('Ваша доска:')
				self.player_user.own_board.display()
			if self.player_user.own_board.live_ships == 0:
				print("ИИ выиграл!")
				break

	def start(self):
		self.greet()
		self.loop()


s1 = Game()
s1.start()

















