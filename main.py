import cv2
import mediapipe as mp
import math
import time
import pyautogui
pyautogui.FAILSAFE = False


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_hands = mp.solutions.hands

current_control = 'up'
new_control = ''
speed = 1


# Tạo webcam:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
	model_complexity=0,
	min_detection_confidence=0.5,
	min_tracking_confidence=0.5) as hands:
	while cap.isOpened():
		success, image = cap.read()
		if not success:
			print("Ignoring empty camera frame.")
			# Nếu đang tải video, hãy sử dụng 'ngắt' thay vì 'tiếp tục'.
			continue

		# To improve performance, optionally mark the image as not writeable to
		# pass by reference.
		image.flags.writeable = False
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		results = hands.process(image)

		# Draw the hand annotations on the image.
		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		height, width, _ = image.shape # Lấy chiều cao và bề ngang của frame

		hand_centers = []
		if results.multi_hand_landmarks: # Detect được bàn tay
			
			for hand_landmarks in results.multi_hand_landmarks:

				hand_centers.append([int(hand_landmarks.landmark[9].x * width), int(hand_landmarks.landmark[9].y * height)])
				# mp_drawing.draw_landmarks(
				# 	image,
				# 	hand_landmarks,
				# 	mp_hands.HAND_CONNECTIONS,
				# 	mp_drawing_styles.get_default_hand_landmarks_style(),
				# 	mp_drawing_styles.get_default_hand_connections_style())
		
		
		# Kiểm tra hướng di chuyển từ camera để tương tác với bàn phím
		if len(hand_centers) == 2:
			cv2.line(image, (hand_centers[0][0], hand_centers[0][1]), (hand_centers[1][0], hand_centers[1][1]), (0, 255, 0), 5)
			center_x = (hand_centers[0][0] + hand_centers[1][0]) // 2
			center_y = (hand_centers[0][1] + hand_centers[1][1]) // 2
			radius = int(math.sqrt((hand_centers[0][0] - hand_centers[1][0]) ** 2 + (hand_centers[0][1] - hand_centers[1][1])**2) //2)
			cv2.circle(image, (center_x, center_y), radius, (0, 255, 0), 5)
			cv2.circle(image, (center_x, center_y), 5, (0, 255, 0), 5)
			
			x1 = hand_centers[0][0]
			y1 = hand_centers[0][1]

			x2 = hand_centers[1][0]
			y2 = hand_centers[1][1]

			if x1 > x2:
				x2, x1 = x1, x2
				y2, y1 = y1, y2

			

			if abs(y1 - y2) < 30:
				new_control = 'up'
				print('up')

			elif y1 < y2 and x1 < x2:
				new_control = 'left'
				print('left')
			else:
				new_control = 'right'
				print('right')
			# assert(False)
		else:
			new_control = 'down'
			print('down')


		speed += 7
		if new_control != current_control:
			speed = 0
			pyautogui.keyUp(current_control)
			current_control = new_control
			pyautogui.keyDown(current_control)

				
		# Vẽ chú thích hướng di chuyển
		text = ''
		if current_control == 'up':
			text = '^'
		elif current_control == 'down':
			text = 'v'
		elif current_control == 'left':
			text = '>'
		else:
			text = '<'

		
		cv2.putText(image, text, (45, height-20), cv2.FONT_HERSHEY_TRIPLEX, 2, (0, 255, 0), 2)
		cv2.putText(image, '[ ]', (20, height-20), cv2.FONT_HERSHEY_TRIPLEX, 2, (0,0,255), 3)

		# show và lật ngược camera (vì camera mặc định bị ngược)
		cv2.imshow('Salmon control', cv2.flip(image, 1)) 

		if cv2.waitKey(10) & 0xFF == 27:
			break
cap.release()
cv2.destroyAllWindows()
